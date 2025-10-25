from typing import TypedDict, List, Literal, Optional
from langgraph.graph import StateGraph, END
from ..services.kb import best_contexts
from ..services.mcp_bridge import web_search

class AgentState(TypedDict):
    question: str
    source: Literal["kb","web","none"]
    contexts: List[str]
    citations: List[str]
    final: Optional[str]

def node_kb(state: AgentState) -> AgentState:
    hits = best_contexts(state["question"], top_k=3)
    if hits:
        return {
            **state,
            "source": "kb",
            "contexts": [h["meta"].get("s", h["text"]) for h in hits],
            "citations": [],
        }
    return {**state, "source": "none", "contexts": [], "citations": []}

def node_web(state: AgentState) -> AgentState:
    snippets, links = web_search(state["question"])
    if snippets:
        return {**state, "source": "web", "contexts": snippets, "citations": links}
    return {**state, "source": "none", "contexts": [], "citations": []}

def _pick_best_sentence(text: str) -> str:
    # split to sentences and pick the most definitional / succinct
    import re
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    scored = []
    for s in sents:
        score = 0
        if " is " in s.lower(): score += 3
        if any(k in s for k in ["=", "≈"]): score += 2
        if len(s) <= 160: score += 1
        scored.append((score, s))
    scored.sort(key=lambda x: x[0], reverse=True)
    return (scored[0][1] if scored else (text[:180].rstrip()+"…"))

def node_synthesize(state: AgentState) -> AgentState:
    if state["source"] == "kb" and state["contexts"]:
        return {**state, "final": state["contexts"][0].strip()}

    if state["source"] == "web" and state["contexts"]:
        joined = " ".join(state["contexts"][:2]).strip()
        # tiny example rule for Euler’s formula → make a crisp statement
        low = joined.lower()
        if "e^(ix)" in joined or "e^{ix}" in joined or ("e^(" in joined and "cos" in low and "sin" in low):
            return {**state, "final": "Euler’s formula: e^(ix) = cos(x) + i·sin(x)."}

        final = _pick_best_sentence(joined)[:220]
        return {**state, "final": final}

    return {**state, "final": "No clear answer found."}

def router(state: AgentState) -> str:
    return "synthesize" if state["source"] == "kb" else "web"

graph = StateGraph(AgentState)
graph.add_node("kb", node_kb)
graph.add_node("web", node_web)
graph.add_node("synthesize", node_synthesize)
graph.set_entry_point("kb")
graph.add_conditional_edges("kb", router, {"web": "web", "synthesize": "synthesize"})
graph.add_edge("web", "synthesize")
graph.add_edge("synthesize", END)
app_graph = graph.compile()

def run_agent(question: str):
    init: AgentState = {"question": question, "source": "none", "contexts": [], "citations": [], "final": None}
    result = app_graph.invoke(init)
    return result
