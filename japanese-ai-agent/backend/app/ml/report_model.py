import hashlib
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# Font yang mendukung huruf Jepang di Windows
plt.rcParams["font.family"] = ["Yu Gothic", "Meiryo", "MS Gothic", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

BASE = Path(__file__).resolve().parents[2]
OUT = BASE / "reports"
OUT.mkdir(exist_ok=True)
WALK_DIR = OUT / "walkthroughs"
WALK_DIR.mkdir(exist_ok=True)

LEVELS = ["N5", "N4", "N3", "N2", "N1"]
COLORS = ["#6366f1", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"]

df = pd.read_csv(BASE / "data" / "sentences.csv").dropna()
X, y = df["text"].str.strip(), df["level"]

pipe = Pipeline([
    ("tfidf", TfidfVectorizer(analyzer="char", ngram_range=(1, 3), sublinear_tf=True)),
    ("clf", LogisticRegression(max_iter=1000, C=5.0, class_weight="balanced")),
]).fit(X, y)

tfidf = pipe.named_steps["tfidf"]
clf = pipe.named_steps["clf"]
features = np.array(tfidf.get_feature_names_out())
classes = list(clf.classes_)

# ---------- 08. Potongan karakter terpenting per level ----------
# Gambar ini hanya bergantung pada data latih, bukan pada kalimat yang diuji
fig, axes = plt.subplots(2, 3, figsize=(13, 7))
axes = axes.ravel()
for ax, level, color in zip(axes, LEVELS, COLORS):
    coef = clf.coef_[classes.index(level)]
    top = np.argsort(coef)[-10:]
    ax.barh(features[top], coef[top], color=color)
    ax.set_title(f"Potongan terkuat untuk {level}")
    ax.set_xlabel("Bobot Logistic Regression")
axes[-1].axis("off")
fig.suptitle("Apa yang dipelajari model (bobot tertinggi per level)", fontsize=13)
fig.tight_layout()
fig.savefig(OUT / "08_top_ngrams_per_level.png", dpi=150)
plt.close(fig)
print("Tersimpan:", OUT / "08_top_ngrams_per_level.png")

# ---------- 09. Satu kalimat dari awal sampai prediksi ----------
sentence = sys.argv[1] if len(sys.argv) > 1 else "彼の意見には賛成しかねる。"

# Nama file unik per kalimat: kalimat berbeda tidak akan saling menimpa
slug = hashlib.md5(sentence.encode("utf-8")).hexdigest()[:8]
walk_path = WALK_DIR / f"walkthrough_{slug}.png"

row = tfidf.transform([sentence]).toarray()[0]
nz = np.nonzero(row)[0]
probs = pipe.predict_proba([sentence])[0]
best = int(probs.argmax())

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

top = nz[np.argsort(row[nz])[-12:]]
axes[0].barh(features[top], row[top], color="#f59e0b")
axes[0].set_title("1. Bobot TF-IDF\n(12 potongan tertinggi)")
axes[0].set_xlabel("Bobot TF-IDF")

contrib = row * clf.coef_[best]
top = nz[np.argsort(contrib[nz])[-12:]]
axes[1].barh(features[top], contrib[top], color="#8b5cf6")
axes[1].set_title(f"2. Kontribusi ke {classes[best]}\n(bobot TF-IDF x bobot model)")
axes[1].set_xlabel("Kontribusi ke skor")

order = [classes.index(level) for level in LEVELS]
bars = axes[2].bar(LEVELS, probs[order], color=["#cbd5e1"] * 5)
bars[LEVELS.index(classes[best])].set_color("#8b5cf6")
axes[2].bar_label(bars, labels=[f"{p:.0%}" for p in probs[order]])
axes[2].set_ylim(0, 1)
axes[2].set_title("3. Probabilitas tiap level")

fig.suptitle(f"Kalimat: {sentence}", fontsize=13)
fig.tight_layout()
fig.savefig(walk_path, dpi=150)
plt.close(fig)
print("Tersimpan:", walk_path)

# ---------- Catat di index.md (daftar semua kalimat yang pernah diuji) ----------
index_path = WALK_DIR / "index.md"
entry = f"![{sentence}](backend/reports/walkthroughs/{walk_path.name})"
existing = index_path.read_text(encoding="utf-8") if index_path.exists() else ""
if entry not in existing:
    with open(index_path, "a", encoding="utf-8") as f:
        f.write(f"### {sentence}\n{entry}\n\n")

print("\nBaris untuk ditempel di README:")
print(entry)