"""Quiz Agent: membuat soal pilihan ganda dari database (jawaban pasti benar, tanpa LLM)."""
import random

from app.database import repository as repo
from app.schemas import ChatResponse

BLANK = "（　　）"

PROMPTS = {
    "id": {
        "vocab_meaning": "Apa arti 「{x}」?",
        "vocab_reading": "Bagaimana cara membaca 「{x}」?",
        "vocab_cloze": "Pilih kata yang tepat untuk bagian kosong:\n{x}",
        "grammar_meaning": "Apa arti pola 「{x}」?",
        "grammar_cloze": "Pilih pola yang tepat untuk bagian kosong:\n{x}",
        "kanji_meaning": "Apa arti kanji 「{x}」?",
        "title": "Kuis",
        "intro": "Berikut {n} soal. Pilih jawabanmu, jawaban benar ditampilkan setelah dipilih.",
        "short": "Hanya {n} soal yang bisa dibuat dari data yang ada. Tambahkan data di CSV untuk soal lebih banyak.",
        "empty": "Data belum cukup untuk membuat kuis. Tambahkan kosakata, kanji, atau grammar di file CSV lalu jalankan seed.",
        "strokes": "goresan",
    },
    "en": {
        "vocab_meaning": "What does 「{x}」 mean?",
        "vocab_reading": "How do you read 「{x}」?",
        "vocab_cloze": "Choose the right word for the blank:\n{x}",
        "grammar_meaning": "What does the pattern 「{x}」 mean?",
        "grammar_cloze": "Choose the right pattern for the blank:\n{x}",
        "kanji_meaning": "What does the kanji 「{x}」 mean?",
        "title": "Quiz",
        "intro": "Here are {n} questions. Pick an answer and the correct one is shown after you choose.",
        "short": "Only {n} questions could be made from the current data. Add more data in the CSV files for more questions.",
        "empty": "Not enough data to build a quiz. Add vocabulary, kanji, or grammar to the CSV files and run the seed.",
        "strokes": "strokes",
    },
}


def _options(correct, pool, k=4):
    """Pilihan jawaban: 1 benar + sampai k-1 pengecoh dari pool. None jika pengecoh kurang."""
    others = [p for p in dict.fromkeys(pool) if p and p != correct]
    random.shuffle(others)
    opts = others[: k - 1] + [correct]
    if len(opts) < 3:
        return None
    random.shuffle(opts)
    return opts, opts.index(correct)


def _example(item):
    ex = item.get("example_jp") or ""
    tr = item.get("example_tr") or ""
    return f"\n{ex}" + (f" — {tr}" if tr else "") if ex else ""


def _build(prompt, correct, pool, explanation):
    opt = _options(correct, pool)
    if not opt:
        return None
    choices, answer = opt
    return {"prompt": prompt, "choices": choices, "answer": answer, "explanation": explanation}


# ---------- Pembuat soal per jenis ----------
def _vocab_meaning(v, vocab, P):
    expl = f"{v['word']} ({v['reading']}) = {v['meaning']}" + _example(v)
    return _build(P["vocab_meaning"].format(x=v["word"]), v["meaning"], [x["meaning"] for x in vocab], expl)


def _vocab_reading(v, vocab, P):
    if v["reading"] == v["word"]:
        return None  # kata tanpa kanji tidak perlu soal bacaan
    expl = f"{v['word']} dibaca {v['reading']} ({v['romaji']}) = {v['meaning']}"
    return _build(P["vocab_reading"].format(x=v["word"]), v["reading"], [x["reading"] for x in vocab], expl)


def _vocab_cloze(v, vocab, P):
    ex = v.get("example_jp") or ""
    if v.get("pos") != "noun" or v["word"] not in ex:
        return None
    sentence = ex.replace(v["word"], BLANK, 1)
    if v.get("example_tr"):
        sentence += f"\n({v['example_tr']})"
    nouns = [x["word"] for x in vocab if x.get("pos") == "noun"]
    expl = f"{v['word']} ({v['reading']}) = {v['meaning']}\n{ex}"
    return _build(P["vocab_cloze"].format(x=sentence), v["word"], nouns, expl)


