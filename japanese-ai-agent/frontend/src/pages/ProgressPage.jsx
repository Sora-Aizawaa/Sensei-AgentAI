import { useState } from "react";
import { clearProgress, loadProgress, summarize } from "../services/progress";
import { Button, Notice, PageIntro } from "../components/ui";

function Bar({ label, right, total }) {
  const pct = total ? Math.round((right / total) * 100) : 0;
  return (
    <div>
      <div className="mb-1 flex justify-between text-xs">
        <span className="font-semibold">{label}</span>
        <span className="text-slate-500">
          {right}/{total} benar ({pct}%)
        </span>
      </div>
      <div className="h-2 rounded bg-slate-100 dark:bg-slate-800">
        <div
          className="h-2 rounded bg-indigo-500"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

export default function ProgressPage() {
  const [data, setData] = useState(loadProgress);
  const s = summarize(data);

  const reset = () => {
    if (window.confirm("Hapus seluruh catatan kuis dan reading?")) {
      clearProgress();
      setData(loadProgress());
    }
  };

  if (s.quizCount === 0) {
    return (
      <div className="space-y-4">
        <PageIntro>Ringkasan belajarmu dari kuis dan soal reading.</PageIntro>
        <Notice>
          Belum ada catatan. Kerjakan satu kuis di menu Kuis atau Reading, lalu
          hasilnya muncul di sini.
        </Notice>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageIntro>
        Ringkasan dari kuis dan soal reading yang sudah kamu selesaikan. Data
        disimpan di browser ini saja.
      </PageIntro>

      <div className="grid grid-cols-3 gap-3 text-center">
        {[
          ["Kuis selesai", s.quizCount],
          ["Soal dijawab", s.totalQ],
          [
            "Akurasi",
            s.accuracy === null ? "-" : `${Math.round(s.accuracy * 100)}%`,
          ],
        ].map(([label, value]) => (
          <div
            key={label}
            className="rounded-xl border border-slate-100 p-3 dark:border-slate-800"
          >
            <p className="text-2xl font-bold">{value}</p>
            <p className="text-xs text-slate-500">{label}</p>
          </div>
        ))}
      </div>

      <section className="space-y-3">
        <h3 className="font-semibold">Akurasi per jenis soal</h3>
        {Object.entries(s.byGroup).map(([g, v]) => (
          <Bar key={g} label={g} right={v.right} total={v.total} />
        ))}
      </section>

      <section>
        <h3 className="mb-2 font-semibold">Perlu diulang</h3>
        {s.weak.length === 0 ? (
          <p className="text-sm text-slate-500">
            Belum ada jawaban yang salah. Bagus!
          </p>
        ) : (
          <ul className="space-y-1 text-sm">
            {s.weak.map((w) => (
              <li
                key={w.subject}
                className="flex justify-between rounded-lg border border-slate-100 px-3 py-2 dark:border-slate-800"
              >
                <span className="font-semibold">{w.subject}</span>
                <span className="text-slate-500">
                  salah {w.wrong}x, benar {w.right}x
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section>
        <h3 className="mb-2 font-semibold">Riwayat terakhir</h3>
        <ul className="space-y-1 text-sm">
          {s.recent.map((q) => (
            <li
              key={q.date}
              className="flex justify-between rounded-lg border border-slate-100 px-3 py-2 dark:border-slate-800"
            >
              <span>{q.title}</span>
              <span className="text-slate-500">
                {q.score}/{q.total} ·{" "}
                {new Date(q.date).toLocaleDateString("id-ID")}
              </span>
            </li>
          ))}
        </ul>
      </section>

      <Button onClick={reset} className="!bg-slate-500 hover:!bg-slate-600">
        Hapus catatan
      </Button>
    </div>
  );
}
