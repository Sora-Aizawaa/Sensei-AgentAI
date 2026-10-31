// Progres belajar disimpan di browser (localStorage), tanpa akun dan tanpa backend.
const KEY = "sensei.progress.v1";

const empty = () => ({ quizzes: [], missed: {} });

export function loadProgress() {
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? { ...empty(), ...JSON.parse(raw) } : empty();
  } catch {
    return empty();
  }
}

function save(data) {
  try {
    localStorage.setItem(KEY, JSON.stringify(data));
  } catch {
    /* abaikan */
  }
}

// answers: [{ kind, subject, correct }]
export function saveQuizResult({ title, answers }) {
  const data = loadProgress();
  const score = answers.filter((a) => a.correct).length;
  data.quizzes.unshift({
    date: new Date().toISOString(),
    title,
    score,
    total: answers.length,
    answers: answers.map(({ kind, subject, correct }) => ({
      kind,
      subject,
      correct,
    })),
  });
  data.quizzes = data.quizzes.slice(0, 100); // simpan 100 kuis terakhir

  answers.forEach((a) => {
    if (!a.subject) return;
    const m = data.missed[a.subject] || { wrong: 0, right: 0, kind: a.kind };
    if (a.correct) m.right += 1;
    else m.wrong += 1;
    data.missed[a.subject] = m;
  });
  save(data);
  return data;
}

export function clearProgress() {
  try {
    localStorage.removeItem(KEY);
  } catch {
    /* abaikan */
  }
}

export function groupOf(kind = "") {
  if (kind.startsWith("vocab")) return "Kosakata";
  if (kind.startsWith("grammar")) return "Grammar";
  if (kind.startsWith("kanji")) return "Kanji";
  if (kind === "reading") return "Reading";
  return "Lainnya";
}

export function summarize(data) {
  const byGroup = {};
  data.quizzes.forEach((q) =>
    q.answers.forEach((a) => {
      const g = groupOf(a.kind);
      byGroup[g] = byGroup[g] || { right: 0, total: 0 };
      byGroup[g].total += 1;
      if (a.correct) byGroup[g].right += 1;
    }),
  );

  const totalQ = data.quizzes.reduce((s, q) => s + q.total, 0);
  const totalRight = data.quizzes.reduce((s, q) => s + q.score, 0);

  const weak = Object.entries(data.missed)
    .map(([subject, m]) => ({ subject, ...m }))
    .filter((m) => m.wrong > 0)
    .sort((a, b) => b.wrong - a.wrong || a.right - b.right)
    .slice(0, 10);

  return {
    quizCount: data.quizzes.length,
    totalQ,
    totalRight,
    accuracy: totalQ ? totalRight / totalQ : null,
    byGroup,
    weak,
    recent: data.quizzes.slice(0, 8),
  };
}
