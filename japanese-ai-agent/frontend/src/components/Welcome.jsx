import {
  PenLine,
  BookOpen,
  ClipboardList,
  BookMarked,
  Plus,
} from "lucide-react";

const actions = [
  {
    label: "Koreksi kalimat",
    icon: PenLine,
    color: "bg-amber-100 text-amber-600",
    prompt: "Tolong koreksi kalimat saya: ",
  },
  {
    label: "Kosakata N3",
    icon: BookOpen,
    color: "bg-sky-100 text-sky-600",
    prompt: "Berikan 10 kosakata N3 tentang ",
  },
  {
    label: "Buat kuis",
    icon: ClipboardList,
    color: "bg-emerald-100 text-emerald-600",
    prompt: "Buat 5 soal kuis N3 tentang ",
  },
  {
    label: "Latihan reading",
    icon: BookMarked,
    color: "bg-pink-100 text-pink-600",
    prompt: "Buat teks reading N3 tentang ",
  },
];

export default function Welcome({ onPick }) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center px-6">
      <h1 className="text-4xl font-extrabold dark:text-white">
        Selamat datang! こんにちは 👋
      </h1>
      <p className="mt-3 max-w-md text-center text-sm text-slate-500">
        Saya Sensei AI, partner belajar JLPT N3 kamu. Pilih salah satu aksi di
        bawah atau langsung ketik kalimat bahasa Jepang.
      </p>

      <div className="mt-8 grid w-full max-w-xl grid-cols-2 gap-3">
        {actions.map((a) => (
          <button
            key={a.label}
            onClick={() => onPick(a.prompt)}
            className="flex items-center gap-3 rounded-xl border border-slate-100 bg-white p-3 text-left shadow-sm transition hover:shadow-md dark:border-slate-800 dark:bg-slate-900"
          >
            <span
              className={`grid h-9 w-9 place-items-center rounded-lg ${a.color}`}
            >
              <a.icon size={18} />
            </span>
            <span className="flex-1 text-sm font-semibold dark:text-white">
              {a.label}
            </span>
            <Plus size={14} className="text-slate-400" />
          </button>
        ))}
      </div>
    </div>
  );
}
