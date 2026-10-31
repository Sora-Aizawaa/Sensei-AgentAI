import { useState } from "react";
import { getKanji } from "../services/api";
import { KanjiList } from "../components/Cards";
import {
  LevelSelect,
  PageIntro,
  Result,
  inputCls,
  useDebounced,
  useLoader,
} from "../components/ui";

export default function KanjiPage({ language }) {
  const [q, setQ] = useState("");
  const [level, setLevel] = useState("");
  const dq = useDebounced(q);
  const state = useLoader(
    () => getKanji({ q: dq, level, lang: language, limit: 50 }),
    [dq, level, language],
  );

  return (
    <div className="space-y-4">
      <PageIntro>
        Kanji beserta on'yomi, kun'yomi, jumlah goresan, dan contoh kata.
      </PageIntro>
      <div className="flex flex-wrap gap-2">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Cari kanji, bacaan, atau arti..."
          className={`${inputCls} min-w-[12rem] flex-1`}
        />
        <LevelSelect value={level} onChange={setLevel} />
      </div>
      <Result state={state} empty="Tidak ada kanji yang cocok.">
        <p className="text-xs text-slate-400">{state.data?.count} kanji</p>
        <KanjiList items={state.data?.items || []} />
      </Result>
    </div>
  );
}
