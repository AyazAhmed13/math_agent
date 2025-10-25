
# app/routers/kb.py
from __future__ import annotations
from typing import List
from fastapi import APIRouter
from pydantic import BaseModel

from ..models.schemas import (
    KBSearchRequest,
    KBSearchResponse,
    KBSearchResult,
)
from ..services.kb import best_contexts, kb_upsert

router = APIRouter()

# --- SEARCH --------------------------------------------------------------

@router.post("/kb/search", response_model=KBSearchResponse)
def kb_search(req: KBSearchRequest) -> KBSearchResponse:
    hits = best_contexts(req.query, top_k=req.top_k)
    # Prefer returning the stored solution text; fall back to raw text
    results: List[KBSearchResult] = []
    for h in hits:
        sol = (h.get("meta") or {}).get("s") or h.get("text") or ""
        results.append(KBSearchResult(text=sol, score=float(h.get("score", 0.0))))
    return KBSearchResponse(results=results)

# --- UPSERT (batch) ------------------------------------------------------

class KBUpsertItem(BaseModel):
    question: str
    solution: str

class KBUpsertRequest(BaseModel):
    items: List[KBUpsertItem]

@router.post("/kb/upsert")
def kb_upsert_route(req: KBUpsertRequest):
    pairs = [(it.question.strip(), it.solution.strip()) for it in req.items if it.question.strip() and it.solution.strip()]
    n = kb_upsert(pairs) if pairs else 0
    return {"inserted": n}
