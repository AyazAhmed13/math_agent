🧮 Math Agent — KB-first with MCP Web Fallback

AI-powered math assistant that first searches its local knowledge base (Qdrant), and when no strong match is found, automatically falls back to a web search via MCP (Tavily MCP server) — all behind a clean React + FastAPI interface.

🚀 Quick Start
1️⃣ Backend Setup
cd api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt


Add .env:

KB_BACKEND=qdrant
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=math_kb
SIMILARITY_THRESHOLD=0.65
TOP_K=5
STRICT_MCP_ONLY=1
MCP_SEARCH_CMD=tavily-mcp
MCP_SEARCH_ARGS=--api-key tvly-dev-XXXXXXXXXXXX


Then:

# Start Qdrant (local)
docker run -p 6333:6333 -v qdrant_storage:/qdrant/storage qdrant/qdrant:latest

# Ingest KB
python -m scripts.ingest_kb ..\data\sample_kb.jsonl

# Run API
uvicorn app.main:app --reload --port 8000

2️⃣ Frontend Setup
cd web
npm install
npm run dev


Configure web/.env:

VITE_API_BASE=http://127.0.0.1:8000

🧠 Architecture Overview
React (Vite)
   │
   ▼
FastAPI (/answer)
   └── LangGraph Router
        ├─ KB route → Qdrant (FastEmbed)
        └─ Web route → MCP client → Tavily MCP → Tavily API
   ▼
Guardrails → Output (steps + answer + citations)
   ▼
Feedback API → /feedback → /feedback/report


Knowledge Base: Qdrant vector DB with FastEmbed embeddings

Web Search: MCP client wrapping Tavily API

Guardrails: Input filtering, output sanitization, similarity threshold

Human-in-the-loop: Feedback + analytics (/feedback/report)

✨ Key Features
Feature	Description
KB-first search	Queries Qdrant collection (math_kb) for similar problems
MCP web fallback	Uses MCP client (tavily-mcp) when KB has no strong match
FastEmbed	Lightweight sentence embeddings for efficient retrieval
LangGraph	Simple agentic flow: KB → Web → Synthesis
Guardrails	Blocks unsafe inputs and overlong outputs
Feedback	Thumbs up/down + comments stored in /feedback
Reports	Aggregates feedback stats (/feedback/report)
Frontend	React (Vite, Tailwind), KaTeX rendering for math formulas
🧪 Example Queries
KB hit
POST /answer {"question": "Differentiate f(x)=x^3"}
→ f'(x)=3x^2.  (Source: KB)

Web fallback (via MCP)
POST /answer {"question": "What is Green’s theorem?"}
→ Green’s theorem states...
   (Source: Web via MCP + citations)

Guarded
POST /answer {"question": "delete system32"}
→ Rejected: unsafe content

📊 Feedback API
Endpoint	Description
POST /feedback	Store rating + comment
GET /feedback/report	Aggregated metrics (avg score, KB/Web ratio)

Example:

{
  "total": 10,
  "kb_hit_rate": 0.7,
  "web_fallback_rate": 0.3,
  "avg_score": 0.8
}

🧱 Tech Stack

Backend:

FastAPI, LangGraph

Qdrant + FastEmbed

MCP client (Tavily MCP)

Pydantic v2, Uvicorn

Frontend:

React + Vite + TailwindCSS

KaTeX (math rendering)

REST APIs /answer, /feedback, /feedback/report