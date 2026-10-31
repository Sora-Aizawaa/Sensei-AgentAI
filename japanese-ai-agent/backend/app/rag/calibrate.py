"""Memilih RAG_MIN_SCORE dan RAG_KEEP_RATIO berdasarkan data, bukan tebakan.
Jalankan:  python -m app.rag.calibrate"""
import statistics

from app.rag import retriever
from app.rag.context import filter_hits
from app.rag.eval import TESTS

# Pertanyaan yang SEHARUSNYA tidak menemukan apa pun di database
OFFTOPIC = [
    "cuaca hari ini", "tabini", "resep nasi goreng", "harga laptop terbaru",
    "asdfghjkl", "siapa presiden pertama indonesia", "how to install python",
    "klub sepak bola terbaik", "jadwal kereta ke bandung", "terjemahkan lagu ini",
]

FLOORS = [0, 0.40, 0.45, 0.50, 0.55]
RATIOS = [0.0, 0.80, 0.85, 0.90]


def best(h):
    return h["semantic"] if h.get("semantic") is not None else h["lexical"]


def main():
    sample = retriever.search("tes", k=1, mode="semantic")
    if not sample or sample[0]["via"] != "semantic":
        print("Embedding tidak tersedia. Jalankan: ollama pull bge-m3 lalu python -m app.rag.index")
        return

    rows = []  # (hits top-3, jawaban benar ada?, skor benar, skor salah tertinggi)
    for q, ent, key, _ in TESTS:
        hits = retriever.search(q, k=50, mode="semantic")
        correct = [best(h) for h in hits if h["entity"] == ent and key in h["title"]]
        wrong = [best(h) for h in hits if not (h["entity"] == ent and key in h["title"])]
        rows.append((hits[:3], bool(correct), correct[0] if correct else 0.0, wrong[0] if wrong else 0.0))
    off = [retriever.search(q, k=3, mode="semantic") for q in OFFTOPIC]
    off_top = [best(h[0]) for h in off]

    print("Skor semantic (cosine) pada data kamu:")
    print(f"  dokumen BENAR      : min {min(r[2] for r in rows):.2f} | median {statistics.median(r[2] for r in rows):.2f}")
    print(f"  dokumen SALAH teratas: median {statistics.median(r[3] for r in rows):.2f} | maks {max(r[3] for r in rows):.2f}")
    print(f"  pertanyaan di luar topik (skor teratas): median {statistics.median(off_top):.2f} | maks {max(off_top):.2f}")

    print(f"\n{'floor':>6}{'ratio':>7}{'recall':>9}{'rata2 dok':>11}{'tolak off-topic':>17}")
    best_cfg = None
    for floor in FLOORS:
        for ratio in RATIOS:
            kept = [filter_hits(r[0], floor, ratio) for r in rows]
            recall = sum(
                any(h["entity"] == ent and key in h["title"] for h in k)
                for k, (_, ent, key, _) in zip(kept, TESTS)
            ) / len(TESTS)
            avg = statistics.mean(len(k) for k in kept)
            rejected = sum(len(filter_hits(h, floor, ratio)) == 0 for h in off) / len(off)
            print(f"{floor:>6.2f}{ratio:>7.2f}{recall:>9.0%}{avg:>11.1f}{rejected:>17.0%}")
            score = (min(recall, rejected), -avg)  # utamakan keduanya tinggi, lalu konteks ringkas
            if best_cfg is None or score > best_cfg[0]:
                best_cfg = (score, floor, ratio, recall, rejected, avg)

    _, floor, ratio, recall, rejected, avg = best_cfg
    print(f"\nUsulan: RAG_MIN_SCORE={floor}  RAG_KEEP_RATIO={ratio}  "
          f"(recall {recall:.0%}, tolak off-topic {rejected:.0%}, rata-rata {avg:.1f} dokumen)")
    print("Letakkan di backend/.env lalu restart backend.")


if __name__ == "__main__":
    main()