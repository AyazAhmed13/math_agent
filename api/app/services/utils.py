from __future__ import annotations
import re
from typing import List, Tuple
from ..models.schemas import Step

MATH_TOKENS = r"[0-9+\-*/^().=xXyYzZπe√∫ΣΔθλμαβγ≠≤≥]"
FORBIDDEN = ["import ", "os.", "sys.", "subprocess", "eval(", "exec(", "`", "${", "</", "<script"]

def guard_input(q: str) -> Tuple[bool, str]:
    q = (q or "").strip()
    if not q:
        return False, "Please ask a non-empty math question."
    if len(q) > 1000:
        return False, "Question is too long. Please keep it under ~1000 characters."
    lo = q.lower()
    if any(tok in lo for tok in FORBIDDEN):
        return False, "Unsafe content detected. Please ask a math question without code/injections."
    # must contain some math-ish signal
    if not re.search(MATH_TOKENS, q):
        # allow conceptual math terms
        if not any(k in lo for k in ["derivative", "integral", "limit", "matrix", "theorem", "euler", "fourier", "probability", "algebra", "calculus"]):
            return False, "Please ask a math-related question."
    return True, ""

def guard_output(steps: List[Step], final: str) -> Tuple[List[Step], str]:
    # trim excessive whitespace and length
    final = (final or "").strip()
    if len(final) > 800:
        final = final[:800].rstrip() + "…"
    # sanitize weird backticks/markup that might slip from web
    final = final.replace("```", "").replace("\x00", "")
    return steps, final
