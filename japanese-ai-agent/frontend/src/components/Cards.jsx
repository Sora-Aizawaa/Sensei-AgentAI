export const box =
  "rounded-lg border border-slate-100 p-2 text-xs dark:border-slate-800";

export function VocabList({ items }) {
  return (
    <ul className="space-y-2">
      {items.map((v) => (
        <li key={v.id} className={box}>
          <p>
            <span className="text-lg font-semibold">{v.word}</span>{" "}
            <span className="text-slate-500">
              {v.reading} · {v.romaji}
            </span>{" "}
            <span className="text-slate-400">{v.jlpt_level}</span>
          </p>
          <p className="font-semibold">{v.meaning}</p>
          {v.example_jp && (
            <p className="mt-1 text-slate-500">
              {v.example_jp}
              {v.example_tr && (
                <span className="text-slate-400"> — {v.example_tr}</span>
              )}
            </p>
          )}
        </li>
      ))}
    </ul>
  );
}

export function KanjiList({ items }) {
  return (
    <ul className="space-y-2">
      {items.map((k) => (
        <li key={k.id} className={`${box} flex gap-3`}>
          <span className="text-4xl font-semibold">{k.character}</span>
          <div>
            <p className="font-semibold">{k.meaning}</p>
            <p className="text-slate-500">
              On: {k.onyomi || "-"} · Kun:{" "}
              {(k.kunyomi || "-").split("|").join(", ")}
            </p>
            <p className="text-slate-400">
              {k.stroke_count} goresan · {k.jlpt_level}
              {k.example_words && ` · ${k.example_words.split("|").join("、")}`}
            </p>
          </div>
        </li>
      ))}
    </ul>
  );
}

export function GrammarList({ items }) {
  return (
    <ul className="space-y-2">
      {items.map((g) => (
        <li key={g.id} className={box}>
          <p>
            <span className="text-lg font-semibold">{g.pattern}</span>{" "}
            <span className="text-slate-400">{g.jlpt_level}</span>
          </p>
          <p className="font-semibold">{g.meaning}</p>
          {g.formation && (
            <p className="text-slate-500">Bentuk: {g.formation}</p>
          )}
          {g.example_jp && (
            <p className="mt-1">
              {g.example_jp}
              {g.example_reading && (
                <span className="block text-slate-400">
                  {g.example_reading}
                </span>
              )}
              {g.example_tr && (
                <span className="block text-slate-500">{g.example_tr}</span>
              )}
            </p>
          )}
        </li>
      ))}
    </ul>
  );
}
