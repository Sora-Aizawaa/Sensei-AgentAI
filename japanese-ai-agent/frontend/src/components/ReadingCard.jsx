import { useState } from "react";
import { box } from "./Cards";
import QuizCard from "./QuizCard";

const TOGGLES = [
  ["hiragana", "Hiragana"],
  ["romaji", "Romaji"],
  ["translation", "Terjemahan"],
];

export default function ReadingCard({ data }) {
  const [show, setShow] = useState({
    hiragana: false,
    romaji: false,
    translation: false,
  });
  const toggle = (k) => setShow((s) => ({ ...s, [k]: !s[k] }));

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-2">
        <h3 className="text-lg font-bold">{data.title}</h3>
        {data.jlpt_ml && (
          <span className="rounded bg-indigo-100 px-2 py-0.5 text-xs font-semibold text-indigo-700">
            ML: {data.jlpt_ml}
          </span>
        )}
        {data.topic && (
          <span className="text-xs text-slate-400">topik: {data.topic}</span>
        )}
      </div>

      <p className="whitespace-pre-line text-lg leading-relaxed">
        {data.passage}
      </p>

      <div className="flex flex-wrap gap-2">
        {TOGGLES.map(([key, label]) =>
          data[key] ? (
            <button
              key={key}
              onClick={() => toggle(key)}
              className={`rounded-lg border px-2 py-1 text-xs ${
                show[key]
                  ? "border-indigo-500 bg-indigo-50 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-200"
                  : "border-slate-200 text-slate-500 dark:border-slate-700"
              }`}
            >
              {show[key] ? "Sembunyikan" : "Tampilkan"} {label}
            </button>
          ) : null,
        )}
      </div>

      {show.hiragana && <p className="text-slate-500">{data.hiragana}</p>}
      {show.romaji && <p className="italic text-slate-400">{data.romaji}</p>}
      {show.translation && (
        <p className="border-t border-slate-100 pt-2 dark:border-slate-800">
          {data.translation}
        </p>
      )}

      {data.vocabulary?.length > 0 && (
        <div className={box}>
          <p className="mb-1 font-semibold">
            📚 Kosakata dari database yang muncul di bacaan
          </p>
          <ul className="space-y-1">
            {data.vocabulary.map((v) => (
              <li key={v.id}>
                <span className="font-semibold">{v.word}</span>{" "}
                <span className="text-slate-500">({v.reading})</span>{" "}
                {v.meaning}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="border-t border-slate-100 pt-3 dark:border-slate-800">
        <p className="mb-2 text-sm font-semibold">Soal pemahaman</p>
        <QuizCard
          quiz={{ title: `Reading: ${data.title}`, questions: data.questions }}
        />
      </div>

      <p className="text-[11px] text-slate-400">
        Bacaan dan soal dibuat oleh AI lalu divalidasi bentuknya, tetapi isinya
        bisa mengandung kekeliruan.
      </p>
    </div>
  );
}
