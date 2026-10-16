import { useState, useEffect, useRef } from "react";
import Sidebar from "./components/Sidebar";
import RightPanel from "./components/RightPanel";
import Welcome from "./components/Welcome";
import ChatInput from "./components/ChatInput";
import ChatMessage from "./components/ChatMessage";
import { sendChat } from "./services/api";

const MODES = [
  ["auto", "Otomatis"],
  ["chat", "Ngobrol"],
  ["correction", "Koreksi"],
];

export default function App() {
  const [dark, setDark] = useState(false);
  const [active, setActive] = useState("chat");
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState("id");
  const [mode, setMode] = useState("auto");
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

  return (
    <div className="flex h-screen bg-white dark:bg-slate-950">
      <Sidebar
        dark={dark}
        setDark={setDark}
        active={active}
        setActive={setActive}
      />

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
    </div>
  );
}
