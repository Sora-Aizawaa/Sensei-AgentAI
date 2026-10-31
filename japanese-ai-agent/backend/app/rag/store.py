"""Penyimpanan dokumen dan vektor di SQLite (tabel rag_chunks)."""
from contextlib import closing

import numpy as np

from app.database.connection import get_conn

RAG_SCHEMA = """
CREATE TABLE IF NOT EXISTS rag_chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity TEXT NOT NULL,
    entity_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    text TEXT NOT NULL,
    embedding BLOB,
    model TEXT,
    UNIQUE (entity, entity_id)
);
"""


def save(docs, embeddings, model):
    """Ganti seluruh isi indeks. embeddings boleh None (hanya pencarian lexical)."""
    with closing(get_conn()) as conn:
        conn.executescript(RAG_SCHEMA)
        conn.execute("DELETE FROM rag_chunks")
        for i, d in enumerate(docs):
            blob = embeddings[i].astype(np.float32).tobytes() if embeddings is not None else None
            conn.execute(
                "INSERT INTO rag_chunks (entity, entity_id, title, text, embedding, model) VALUES (?, ?, ?, ?, ?, ?)",
                (d["entity"], d["entity_id"], d["title"], d["text"], blob, model if blob else None),
            )
        conn.commit()


def load():
    """Kembalikan (daftar dokumen, matriks vektor atau None, nama model embedding)."""
    with closing(get_conn()) as conn:
        conn.executescript(RAG_SCHEMA)
        rows = conn.execute("SELECT * FROM rag_chunks ORDER BY id").fetchall()

    docs = [{k: r[k] for k in ("entity", "entity_id", "title", "text")} for r in rows]
    if not rows or any(r["embedding"] is None for r in rows):
        return docs, None, None
    matrix = np.vstack([np.frombuffer(r["embedding"], dtype=np.float32) for r in rows])
    return docs, matrix, rows[0]["model"]