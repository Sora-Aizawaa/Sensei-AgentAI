from functools import lru_cache
from pathlib import Path

import joblib

MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "jlpt_classifier.joblib"


@lru_cache(maxsize=1)
def _load():
    if not MODEL_PATH.exists():
        return None
    return joblib.load(MODEL_PATH)


def predict_level(text: str):
    model = _load()
    if model is None:
        return None
    probs = model.predict_proba([text])[0]
    best = int(probs.argmax())
    return {
        "level": str(model.classes_[best]),
        "confidence": round(float(probs[best]), 2),
        "probabilities": {str(c): round(float(p), 2) for c, p in zip(model.classes_, probs)},
    }