from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
import asyncpg
from sentence_transformers import SentenceTransformer
from mangum import Mangum

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model once
model = SentenceTransformer("all-MiniLM-L6-v2")
executor = ThreadPoolExecutor(max_workers=2)

# Singleton DB pool
db_pool: asyncpg.pool.Pool = None
async def get_db_pool():
    global db_pool
    if db_pool is None:
        db_pool = await asyncpg.create_pool(
            dsn=os.getenv("SUPABASE_DB_URL"),
            min_size=1,
            max_size=5
        )
    return db_pool

# Request model
class SearchRequest(BaseModel):
    query: str
    mode: str = "hybrid"

# Encode text asynchronously
async def get_embedding(text: str):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, model.encode, text)

@app.post("/search")
async def search(req: SearchRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        query_embedding = await get_embedding(req.query)
        query_embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"

        async with (await get_db_pool()).acquire() as conn:
            if req.mode == "keyword":
                sql = """
                    SELECT id, title, body,
                    ts_rank(to_tsvector('english', title || ' ' || body), plainto_tsquery('english', $1)) AS fts_score
                    FROM documents
                    ORDER BY fts_score DESC
                    LIMIT 10;
                """
                results = await conn.fetch(sql, req.query)

            elif req.mode == "semantic":
                sql = """
                    SELECT id, title, body,
                    1 - (embedding <=> $1::vector) AS vector_score
                    FROM documents
                    ORDER BY vector_score DESC
                    LIMIT 10;
                """
                results = await conn.fetch(sql, query_embedding_str)

            else:  # hybrid
                sql = """
                    SELECT id, title, body,
                    ts_rank(to_tsvector('english', title || ' ' || body), plainto_tsquery('english', $1)) AS fts_score,
                    1 - (embedding <=> $2::vector) AS vector_score
                    FROM documents
                    ORDER BY 0.5 * ts_rank(to_tsvector('english', title || ' ' || body), plainto_tsquery('english', $1)) 
                             + 0.5 * (1 - (embedding <=> $2::vector)) DESC
                    LIMIT 10;
                """
                results = await conn.fetch(sql, req.query, query_embedding_str)

        output = []
        for r in results:
            row = {
                "id": r["id"],
                "title": r["title"],
                "body": r["body"]
            }
            if "fts_score" in r:
                row["fts_score"] = float(r["fts_score"])
            if "vector_score" in r:
                row["vector_score"] = float(r["vector_score"])
            output.append(row)

        return output

    except Exception as e:
        print("Search error:", e)
        raise HTTPException(status_code=500, detail="Search failed. Check backend logs.")

# Vercel serverless handler
handler = Mangum(app)
