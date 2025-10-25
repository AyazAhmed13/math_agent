import React from "react";
import "katex/dist/katex.min.css";
import { InlineMath } from "react-katex";

function SourceBadge({ source }) {
  if (!source) return null;
  const isKB = source === "kb";
  const label = isKB ? "Source: KB" : (source === "web" ? "Source: Web via MCP" : "Source: None");
  const bg = isKB ? "#E1FCEA" : (source === "web" ? "#E7F0FF" : "#EEE");
  const color = isKB ? "#0F8A3C" : (source === "web" ? "#0A58CA" : "#333");
  return (
    <span style={{background:bg,color, padding:"4px 8px", borderRadius:999, fontSize:12, fontWeight:600}}>
      {label}
    </span>
  );
}

function maybeRenderMath(text) {
  // Simple heuristic: if it contains ^, ∫, or LaTeX-ish braces, render inline math chunks
  // We keep this light to avoid breaking plain text.
  const hasMathCue = /(\^|∫|\\[a-zA-Z]+|e\^\(|\d\)|\bi\b)/.test(text || "");
  if (!hasMathCue) return <span>{text}</span>;

  // split by $...$ if present; else render whole as text with minimal inline math of e^(...) patterns
  // simplest: just return InlineMath around the whole string if short; else fallback to text.
  if ((text || "").length <= 80) {
    try { return <InlineMath math={text} />; } catch { return <span>{text}</span>; }
  }
  return <span>{text}</span>;
}

export default function AnswerPanel({ steps, finalText, citations, source }) {
  return (
    <div style={{display:"grid", gap:12}}>
      <div style={{display:"flex", alignItems:"center", justifyContent:"space-between"}}>
        <h3 style={{margin:0}}>Result</h3>
        <SourceBadge source={source} />
      </div>

      <div style={{padding:12, border:"1px solid #eee", borderRadius:12, boxShadow:"0 1px 3px rgba(0,0,0,0.06)"}}>
        <div style={{fontSize:18, fontWeight:600, marginBottom:8}}>Final Answer</div>
        <div style={{fontSize:16, lineHeight:1.5}}>
          {maybeRenderMath(finalText)}
        </div>

        {Array.isArray(citations) && citations.length > 0 && (
          <>
            <div style={{marginTop:12, fontSize:14, color:"#555", fontWeight:600}}>Sources</div>
            <ul style={{marginTop:6, paddingLeft:18}}>
              {citations.slice(0,3).map((u, i) => (
                <li key={i}><a href={u} target="_blank" rel="noreferrer">{u}</a></li>
              ))}
            </ul>
          </>
        )}
      </div>

      <div>
        <div style={{fontSize:14, fontWeight:600, marginBottom:6}}>Steps</div>
        <ol style={{margin:0, paddingLeft:18}}>
          {(steps || []).map(s => <li key={s.index} style={{marginBottom:4}}>{s.text}</li>)}
        </ol>
      </div>
    </div>
  );
}
