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

            {msg.text.feedback && (
              <p className="rounded-lg bg-amber-50 p-2 text-xs text-amber-800 dark:bg-amber-950 dark:text-amber-200">
                💡 {msg.text.feedback}
              </p>
            )}

            {msg.text.db_vocabulary?.length > 0 && (
              <div className="rounded-lg border border-slate-100 p-2 text-xs dark:border-slate-800">
                <p className="mb-1 font-semibold">📚 Kosakata dari database</p>
                <ul className="space-y-1">
                  {msg.text.db_vocabulary.map((v) => (
                    <li key={v.id}>
                      <span className="font-semibold">{v.word}</span>{" "}
                      <span className="text-slate-500">
                        ({v.reading} · {v.romaji})
                      </span>{" "}
                      {v.meaning}{" "}
                      <span className="text-slate-400">{v.jlpt_level}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {msg.text.db_grammar?.length > 0 && (
              <div className="rounded-lg border border-slate-100 p-2 text-xs dark:border-slate-800">
                <p className="mb-1 font-semibold">📝 Grammar dari database</p>
                <ul className="space-y-1">
                  {msg.text.db_grammar.map((g) => (
                    <li key={g.id}>
                      <span className="font-semibold">{g.pattern}</span>{" "}
                      {g.meaning}{" "}
                      <span className="text-slate-400">{g.jlpt_level}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div>
              {msg.text.jlpt && (
                <span className="inline-block rounded bg-emerald-100 px-2 py-0.5 text-xs font-semibold text-emerald-700">
                  LLM: {msg.text.jlpt}
                </span>
              )}
              {msg.text.jlpt_ml && (
                <span className="ml-2 inline-block rounded bg-indigo-100 px-2 py-0.5 text-xs font-semibold text-indigo-700">
                  ML: {msg.text.jlpt_ml}
                </span>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
