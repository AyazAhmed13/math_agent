import React, { useState } from "react";
import { sendFeedback } from "../api";

export default function FeedbackBox({ question, finalText, source, onSubmitted }) {
  const [rating, setRating] = useState(null); // "up" | "neutral" | "down"
  const [comment, setComment] = useState("");
  const [busy, setBusy] = useState(false);
  const canSend = !!rating && !busy;

  async function submit() {
    if (!canSend) return;
    setBusy(true);
    try {
      await sendFeedback({ question, final: finalText || "", source: source || "none", rating, comment });
      setComment("");
      if (onSubmitted) onSubmitted();
      alert("Thanks for the feedback!");
    } catch (e) {
      console.error(e);
      alert("Failed to submit feedback.");
    } finally {
      setBusy(false);
    }
  }

  const btnStyle = (active) => ({
    padding:"6px 10px",
    borderRadius:8,
    border:"1px solid #ddd",
    cursor:"pointer",
    background: active ? "#F2F4F7" : "white"
  });

  return (
    <div style={{marginTop:12, padding:10, border:"1px dashed #ddd", borderRadius:10}}>
      <div style={{display:"flex", gap:8, alignItems:"center"}}>
        <span style={{fontSize:14, fontWeight:600}}>Was this helpful?</span>
        <button style={btnStyle(rating==="up")} onClick={()=>setRating("up")}>👍</button>
        <button style={btnStyle(rating==="neutral")} onClick={()=>setRating("neutral")}>😐</button>
        <button style={btnStyle(rating==="down")} onClick={()=>setRating("down")}>👎</button>
      </div>
      <div style={{marginTop:8}}>
        <textarea
          placeholder="Optional note (what was good / missing / wrong)"
          value={comment}
          onChange={e=>setComment(e.target.value)}
          rows={2}
          style={{width:"100%", padding:8, borderRadius:8, border:"1px solid #ddd"}}
        />
      </div>
      <div style={{marginTop:8}}>
        <button disabled={!canSend} onClick={submit} style={{padding:"8px 12px", borderRadius:8, border:"none", background:"#0A58CA", color:"white", cursor: canSend ? "pointer" : "not-allowed"}}>
          Submit feedback
        </button>
      </div>
    </div>
  );
}
