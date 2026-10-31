import { useState } from "react";
import { getRandomVocabulary, getTopics, getVocabulary } from "../services/api";
import { VocabList } from "../components/Cards";
import {
  Button,
  LevelSelect,
  PageIntro,
  Result,
  inputCls,
  useDebounced,
  useLoader,
} from "../components/ui";

export default function VocabularyPage({ language }) {
  const [q, setQ] = useState("");
  const [level, setLevel] = useState("");
  const [topic, setTopic] = useState("");
  const [shuffle, setShuffle] = useState(0); // 0 = daftar biasa, naik setiap kali tombol Acak diklik
  const dq = useDebounced(q);

  const topics = useLoader(getTopics, []);
  const state = useLoader(
    () =>
      shuffle
        ? getRandomVocabulary({ n: 10, level, topic, lang: language })
        : getVocabulary({ q: dq, level, topic, lang: language, limit: 50 }),
    [dq, level, topic, language, shuffle],
  );

  return (
    <div className="space-y-4">
      <PageIntro>
        Cari kosakata dari database. Bisa dicari dengan kanji, bacaan, romaji,
        atau arti.
      </PageIntro>

      <div className="flex flex-wrap gap-2">
        <input
          value={q}
          onChange={(e) => {
            setQ(e.target.value);
            setShuffle(0);
          }}
          placeholder="Cari kata atau arti..."
          className={`${inputCls} min-w-[12rem] flex-1`}
        />
        <LevelSelect value={level} onChange={setLevel} />
        <select
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          className={inputCls}
        >
          <option value="">Semua topik</option>
          {topics.data?.items.map((t) => (
            <option key={t.topic} value={t.topic}>
              {t.topic} ({t.total})
            </option>
          ))}
        </select>
        <Button onClick={() => setShuffle((n) => n + 1)}>🎲 Acak 10</Button>
      </div>

      <Result state={state} empty="Tidak ada kosakata yang cocok.">
        <p className="text-xs text-slate-400">
          {state.data?.count} kata{shuffle ? " (acak)" : ""}
        </p>
        <VocabList items={state.data?.items || []} />
      </Result>
    </div>
  );
}
