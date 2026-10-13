from pathlib import Path

import joblib
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import cross_val_predict,  StratifiedKFold
from sklearn.pipeline import Pipeline


BASE = Path(__file__).resolve().parents[2]  # folder backend/
DATA_PATH = BASE / "data" / "sentences.csv"
MODEL_PATH = BASE / "models" / "jlpt_classifier.joblib"
LEVELS = ["N5", "N4", "N3", "N2", "N1"]


def main():
    df = pd.read_csv(DATA_PATH).dropna()
    df["text"] = df["text"].str.strip()
    X, y = df["text"], df["level"]

    print("Jumlah data per level:")
    print(y.value_counts().reindex(LEVELS).fillna(0).astype(int), "\n")

    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(analyzer="char", ngram_range=(1, 3), sublinear_tf=True)),
        ("clf", LogisticRegression(max_iter=1000, C=5.0, class_weight="balanced")),
    ])

    # Evaluasi dengan cross-validation (cocok untuk data kecil)
    folds = min(5, int(y.value_counts().min()))
    if folds >= 2:
        cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=42)
        pred = cross_val_predict(pipe, X, y, cv=cv)
        print(f"=== Evaluasi ({folds}-fold cross-validation) ===")
        print(classification_report(y, pred, labels=LEVELS, zero_division=0))
        print("Confusion matrix (baris = asli, kolom = prediksi):")
        print(pd.DataFrame(confusion_matrix(y, pred, labels=LEVELS), index=LEVELS, columns=LEVELS))
        
        order = {"N5": 5, "N4": 4, "N3": 3, "N2": 2, "N1": 1}
        diff = np.abs(pd.Series(pred).map(order).values - y.map(order).values)
        print(f"\nAkurasi persis      : {(diff == 0).mean():.0%}")
        print(f"Akurasi dalam ±1 level: {(diff <= 1).mean():.0%}")
    else:
        print("Data terlalu sedikit untuk evaluasi, tambah data dulu.")

    # Latih final dengan seluruh data lalu simpan
    pipe.fit(X, y)
    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(pipe, MODEL_PATH)
    print(f"\nModel disimpan ke {MODEL_PATH}")


if __name__ == "__main__":
    main()