from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = SentenceTransformer('all-MiniLM-L6-v2')
conn = psycopg2.connect(os.getenv("SUPABASE_DB_URL"))
cur = conn.cursor()

class SearchRequest(BaseModel):
    query: str
    mode: str = "hybrid"

@app.post("/search")
def search(req: SearchRequest):
    query_embedding = model.encode(req.query).tolist()

    if req.mode == "keyword":
        cur.execute("""
            SELECT id, title, body,
            ts_rank(to_tsvector('english', title || ' ' || body), plainto_tsquery('english', %s)) AS fts_score
            FROM documents
            ORDER BY fts_score DESC
            LIMIT 10;
        """, (req.query,))
    elif req.mode == "semantic":
        cur.execute("""
            SELECT id, title, body,
            1 - (embedding <=> %s::vector) AS vector_score
            FROM documents
            ORDER BY vector_score DESC
            LIMIT 10;
        """, (query_embedding,))
    else:  # hybrid
        cur.execute("""
            SELECT id, title, body,
            ts_rank(to_tsvector('english', title || ' ' || body), plainto_tsquery('english', %s)) AS fts_score,
            1 - (embedding <=> %s::vector) AS vector_score
            FROM documents
            ORDER BY 0.5 * ts_rank(to_tsvector('english', title || ' ' || body), plainto_tsquery('english', %s)) 
                     + 0.5 * (1 - (embedding <=> %s::vector)) DESC
            LIMIT 10;
        """, (req.query, query_embedding, req.query, query_embedding))

    results = cur.fetchall()
    output = []
    for r in results:
        row = {"id": r[0], "title": r[1], "body": r[2]}
        if req.mode == "keyword":
            row["fts_score"] = r[3]
        elif req.mode == "semantic":
            row["vector_score"] = r[3]
        else:
            row["fts_score"] = r[3]
            row["vector_score"] = r[4]
        output.append(row)
    return output
