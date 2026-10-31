const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options) {
  const res = await fetch(`${API_URL}${path}`, options);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Server error (${res.status})`);
  }
  return res.json();
}

// {a: 1, b: "", c: undefined} -> "?a=1" (nilai kosong dibuang)
function query(params = {}) {
  const q = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== "") q.set(k, v);
  });
  const s = q.toString();
  return s ? `?${s}` : "";
}

const post = (path, body) =>
  request(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

export const sendChat = (
  message,
  language,
  { mode = "auto", previousType = null, history = [] } = {},
) =>
  post("/api/chat", {
    message,
    language,
    mode,
    previous_type: previousType,
    history,
  });

export const getHealth = () => request("/api/health");
export const getTopics = () => request("/api/topics");
export const getVocabulary = (p) => request(`/api/vocabulary${query(p)}`);
export const getRandomVocabulary = (p) =>
  request(`/api/vocabulary/random${query(p)}`);
export const getKanji = (p) => request(`/api/kanji${query(p)}`);
export const getGrammar = (p) => request(`/api/grammar${query(p)}`);
export const getQuiz = (p) => request(`/api/quiz${query(p)}`);
export const getReadingPractice = (topic, language) =>
  post("/api/dokkai", { topic: topic || null, language });
