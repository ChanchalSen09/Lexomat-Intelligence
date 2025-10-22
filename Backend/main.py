from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import asyncpg
import os
from dotenv import load_dotenv
import asyncio
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

# FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load SentenceTransformer model (sync)
model = SentenceTransformer("all-MiniLM-L6-v2")

# Thread pool for running synchronous encode() in async
executor = ThreadPoolExecutor(max_workers=2)

# Database connection pool (async)
db_pool: asyncpg.pool.Pool = None

async def init_db_pool():
    global db_pool
    db_pool = await asyncpg.create_pool(dsn=os.getenv("SUPABASE_DB_URL"), min_size=1, max_size=10)

# Run pool initialization on startup
@app.on_event("startup")
async def startup():
    await init_db_pool()

# Request model
class SearchRequest(BaseModel):
    query: str
    mode: str = "hybrid"

# Helper: async encode
async def get_embedding(text: str):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, model.encode, text)

@app.post("/search")
async def search(req: SearchRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        query_embedding = await get_embedding(req.query)
        query_embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"  # asyncpg vector as text

        async with db_pool.acquire() as conn:
            if req.mode == "keyword":
                results = await conn.fetch("""
                    SELECT id, title, body,
                    ts_rank(to_tsvector('english', title || ' ' || body), plainto_tsquery('english', $1)) AS fts_score
                    FROM documents
                    ORDER BY fts_score DESC
                    LIMIT 10;
                """, req.query)

            elif req.mode == "semantic":
                results = await conn.fetch("""
                    SELECT id, title, body,
                    1 - (embedding <=> $1::vector) AS vector_score
                    FROM documents
                    ORDER BY vector_score DESC
                    LIMIT 10;
                """, query_embedding_str)

            else:  # hybrid
                results = await conn.fetch("""
                    SELECT id, title, body,
                    ts_rank(to_tsvector('english', title || ' ' || body), plainto_tsquery('english', $1)) AS fts_score,
                    1 - (embedding <=> $2::vector) AS vector_score
                    FROM documents
                    ORDER BY 0.5 * ts_rank(to_tsvector('english', title || ' ' || body), plainto_tsquery('english', $1)) 
                             + 0.5 * (1 - (embedding <=> $2::vector)) DESC
                    LIMIT 10;
                """, req.query, query_embedding_str)

        output = []
        for r in results:
            row = {"id": r["id"], "title": r["title"], "body": r["body"]}
            if req.mode == "keyword":
                row["fts_score"] = float(r["fts_score"])
            elif req.mode == "semantic":
                row["vector_score"] = float(r["vector_score"])
            else:
                row["fts_score"] = float(r["fts_score"])
                row["vector_score"] = float(r["vector_score"])
            output.append(row)

        return output

    except Exception as e:
        print("Search error:", e)
        raise HTTPException(status_code=500, detail="Search failed. Check backend logs.")
