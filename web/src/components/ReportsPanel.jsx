import React, { useEffect, useState } from "react";
import { fetchReport } from "../api";

export default function ReportsPanel() {
  const [data, setData] = useState(null);
  const [err, setErr] = useState("");

  async function load() {
    setErr("");
    try {
      const r = await fetchReport();
      setData(r);
    } catch (e) {
      console.error(e);
      setErr("Failed to load report");
    }
  }

  useEffect(()=>{ load(); }, []);

  return (
    <div style={{marginTop:16, padding:12, border:"1px solid #eee", borderRadius:12}}>
      <div style={{display:"flex", justifyContent:"space-between", alignItems:"center"}}>
        <h4 style={{margin:0}}>Feedback Report</h4>
        <button onClick={load} style={{padding:"6px 10px", border:"1px solid #ddd", borderRadius:8, background:"white"}}>Refresh</button>
      </div>
      {err && <div style={{color:"#b00020", marginTop:8}}>{err}</div>}
      {data && (
        <div style={{marginTop:8, display:"grid", gap:8}}>
          <div>Total: <b>{data.total}</b></div>
          <div>KB hit rate: <b>{(data.kb_hit_rate*100).toFixed(1)}%</b></div>
          <div>Web fallback rate: <b>{(data.web_fallback_rate*100).toFixed(1)}%</b></div>
          <div>Average score: <b>{data.avg_score}</b> (up=1, neutral=0, down=-1)</div>
          <div>By source: <code>{JSON.stringify(data.counts_by_source)}</code></div>
          <div>By rating: <code>{JSON.stringify(data.counts_by_rating)}</code></div>
        </div>
      )}
    </div>
  );
}
