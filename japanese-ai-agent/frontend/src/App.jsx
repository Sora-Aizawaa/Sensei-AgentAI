import { useState, useEffect, useRef } from "react";
import Sidebar from "./components/Sidebar";
import RightPanel from "./components/RightPanel";
import Welcome from "./components/Welcome";
import ChatInput from "./components/ChatInput";
import ChatMessage from "./components/ChatMessage";
import { sendChat } from "./services/api";

export default function App() {
  const [dark, setDark] = useState(false);
  const [active, setActive] = useState("chat");
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const [language, setLanguage] = useState("id");

  const bottomRef = useRef(null);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
  }, [dark]);

  // Scroll otomatis ke pesan terbaru
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const userText = input;
    setMessages((prev) => [...prev, { sender: "user", text: userText }]);
    setInput("");
    setLoading(true);

    try {
      const data = await sendChat(userText, language);
      setMessages((prev) => [...prev, { sender: "sensei", text: data }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          sender: "sensei",
          text: "⚠️ Gagal terhubung ke server. Pastikan backend sedang berjalan.",
        },
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
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="rounded-lg border border-slate-200 bg-white px-2 py-1 text-xs dark:border-slate-700 dark:bg-slate-900 dark:text-white"
          >
            <option value="id">Bahasa Indonesia</option>
            <option value="en">English</option>
          </select>
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
