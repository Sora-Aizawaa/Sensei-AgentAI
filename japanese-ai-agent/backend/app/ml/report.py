from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # simpan ke file, tanpa membuka jendela
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import StratifiedKFold, cross_val_predict, learning_curve
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

BASE = Path(__file__).resolve().parents[2]
OUT = BASE / "reports"
OUT.mkdir(exist_ok=True)

LEVELS = ["N5", "N4", "N3", "N2", "N1"]
ORDER = {"N5": 5, "N4": 4, "N3": 3, "N2": 2, "N1": 1}
COLORS = ["#6366f1", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"]

df = pd.read_csv(BASE / "data" / "sentences.csv").dropna()
X, y = df["text"].str.strip(), df["level"]
folds = min(5, int(y.value_counts().min()))
cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=42)


def make_pipe(ngram=(1, 3), clf=None):
    clf = clf or LogisticRegression(max_iter=1000, C=5.0, class_weight="balanced")
    return Pipeline([
        ("tfidf", TfidfVectorizer(analyzer="char", ngram_range=ngram, sublinear_tf=True)),
        ("clf", clf),
    ])


def acc_scores(true, pred):
    diff = np.abs(pd.Series(pred).map(ORDER).values - pd.Series(true).map(ORDER).values)
    return (diff == 0).mean(), (diff <= 1).mean()


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=150)
    plt.close(fig)
    print("Tersimpan:", OUT / name)


# Prediksi cross-validation untuk model utama
pred = cross_val_predict(make_pipe(), X, y, cv=cv)
exact, within1 = acc_scores(y, pred)

# ---------- 1. Distribusi data ----------
counts = y.value_counts().reindex(LEVELS).fillna(0).astype(int)
fig, ax = plt.subplots(figsize=(6, 4))
bars = ax.bar(LEVELS, counts.values, color=COLORS)
ax.bar_label(bars)
ax.set_title(f"Training data per level (total {len(df)})")
ax.set_xlabel("JLPT level")
ax.set_ylabel("Number of sentences")
save(fig, "01_class_distribution.png")

# ---------- 2. Confusion matrix ----------
cm = confusion_matrix(y, pred, labels=LEVELS)
fig, ax = plt.subplots(figsize=(6, 5))
im = ax.imshow(cm, cmap="Blues")
ax.set_xticks(range(len(LEVELS)))
ax.set_xticklabels(LEVELS)
ax.set_yticks(range(len(LEVELS)))
ax.set_yticklabels(LEVELS)
for i in range(len(LEVELS)):
    for j in range(len(LEVELS)):
        ax.text(j, i, cm[i, j], ha="center", va="center",
                color="white" if cm[i, j] > cm.max() / 2 else "black")
ax.set_xlabel("Predicted level")
ax.set_ylabel("Actual level")
ax.set_title("Confusion matrix (cross-validation)")
fig.colorbar(im, ax=ax)
save(fig, "02_confusion_matrix.png")

# ---------- 3. Precision / recall / f1 per level ----------
p, r, f, _ = precision_recall_fscore_support(y, pred, labels=LEVELS, zero_division=0)
x = np.arange(len(LEVELS))
w = 0.26
fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(x - w, p, w, label="Precision", color="#6366f1")
ax.bar(x, r, w, label="Recall", color="#10b981")
ax.bar(x + w, f, w, label="F1-score", color="#f59e0b")
ax.set_xticks(x)
ax.set_xticklabels(LEVELS)
ax.set_ylim(0, 1)
ax.set_ylabel("Score")
ax.set_title("Per-level metrics (cross-validation)")
ax.legend()
save(fig, "03_per_class_metrics.png")

# ---------- 4. Akurasi vs baseline acak ----------
nums = list(ORDER.values())
base_exact = 1 / len(nums)
base_within1 = np.mean([sum(abs(a - b) <= 1 for b in nums) / len(nums) for a in nums])
fig, ax = plt.subplots(figsize=(6, 4))
x = np.arange(2)
b1 = ax.bar(x - 0.18, [exact, within1], 0.36, label="Model", color="#6366f1")
b2 = ax.bar(x + 0.18, [base_exact, base_within1], 0.36, label="Random baseline", color="#cbd5e1")
ax.bar_label(b1, labels=[f"{v:.0%}" for v in (exact, within1)])
ax.bar_label(b2, labels=[f"{v:.0%}" for v in (base_exact, base_within1)])
ax.set_xticks(x)
ax.set_xticklabels(["Exact accuracy", "Within ±1 level"])
ax.set_ylim(0, 1)
ax.set_title("Model vs random baseline")
ax.legend()
save(fig, "04_accuracy_vs_baseline.png")

