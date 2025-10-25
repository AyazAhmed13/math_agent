
from __future__ import annotations
from typing import List, Tuple, Optional, Dict
import os, re
import numpy as np
from uuid import uuid4
from fastembed import TextEmbedding
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

KB_BACKEND = os.getenv("KB_BACKEND", "memory").lower()
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "math_kb")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
TOP_K = int(os.getenv("TOP_K", "3"))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.6"))

_embedding_model: Optional[TextEmbedding] = None
_memory_store: List[Dict] = []
_qdrant_client = None

VERBS = ("integrate", "differentiate", "derive", "derivative", "solve", "limit")

def _get_embedder() -> TextEmbedding:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = TextEmbedding(model_name=EMBEDDING_MODEL)
    return _embedding_model

def _normalize_ops(text: str) -> str:
    t = text
    t = t.replace("∫", " integrate ")
    t = t.replace("d/dx", " differentiate ")
    t = re.sub(r"\s+", " ", t)
    return t

def detect_verb(text: str) -> str:
    t = _normalize_ops(text.lower())
    if "derivative" in t or "derive" in t:
        return "differentiate"
    for v in VERBS:
        if re.search(rf"\b{re.escape(v)}\b", t):
            return v
    return ""

def embed(texts: List[str]) -> np.ndarray:
    model = _get_embedder()
    vecs = list(model.embed(texts))
    return np.array(vecs, dtype=np.float32)

def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) + 1e-8
    return float(np.dot(a, b) / denom)

def memory_upsert(pairs: List[Tuple[str, str]]) -> int:
    texts = [q + " ||| " + s for q, s in pairs]
    vecs = embed(texts)
    for (q, s), v in zip(pairs, vecs):
        _memory_store.append({"text": q + " ||| " + s, "vector": v, "meta": {"q": q, "s": s}})
    return len(_memory_store)

def memory_search(query: str, top_k: int = TOP_K):
    if not _memory_store:
        return []
    qv = embed([_normalize_ops(query)])[0]
    scored = []
    qverb = detect_verb(query)
    for item in _memory_store:
        sim = cosine_sim(qv, item["vector"])
        meta = item["meta"]
        ans = meta.get("s", "")
        # penalize if operator class mismatches
        if qverb and qverb not in (_normalize_ops(meta.get("q", "")).lower() + " " + _normalize_ops(ans).lower()):
            sim *= 0.85
        scored.append((item["text"], sim, meta))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]

def _get_qdrant():
    global _qdrant_client
    if _qdrant_client is None:
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, VectorParams
        _qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY or None, timeout=30)
        try:
            _qdrant_client.get_collection(QDRANT_COLLECTION)
        except Exception:
            dim = len(embed(["dim check"])[0])
            _qdrant_client.recreate_collection(
                collection_name=QDRANT_COLLECTION,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE)
            )
    return _qdrant_client

def qdrant_upsert(pairs: List[Tuple[str, str]]) -> int:
    client = _get_qdrant()
    from qdrant_client.models import PointStruct
    texts = [q + " ||| " + s for q, s in pairs]
    vecs = embed(texts)
    points = []
    for (q, s), v, t in zip(pairs, vecs, texts):
        points.append(PointStruct(id=str(uuid4()), vector=v.tolist(), payload={"text": t, "q": q, "s": s}))
    client.upsert(collection_name=QDRANT_COLLECTION, points=points)
    return len(points)

def qdrant_search(query: str, top_k: int = TOP_K):
    client = _get_qdrant()
    qv = embed([_normalize_ops(query)])[0].tolist()
    res = client.search(collection_name=QDRANT_COLLECTION, query_vector=qv, limit=top_k)
    out = []
    qverb = detect_verb(query)
    for p in res:
        payload = p.payload or {}
        s = float(p.score)
        q = payload.get("q", "")
        a = payload.get("s", "")
        if qverb and qverb not in (_normalize_ops(q).lower() + " " + _normalize_ops(a).lower()):
            s *= 0.85
        out.append((payload.get("text", ""), s, {"q": q, "s": a}))
    out.sort(key=lambda x: x[1], reverse=True)
    return out[:top_k]

def kb_upsert(pairs: List[Tuple[str, str]]) -> int:
    if KB_BACKEND == "qdrant":
        return qdrant_upsert(pairs)
    return memory_upsert(pairs)

def kb_search(query: str, top_k: int = TOP_K):
    if KB_BACKEND == "qdrant":
        return qdrant_search(query, top_k)
    return memory_search(query, top_k)

def best_contexts(query: str, top_k: int = TOP_K, threshold: float = SIMILARITY_THRESHOLD):
    hits = kb_search(query, top_k=top_k)
    filtered = [{"text": t, "score": s, "meta": m} for (t, s, m) in hits if s >= threshold]
    return filtered
