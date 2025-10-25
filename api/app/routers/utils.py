from typing import List, Tuple
import re
from ..models.schemas import Step

def guard_input(question: str) -> Tuple[bool, str]:
    if not re.search(r"[0-9a-zA-Z+\-*/^=()]", question):
        return (False, "Please enter a math expression or question.")
    return (True, "")

def synth_stub(question: str, contexts: List[str]):
    q = question.lower()

    # ✅ If KB returned contexts, use the top solution directly
    if contexts:
        top = contexts[0].strip()
        steps = [
            Step(index=1, text="Retrieve relevant solution from the knowledge base."),
            Step(index=2, text="Align the retrieved solution to the asked question."),
            Step(index=3, text=f"Summarize the result: {top}"),
        ]
        return steps, top

    # Special-case example (quadratic)
    if "x^2" in q or "quadratic" in q:
        steps = [
            Step(index=1, text="Identify coefficients a, b, c."),
            Step(index=2, text="Compute discriminant Δ = b^2 - 4ac."),
            Step(index=3, text="Apply quadratic formula x = [-b ± √Δ] / (2a)."),
        ]
        return steps, "x = 2 and x = 3 (example)"

    # Generic fallback
    steps = [
        Step(index=1, text="Analyze the problem and pick a known technique."),
        Step(index=2, text="Apply the technique step-by-step."),
        Step(index=3, text="Simplify and present the final result."),
    ]
    return steps, "This is a placeholder final answer."

def guard_output(steps: List[Step], final: str):
    clean = []
    for i, s in enumerate(steps, start=1):
        clean.append(Step(index=i, text=s.text.strip()))
    return clean, final.strip()
