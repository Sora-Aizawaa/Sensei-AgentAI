import { useState } from "react";
import { getQuiz, getTopics } from "../services/api";
import QuizCard from "../components/QuizCard";
import {
  Button,
  LevelSelect,
  Notice,
  PageIntro,
  inputCls,
  useLoader,
} from "../components/ui";

const FOCUS = [
  ["", "Campuran"],
  ["vocabulary", "Kosakata"],
  ["grammar", "Grammar"],
  ["kanji", "Kanji"],
];

export default function QuizPage({ language }) {
  const [focus, setFocus] = useState("");
  const [level, setLevel] = useState("");
  const [topic, setTopic] = useState("");
  const [n, setN] = useState(5);
  const [run, setRun] = useState({
    key: 0,
    loading: false,
    error: "",
    result: null,
  });
  const topics = useLoader(getTopics, []);

  const start = async () => {
    setRun((r) => ({ ...r, loading: true, error: "" }));
    try {
      const result = await getQuiz({
        focus,
        level,
        topic: focus === "vocabulary" || !focus ? topic : "",
        n,
        lang: language,
      });
      setRun((r) => ({ key: r.key + 1, loading: false, error: "", result }));
    } catch (err) {
      setRun((r) => ({ ...r, loading: false, error: err.message }));
    }
  };

  return (
    <div className="space-y-4">
      <PageIntro>
        Soal dibuat dari database (arti kata, bacaan, isi bagian kosong, arti
        pola), jadi kunci jawabannya pasti benar. Hasilnya dicatat di menu
        Progress.
      </PageIntro>

      <div className="flex flex-wrap gap-2">
        <select
          value={focus}
          onChange={(e) => setFocus(e.target.value)}
          className={inputCls}
        >
          {FOCUS.map(([v, label]) => (
            <option key={v} value={v}>
              {label}
            </option>
          ))}
        </select>
        <LevelSelect value={level} onChange={setLevel} />
        <select
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          disabled={focus === "grammar" || focus === "kanji"}
          className={inputCls}
        >
          <option value="">Semua topik</option>
          {topics.data?.items.map((t) => (
            <option key={t.topic} value={t.topic}>
              {t.topic}
            </option>
          ))}
        </select>
        <select
          value={n}
          onChange={(e) => setN(Number(e.target.value))}
          className={inputCls}
        >
          {[3, 5, 8, 10].map((v) => (
            <option key={v} value={v}>
              {v} soal
            </option>
          ))}
        </select>
        <Button onClick={start} disabled={run.loading}>
          {run.loading ? "Membuat..." : "Mulai kuis"}
        </Button>
      </div>

      {run.error && <Notice tone="error">{run.error}</Notice>}
      {run.result?.type === "info" && <Notice>{run.result.message}</Notice>}
      {run.result?.type === "quiz" && (
        <div className="rounded-xl border border-slate-100 p-4 dark:border-slate-800">
          <QuizCard key={run.key} quiz={run.result.quiz} />
        </div>
      )}
    </div>
  );
}