# ---------- 5. Perbandingan konfigurasi model ----------
configs = {
    "char(1,2)\nLogReg": ((1, 2), None),
    "char(1,3)\nLogReg": ((1, 3), None),
    "char(1,4)\nLogReg": ((1, 4), None),
    "char(2,4)\nLogReg": ((2, 4), None),
    "char(1,3)\nLogReg C=20": ((1, 3), LogisticRegression(max_iter=1000, C=20, class_weight="balanced")),
    "char(1,3)\nLinearSVC": ((1, 3), LinearSVC(class_weight="balanced")),
}
names, ex_list, w1_list = [], [], []
for name, (ngram, clf) in configs.items():
    pr = cross_val_predict(make_pipe(ngram, clf), X, y, cv=cv)
    e, w1 = acc_scores(y, pr)
    names.append(name)
    ex_list.append(e)
    w1_list.append(w1)

x = np.arange(len(names))
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.bar(x - 0.18, ex_list, 0.36, label="Exact", color="#6366f1")
ax.bar(x + 0.18, w1_list, 0.36, label="Within ±1 level", color="#10b981")
ax.set_xticks(x)
ax.set_xticklabels(names, fontsize=8)
ax.set_ylim(0, 1)
ax.set_ylabel("Accuracy")
ax.set_title(f"Model configurations (n={len(df)}; differences are within noise at this size)")
ax.legend()
save(fig, "05_model_comparison.png")

# ---------- 6. Learning curve ----------
sizes, _, val = learning_curve(
    make_pipe(), X, y, cv=cv,
    train_sizes=[0.2, 0.4, 0.6, 0.8, 1.0],
    scoring="accuracy", shuffle=True, random_state=42,
)
mean, std = val.mean(axis=1), val.std(axis=1)
fig, ax = plt.subplots(figsize=(6.5, 4.2))
ax.plot(sizes, mean, marker="o", color="#6366f1", label="Validation accuracy")
ax.fill_between(sizes, mean - std, mean + std, alpha=0.2, color="#6366f1", label="±1 std across folds")
ax.axhline(base_exact, ls="--", color="#94a3b8", label="Random baseline")
ax.set_xlabel("Training sentences")
ax.set_ylabel("Accuracy")
ax.set_ylim(0, 1)
ax.set_title("Learning curve")
ax.legend()
save(fig, "06_learning_curve.png")

# ---------- 7. Probabilitas untuk contoh kalimat ----------
samples = [
    "私は毎朝パンを食べます。",
    "雨が降りそうなので、出かけないことにした。",
    "彼の発言は看過しがたいものがある。",
]
final = make_pipe().fit(X, y)
probs = final.predict_proba(samples)
order_idx = [list(final.classes_).index(l) for l in LEVELS]
probs = probs[:, order_idx]

x = np.arange(len(LEVELS))
w = 0.26
fig, ax = plt.subplots(figsize=(7.5, 4.2))
for i in range(len(samples)):
    ax.bar(x + (i - 1) * w, probs[i], w, label=f"Sentence S{i + 1}")
ax.set_xticks(x)
ax.set_xticklabels(LEVELS)
ax.set_ylim(0, 1)
ax.set_ylabel("Predicted probability")
ax.set_title("Probability per level for sample sentences")
ax.legend()
save(fig, "07_sample_predictions.png")
print("\nKamus contoh kalimat (untuk keterangan di README):")
for i, s in enumerate(samples, 1):
    print(f"  S{i}: {s}")

# ---------- Ringkasan angka ----------
print("\n=== RINGKASAN (untuk README) ===")
print(f"Jumlah data        : {len(df)}")
print(f"Cross-validation   : {folds}-fold, seed 42")
print(f"Akurasi persis     : {exact:.0%} (baseline acak {base_exact:.0%})")
print(f"Akurasi dalam ±1   : {within1:.0%} (baseline acak {base_within1:.0%})")