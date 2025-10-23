# Lexomat Intelligence - Hybrid Search Demo

A full-stack hybrid search application combining keyword-based full-text search with semantic vector search, built with Next.js, FastAPI, and Supabase.

![Hybrid Search Demo](https://img.shields.io/badge/Status-Live-success)
![Next.js](https://img.shields.io/badge/Next.js-14-black)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-336791)

## 🔗 Links

- **Live Demo:** [https://lexomat-intelligence.vercel.app/](https://lexomat-intelligence.vercel.app/)
- **GitHub Repository:** [https://github.com/ChanchalSen09/Lexomat-Intelligence](https://github.com/ChanchalSen09/Lexomat-Intelligence)

## 📋 Overview

This application demonstrates intelligent hybrid search by combining:

1. **Keyword Search** - PostgreSQL Full-Text Search (FTS) with `ts_rank` scoring
2. **Semantic Search** - Dense vector embeddings using pgvector and cosine similarity
3. **Hybrid Search** - Weighted combination of both approaches for optimal relevance

## ✨ Features

- 🔍 **Three Search Modes**
  - Keyword-only (traditional full-text search)
  - Semantic-only (AI-powered vector similarity)
  - Hybrid (best of both worlds - default)

- 📊 **Transparent Scoring**
  - Individual FTS scores
  - Vector similarity scores
  - Combined hybrid scores

- 🎨 **Modern UI**
  - Clean, responsive interface
  - Real-time search results
  - Mode toggle for comparison

- 🚀 **Production-Ready**
  - Deployed frontend on Vercel
  - Backend API on Railway
  - Supabase managed database

## 🏗️ Architecture
```
┌─────────────┐         ┌──────────────┐         ┌───────────────┐
│   Next.js   │────────▶│   FastAPI    │────────▶│   Supabase    │
│  Frontend   │   API   │   Backend    │   SQL   │  PostgreSQL   │
│  (Vercel)   │◀────────│  (Railway)   │◀────────│  + pgvector   │
└─────────────┘         └──────────────┘         └───────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Sentence Trans.  │
                    │  (all-MiniLM-L6) │
                    └──────────────────┘
```

## 🛠️ Tech Stack

### Frontend
- **Framework:** Next.js 14 (App Router)
- **Styling:** Tailwind CSS
- **UI Components:** Custom React components
- **Deployment:** Vercel

### Backend
- **Framework:** FastAPI (Python 3.11)
- **Embeddings:** sentence-transformers
- **Model:** all-MiniLM-L6-v2 (384-dimensional vectors)
- **Database Client:** asyncpg
- **Deployment:** Railway

### Database
- **Platform:** Supabase
- **Database:** PostgreSQL 15
- **Extensions:** pgvector
- **Features:** Full-Text Search, Vector Similarity

## 🔬 Hybrid Scoring Formula

The hybrid search combines normalized scores from both search methods:
```python
Hybrid Score = 0.5 × normalize(FTS_rank) + 0.5 × (1 - cosine_distance)
```

**Where:**
- `FTS_rank` = PostgreSQL `ts_rank()` score for keyword relevance
- `cosine_distance` = pgvector `<=>` operator for semantic similarity
- Weights: 50% keyword + 50% semantic (customizable)

**Normalization:**
- FTS scores are already normalized by `ts_rank`
- Vector scores computed as `1 - cosine_distance` (higher = more similar)

## 📚 Sample Dataset

The database contains **40+ curated documents** across multiple technology domains:

- **AI/ML:** Machine learning, neural networks, model deployment
- **Web Development:** React, performance optimization, SSR
- **Cloud Computing:** Docker, serverless
- **DevOps:** CI/CD, testing, monitoring
- **Databases:** SQL, vector search, indexing


## 🔍 Example Queries

Try these queries to see the hybrid search in action:

### 1. **"benefits of unit testing"**
Tests keyword matching for development best practices

### 2. **"machine learning model deployment"**
Combines technical terminology with semantic understanding

### 3. **"improve page performance"**
Searches for web optimization techniques

### 4. **"vector similarity search"**
Technical query about database and AI concepts

### 5. **"cloud infrastructure scalability"**
Tests understanding across related cloud computing concepts

### 6. **"react server components"**
Modern web development framework features

### 7. **"continuous integration pipeline"**
DevOps and automation workflows

## 📊 Search Modes Comparison

| Mode | Speed | Accuracy | Use Case |
|------|-------|----------|----------|
| **Keyword** | ⚡ Fastest | Good for exact terms | Known terminology |
| **Semantic** | 🔄 Medium | Best for concepts | Natural language |
| **Hybrid** | 🎯 Balanced | Highest relevance | General purpose |


### Embedding Model Choice

**all-MiniLM-L6-v2** was chosen for:
- ✅ Fast inference (384 dimensions vs 768+)
- ✅ Good quality-to-speed ratio
- ✅ Suitable for short-to-medium documents
- ✅ Low memory footprint

Alternatives to consider:
- `all-mpnet-base-v2` - Higher quality, slower
- `OpenAI text-embedding-ada-002` - Best quality, API cost
- Domain-specific models - If specialized content

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 👤 Author

**Chanchal Sen**

- GitHub: [@ChanchalSen09](https://github.com/ChanchalSen09)
- Project: [Lexomat Intelligence Demo](https://lexomat-intelligence.vercel.app/)

## 🙏 Acknowledgments

- Supabase for managed PostgreSQL + pgvector
- Sentence Transformers for embedding models
- Vercel for seamless frontend deployment
- Railway for backend hosting

---

**Built with ❤️ for intelligent search experiences**
