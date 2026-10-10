import {
  MessageCircle,
  BookOpen,
  Languages,
  FileText,
  ClipboardList,
  BookMarked,
  BarChart3,
  Settings,
  HelpCircle,
  Search,
  Sun,
  Moon,
} from "lucide-react";

const menu = [
  { id: "chat", label: "Sensei Chat", icon: MessageCircle },
  { id: "vocab", label: "Kosakata", icon: BookOpen },
  { id: "kanji", label: "Kanji", icon: Languages },
  { id: "grammar", label: "Tata Bahasa", icon: FileText },
  { id: "quiz", label: "Kuis", icon: ClipboardList },
  { id: "reading", label: "Reading", icon: BookMarked },
  { id: "progress", label: "Progress", icon: BarChart3 },
];

function Item({ icon: Icon, label, active, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm transition ${
        active
          ? "bg-white font-semibold shadow-sm dark:bg-slate-800"
          : "text-slate-600 hover:bg-white/70 dark:text-slate-400 dark:hover:bg-slate-800/60"
      }`}
    >
      <Icon size={16} className={active ? "text-indigo-600" : ""} />
      {label}
    </button>
  );
}

export default function Sidebar({ dark, setDark, active, setActive }) {
  return (
    <aside className="flex w-60 shrink-0 flex-col bg-slate-100 p-4 dark:bg-slate-900">
      {/* Logo */}
      <div className="mb-5 flex items-center gap-2 px-1">
        <div className="grid h-8 w-8 place-items-center rounded-lg bg-indigo-600 text-lg text-white">
          日
        </div>
        <span className="font-bold dark:text-white">Sensei AI</span>
      </div>

      {/* Search */}
      <div className="mb-4 flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-400 dark:border-slate-700 dark:bg-slate-800">
        <Search size={14} /> Cari...
      </div>

      {/* Menu utama */}
      <nav className="space-y-1">
        {menu.map((m) => (
          <Item
            key={m.id}
            {...m}
            active={active === m.id}
            onClick={() => setActive(m.id)}
          />
        ))}
      </nav>

      <p className="mb-2 mt-6 px-3 text-xs text-slate-400">
        Pengaturan & Bantuan
      </p>
      <Item icon={Settings} label="Pengaturan" />
      <Item icon={HelpCircle} label="Bantuan" />

      {/* Toggle tema */}
      <div className="mt-auto">
        <div className="mb-4 grid grid-cols-2 rounded-lg bg-slate-200 p-1 text-xs dark:bg-slate-800">
          <button
            onClick={() => setDark(false)}
            className={`flex items-center justify-center gap-1 rounded-md py-1.5 ${!dark ? "bg-white shadow" : "text-slate-400"}`}
          >
            <Sun size={12} /> Light
          </button>
          <button
            onClick={() => setDark(true)}
            className={`flex items-center justify-center gap-1 rounded-md py-1.5 ${dark ? "bg-slate-700 text-white shadow" : "text-slate-500"}`}
          >
            <Moon size={12} /> Dark
          </button>
        </div>

        {/* Profil */}
        <div className="flex items-center gap-2 px-1">
          <div className="grid h-8 w-8 place-items-center rounded-full bg-indigo-200 text-sm font-bold text-indigo-700">
            L
          </div>
          <div className="text-xs">
            <p className="font-semibold dark:text-white">Leo</p>
            <p className="text-slate-400">Target: JLPT N3</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
