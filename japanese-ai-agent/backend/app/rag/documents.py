
"""Mengubah baris database menjadi 'dokumen' teks yang bisa dicari."""
from contextlib import closing

from app.database.connection import get_conn


def _translations(conn, entity):
    """{entity_id: {"meaning": [(lang, teks)], "example": [(lang, teks)]}}"""
    rows = conn.execute(
        "SELECT entity_id, field, lang, text FROM translations WHERE entity = ? ORDER BY lang",
        (entity,),
    ).fetchall()
    out = {}
    for r in rows:
        out.setdefault(r["entity_id"], {}).setdefault(r["field"], []).append((r["lang"], r["text"]))
    return out


def _join(pairs):
    return " / ".join(text for _, text in pairs)  # semua bahasa digabung agar pencarian lintas bahasa bisa jalan


def build_documents():
    docs = []
    with closing(get_conn()) as conn:
        # ----- Kosakata -----
        tr = _translations(conn, "vocabulary")
        for r in conn.execute("SELECT * FROM vocabulary ORDER BY id"):
            t = tr.get(r["id"], {})
            parts = [
                f"Kosakata {r['jlpt_level']}: {r['word']} ({r['reading']}, {r['romaji']}).",
                f"Arti: {_join(t.get('meaning', []))}.",
            ]
            if r["topic"]:
                parts.append(f"Topik: {r['topic']}.")
            if r["example_jp"]:
                parts.append(f"Contoh: {r['example_jp']} {_join(t.get('example', []))}")
            docs.append({
                "entity": "vocabulary",
                "entity_id": r["id"],
                "title": f"{r['word']} ({r['reading']})",
                "text": " ".join(parts),
            })

        # ----- Grammar -----
        tr = _translations(conn, "grammar")
        for r in conn.execute("SELECT * FROM grammar ORDER BY id"):
            t = tr.get(r["id"], {})
            parts = [
                f"Tata bahasa {r['jlpt_level']}: {r['pattern']}.",
                f"Arti: {_join(t.get('meaning', []))}.",
            ]
            if r["formation"]:
                parts.append(f"Bentuk: {r['formation']}.")
            if r["example_jp"]:
                parts.append(f"Contoh: {r['example_jp']} {_join(t.get('example', []))}")
            docs.append({
                "entity": "grammar",
                "entity_id": r["id"],
                "title": r["pattern"],
                "text": " ".join(parts),
            })

        # ----- Kanji -----
        tr = _translations(conn, "kanji")
        for r in conn.execute("SELECT * FROM kanji ORDER BY id"):
            t = tr.get(r["id"], {})
            parts = [
                f"Kanji {r['jlpt_level']}: {r['character']}.",
                f"Arti: {_join(t.get('meaning', []))}.",
                f"On'yomi: {r['onyomi'] or '-'}. Kun'yomi: {(r['kunyomi'] or '-').replace('|', ', ')}.",
            ]
            if r["example_words"]:
                parts.append(f"Contoh kata: {r['example_words'].replace('|', ', ')}.")
            docs.append({
                "entity": "kanji",
                "entity_id": r["id"],
                "title": r["character"],
                "text": " ".join(parts),
            })
    return docs