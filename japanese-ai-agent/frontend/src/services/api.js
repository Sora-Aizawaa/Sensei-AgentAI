const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function sendChat(
  message,
  language,
  { mode = "auto", previousType = null, history = [] } = {},
) {
  const res = await fetch(`${API_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      language,
      mode,
      previous_type: previousType,
      history,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Server error (${res.status})`);
  }
  return res.json();
}
