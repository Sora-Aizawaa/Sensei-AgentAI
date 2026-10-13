from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

BASE = Path(__file__).resolve().parents[2]
df = pd.read_csv(BASE / "data" / "sentences.csv").dropna()
X, y = df["text"].str.strip(), df["level"].values
ORDER = {"N5": 5, "N4": 4, "N3": 3, "N2": 2, "N1": 1}
y_num = pd.Series(y).map(ORDER).values

configs = {
    "char(1,2) + LogReg C=5": ((1, 2), LogisticRegression(max_iter=1000, C=5, class_weight="balanced")),
    "char(1,3) + LogReg C=5": ((1, 3), LogisticRegression(max_iter=1000, C=5, class_weight="balanced")),
    "char(1,4) + LogReg C=5": ((1, 4), LogisticRegression(max_iter=1000, C=5, class_weight="balanced")),
    "char(2,4) + LogReg C=5": ((2, 4), LogisticRegression(max_iter=1000, C=5, class_weight="balanced")),
    "char(1,3) + LogReg C=20": ((1, 3), LogisticRegression(max_iter=1000, C=20, class_weight="balanced")),
    "char(1,3) + LinearSVC": ((1, 3), LinearSVC(class_weight="balanced")),
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

print(f"{'Konfigurasi':<28}{'Persis':>8}{'±1 level':>10}")
for name, (ngram, clf) in configs.items():
    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(analyzer="char", ngram_range=ngram, sublinear_tf=True)),
        ("clf", clf),
    ])
    pred = cross_val_predict(pipe, X, y, cv=cv)
    diff = np.abs(pd.Series(pred).map(ORDER).values - y_num)
    print(f"{name:<28}{(diff == 0).mean():>8.0%}{(diff <= 1).mean():>10.0%}")