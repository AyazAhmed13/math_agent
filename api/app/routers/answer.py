
from fastapi import APIRouter
from ..models.schemas import AnswerRequest, AnswerResponse, Step
from .utils import guard_input, guard_output
from ..graph.agent import run_agent
import os

router = APIRouter()

@router.post("/answer", response_model=AnswerResponse)
def answer(req: AnswerRequest) -> AnswerResponse:
    ok, msg = guard_input(req.question)
    if not ok:
        return AnswerResponse(steps=[Step(index=1, text=msg)], final="", citations=None, source="none")

    result = run_agent(req.question)
    source = result["source"]
    final = result["final"] or ""
    citations = result.get("citations") or None

    if source == "kb":
        steps = [
            Step(index=1, text="Searched the internal knowledge base (Qdrant)."),
            Step(index=2, text="Selected the most relevant stored solution."),
            Step(index=3, text="Summarized the result."),
        ]
    else:
        used = "web search via MCP" if (citations and len(citations) > 0 and os.getenv("MCP_SEARCH_CMD")) else ("web (Tavily)" if (citations and len(citations) > 0 and os.getenv("TAVILY_API_KEY")) else "web fallback (not configured)")
        steps = [
            Step(index=1, text=f"No strong KB match; used {used}."),
            Step(index=2, text="Aggregated top snippets." if citations else "Returned a safe placeholder."),
            Step(index=3, text="Summarized the result."),
        ]

    steps, final = guard_output(steps, final)
    return AnswerResponse(steps=steps, final=final, citations=citations, source=source)
