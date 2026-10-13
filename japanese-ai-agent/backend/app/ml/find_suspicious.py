from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline

BASE = Path(__file__).resolve().parents[2]
df = pd.read_csv(BASE / "data" / "sentences.csv").dropna().reset_index(drop=True)
X, y = df["text"].str.strip(), df["level"]

pipe = Pipeline([
    ("tfidf", TfidfVectorizer(analyzer="char", ngram_range=(1, 3), sublinear_tf=True)),
    ("clf", LogisticRegression(max_iter=1000, C=5.0, class_weight="balanced")),
])

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
proba = cross_val_predict(pipe, X, y, cv=cv, method="predict_proba")

classes = sorted(y.unique())  # urutan kolom predict_proba
p_label = proba[np.arange(len(y)), [classes.index(l) for l in y]]
pred = [classes[i] for i in proba.argmax(axis=1)]

out = df.assign(
    baris_csv=df.index + 2,
    prediksi=pred,
    skor_label_asli=p_label.round(2),
    skor_prediksi=proba.max(axis=1).round(2),
)
out = out[out.prediksi != out.level].sort_values("skor_label_asli")
print(out.to_string(index=False))