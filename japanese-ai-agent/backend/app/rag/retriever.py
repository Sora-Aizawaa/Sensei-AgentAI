"""Pencarian dokumen: lexical (TF-IDF), semantic (embedding), atau hybrid (keduanya digabung)."""
import threading

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from app.config import EMBED_MODEL, RAG_MODE
from app.rag import store

RRF_K = 60  # konstanta Reciprocal Rank Fusion

_lock = threading.Lock()
_index = None


class _Index:
    def __init__(self):
        self.docs, self.matrix, self.model = store.load()
        self.vectorizer, self.tfidf = None, None
        if self.docs:
            self.vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(1, 3), sublinear_tf=True)
            self.tfidf = self.vectorizer.fit_transform([d["text"] for d in self.docs])


def reload():
    """Muat ulang indeks dari database (panggil setelah membangun ulang indeks)."""
    global _index
    with _lock:
        _index = None


def _get() -> _Index:
    global _index
    with _lock:
        if _index is None:
            _index = _Index()
        return _index


def _ranks(scores: np.ndarray) -> np.ndarray:
    """rank[i] = peringkat dokumen i (0 = terbaik)."""
    order = np.argsort(-scores)
    ranks = np.empty(len(scores), dtype=int)
    ranks[order] = np.arange(len(scores))
    return ranks


def search(query: str, k: int = 5, mode: str | None = None, entity: str | None = None) -> list[dict]:
    idx = _get()
    if not idx.docs or not query.strip():
        return []
    mode = mode or RAG_MODE

    lexical = linear_kernel(idx.vectorizer.transform([query]), idx.tfidf).ravel()

    semantic = None
    if mode in ("semantic", "hybrid") and idx.matrix is not None:
        if idx.model != EMBED_MODEL:
            print(f"RAG: indeks dibuat dengan model '{idx.model}', sekarang '{EMBED_MODEL}'. Bangun ulang indeks.")
        else:
            try:
                from app.rag.embeddings import embed

                semantic = idx.matrix @ embed([query])[0]
            except Exception as e:
                print("RAG: embedding pertanyaan gagal, memakai pencarian lexical saja:", repr(e))

    if mode == "lexical" or semantic is None:
        combined, via = lexical, "lexical" if mode == "lexical" else "lexical (cadangan)"
    elif mode == "semantic":
        combined, via = semantic, "semantic"
    else:  # hybrid: gabungkan peringkat, bukan skor (skor kedua metode tidak sebanding)
        combined = 1.0 / (RRF_K + _ranks(lexical)) + 1.0 / (RRF_K + _ranks(semantic))
        via = "hybrid"

    hits = []
    for i in np.argsort(-combined):
        d = idx.docs[i]
        if entity and d["entity"] != entity:
            continue
        hits.append({
            **d,
            "score": round(float(combined[i]), 4),
            "lexical": round(float(lexical[i]), 3),
            "semantic": round(float(semantic[i]), 3) if semantic is not None else None,
            "via": via,
        })
        if len(hits) >= k:
            break
    return hits