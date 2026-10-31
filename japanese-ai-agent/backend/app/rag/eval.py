"""Membandingkan pencarian lexical, semantic, dan hybrid.
Jalankan:  python -m app.rag.eval  [--plot]"""
import sys
from pathlib import Path

from app.rag import retriever

# (pertanyaan, jenis dokumen yang benar, potongan judul dokumen yang benar)
# Kelompok 'mudah': kata pada pertanyaan mirip dengan isi dokumen.
# Kelompok 'sulit': parafrase dengan sedikit kata yang sama (di sinilah pencarian semantic diuji).
EASY = [
    ("setiap kali mendengar lagu itu saya teringat kampung", "grammar", "たびに"),
    ("bukan berarti saya tidak suka", "grammar", "わけではない"),
    ("gara-gara hujan acaranya batal", "grammar", "せいで"),
    ("berkat bantuan guru saya lulus", "grammar", "おかげで"),
    ("sekalian mampir ke kantor pos", "grammar", "ついでに"),
    ("selagi masih muda", "grammar", "うちに"),
    ("dia pasti lupa janjinya", "grammar", "に違いない"),
    ("dia hanya main game terus", "grammar", "ばかり"),
    ("saya memutuskan untuk berolahraga", "grammar", "ことにする"),
    ("he should have arrived already", "grammar", "はずだ"),
    ("minta maaf karena terlambat", "vocabulary", "謝る"),
    ("rapat kantor besok", "vocabulary", "会議"),
    ("kebiasaan jalan pagi", "vocabulary", "習慣"),
    ("dilarang parkir di sini", "vocabulary", "禁止"),
    ("gugup sebelum wawancara", "vocabulary", "緊張"),
    ("merasa lega setelah mendengar hasilnya", "vocabulary", "安心"),
    ("ask someone for help", "vocabulary", "求める"),
    ("menyiapkan perjalanan", "vocabulary", "準備"),
    ("ibu khawatir pada saya", "vocabulary", "心配"),
    ("merepotkan orang lain", "vocabulary", "迷惑"),
    ("kanji untuk bekerja", "kanji", "働"),
    ("彼は嘘をついたに違いない", "grammar", "に違いない"),
    ("雨のせいで遅れた", "grammar", "せいで"),
]

HARD = [
    ("ungkapan terima kasih karena bantuan seseorang menghasilkan hal baik", "grammar", "おかげで"),
    ("alasan negatif penyebab sesuatu gagal terjadi", "grammar", "せいで"),
    ("melakukan satu hal terus menerus tanpa henti", "grammar", "ばかり"),
    ("kesempatan sambil pergi ke tempat lain", "grammar", "ついでに"),
    ("pola untuk menyatakan keputusan pribadi", "grammar", "ことにする"),
    ("how to say something is certainly true based on logic", "grammar", "はずだ"),
    ("perasaan cemas sebelum tampil di depan orang", "vocabulary", "緊張"),
    ("aturan yang melarang sesuatu", "vocabulary", "禁止"),
    ("pertemuan formal di kantor", "vocabulary", "会議"),
    ("worried about a family member", "vocabulary", "心配"),
    ("being relieved after hearing good news", "vocabulary", "安心"),
    ("kata kerja untuk memberi tahu informasi kepada orang", "vocabulary", "伝える"),
]

TESTS = [(q, e, k, "mudah") for q, e, k in EASY] + [(q, e, k, "sulit") for q, e, k in HARD]

MODES = ["lexical", "semantic", "hybrid"]


def evaluate(mode):
    stats = {g: {"n": 0, "hit1": 0.0, "hit3": 0.0, "rr": 0.0} for g in ("mudah", "sulit", "semua")}
    misses = []
    for query, entity, key, group in TESTS:
        hits = retriever.search(query, k=5, mode=mode)
        if mode != "lexical" and hits and hits[0]["via"].startswith("lexical"):
            return None  # embedding tidak tersedia, hasilnya bukan hasil mode ini
        rank = next(
            (i for i, h in enumerate(hits, 1) if h["entity"] == entity and key in h["title"]),
            None,
        )
        for g in (group, "semua"):
            stats[g]["n"] += 1
            stats[g]["hit1"] += rank == 1
            stats[g]["hit3"] += bool(rank and rank <= 3)
            stats[g]["rr"] += 1 / rank if rank else 0
        if rank != 1:
            top = hits[0]["title"] if hits else "-"
            misses.append(f"  - [{group}] {query!r}: harusnya {key}, peringkat {rank or '>5'}, teratas {top}")
    out = {
        g: {"hit1": v["hit1"] / v["n"], "hit3": v["hit3"] / v["n"], "mrr": v["rr"] / v["n"], "n": v["n"]}
        for g, v in stats.items()
    }
    out["misses"] = misses
    return out


def main():
    results = {}
    print(f"{len(TESTS)} pertanyaan uji ({len(EASY)} mudah, {len(HARD)} sulit)\n")
    print(f"{'Mode':<10}{'Kelompok':<10}{'Hit@1':>8}{'Hit@3':>8}{'MRR':>8}")
    for mode in MODES:
        r = evaluate(mode)
        if r is None:
            print(f"{mode:<10}(dilewati: embedding tidak tersedia, jalankan: python -m app.rag.index)")
            continue
        results[mode] = r
        for g in ("mudah", "sulit", "semua"):
            print(f"{mode if g == 'mudah' else '':<10}{g:<10}{r[g]['hit1']:>8.0%}{r[g]['hit3']:>8.0%}{r[g]['mrr']:>8.2f}")

    for mode, r in results.items():
        if r["misses"]:
            print(f"\nPertanyaan yang belum tepat di peringkat 1 ({mode}):")
            print("\n".join(r["misses"]))

    if "--plot" in sys.argv and results:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np

        out = Path(__file__).resolve().parents[2] / "reports"
        out.mkdir(exist_ok=True)
        names = list(results)
        x = np.arange(len(names))
        fig, ax = plt.subplots(figsize=(7.5, 4.2))
        ax.bar(x - 0.27, [results[m]["mudah"]["hit1"] for m in names], 0.27, label="Hit@1 (mudah)", color="#10b981")
        ax.bar(x, [results[m]["sulit"]["hit1"] for m in names], 0.27, label="Hit@1 (sulit)", color="#ef4444")
        ax.bar(x + 0.27, [results[m]["semua"]["mrr"] for m in names], 0.27, label="MRR (semua)", color="#6366f1")
        ax.set_xticks(x)
        ax.set_xticklabels(names)
        ax.set_ylim(0, 1.05)
        ax.set_title(f"Retrieval: lexical vs semantic vs hybrid (n={len(TESTS)})")
        ax.legend()
        fig.tight_layout()
        fig.savefig(out / "10_rag_comparison.png", dpi=150)
        print("\nGrafik tersimpan:", out / "10_rag_comparison.png")


if __name__ == "__main__":
    main()