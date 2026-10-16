import re
from dataclasses import dataclass, field

from app import llm
from app.database import repository as repo

TOOL_INTENTS = {"vocabulary", "kanji", "grammar", "quiz"}

JP_CHAR = re.compile(r"[\u3040-\u30ff\u4e00-\u9fff]")
JP_RUN = re.compile(r"[〜~]?[\u3040-\u30ff\u4e00-\u9fff]+")
LEVEL_RE = re.compile(r"\bN([1-5])\b", re.IGNORECASE)
NUM_RE = re.compile(r"\b(\d{1,2})\b")

QUIZ_WORDS = ("kuis", "quiz", "soal", "test me")
GRAMMAR_WORDS = ("grammar", "tata bahasa", "pola kalimat", "pola tata", "bunpou", "文法")
KANJI_WORDS = ("kanji",)
VOCAB_WORDS = ("kosakata", "kosa kata", "vocab", "vocabulary", "kata baru", "daftar kata")
MEANING_WORDS = ("arti", "artinya", "makna", "meaning", "baca", "bacaan")
EXPLAIN_WORDS = ("jelaskan", "terangkan", "explain")
READING_WORDS = ("reading", "dokkai", "読解")
CORRECTION_WORDS = ("koreksi", "periksa kalimat", "cek kalimat", "benarkan")


@dataclass
class Route:
    intent: str  # correction | chat | vocabulary | kanji | grammar | quiz | reading
    params: dict = field(default_factory=dict)
    via: str = "rule"  # rule | mode | sticky | llm | default


def _has_any(lower: str, tokens: set, words) -> bool:
    for w in words:
        if (" " in w and w in lower) or w in tokens or (not w.isascii() and w in lower):
            return True
    return False


def _topics() -> list[str]:
    try:
        return [t["topic"] for t in repo.list_topics()]
    except Exception:
        return []  # database belum di-seed


def extract_params(message: str) -> dict:
    """Ambil parameter dari kalimat: level, jumlah, topik, dan kata/pola Jepang yang dicari."""
    params = {}
    lower = message.lower()

    m = LEVEL_RE.search(message)
    if m:
        params["level"] = f"N{m.group(1)}"

    n = NUM_RE.search(LEVEL_RE.sub(" ", message))  # angka di "N3" jangan dihitung
    if n:
        params["n"] = max(1, min(int(n.group(1)), 20))

    for topic in _topics():
        if topic.lower() in lower:
            params["topic"] = topic
            break

    runs = JP_RUN.findall(message)
    if runs:
        params["q"] = max(runs, key=len).lstrip("〜~")
    return params


ROUTER_PROMPT = """Klasifikasikan maksud pesan pengguna aplikasi belajar bahasa Jepang ke SATU intent:
- chat: ingin mengobrol, menyapa, atau bertanya hal umum
- vocabulary: meminta daftar atau arti kosakata
- kanji: menanyakan kanji
- grammar: menanyakan pola tata bahasa
- quiz: meminta soal latihan atau kuis
Balas HANYA JSON: {"intent": "<salah satu di atas>"}"""


def llm_route(message: str):
    """Cadangan untuk pesan yang tidak cocok dengan aturan. Gagal = None."""
    try:
        data = llm.chat_json(
            [{"role": "system", "content": ROUTER_PROMPT}, {"role": "user", "content": message}],
            max_tokens=60,
        )
        intent = str(data.get("intent", "")).strip().lower()
        if intent == "chat" or intent in TOOL_INTENTS:
            return intent
    except Exception as e:
        print("ROUTER LLM ERROR:", repr(e))
    return None


def route(message: str, mode: str = "auto", previous_type=None) -> Route:
    params = extract_params(message)
    lower = message.lower()
    tokens = set(re.findall(r"[a-z]+", lower))
    has_jp = bool(JP_CHAR.search(message))

    # 1. Permintaan alat (selalu didahulukan, apa pun modenya)
    if _has_any(lower, tokens, QUIZ_WORDS):
        if _has_any(lower, tokens, GRAMMAR_WORDS):
            params["focus"] = "grammar"
        elif _has_any(lower, tokens, KANJI_WORDS):
            params["focus"] = "kanji"
        elif _has_any(lower, tokens, VOCAB_WORDS) or "topic" in params:
            params["focus"] = "vocabulary"
        return Route("quiz", params, "rule")

    pattern_mark = "〜" in message or "~" in message
    if _has_any(lower, tokens, GRAMMAR_WORDS) or (
        pattern_mark and _has_any(lower, tokens, EXPLAIN_WORDS + MEANING_WORDS)
    ):
        return Route("grammar", params, "rule")

    if _has_any(lower, tokens, KANJI_WORDS):
        return Route("kanji", params, "rule")

    if _has_any(lower, tokens, READING_WORDS):
        return Route("reading", params, "rule")  # belum ada Reading Agent, dijawab dengan info

    short_word = len(params.get("q", "")) <= 8  # "arti 迷惑" ya, "arti kalimat panjang" bukan
    if _has_any(lower, tokens, VOCAB_WORDS) or (
        has_jp and short_word and _has_any(lower, tokens, MEANING_WORDS)
    ):
        return Route("vocabulary", params, "rule")

    # 2. Mode percakapan
    if _has_any(lower, tokens, CORRECTION_WORDS):
        return Route("correction", params, "rule")
    if mode in ("chat", "correction"):
        return Route(mode, params, "mode")
    if previous_type == "chat":
        return Route("chat", params, "sticky")  # lanjutkan obrolan yang sedang berjalan

    # 3. Mode otomatis
    if has_jp:
        return Route("correction", params, "rule")  # teks Jepang = minta diperiksa
    intent = llm_route(message)
    if intent:
        return Route(intent, params, "llm")
    return Route("chat", params, "default")