import { getHealth } from "../services/api";
import { clearProgress } from "../services/progress";
import {
  Button,
  Notice,
  PageIntro,
  inputCls,
  useLoader,
} from "../components/ui";

export default function SettingsPage({
  language,
  setLanguage,
  mode,
  setMode,
  dark,
  setDark,
}) {
  const health = useLoader(getHealth, []);

  const Row = ({ label, hint, children }) => (
    <div className="flex items-center justify-between gap-4 border-b border-slate-100 py-3 dark:border-slate-800">
      <div>
        <p className="text-sm font-semibold">{label}</p>
        {hint && <p className="text-xs text-slate-500">{hint}</p>}
      </div>
      {children}
    </div>
  );

  return (
    <div className="space-y-4">
      <PageIntro>Pengaturan disimpan di browser ini.</PageIntro>

      <Row
        label="Bahasa terjemahan"
        hint="Dipakai di chat, kosakata, grammar, kuis, dan reading."
      >
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          className={inputCls}
        >
          <option value="id">Bahasa Indonesia</option>
          <option value="en">English</option>
        </select>
      </Row>

      <Row
        label="Mode chat"
        hint="Otomatis: Router memilih. Ngobrol atau Koreksi: memaksa mode untuk pesan biasa."
      >
        <select
          value={mode}
          onChange={(e) => setMode(e.target.value)}
          className={inputCls}
        >
          <option value="auto">Otomatis</option>
          <option value="chat">Ngobrol</option>
          <option value="correction">Koreksi</option>
        </select>
      </Row>

      <Row label="Tema">
        <select
          value={dark ? "dark" : "light"}
          onChange={(e) => setDark(e.target.value === "dark")}
          className={inputCls}
        >
          <option value="light">Terang</option>
          <option value="dark">Gelap</option>
        </select>
      </Row>

      <Row
        label="Catatan belajar"
        hint="Menghapus riwayat kuis dan reading di menu Progress."
      >
        <Button
          className="!bg-slate-500 hover:!bg-slate-600"
          onClick={() =>
            window.confirm("Hapus seluruh catatan belajar?") && clearProgress()
          }
        >
          Hapus catatan
        </Button>
      </Row>

      <section className="space-y-2 pt-2">
        <h3 className="font-semibold">Status backend</h3>
        {health.loading && (
          <p className="text-sm italic text-slate-400">Memeriksa...</p>
        )}
        {health.error && (
          <Notice tone="error">Backend tidak terjangkau: {health.error}</Notice>
        )}
        {health.data && (
          <Notice>
            Terhubung. Model LLM: <b>{health.data.model}</b> di{" "}
            {health.data.base_url}
          </Notice>
        )}
      </section>
    </div>
  );
}
