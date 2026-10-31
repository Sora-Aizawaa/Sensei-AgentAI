"""Membangun indeks RAG dari database.  Jalankan:  python -m app.rag.index  [--no-embed]"""
import sys

from app.config import EMBED_MODEL
from app.rag import store
from app.rag.documents import build_documents


def build(with_embeddings: bool = True) -> int:
    docs = build_documents()
    embeddings = None
    if with_embeddings and docs:
        try:
            from app.rag.embeddings import embed

            embeddings = embed([d["text"] for d in docs])
            print(f"Embedding selesai: {embeddings.shape[0]} dokumen x {embeddings.shape[1]} dimensi ({EMBED_MODEL})")
        except Exception as e:
            print("PERINGATAN: embedding gagal, indeks hanya untuk pencarian lexical.")
            print("  Penyebab:", repr(e))
            print(f"  Pastikan Ollama aktif dan model sudah diunduh:  ollama pull {EMBED_MODEL}")
    store.save(docs, embeddings, EMBED_MODEL)
    return len(docs)


if __name__ == "__main__":
    n = build(with_embeddings="--no-embed" not in sys.argv)
    print(f"Indeks selesai: {n} dokumen tersimpan di tabel rag_chunks.")