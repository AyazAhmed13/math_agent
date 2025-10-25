

from __future__ import annotations
from fastapi import APIRouter
from ..models.schemas import FeedbackRequest, FeedbackAck, FeedbackReport
from datetime import datetime
from pathlib import Path
import json, uuid

router = APIRouter()

FEED_PATH = Path(__file__).resolve().parents[2] / "data" / "feedback.jsonl"
FEED_PATH.parent.mkdir(parents=True, exist_ok=True)

def _score_of(rating: str) -> int:
    return {"up": 1, "neutral": 0, "down": -1}.get(rating, 0)

@router.post("/feedback", response_model=FeedbackAck)
def submit_feedback(req: FeedbackRequest) -> FeedbackAck:
    entry = req.model_dump()
    entry["id"] = str(uuid.uuid4())
    entry["timestamp"] = (entry.get("timestamp") or datetime.utcnow()).isoformat()

    with FEED_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return FeedbackAck(ok=True, id=entry["id"])

@router.get("/feedback/report", response_model=FeedbackReport)
def feedback_report() -> FeedbackReport:
    total = 0
    counts_by_source = {"kb": 0, "web": 0, "none": 0}
    counts_by_rating = {"up": 0, "neutral": 0, "down": 0}
    sum_score = 0

    if FEED_PATH.exists():
        with FEED_PATH.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                total += 1
                src = obj.get("source", "none")
                rat = obj.get("rating", "neutral")
                counts_by_source[src] = counts_by_source.get(src, 0) + 1
                counts_by_rating[rat] = counts_by_rating.get(rat, 0) + 1
                sum_score += _score_of(rat)

    kb_hit_rate = (counts_by_source.get("kb", 0) / total) if total else 0.0
    web_fallback_rate = (counts_by_source.get("web", 0) / total) if total else 0.0
    avg_score = (sum_score / total) if total else 0.0

    return FeedbackReport(
        total=total,
        counts_by_source=counts_by_source,
        counts_by_rating=counts_by_rating,
        kb_hit_rate=round(kb_hit_rate, 3),
        web_fallback_rate=round(web_fallback_rate, 3),
        avg_score=round(avg_score, 3),
    )
