Prereqs: Node 18+, Python 3.11+, Docker Desktop (only if you want local Qdrant; you already used it), Tavily key.

Env: example .env (KB_BACKEND, QDRANT_URL, SIMILARITY_THRESHOLD, MCP vars, STRICT_MCP_ONLY=1).

Run:

Qdrant: docker run -p 6333:6333 -v qdrant_storage:/qdrant/storage qdrant/qdrant:latest

Backend:

cd api && .\.venv\Scripts\activate
pip install -r requirements.txt
python -m scripts.ingest_kb ..\data\sample_kb.jsonl
uvicorn app.main:app --reload --port 8000


Frontend: cd web && npm i && npm run dev