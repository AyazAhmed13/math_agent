
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import answer, kb, feedback
from .core.config import settings
import os, json
from .services.kb import kb_upsert

app = FastAPI(title="Math Agent API", version="0.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(answer.router)
app.include_router(kb.router)
app.include_router(feedback.router)

def _read_jsonl(path: str):
    pairs = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            q = obj.get("question", "").strip()
            s = obj.get("solution", "").strip()
            if q and s:
                pairs.append((q, s))
    return pairs

@app.on_event("startup")
def bootstrap_kb():
    p = os.getenv("KB_BOOTSTRAP_JSONL", "").strip()
    if p:
        try:
            n = kb_upsert(_read_jsonl(p))
            print(f"[startup] KB loaded {n} items from {p}")
        except Exception as e:
            print(f"[startup] KB load failed: {e}")