def _grammar_meaning(g, grammar, P):
    expl = f"{g['pattern']} = {g['meaning']}\n{g.get('formation') or ''}" + _example(g)
    return _build(P["grammar_meaning"].format(x=g["pattern"]), g["meaning"], [x["meaning"] for x in grammar], expl)


def _core(g):
    return g["pattern"].lstrip("〜~")


def _grammar_cloze(g, grammar, P):
    ex = g.get("example_jp") or ""
    core = _core(g)
    if not core or core not in ex:
        return None  # contoh memakai bentuk lain (misalnya ～ません), lewati
    sentence = ex.replace(core, BLANK, 1)
    if g.get("example_tr"):
        sentence += f"\n({g['example_tr']})"
    expl = f"{g['pattern']} = {g['meaning']}\n{ex}"
    return _build(P["grammar_cloze"].format(x=sentence), core, [_core(x) for x in grammar], expl)


def _kanji_meaning(k, kanji, P):
    expl = (
        f"{k['character']}: on'yomi {k.get('onyomi') or '-'}, kun'yomi {k.get('kunyomi') or '-'}, "
        f"{k.get('stroke_count') or '?'} {P['strokes']}. {k.get('example_words') or ''}"
    )
    return _build(P["kanji_meaning"].format(x=k["character"]), k["meaning"], [x["meaning"] for x in kanji], expl)


def generate(params: dict, lang: str = "id") -> ChatResponse:
    P = PROMPTS.get(lang, PROMPTS["id"])
    n = max(1, min(int(params.get("n", 5)), 10))
    level, topic, focus = params.get("level"), params.get("topic"), params.get("focus")
    if topic and not focus:
        focus = "vocabulary"  # topik hanya ada di kosakata

    vocab = [v for v in repo.search_vocabulary(level=level, lang=lang, limit=500) if v.get("meaning")]
    grammar = [g for g in repo.search_grammar(level=level, lang=lang, limit=500) if g.get("meaning")]
    kanji = [k for k in repo.search_kanji(level=level, lang=lang, limit=500) if k.get("meaning")]

    # Kandidat soal: (jenis, subjek, fungsi pembuat)
    cands = []
    if focus in (None, "vocabulary"):
        for v in vocab:
            if topic and v.get("topic") != topic:
                continue
            cands += [
                ("vocab_meaning", v["word"], lambda v=v: _vocab_meaning(v, vocab, P)),
                ("vocab_reading", v["word"], lambda v=v: _vocab_reading(v, vocab, P)),
                ("vocab_cloze", v["word"], lambda v=v: _vocab_cloze(v, vocab, P)),
            ]
    if focus in (None, "grammar"):
        for g in grammar:
            cands += [
                ("grammar_meaning", g["pattern"], lambda g=g: _grammar_meaning(g, grammar, P)),
                ("grammar_cloze", g["pattern"], lambda g=g: _grammar_cloze(g, grammar, P)),
            ]
    if focus in (None, "kanji"):
        for k in kanji:
            cands.append(("kanji_meaning", k["character"], lambda k=k: _kanji_meaning(k, kanji, P)))
    random.shuffle(cands)

    questions, used, used_subjects = [], set(), set()
    for allow_repeat in (False, True):  # putaran 1: tiap subjek sekali, putaran 2: boleh berulang
        for kind, subject, make in cands:
            if len(questions) >= n:
                break
            if (kind, subject) in used or (not allow_repeat and subject in used_subjects):
                continue
            q = make()
            if not q:
                continue
            used.add((kind, subject))
            used_subjects.add(subject)
            questions.append({"id": len(questions) + 1, "kind": kind, **q})

    if not questions:
        return ChatResponse(type="info", message=P["empty"])

    label = {"vocabulary": "kosakata", "grammar": "grammar", "kanji": "kanji"}.get(focus, "")
    title = " ".join(x for x in [P["title"], label if lang == "id" else focus or "", level or ""] if x)
    message = P["intro"].format(n=len(questions))
    if len(questions) < n:
        message += " " + P["short"].format(n=len(questions))
    return ChatResponse(type="quiz", message=message, quiz={"title": title, "questions": questions})


def run(params: dict, lang: str = "id") -> ChatResponse:
    return generate(params, lang)