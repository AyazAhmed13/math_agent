


from __future__ import annotations
import os, asyncio, traceback, re
from typing import List, Tuple
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

MCP_CMD  = os.getenv("MCP_SEARCH_CMD", "").strip()
MCP_ARGS = [a for a in os.getenv("MCP_SEARCH_ARGS", "").split() if a]
MCP_ENV  = os.environ.copy()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "").strip()


PREFERRED_DOMAINS = ["wikipedia.org", "khanacademy.org", "mathworld.wolfram.com", "math.stackexchange.com", "geeksforgeeks.org"]

def _fallback(query: str) -> Tuple[List[str], List[str]]:
    return [f"No strong KB match for: {query}. Web search is not configured yet."], []

def _domain_score(url: str) -> int:
    u = (url or "").lower()
    for idx, dom in enumerate(PREFERRED_DOMAINS):
        if dom in u:
            # earlier in list → higher base score
            return 100 - idx * 5
    return 0

def _clean_snippet(s: str) -> str:
    s = (s or "").strip()
    s = re.sub(r"\s+", " ", s)
    return s[:300].rstrip()

def _dedupe(seq: List[str]) -> List[str]:
    seen, out = set(), []
    for x in seq:
        if not x or x in seen:
            continue
        seen.add(x)
        out.append(x)
    return out

def web_search(query: str) -> Tuple[List[str], List[str]]:
    print(f"[mcp] web_search called for: {query!r}")

    # 1) Try MCP server if configured
    if MCP_CMD:
        try:
            return asyncio.run(_web_search_async(query))
        except RuntimeError:
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(_web_search_async(query))
            finally:
                loop.close()
        except Exception as e:
            print("[mcp] MCP call failed:", repr(e))
            traceback.print_exc()

    # 2) Tavily REST fallback
    if TAVILY_API_KEY:
        try:
            from tavily import TavilyClient
            tv = TavilyClient(api_key=TAVILY_API_KEY)
            data = tv.search(query=query, max_results=6)
            items = data.get("results", [])
            if not items:
                return _fallback(query)

            scored = []
            for it in items:
                url = it.get("url") or ""
                snippet = it.get("content") or it.get("title") or ""
                snippet = _clean_snippet(snippet)
                score = _domain_score(url)
                # boost if snippet contains equation-y cues
                if any(k in snippet.lower() for k in ["e^(i", "cos", "sin", "limit", "derivative", "integral"]):
                    score += 5
                scored.append((score, snippet, url))

            scored.sort(key=lambda x: x[0], reverse=True)
            top_snips = _dedupe([s for _, s, _ in scored])[:3]
            top_links = _dedupe([u for _, _, u in scored])[:5]
            if top_snips:
                print(f"[mcp] Tavily REST returned {len(top_snips)} snippets")
                return top_snips, top_links
        except Exception as e:
            print("[mcp] Tavily REST failed:", repr(e))
            traceback.print_exc()

    # 3) Safe placeholder
    print("[mcp] No MCP/Tavily available -> fallback")
    return _fallback(query)

# ---- MCP path ----
async def _web_search_async(query: str) -> Tuple[List[str], List[str]]:
    try:
        from mcp.client.stdio import StdioServerParameters
        from mcp.client.session import ClientSession
    except Exception as e:
        print("[mcp] MCP client import failed:", repr(e))
        return _fallback(query)

    params = StdioServerParameters(command=MCP_CMD, args=MCP_ARGS, env=MCP_ENV)

    async with ClientSession(params) as session:
        await session.initialize()
        tools = await session.list_tools()
        names = [t.name for t in (tools.tools if hasattr(tools, "tools") else tools)]
        print("[mcp] tools exposed by server:", names)
        if "search" not in names:
            print("[mcp] 'search' tool not found on MCP server")
            return _fallback(query)

        try:
            res = await session.call_tool("search", {"query": query})
        except Exception as e:
            print("[mcp] call_tool('search') failed:", repr(e))
            traceback.print_exc()
            return _fallback(query)

        items = []
        if isinstance(res, list):
            items = res
        elif hasattr(res, "content"):
            items = getattr(res, "content", [])
        elif res:
            items = res

        rows = []
        for item in items or []:
            url = (item.get("url") if isinstance(item, dict) else getattr(item, "url", "")) or ""
            snippet = (
                (item.get("snippet") if isinstance(item, dict) else getattr(item, "snippet", "")) or
                (item.get("title")   if isinstance(item, dict) else getattr(item, "title", ""))   or
                (item.get("content") if isinstance(item, dict) else getattr(item, "content", "")) or
                ""
            )
            snippet = _clean_snippet(snippet)
            rows.append((_domain_score(url), snippet, url))

        rows.sort(key=lambda x: x[0], reverse=True)
        snips = _dedupe([s for _, s, _ in rows])[:3]
        links = _dedupe([u for _, _, u in rows])[:5]
        if not snips:
            print("[mcp] MCP returned no snippets")
            return _fallback(query)

        print(f"[mcp] MCP returned {len(snips)} snippets")
        return snips, links
