from contextlib import closing

from app.database.connection import get_conn

# JOIN terjemahan: arti (meaning) dan terjemahan contoh (example) untuk bahasa :lang
TR_JOIN = """
LEFT JOIN translations tm ON tm.entity = '{e}' AND tm.entity_id = {a}.id
    AND tm.field = 'meaning' AND tm.lang = :lang
LEFT JOIN translations te ON te.entity = '{e}' AND te.entity_id = {a}.id
    AND te.field = 'example' AND te.lang = :lang
"""


def _fetch(sql, params=None):
    with closing(get_conn()) as conn:
        return [dict(r) for r in conn.execute(sql, params or {}).fetchall()]


# ---------- Kosakata ----------
def search_vocabulary(q=None, level=None, topic=None, lang="id", limit=20):
    sql = (
        "SELECT v.*, tm.text AS meaning, te.text AS example_tr FROM vocabulary v "
        + TR_JOIN.format(e="vocabulary", a="v")
        + " WHERE 1=1"
    )
    params = {"lang": lang, "limit": limit}
    if q:
        sql += " AND (v.word LIKE :q OR v.reading LIKE :q OR v.romaji LIKE :q OR tm.text LIKE :q)"
        params["q"] = f"%{q}%"
    if level:
        sql += " AND v.jlpt_level = :level"
        params["level"] = level
    if topic:
        sql += " AND v.topic = :topic"
        params["topic"] = topic
    sql += " ORDER BY v.id LIMIT :limit"
    return _fetch(sql, params)


def random_vocabulary(n=10, level=None, topic=None, lang="id"):
    sql = (
        "SELECT v.*, tm.text AS meaning, te.text AS example_tr FROM vocabulary v "
        + TR_JOIN.format(e="vocabulary", a="v")
        + " WHERE 1=1"
    )
    params = {"lang": lang, "n": n}
    if level:
        sql += " AND v.jlpt_level = :level"
        params["level"] = level
    if topic:
        sql += " AND v.topic = :topic"
        params["topic"] = topic
    sql += " ORDER BY RANDOM() LIMIT :n"
    return _fetch(sql, params)


def list_topics():
    return _fetch(
        "SELECT topic, COUNT(*) AS total FROM vocabulary "
        "WHERE topic IS NOT NULL AND topic != '' GROUP BY topic ORDER BY topic"
    )


# ---------- Kanji ----------
def search_kanji(q=None, level=None, lang="id", limit=20):
    sql = (
        "SELECT k.*, tm.text AS meaning FROM kanji k "
        + TR_JOIN.format(e="kanji", a="k")
        + " WHERE 1=1"
    )
    params = {"lang": lang, "limit": limit}
    if q:
        sql += (
            " AND (k.character LIKE :q OR k.onyomi LIKE :q OR k.kunyomi LIKE :q"
            " OR k.example_words LIKE :q OR tm.text LIKE :q)"
        )
        params["q"] = f"%{q}%"
    if level:
        sql += " AND k.jlpt_level = :level"
        params["level"] = level
    sql += " ORDER BY k.id LIMIT :limit"
    return _fetch(sql, params)


# ---------- Grammar ----------
def search_grammar(q=None, level=None, lang="id", limit=20):
    sql = (
        "SELECT g.*, tm.text AS meaning, te.text AS example_tr FROM grammar g "
        + TR_JOIN.format(e="grammar", a="g")
        + " WHERE 1=1"
    )
    params = {"lang": lang, "limit": limit}
    if q:
        sql += " AND (g.pattern LIKE :q OR g.example_jp LIKE :q OR tm.text LIKE :q)"
        params["q"] = f"%{q}%"
    if level:
        sql += " AND g.jlpt_level = :level"
        params["level"] = level
    sql += " ORDER BY g.id LIMIT :limit"
    return _fetch(sql, params)


# ---------- Analisis teks: cari kata/kanji/pola yang ada di sebuah kalimat ----------
def analyze_text(text, lang="id"):
    params = {"lang": lang, "text": text}

    # Kosakata: cocok kalau kata muncul utuh, atau (untuk kata kerja) batang katanya muncul
    vocab = _fetch(
        "SELECT v.*, tm.text AS meaning FROM vocabulary v "
        + TR_JOIN.format(e="vocabulary", a="v")
        + " WHERE instr(:text, v.word) > 0"
        "    OR (v.pos = 'verb' AND instr(:text, substr(v.word, 1, length(v.word) - 1)) > 0)"
        " ORDER BY v.id",
        params,
    )

    # Grammar: buang tanda 〜 / ~ di awal pola lalu cari di kalimat
    grammar = _fetch(
        "SELECT g.*, tm.text AS meaning FROM grammar g "
        + TR_JOIN.format(e="grammar", a="g")
        + " WHERE instr(:text, replace(replace(g.pattern, '〜', ''), '~', '')) > 0"
        " ORDER BY g.id",
        params,
    )

    # Kanji: ambil karakter kanji unik dari kalimat lalu cari di tabel kanji
    chars = sorted({c for c in text if "\u4e00" <= c <= "\u9fff"})
    kanji = []
    if chars:
        names = {f"c{i}": c for i, c in enumerate(chars)}
        placeholders = ", ".join(f":{n}" for n in names)
        kanji = _fetch(
            "SELECT k.*, tm.text AS meaning FROM kanji k "
            + TR_JOIN.format(e="kanji", a="k")
            + f" WHERE k.character IN ({placeholders}) ORDER BY k.id",
            {**params, **names},
        )

    return {"vocabulary": vocab, "grammar": grammar, "kanji": kanji}