import { GrammarList, KanjiList, VocabList, box } from "./Cards";
import QuizCard from "./QuizCard";
import ReadingCard from "./ReadingCard";

const ENTITY_LABEL = { vocabulary: "Kosakata", grammar: "Grammar", kanji: "Kanji" };

// Daftar referensi database yang ditemukan RAG (bisa dibuka untuk melihat isinya)
function SourceList({ sources, title }) {
  return (
    <div className={box}>
      <p className="mb-1 font-semibold">{title}</p>
      <ul className="space-y-1">
        {sources.map((s, i) => (
          <li key={`${s.entity}-${s.entity_id}-${i}`}>
            <details>
              <summary className="cursor-pointer">
                <span className="font-semibold">{s.title}</span>{" "}
                <span className="text-slate-400">
                  {ENTITY_LABEL[s.entity] || s.entity} · skor {s.score}
                  {s.used === true && " · dipakai AI"}
                </span>
              </summary>
              <p className="mt-1 whitespace-pre-line text-slate-500">{s.text}</p>
            </details>
          </li>
        ))}
      </ul>
    </div>
  );
}

// Tampilan untuk balasan Sensei: koreksi atau ngobrol
function LanguageReply({ t }) {
  return (
    <div className="space-y-2">
      <p className="text-lg font-semibold">{t.japanese}</p>
      <p className="text-slate-500">{t.hiragana}</p>
      <p className="italic text-slate-400">{t.romaji}</p>
      <p className="border-t border-slate-100 pt-2 dark:border-slate-800">🇮🇩 {t.translation}</p>

      {t.warning && (
        <p className="rounded-lg bg-red-50 p-2 text-xs text-red-700 dark:bg-red-950 dark:text-red-200">
          ⚠️ {t.warning}
        </p>
      )}

      {t.errors?.length > 0 && (
        <div className="rounded-lg bg-rose-50 p-2 text-xs text-rose-800 dark:bg-rose-950 dark:text-rose-200">
          <p className="mb-1 font-semibold">🔎 Kesalahan yang ditemukan</p>
          <ul className="list-disc space-y-1 pl-4">
            {t.errors.map((e, i) => (
              <li key={i}>{e}</li>
            ))}
          </ul>
        </div>
      )}

      {t.rule_hints?.length > 0 && (
        <div className={box}>
          <p className="mb-1 font-semibold">🧪 Pemeriksa otomatis (berbasis aturan)</p>
          <ul className="space-y-1">
            {t.rule_hints.map((h, i) => (
              <li key={i}>
                <span className="font-semibold">
                  {h.wrong} → {h.right}
                </span>{" "}
                · {h.reason}
              </li>
            ))}
          </ul>
        </div>
      )}

      {t.feedback && (
        <p className="rounded-lg bg-amber-50 p-2 text-xs text-amber-800 dark:bg-amber-950 dark:text-amber-200">
          💡 {t.feedback}
        </p>
      )}

      {t.db_vocabulary?.length > 0 && (
        <div className={box}>
          <p className="mb-1 font-semibold">📚 Kosakata dari database</p>
          <ul className="space-y-1">
            {t.db_vocabulary.map((v) => (
              <li key={v.id}>
                <span className="font-semibold">{v.word}</span>{" "}
                <span className="text-slate-500">
                  ({v.reading} · {v.romaji})
                </span>{" "}
                {v.meaning} <span className="text-slate-400">{v.jlpt_level}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {t.db_grammar?.length > 0 && (
        <div className={box}>
          <p className="mb-1 font-semibold">📝 Grammar dari database</p>
          <ul className="space-y-1">
            {t.db_grammar.map((g) => (
              <li key={g.id}>
                <span className="font-semibold">{g.pattern}</span> {g.meaning}{" "}
                <span className="text-slate-400">{g.jlpt_level}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {t.sources?.length > 0 && <SourceList sources={t.sources} title="📎 Referensi dari database (RAG)" />}

      <div>
        {t.jlpt && (
          <span className="inline-block rounded bg-emerald-100 px-2 py-0.5 text-xs font-semibold text-emerald-700">
            LLM: {t.jlpt}
          </span>
        )}
        {t.jlpt_ml && (
          <span className="ml-2 inline-block rounded bg-indigo-100 px-2 py-0.5 text-xs font-semibold text-indigo-700">
            ML: {t.jlpt_ml}
          </span>
        )}
      </div>
    </div>
  );
}

export default function ChatMessage({ msg }) {
  const isUser = msg.sender === "user";
  const t = msg.text;
  const isObject = typeof t === "object" && t !== null;
  const type = isObject ? t.type || "correction" : "text";
  const wide = ["quiz", "vocabulary", "kanji", "grammar", "ask", "reading"].includes(type);

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`${wide ? "w-full max-w-[90%]" : "max-w-[80%]"} rounded-2xl px-4 py-3 text-sm ${
          isUser
            ? "bg-indigo-600 text-white"
            : "border border-slate-100 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900 dark:text-white"
        }`}
      >
        {!isObject && t}

        {isObject && (
          <div className="space-y-2">
            {t.message && <p className={type === "info" || type === "ask" ? "" : "text-slate-500"}>{t.message}</p>}

            {type === "vocabulary" && <VocabList items={t.items} />}
            {type === "kanji" && <KanjiList items={t.items} />}
            {type === "grammar" && <GrammarList items={t.items} />}
            {type === "quiz" && t.quiz && <QuizCard quiz={t.quiz} />}
            {type === "reading" && t.dokkai && <ReadingCard data={t.dokkai} />}
            {type === "ask" && t.sources?.length > 0 && <SourceList sources={t.sources} title="📎 Sumber dari database" />}
            {(type === "correction" || type === "chat") && <LanguageReply t={t} />}

            {t.route && <p className="text-[10px] text-slate-400">router: {t.route}</p>}
          </div>
        )}
      </div>
    </div>
  );
}
