import psycopg2
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os
load_dotenv()
model = SentenceTransformer('all-MiniLM-L6-v2')
conn = psycopg2.connect(os.getenv("SUPABASE_DB_URL"))
cur = conn.cursor()
documents = [
    {"title": "Unit Testing Benefits", "body": "Unit tests improve software quality and reduce bugs."},
    {"title": "Renewable Energy Storage", "body": "Batteries and pumped hydro are common methods of energy storage."},
    {"title": "Improve Page Performance", "body": "Avoid render-blocking resources to enhance web page speed."},
    {"title": "Test Coverage vs Confidence", "body": "High test coverage does not always mean high confidence in software."},
    {"title": "Store Vectors for Similarity Search", "body": "Vectors can be stored in Postgres using pgvector for semantic search."},
]

for doc in documents:
    embedding = model.encode(doc['body']).tolist() 
    cur.execute(
        "INSERT INTO documents (title, body, embedding) VALUES (%s, %s, %s)",
        (doc['title'], doc['body'], embedding)
    )

conn.commit()
cur.close()
conn.close()
print("Sample documents inserted successfully!")
