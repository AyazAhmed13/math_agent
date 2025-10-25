KB hit

POST /answer {"question":"Differentiate f(x)=x^3"}
→ source: "kb", final: "f'(x)=3x^2."


KB miss → MCP web

POST /answer {"question":"What is Green's theorem?"}
→ source: "web", citations: [...wiki/…]


guardrails

POST /answer {"question":"import os; ..."}
→ blocked with safe message


feedback

POST /feedback  {...}
GET /feedback/report → totals, kb/web %, avg score


Qdrant check: open http://localhost:6333/dashboard → math_kb has N points.