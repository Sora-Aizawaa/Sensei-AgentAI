from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, learning_curve
from sklearn.pipeline import Pipeline

BASE = Path(__file__).resolve().parents[2]
df = pd.read_csv(BASE / "data" / "sentences.csv").dropna()
X, y = df["text"].str.strip(), df["level"]

pipe = Pipeline([
    ("tfidf", TfidfVectorizer(analyzer="char", ngram_range=(1, 3), sublinear_tf=True)),
    ("clf", LogisticRegression(max_iter=1000, C=5.0, class_weight="balanced")),
])

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
sizes, _, val_scores = learning_curve(
    pipe, X, y, cv=cv,
    train_sizes=[0.4, 0.6, 0.8, 1.0],
    scoring="accuracy", shuffle=True, random_state=42,
)

print("Data latih -> akurasi validasi")
for n, s in zip(sizes, val_scores.mean(axis=1)):
    print(f"{n:>5} kalimat -> {s:.0%}")