export type Step = { index: number; text: string }
export type AnswerResponse = { steps: Step[]; final: string; citations?: string[] }
const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8000'
export async function ask(question: string): Promise<AnswerResponse> {
  const res = await fetch(`${API_BASE}/answer`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question }) })
  if (!res.ok) throw new Error('API error')
  return res.json()
}
export async function feedback(payload: {question: string; answer: string; label: string; notes?: string}) {
  const res = await fetch(`${API_BASE}/feedback`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
  if (!res.ok) throw new Error('API error')
  return res.json()
}
