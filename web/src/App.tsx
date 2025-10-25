import React, { useState } from 'react'
import { ask, feedback, AnswerResponse } from './api'
export default function App(){
  const [q,setQ]=useState(''); const [ans,setAns]=useState<AnswerResponse|null>(null); const [loading,setLoading]=useState(false); const [error,setError]=useState<string|null>(null);
  const onAsk=async()=>{ setLoading(true); setError(null); try{ const res=await ask(q); setAns(res);}catch(e:any){ setError(e.message??'Something went wrong');}finally{ setLoading(false);} }
  const onFeedback=async(label:'correct'|'partial'|'wrong')=>{ if(!ans) return; await feedback({question:q, answer: ans.final, label}); alert('Thanks for the feedback!') }
  return (<div style={{maxWidth:800, margin:'32px auto', fontFamily:'Inter, system-ui, sans-serif'}}>
    <h1 style={{fontSize:28, marginBottom:8}}>Math Agent</h1>
    <p style={{color:'#666', marginBottom:16}}>Ask a math question. The backend uses KB-first routing; if no KB match, it falls back to a web placeholder.</p>
    <div style={{display:'flex', gap:8}}>
      <input placeholder='e.g., Solve x^2 - 5x + 6 = 0' value={q} onChange={e=>setQ(e.target.value)} style={{flex:1, padding:12, borderRadius:8, border:'1px solid #ddd'}} />
      <button onClick={onAsk} disabled={loading} style={{padding:'12px 16px', borderRadius:8, border:'1px solid #333', background:'#111', color:'#fff'}}>{loading?'Thinking…':'Ask'}</button>
    </div>
    {error && <div style={{marginTop:12, color:'crimson'}}>{error}</div>}
    {ans && (<div style={{marginTop:24, padding:16, border:'1px solid #eee', borderRadius:12}}>
      <h2 style={{fontSize:20, marginBottom:8}}>Steps</h2>
      <ol>{ans.steps.map(s=> <li key={s.index} style={{marginBottom:6}}>{s.text}</li>)}</ol>
      <h3 style={{fontSize:18, marginTop:12}}>Final Answer</h3>
      <div style={{fontWeight:600, marginBottom:8}}>{ans.final}</div>
      {ans.citations && ans.citations.length>0 && (<div style={{fontSize:14, color:'#666'}}>Sources: {ans.citations.map((u,i)=><a key={i} href={u} target='_blank' style={{marginRight:8}}>{u}</a>)}</div>)}
      <div style={{marginTop:12, display:'flex', gap:8}}>
        <button onClick={()=>onFeedback('correct')}>👍 Correct</button>
        <button onClick={()=>onFeedback('partial')}>😐 Partial</button>
        <button onClick={()=>onFeedback('wrong')}>👎 Wrong</button>
      </div>
    </div>)}
  </div>) }
