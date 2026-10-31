import { useState, useEffect, useRef } from "react";
import Sidebar from "./components/Sidebar";
import RightPanel from "./components/RightPanel";
import Welcome from "./components/Welcome";
import ChatInput from "./components/ChatInput";
import ChatMessage from "./components/ChatMessage";
import usePersistentState from "./hooks/usePersistentState";
import { sendChat } from "./services/api";
import GrammarPage from "./pages/GrammarPage";
import HelpPage from "./pages/HelpPage";
import KanjiPage from "./pages/KanjiPage";
import ProgressPage from "./pages/ProgressPage";
import QuizPage from "./pages/QuizPage";
import ReadingPage from "./pages/ReadingPage";
import SettingsPage from "./pages/SettingsPage";
import VocabularyPage from "./pages/VocabularyPage";

const MODES = [
  ["auto", "Otomatis"],
  ["chat", "Ngobrol"],
  ["correction", "Koreksi"],
];

// id menu di Sidebar -> halaman dan judulnya
const PAGES = {
  vocab: [VocabularyPage, "Kosakata"],
  kanji: [KanjiPage, "Kanji"],
  grammar: [GrammarPage, "Tata Bahasa"],
  quiz: [QuizPage, "Kuis"],
  reading: [ReadingPage, "Reading"],
  progress: [ProgressPage, "Progress"],
  settings: [SettingsPage, "Pengaturan"],
  help: [HelpPage, "Bantuan"],
};

export default function App() {
  const [dark, setDark] = usePersistentState("sensei.dark", false);
  const [language, setLanguage] = usePersistentState("sensei.language", "id");
  const [mode, setMode] = usePersistentState("sensei.mode", "auto");
  const [active, setActive] = useState("chat");
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
  }, [dark]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const userText = input;

    // Riwayat untuk mode ngobrol: 8 pesan terakhir sebelum pesan ini
    const history = messages
      .slice(-8)
      .map((m) => ({
        role: m.sender === "user" ? "user" : "assistant",
        content:
          typeof m.text === "string"
            ? m.text
            : m.text.japanese || m.text.message || "",
      }))
      .filter((h) => h.content && !h.content.startsWith("⚠️"));

    // Jenis balasan Sensei terakhir, supaya obrolan yang sedang berjalan bisa dilanjutkan
    const lastSensei = [...messages]
      .reverse()
      .find((m) => m.sender === "sensei");
    const previousType =
      lastSensei && typeof lastSensei.text === "object"
        ? lastSensei.text.type
        : null;

    setMessages((prev) => [...prev, { sender: "user", text: userText }]);
    setInput("");
    setLoading(true);

    try {
      const data = await sendChat(userText, language, {
        mode,
        previousType,
        history,
      });
      setMessages((prev) => [...prev, { sender: "sensei", text: data }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { sender: "sensei", text: `⚠️ ${err.message}` },
      ]);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Dari halaman Bantuan: isi kotak chat dengan contoh lalu pindah ke chat
  const tryExample = (text) => {
    setInput(text);
    setActive("chat");
  };

  const page = PAGES[active];
  const Page = page?.[0];

  return (
    <div className="flex h-screen bg-white dark:bg-slate-950">
      <Sidebar
        dark={dark}
        setDark={setDark}
        active={active}
        setActive={setActive}
      />

      {!Page ? (
        <>
          <main className="flex min-w-0 flex-1 flex-col">
            <header className="flex items-center justify-between border-b border-slate-100 px-6 py-3 dark:border-slate-800">
              <h2 className="font-bold dark:text-white">Sensei Chat</h2>

              <div className="flex items-center gap-3">
                <div className="flex gap-1 rounded-lg bg-slate-100 p-1 text-xs dark:bg-slate-800">
                  {MODES.map(([id, label]) => (
                    <button
                      key={id}
                      onClick={() => setMode(id)}
                      className={`rounded-md px-2 py-1 ${
                        mode === id
                          ? "bg-white font-semibold shadow dark:bg-slate-700 dark:text-white"
                          : "text-slate-500"
                      }`}
                    >
                      {label}
                    </button>
                  ))}
                </div>

                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="rounded-lg border border-slate-200 bg-white px-2 py-1 text-xs dark:border-slate-700 dark:bg-slate-900 dark:text-white"
                >
                  <option value="id">Bahasa Indonesia</option>
                  <option value="en">English</option>
                </select>
              </div>
            </header>

            {messages.length === 0 ? (
              <Welcome onPick={setInput} />
            ) : (
              <div className="flex-1 space-y-4 overflow-y-auto px-6 py-6">
                <div className="mx-auto max-w-2xl space-y-4">
                  {messages.map((m, i) => (
                    <ChatMessage key={i} msg={m} />
                  ))}
                  {loading && (
                    <p className="text-xs italic text-slate-400">
                      Sensei sedang mengetik...
                    </p>
                  )}
                  <div ref={bottomRef} />
                </div>
              </div>
            )}

            <ChatInput
              value={input}
              setValue={setInput}
              onSend={handleSend}
              loading={loading}
            />
          </main>

          <RightPanel />
        </>
      ) : (
        <main className="flex min-w-0 flex-1 flex-col">
          <header className="border-b border-slate-100 px-6 py-3 dark:border-slate-800">
            <h2 className="font-bold dark:text-white">{page[1]}</h2>
          </header>
          <div className="flex-1 overflow-y-auto px-6 py-6 dark:text-white">
            <div className="mx-auto max-w-3xl">
              <Page
                language={language}
                setLanguage={setLanguage}
                mode={mode}
                setMode={setMode}
                dark={dark}
                setDark={setDark}
                onTry={tryExample}
              />
            </div>
          </div>
        </main>
      )}
    </div>
  );
}
