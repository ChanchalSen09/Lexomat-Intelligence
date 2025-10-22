from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
import asyncpg
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="Lexomat Intelligence API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ThreadPool for blocking model calls
executor = ThreadPoolExecutor(max_workers=2)

# Database pool
db_pool: asyncpg.pool.Pool = None

# Model (lazy-loaded)
model = None

async def get_model():
    global model
    if model is None:
        from sentence_transformers import SentenceTransformer
        logger.info("Loading embedding model...")
        model = SentenceTransformer("paraphrase-MiniLM-L3-v2")  # smaller model
        logger.info("Model loaded successfully")
    return model

# Startup event: initialize DB
@app.on_event("startup")
async def startup():
    global db_pool
    logger.info("Starting up... Initializing database pool")
    try:
        db_pool = await asyncpg.create_pool(
            dsn=os.getenv("SUPABASE_DB_URL"),
            min_size=1,
            max_size=5,
            command_timeout=60
        )
        logger.info("Database pool created successfully")
    except Exception as e:
        logger.error(f"Failed to create database pool: {e}")
        raise

# Shutdown event: close DB
@app.on_event("shutdown")
async def shutdown():
    global db_pool
    if db_pool:
        logger.info("Shutting down... Closing database pool")
        await db_pool.close()

# Pydantic request model
class SearchRequest(BaseModel):
    query: str
    mode: str = "hybrid"

# Get embedding (async)
async def get_embedding(text: str):
    model_instance = await get_model()
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, model_instance.encode, text)

# Health check endpoints
@app.get("/")
async def health_check():
    return {
        "status": "healthy",
        "message": "Lexomat Intelligence API is running",
        "endpoints": ["/search"]
    }

@app.get("/health")
async def health():
    try:
        async with db_pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}

# Search endpoint
@app.post("/search")
async def search(req: SearchRequest):
    logger.info(f"Search request received - Query: {req.query}, Mode: {req.mode}")
    
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        # Get embedding
        query_embedding = await get_embedding(req.query)
        query_embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"

        async with db_pool.acquire() as conn:
            if req.mode == "keyword":
                sql = """
                    SELECT id, title, body,
                    ts_rank(to_tsvector('english', title || ' ' || body), plainto_tsquery('english', $1)) AS fts_score
                    FROM documents
                    WHERE to_tsvector('english', title || ' ' || body) @@ plainto_tsquery('english', $1)
                    ORDER BY fts_score DESC
                    LIMIT 10;
                """
                results = await conn.fetch(sql, req.query)
                logger.info(f"Keyword search returned {len(results)} results")

            elif req.mode == "semantic":
                sql = """
                    SELECT id, title, body,
                    1 - (embedding <=> $1::vector) AS vector_score
                    FROM documents
                    ORDER BY vector_score DESC
                    LIMIT 10;
                """
                results = await conn.fetch(sql, query_embedding_str)
                logger.info(f"Semantic search returned {len(results)} results")

            else:  # hybrid
                sql = """
                    SELECT id, title, body,
                    ts_rank(to_tsvector('english', title || ' ' || body), plainto_tsquery('english', $1)) AS fts_score,
                    1 - (embedding <=> $2::vector) AS vector_score
                    FROM documents
                    ORDER BY 0.5 * COALESCE(ts_rank(to_tsvector('english', title || ' ' || body), plainto_tsquery('english', $1)), 0) 
                             + 0.5 * (1 - (embedding <=> $2::vector)) DESC
                    LIMIT 10;
                """
                results = await conn.fetch(sql, req.query, query_embedding_str)
                logger.info(f"Hybrid search returned {len(results)} results")

        # Prepare output
        output = []
        for r in results:
            row = {
                "id": r["id"],
                "title": r["title"],
                "body": r["body"]
            }
            if "fts_score" in r:
                row["fts_score"] = float(r["fts_score"]) if r["fts_score"] else 0.0
            if "vector_score" in r:
                row["vector_score"] = float(r["vector_score"])
            output.append(row)

        logger.info(f"Returning {len(output)} results")
        return {"results": output, "count": len(output)}

    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
