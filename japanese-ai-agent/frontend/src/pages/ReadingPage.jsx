import { useState } from "react";
import { getReadingPractice, getTopics } from "../services/api";
import ReadingCard from "../components/ReadingCard";
import {
  Button,
  Notice,
  PageIntro,
  inputCls,
  useLoader,
} from "../components/ui";

export default function ReadingPage({ language }) {
  const [topic, setTopic] = useState("");
  const [run, setRun] = useState({
    key: 0,
    loading: false,
    error: "",
    data: null,
  });
  const topics = useLoader(getTopics, []);

  const start = async () => {
    setRun((r) => ({ ...r, loading: true, error: "" }));
    try {
      const res = await getReadingPractice(topic, language);
      setRun((r) => ({
        key: r.key + 1,
        loading: false,
        error: "",
        data: res.dokkai,
      }));
    } catch (err) {
      setRun((r) => ({ ...r, loading: false, error: err.message }));
    }
  };

  return (
    <div className="space-y-4">
      <PageIntro>
        Bacaan pendek level N4 sampai N3 dengan soal pemahaman. AI menulis
        bacaannya memakai kosakata dari databasemu, lalu hiragana, romaji, dan
        level dihitung oleh komponen terpisah.
      </PageIntro>

      <div className="flex flex-wrap gap-2">
        <select
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          className={inputCls}
        >
          <option value="">Topik acak</option>
          {topics.data?.items.map((t) => (
            <option key={t.topic} value={t.topic}>
              {t.topic}
            </option>
          ))}
        </select>
        <Button onClick={start} disabled={run.loading}>
          {run.loading ? "Menulis bacaan..." : "Buat bacaan"}
        </Button>
      </div>

      {run.loading && (
        <Notice>
          Sensei sedang menulis bacaan. Ini bisa memakan waktu setengah menit
          atau lebih, tergantung modelmu.
        </Notice>
      )}
      {run.error && <Notice tone="error">{run.error}</Notice>}
      {run.data && (
        <div className="rounded-xl border border-slate-100 p-4 dark:border-slate-800">
          <ReadingCard key={run.key} data={run.data} />
        </div>
      )}
    </div>
  );
}
