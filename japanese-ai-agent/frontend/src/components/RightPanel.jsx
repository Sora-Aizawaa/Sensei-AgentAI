import { MoreHorizontal } from "lucide-react";

const history = [
  { title: "Sesi baru", sub: "Mulai percakapan" },
  {
    title: "Koreksi: 昨日、学校に行きました",
    sub: "Kalimat sudah benar, level N5",
  },
  {
    title: "Kosakata topik pekerjaan",
    sub: "10 kata N3 — 働く, 会社, 迷惑...",
  },
  { title: "Kuis tata bahasa わけではない", sub: "Skor 4/5" },
  { title: "Reading: 日本の食文化", sub: "5 pertanyaan" },
];

export default function RightPanel() {
  return (
    <aside className="hidden w-72 shrink-0 border-l border-slate-100 p-4 dark:border-slate-800 xl:block">
      <div className="mb-3 flex items-center justify-between text-xs text-slate-500">
        <span className="font-semibold">Riwayat ({history.length})</span>
        <MoreHorizontal size={16} />
      </div>
      <div className="space-y-2">
        {history.map((h, i) => (
          <div
            key={i}
            className="cursor-pointer rounded-xl border border-slate-100 p-3 transition hover:bg-slate-50 dark:border-slate-800 dark:hover:bg-slate-900"
          >
            <p className="truncate text-xs font-semibold dark:text-white">
              {h.title}
            </p>
            <p className="truncate text-[11px] text-slate-400">{h.sub}</p>
          </div>
        ))}
      </div>
    </aside>
  );
}
