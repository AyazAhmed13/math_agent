React (Vite)
   │  ask / feedback / report
   ▼
FastAPI (/answer, /kb/*, /feedback/*)
   │
   └─ LangGraph Router
        ├─ KB branch
        │    └─ Qdrant (FastEmbed) → contexts → synthesize
        └─ Web branch
             └─ MCP client ──> MCP server (tavily-mcp) ──> Tavily API
                                      │
                                      └─ snippets → citations → synthesize

Guardrails:
- Input filtering (math-only, unsafe term block)
- Similarity threshold & operator normalization
- Safe fallback responses (no hallucination)
Human-in-the-loop:
- /feedback stores ratings + notes
- /feedback/report aggregates metrics
