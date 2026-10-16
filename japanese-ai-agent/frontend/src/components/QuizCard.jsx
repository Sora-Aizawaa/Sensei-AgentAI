import { useState } from "react";

export default function QuizCard({ quiz }) {
  const questions = quiz.questions;
  const [index, setIndex] = useState(0);
  const [picked, setPicked] = useState(null);
  const [score, setScore] = useState(0);
  const [done, setDone] = useState(false);

  const q = questions[index];

  const choose = (i) => {
    if (picked !== null) return; // jawaban sudah dipilih
    setPicked(i);
    if (i === q.answer) setScore((s) => s + 1);
  };

  const next = () => {
    if (index + 1 >= questions.length) {
      setDone(true);
    } else {
      setIndex(index + 1);
      setPicked(null);
    }
  };

  const restart = () => {
    setIndex(0);
    setPicked(null);
    setScore(0);
    setDone(false);
  };

  if (done) {
    return (
      <div className="space-y-2">
        <p className="font-semibold">{quiz.title}: selesai 🎉</p>
        <p className="text-2xl font-bold">
          {score} / {questions.length}
        </p>
        <button
          onClick={restart}
          className="rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white"
        >
          Ulangi kuis
        </button>
      </div>
    );
  }

  const choiceClass = (i) => {
    const base =
      "w-full rounded-lg border px-3 py-2 text-left text-sm transition ";
    if (picked === null) {
      return (
        base +
        "border-slate-200 hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-800"
      );
    }
    if (i === q.answer)
      return base + "border-emerald-500 bg-emerald-50 dark:bg-emerald-950";
    if (i === picked)
      return base + "border-rose-500 bg-rose-50 dark:bg-rose-950";
    return base + "border-slate-200 opacity-60 dark:border-slate-700";
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between text-xs text-slate-500">
        <span className="font-semibold">{quiz.title}</span>
        <span>
          Soal {index + 1}/{questions.length} · skor {score}
        </span>
      </div>

      <p className="whitespace-pre-line text-base font-semibold">{q.prompt}</p>

      <div className="space-y-2">
        {q.choices.map((c, i) => (
          <button key={i} onClick={() => choose(i)} className={choiceClass(i)}>
            <span className="mr-2 text-slate-400">
              {String.fromCharCode(65 + i)}.
            </span>
            {c}
          </button>
        ))}
      </div>

      {picked !== null && (
        <div className="space-y-2">
          <p className="whitespace-pre-line rounded-lg bg-slate-50 p-2 text-xs dark:bg-slate-800">
            {picked === q.answer ? "✅ Benar!" : "❌ Kurang tepat."}
            {"\n"}
            {q.explanation}
          </p>
          <button
            onClick={next}
            className="rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white"
          >
            {index + 1 >= questions.length ? "Lihat skor" : "Soal berikutnya"}
          </button>
        </div>
      )}
    </div>
  );
}
