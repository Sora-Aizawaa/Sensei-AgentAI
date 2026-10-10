export default function ChatMessage({ msg }) {
  const isUser = msg.sender === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm ${
          isUser
            ? "bg-indigo-600 text-white"
            : "border border-slate-100 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900 dark:text-white"
        }`}
      >
        {typeof msg.text === "string" ? (
          msg.text
        ) : (
          <div className="space-y-2">
            <p className="text-lg font-semibold">{msg.text.japanese}</p>
            <p className="text-slate-500">{msg.text.hiragana}</p>
            <p className="italic text-slate-400">{msg.text.romaji}</p>
            <p className="border-t border-slate-100 pt-2 dark:border-slate-800">
              🇮🇩 {msg.text.translation}
            </p>
            <span className="inline-block rounded bg-emerald-100 px-2 py-0.5 text-xs font-semibold text-emerald-700">
              {msg.text.jlpt}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
