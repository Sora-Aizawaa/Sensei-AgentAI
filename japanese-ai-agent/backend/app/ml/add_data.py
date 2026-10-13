from pathlib import Path

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "sentences.csv"
LEVELS = {"5": "N5", "4": "N4", "3": "N3", "2": "N2", "1": "N1"}

print("Ketik kalimat Jepang, lalu level (5/4/3/2/1). Kosongkan kalimat untuk selesai.")
with open(DATA_PATH, "a", encoding="utf-8", newline="") as f:
    while True:
        text = input("Kalimat: ").strip()
        if not text:
            break
        level = LEVELS.get(input("Level (5/4/3/2/1): ").strip())
        if not level or "," in text:
            print("  -> dilewati (level salah atau ada tanda koma di kalimat)\n")
            continue
        f.write(f"{text},{level}\n")
        print("  -> tersimpan\n")

        