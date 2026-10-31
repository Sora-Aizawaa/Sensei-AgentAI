"""Menyiapkan referensi dari database untuk disuntikkan ke prompt LLM."""
from app.config import RAG_KEEP_RATIO, RAG_MIN_SCORE
from app.rag import retriever


def best_score(hit: dict) -> float:
    """Skor cosine mentah: semantic jika ada, kalau tidak lexical. (Skor gabungan hybrid tidak bisa dipakai sebagai ambang.)"""
    return hit["semantic"] if hit.get("semantic") is not None else hit["lexical"]


def filter_hits(hits: list[dict], floor: float, ratio: float) -> list[dict]:
    """Buang referensi yang kurang relevan.
    - floor: batas bawah skor semantic (hanya berlaku bila skor semantic tersedia)
    - ratio: buang yang skornya < ratio x skor tertinggi (tidak bergantung skala skor)"""
    if not hits:
        return []
    top = max(best_score(h) for h in hits)
    kept = []
    for h in hits:
        s = best_score(h)
        if h.get("semantic") is not None and s < floor:
            continue
        if s < top * ratio:
            continue
        kept.append(h)
    return kept


def retrieve(query: str, k: int = 3, entity: str | None = None) -> list[dict]:
    try:
        hits = retriever.search(query, k=k, entity=entity)
    except Exception as e:
        print("RAG ERROR (dilewati):", repr(e))
        return []
    kept = filter_hits(hits, RAG_MIN_SCORE, RAG_KEEP_RATIO)
    print("RAG:", [(h["title"], best_score(h), h["via"]) for h in kept], f"(dari {len(hits)} kandidat)")
    return kept


def reference_block(hits: list[dict]) -> str:
    """Blok teks yang ditempel ke pesan pengguna pada mode koreksi dan ngobrol."""
    if not hits:
        return ""
    lines = "\n".join(f"{i}. {h['text']}" for i, h in enumerate(hits, 1))
    return (
        "[REFERENSI dari database. Pakai hanya jika relevan dengan pesan pengguna. "
        "Jangan mengarang di luar referensi.]\n" + lines
    )


def numbered_references(hits: list[dict]) -> str:
    return "\n".join(f"[{i}] {h['text']}" for i, h in enumerate(hits, 1))


def to_sources(hits: list[dict], used=None) -> list[dict]:
    """Bentuk ringkas untuk ditampilkan di UI."""
    return [
        {
            "entity": h["entity"],
            "entity_id": h["entity_id"],
            "title": h["title"],
            "text": h["text"],
            "score": round(best_score(h), 3),
            "via": h["via"],
            "used": (i + 1 in used) if used is not None else None,
        }
        for i, h in enumerate(hits)
    ]