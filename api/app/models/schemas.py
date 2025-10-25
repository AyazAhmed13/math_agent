
from __future__ import annotations
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime

class Step(BaseModel):
    index: int
    text: str

class AnswerRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=1000)

class AnswerResponse(BaseModel):
    steps: List[Step]
    final: str
    citations: Optional[List[str]] = None
    # NEW: show routing source to the UI
    source: Optional[Literal["kb", "web", "none"]] = None

class KBSearchRequest(BaseModel):
    query: str
    top_k: int = 3

class KBSearchResult(BaseModel):
    text: str
    score: float

class KBSearchResponse(BaseModel):
    results: List[KBSearchResult]

# Feedback
class FeedbackRequest(BaseModel):
    question: str
    final: str
    source: Literal["kb", "web", "none"]
    rating: Literal["up", "neutral", "down"]
    comment: Optional[str] = None
    # timestamp optional; server assigns if not provided
    timestamp: Optional[datetime] = None

class FeedbackAck(BaseModel):
    ok: bool
    id: str

class FeedbackReport(BaseModel):
    total: int
    counts_by_source: dict
    counts_by_rating: dict
    kb_hit_rate: float
    web_fallback_rate: float
    avg_score: float  # up=1, neutral=0, down=-1
