import { Paperclip, Mic, Send } from "lucide-react";

const MAX = 1000;

export default function ChatInput({ value, setValue, onSend, loading }) {
  const handleKey = (e) => {
    // Enter = kirim, Shift+Enter = baris baru
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  return (
    <div className="px-6 pb-4">
      <div className="mx-auto max-w-2xl rounded-xl border-2 border-indigo-200 bg-white p-3 shadow-sm focus-within:border-indigo-500 dark:border-slate-700 dark:bg-slate-900">
        <div className="flex items-start gap-2">
          <textarea
            rows={2}
            maxLength={MAX}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKey}
            placeholder="Ketik kalimat bahasa Jepang atau pertanyaanmu..."
            className="flex-1 resize-none bg-transparent text-sm outline-none dark:text-white"
          />
          <button
            onClick={onSend}
            disabled={loading || !value.trim()}
            className="grid h-8 w-8 place-items-center rounded-lg bg-indigo-600 text-white disabled:opacity-40"
          >
            <Send size={14} />
          </button>
        </div>
        <div className="mt-2 flex items-center gap-4 border-t border-slate-100 pt-2 text-xs text-slate-500 dark:border-slate-800">
          <button className="flex items-center gap-1 hover:text-indigo-600">
            <Paperclip size={12} /> Lampirkan
          </button>
          <button className="flex items-center gap-1 hover:text-indigo-600">
            <Mic size={12} /> Voice
          </button>
          <span className="ml-auto">
            {value.length}/{MAX}
          </span>
        </div>
      </div>
      <p className="mt-2 text-center text-[11px] text-slate-400">
        Sensei AI bisa keliru. Cek ulang tata bahasa penting di sumber resmi
        JLPT.
      </p>
    </div>
  );
}
