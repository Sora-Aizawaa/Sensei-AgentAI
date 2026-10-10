const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function sendChat(message, language) {
  const res = await fetch(`${API_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, language }),
  });

  if (!res.ok) throw new Error(`Server error (${res.status})`);
  return res.json();
}
