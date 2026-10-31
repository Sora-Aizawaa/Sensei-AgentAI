import { useState } from "react";
import { getGrammar } from "../services/api";
import { GrammarList } from "../components/Cards";
import {
  LevelSelect,
  PageIntro,
  Result,
  inputCls,
  useDebounced,
  useLoader,
} from "../components/ui";

export default function GrammarPage({ language }) {
  const [q, setQ] = useState("");
  const [level, setLevel] = useState("");
  const dq = useDebounced(q);
  const state = useLoader(
    () => getGrammar({ q: dq, level, lang: language, limit: 50 }),
    [dq, level, language],
  );

  return (
    <div className="space-y-4">
      <PageIntro>
        Pola tata bahasa dengan bentuk, arti, dan contoh kalimat.
      </PageIntro>
      <div className="flex flex-wrap gap-2">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Cari pola atau arti, misalnya: setiap kali"
          className={`${inputCls} min-w-[12rem] flex-1`}
        />
        <LevelSelect value={level} onChange={setLevel} />
      </div>
      <Result state={state} empty="Tidak ada pola yang cocok.">
        <p className="text-xs text-slate-400">{state.data?.count} pola</p>
        <GrammarList items={state.data?.items || []} />
      </Result>
    </div>
  );
}
