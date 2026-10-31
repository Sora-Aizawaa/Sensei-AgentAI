"""Reading Agent: membuat bacaan N4-N3 pendek dengan soal pemahaman.
LLM menulis bacaannya; kosakata dari database dipakai sebagai bahan, dan hasilnya divalidasi ketat."""
import json
import random
import re

from app import llm
from app.database import repository as repo
from app.ml.difficulty import predict_level
from app.nlp.reading import reading as japanese_reading
from app.prompts import build_reading_prompt
from app.schemas import ChatResponse

JP = re.compile(r"[\u3040-\u30ff\u4e00-\u9fff]")
LETTER_LABEL = re.compile(r"^[A-Da-d][\.\):]\s+")  # "A. teks" -> "teks"
DEFAULT_TOPIC = "kehidupan sehari-hari"


def _pick_topic(topic):
    """Kembalikan (nama topik untuk prompt, kunci topik database atau None)."""
    try:
        known = [t["topic"] for t in repo.list_topics()]
    except Exception:
        known = []
    if topic:
        for k in known:
            if k.lower() == topic.strip().lower():
                return k, k
        return topic.strip(), None  # topik bebas yang tidak ada di database
    if known:
        k = random.choice(known)
        return k, k
    return DEFAULT_TOPIC, None


def _words_block(db_topic, lang):
    try:
        words = repo.random_vocabulary(5, None, db_topic, lang)
        if len(words) < 3:  # topik bebas atau datanya sedikit: ambil dari seluruh database
            words = repo.random_vocabulary(5, None, None, lang)
    except Exception:
        return ""
    if not words:
        return ""
    lines = [f"- {w['word']} ({w['reading']}) = {w.get('meaning') or ''}" for w in words]
    return "Gunakan beberapa kata berikut jika wajar dalam bacaan:\n" + "\n".join(lines)


def _to_str(v):
    return str(v or "").strip()


def _answer_index(answer, choices):
    """Terima huruf (A-D), nomor 1-4, atau teks pilihan itu sendiri. Kembalikan indeks 0-based atau None."""
    n = len(choices)
    if isinstance(answer, bool):
        return None
    if isinstance(answer, int):
        return answer - 1 if 1 <= answer <= n else None
    text = _to_str(answer)
    if len(text) >= 1 and text[0].upper() in "ABCD" and (len(text) == 1 or text[1] in ".):"):
        idx = "ABCD".index(text[0].upper())
        return idx if idx < n else None
    if text.isdigit():
        return int(text) - 1 if 1 <= int(text) <= n else None
    if text in choices:
        return choices.index(text)
    return None


def clean(data: dict) -> dict:
    """Validasi dan rapikan keluaran LLM. Melempar ValueError jika bacaan tidak layak dipakai."""
    data = {str(k).strip().lower(): v for k, v in data.items()}
    title = _to_str(data.get("title")) or "Bacaan"
    passage = _to_str(data.get("passage"))
    if len(passage) < 15 or not JP.search(passage):
        raise ValueError("bacaan kosong atau bukan bahasa Jepang")
    if "..." in passage and len(passage) < 40:
        raise ValueError("bacaan masih berupa placeholder")

    raw = data.get("questions")
    if not isinstance(raw, list):
        raise ValueError("soal tidak ada")

    questions = []
    for q in raw:
        if not isinstance(q, dict):
            continue
        question = _to_str(q.get("question"))
        choices = q.get("choices")
        if not question or not isinstance(choices, list):
            continue
        choices = [LETTER_LABEL.sub("", _to_str(c)) for c in choices if _to_str(c)][:4]
        if len(choices) < 3 or len(set(choices)) != len(choices):
            continue
        idx = _answer_index(q.get("answer"), choices)
        if idx is None:
            continue
        questions.append({
            "id": len(questions) + 1,
            "kind": "reading",
            "subject": title,
            "prompt": question,
            "choices": choices,
            "answer": idx,
            "explanation": _to_str(q.get("explanation")) or "-",
        })
    if len(questions) < 2:
        raise ValueError("soal yang valid kurang dari 2")

    return {"title": title, "passage": passage, "translation": _to_str(data.get("translation")), "questions": questions}


def run(topic, lang: str = "id") -> ChatResponse:
    language_name = llm.LANG_NAMES.get(lang, "Bahasa Indonesia")
    topic_text, db_topic = _pick_topic(topic)
    system = build_reading_prompt(language_name, topic_text, _words_block(db_topic, lang))

    dokkai, last_error = None, None
    for _ in range(2):  # sekali coba ulang jika format tidak valid
        try:
            data = llm.chat_json(
                [{"role": "system", "content": system}, {"role": "user", "content": f"Topik: {topic_text}"}],
                max_tokens=1500,
                temperature=0.7,  # agar bacaan bervariasi antar permintaan
            )
            dokkai = clean(data)
            break
        except (ValueError, json.JSONDecodeError) as e:
            last_error = e
            print("READING AGENT: keluaran tidak valid:", repr(e))
    if dokkai is None:
        raise ValueError(f"Gagal membuat bacaan yang valid: {last_error}")

    # Pengayaan oleh komponen yang bisa dipastikan (bukan LLM)
    passage = dokkai["passage"]
    try:
        dokkai["hiragana"], dokkai["romaji"] = japanese_reading(passage)
    except Exception as e:
        print("READING AGENT: bacaan gagal dihitung:", repr(e))
        dokkai["hiragana"] = dokkai["romaji"] = ""
    try:
        dokkai["vocabulary"] = repo.analyze_text(passage, lang)["vocabulary"]
    except Exception:
        dokkai["vocabulary"] = []
    pred = predict_level(passage)
    dokkai["jlpt_ml"] = f"JLPT {pred['level']} ({int(pred['confidence'] * 100)}%)" if pred else ""
    dokkai["topic"] = topic_text

    return ChatResponse(type="reading", message=f"Bacaan: {dokkai['title']}", dokkai=dokkai)
