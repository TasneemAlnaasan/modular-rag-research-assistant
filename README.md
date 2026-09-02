

# 🔍 Multi-Source Research Assistant

A **Modular RAG** system that routes user questions to the right data source — vector database, SQL database, or live web search — instead of relying on a single fixed retrieval method.

🔗 **Live demo:** [Frontend]( https://modular-rag-research-assistant-frontend.onrender.com) | [API docs](https://modular-rag-research-assistant.onrender.com/docs)

---

## 💡 The idea

Most RAG systems assume all knowledge lives in one place (usually documents). In reality, knowledge is scattered:

- **Company profiles** → best answered from stored documents
- **Numeric/financial data** → best answered with a structured database query
- **Recent news** → only answerable with a live web search

This project uses an LLM-powered **router** to classify each question and dynamically send it to the right source — no single fixed pipeline.

## 🏗️ Architecture

```

User question
      │
      ▼
  Router Node (Groq) — classifies: document / sql / web / none
      │
   ┌──┼──┬──────┐
   ▼  ▼  ▼      ▼
 Docs SQL Web  Fallback
   │  │  │      │
   └──┼──┘      │
      ▼         │
 Generation Node │
      │         │
      └────┬────┘
           ▼
    Final answer to user
```

- **Router** — Groq LLM classifies the question using a few-shot prompt
- **Document search** — ChromaDB vector search over company profiles (semantic similarity)
- **SQL search** — Text-to-SQL: Groq translates natural language into a validated `SELECT` query over a SQLite database
- **Web search** — Tavily API for current news and events
- **Generation** — Groq LLM composes a natural-language answer from whichever source was used

## 📊 Domain

The dataset covers 7 major AI companies: **OpenAI, Anthropic, Google DeepMind, Groq, Mistral, Meta AI, Hugging Face**.

- `data/documents/` — short written profiles (company background, products, vision)
- `data/company_data.db` — SQLite table with funding, valuation, and founding data

> The architecture is fully domain-agnostic — swapping in a different dataset (e.g. drug information, model pricing comparisons) requires no changes to the routing, retrieval, or generation logic.

## 🛠️ Tech stack

| Layer | Tool |
|---|---|
| LLM inference | Groq (`openai/gpt-oss-20b`) |
| Orchestration | LangGraph |
| Vector search | ChromaDB + `sentence-transformers` |
| Structured data | SQLite |
| Web search | Tavily API |
| API | FastAPI |
| UI | Streamlit |
| Deployment | Docker + Render |
| CI | GitHub Actions |

All tools are free-tier.

## 🚀 Running locally

```bash
# 1. Clone and install
git clone https://github.com/TasneemAlnaasan/modular-rag-research-assistant.git
cd modular-rag-research-assistant
pip install -r requirements.txt

# 2. Add API keys
cp .env.example .env   # then fill in GROQ_API_KEY and TAVILY_API_KEY

# 3. Build the vector database
python -m src.ingest_documents

# 4. Run the backend
uvicorn src.api:app --reload --port 8000

# 5. Run the frontend (separate terminal)
streamlit run src/ui.py
```

## 📁 Project structure

```
├── data/
│   ├── documents/          # company text profiles (vector DB source)
│   ├── company_data.db     # SQLite database
│   ├── init_db.py          # creates + seeds the database
│   └── update_db.py        # manual data update helper
├── src/
│   ├── router.py            # question classifier
│   ├── search_documents.py  # ChromaDB retrieval
│   ├── query_sql.py         # Text-to-SQL
│   ├── search_web.py        # Tavily web search
│   ├── graph.py              # LangGraph assembly
│   ├── api.py                # FastAPI backend
│   ├── ui.py                 # Streamlit frontend
│   └── logger.py             # centralized logging
├── Dockerfile                # backend container
├── Dockerfile.streamlit      # frontend container
└── .github/workflows/ci.yml  # CI pipeline
```

## ⚠️ Known limitations

- The router classifies once, upfront — there's no post-generation quality check that re-routes to a different source if the first one returns an insufficient answer (unlike a corrective-RAG setup).
- Free-tier hosting means the backend may take 30–60 seconds to "wake up" after periods of inactivity.
- Financial data (funding/valuation) is manually maintained and reflects a point-in-time snapshot, not a live feed.

## 🔮 Possible extensions

- Add a quality-check step after generation that falls back to web search if the retrieved context doesn't answer the question
- Swap the dataset domain (e.g. model pricing/performance comparisons) without touching the core architecture
