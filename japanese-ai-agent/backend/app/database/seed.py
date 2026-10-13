import csv
import sys
from pathlib import Path

from app.database.connection import DB_PATH, get_conn
from app.database.schema import SCHEMA

DATA = Path(__file__).resolve().parents[2] / "data"

# kolom pertama = kolom unik (kunci)
TABLES = {
    "vocabulary": {
        "file": "vocabulary.csv",
        "cols": ["word", "reading", "romaji", "jlpt_level", "pos", "topic", "example_jp"],
    },
    "kanji": {
        "file": "kanji.csv",
        "cols": ["character", "onyomi", "kunyomi", "jlpt_level", "stroke_count", "example_words"],
    },
    "grammar": {
        "file": "grammar.csv",
        "cols": ["pattern", "jlpt_level", "formation", "example_jp", "example_reading"],
    },
}

# kolom example_* yang BUKAN terjemahan
RESERVED = {"example_jp", "example_reading", "example_words"}


def translation_columns(header):
    """Kolom meaning_xx dan example_xx otomatis dianggap terjemahan bahasa xx."""
    found = []
    for col in header:
        if col in RESERVED:
            continue
        if col.startswith("meaning_"):
            found.append((col, "meaning", col.split("_", 1)[1]))
        elif col.startswith("example_"):
            found.append((col, "example", col.split("_", 1)[1]))
    return found


def seed_table(conn, table, cfg):
    path = DATA / cfg["file"]
    if not path.exists():
        print(f"[dilewati] {path.name} tidak ditemukan")
        return

    cols = cfg["cols"]
    key = cols[0]
    col_list = ", ".join(cols)
    placeholders = ", ".join("?" for _ in cols)
    updates = ", ".join(f"{c}=excluded.{c}" for c in cols[1:])
    upsert_sql = (
        f"INSERT INTO {table} ({col_list}) VALUES ({placeholders}) "
        f"ON CONFLICT({key}) DO UPDATE SET {updates}"
    )
    select_sql = f"SELECT id FROM {table} WHERE {key} = ?"
    trans_sql = (
        "INSERT INTO translations (entity, entity_id, field, lang, text) VALUES (?, ?, ?, ?, ?) "
        "ON CONFLICT(entity, entity_id, field, lang) DO UPDATE SET text=excluded.text"
    )

    count = 0
    # utf-8-sig: aman untuk CSV yang disimpan dari Excel/Notepad (dengan BOM)
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        tcols = translation_columns(reader.fieldnames or [])
        for row in reader:
            values = []
            for c in cols:
                v = (row.get(c) or "").strip()
                if c == "stroke_count":
                    v = int(v) if v else None
                values.append(v)
            if not values[0]:
                continue

            conn.execute(upsert_sql, values)
            entity_id = conn.execute(select_sql, (values[0],)).fetchone()[0]

            for col, field, lang in tcols:
                text = (row.get(col) or "").strip()
                if text:
                    conn.execute(trans_sql, (table, entity_id, field, lang, text))
            count += 1

    print(f"{table}: {count} baris")


def main():
    if "--reset" in sys.argv and DB_PATH.exists():
        DB_PATH.unlink()
        print("Database lama dihapus.")

    conn = get_conn()
    try:
        conn.executescript(SCHEMA)
        for table, cfg in TABLES.items():
            seed_table(conn, table, cfg)
        conn.commit()
    finally:
        conn.close()
    print("Selesai. Database:", DB_PATH)


if __name__ == "__main__":
    main()