const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

export async function ask(question) {
  const res = await fetch(`${API_BASE}/answer`, {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({ question })
  });
  if (!res.ok) throw new Error(`/answer ${res.status}`);
  return res.json();
}

export async function sendFeedback({ question, final, source, rating, comment }) {
  const res = await fetch(`${API_BASE}/feedback`, {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({ question, final, source, rating, comment })
  });
  if (!res.ok) throw new Error(`feedback ${res.status}`);
  return res.json();
}

export async function fetchReport() {
  const res = await fetch(`${API_BASE}/feedback/report`);
  if (!res.ok) throw new Error(`report ${res.status}`);
  return res.json();
}
