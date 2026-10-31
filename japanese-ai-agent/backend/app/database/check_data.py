"""Memeriksa file CSV sebelum di-seed.   Jalankan:  python -m app.database.check_data"""
import csv
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / "data"
LEVELS = {"N1", "N2", "N3", "N4", "N5"}
POS = {"noun", "verb", "adjective", "adverb", "other"}

SPECS = {
    "vocabulary": {
        "pattern": "vocabulary*.csv",
        "key": "word",
        "required": ["word", "reading", "romaji", "jlpt_level", "pos", "meaning_id"],
    },
    "kanji": {
        "pattern": "kanji*.csv",
        "key": "character",
        "required": ["character", "onyomi", "jlpt_level", "stroke_count", "meaning_id"],
    },
    "grammar": {
        "pattern": "grammar*.csv",
        "key": "pattern",
        "required": ["pattern", "jlpt_level", "formation", "example_jp", "meaning_id"],
    },
}


def check_file(name, spec, path, seen, errors, warnings):
    try:
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        errors.append(f"{path.name}: bukan UTF-8. Di VS Code pilih Save with Encoding > UTF-8.")
        return 0

    reader = csv.DictReader(text.splitlines())
    header = reader.fieldnames or []
    missing = [c for c in spec["required"] if c not in header]
    if missing:
        errors.append(f"{path.name}: kolom wajib tidak ada: {', '.join(missing)}")
        return 0

    langs = sorted({c.split("_", 1)[1] for c in header if c.startswith("meaning_")})
    count = 0
    for row in reader:
        line = reader.line_num
        where = f"{path.name} baris {line}"
        if None in row:
            errors.append(f"{where}: kolom berlebih. Ada koma di dalam sel? Pakai 、 atau tulis ulang tanpa koma.")
            continue
        if any(v is None for v in row.values()):
            errors.append(f"{where}: jumlah kolom kurang dari header.")
            continue

        key = (row[spec["key"]] or "").strip()
        if not key:
            errors.append(f"{where}: kolom {spec['key']} kosong.")
            continue
        empty = [c for c in spec["required"] if not (row[c] or "").strip() and c != "onyomi"]
        if empty:
            errors.append(f"{where} ({key}): kolom wajib kosong: {', '.join(empty)}")
        if row["jlpt_level"].strip() not in LEVELS:
            errors.append(f"{where} ({key}): jlpt_level '{row['jlpt_level']}' harus N1 sampai N5 (huruf besar).")
        if name == "vocabulary" and row["pos"].strip() not in POS:
            errors.append(f"{where} ({key}): pos '{row['pos']}' harus salah satu dari {sorted(POS)}.")
        if name == "kanji" and not row["stroke_count"].strip().isdigit():
            errors.append(f"{where} ({key}): stroke_count harus angka.")

        if key in seen:
            errors.append(f"{where} ({key}): duplikat dengan {seen[key]}.")
        seen[key] = where

        for lang in langs:
            if not (row.get(f"meaning_{lang}") or "").strip():
                warnings.append(f"{where} ({key}): meaning_{lang} kosong.")
            if row.get("example_jp") and f"example_{lang}" in header and not (row.get(f"example_{lang}") or "").strip():
                warnings.append(f"{where} ({key}): example_{lang} kosong padahal ada example_jp.")
        count += 1
    return count


def main():
    errors, warnings = [], []
    for name, spec in SPECS.items():
        paths = sorted(DATA.glob(spec["pattern"]))
        if not paths:
            warnings.append(f"tidak ada file {spec['pattern']}")
        seen, total = {}, 0
        for path in paths:
            total += check_file(name, spec, path, seen, errors, warnings)
        print(f"{name}: {total} baris dibaca dari {len(paths)} file")

    for w in warnings:
        print("PERINGATAN:", w)
    for e in errors:
        print("ERROR:", e)
    print(f"\n{len(errors)} error, {len(warnings)} peringatan.")
    if errors:
        print("Perbaiki error di atas sebelum menjalankan: python -m app.database.seed")
        sys.exit(1)
    print("Data siap di-seed.")


if __name__ == "__main__":
    main()