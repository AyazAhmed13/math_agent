import React, { useState } from "react";
import { ask } from "./api";
import AnswerPanel from "./components/AnswerPanel";
import FeedbackBox from "./components/FeedbackBox";
import ReportsPanel from "./components/ReportsPanel";

export default function App() {
  const [q, setQ] = useState("");
  const [answer, setAnswer] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function onAsk() {
    if (!q.trim()) return;
    setBusy(true); setError(""); setAnswer(null);
    try {
      const data = await ask(q.trim());
      setAnswer(data);
    } catch (e) {
      console.error(e);
      setError("Failed to get answer.");
    } finally {
      setBusy(false);
    }
  }

  const container = {maxWidth:760, margin:"40px auto", padding:"0 16px"};
  const card = {padding:16, border:"1px solid #eee", borderRadius:12, boxShadow:"0 1px 4px rgba(0,0,0,0.06)"};

  return (
    <div style={container}>
      <h2 style={{marginBottom:12}}>Math Agent</h2>
      <div style={{...card, display:"grid", gap:10}}>
        <label style={{fontSize:14, fontWeight:600}}>Ask a math question</label>
        <input
          value={q}
          onChange={(e)=>setQ(e.target.value)}
          onKeyDown={(e)=>{ if (e.key==='Enter') onAsk(); }}
          placeholder="e.g., Differentiate x^3, or What is Euler’s formula?"
          style={{padding:"10px 12px", borderRadius:10, border:"1px solid #ddd"}}
        />
        <div>
          <button onClick={onAsk} disabled={busy} style={{padding:"10px 14px", borderRadius:10, border:"none", background:"#0A58CA", color:"white", cursor: busy ? "not-allowed" : "pointer"}}>
            {busy ? "Thinking…" : "Ask"}
          </button>
        </div>
        {error && <div style={{color:"#b00020"}}>{error}</div>}
      </div>

      {answer && (
        <div style={{marginTop:16, display:"grid", gap:12}}>
          <AnswerPanel
            steps={answer.steps}
            finalText={answer.final}
            citations={answer.citations}
            source={answer.source}
          />
          <FeedbackBox
            question={q}
            finalText={answer.final}
            source={answer.source}
            onSubmitted={()=>{}}
          />
        </div>
      )}

      <ReportsPanel />
    </div>
  );
}
