from app.rag import retriever
from app.rag.context import filter_hits


def hit(title, semantic):
    return {"title": title, "semantic": semantic, "lexical": 0.1}


def test_filter_uses_scores_from_real_logs():
    """Skor dari log nyata: dokumen tidak relevan harus tersaring."""
    q1 = [hit("わけではない", .672), hit("うちに", .53), hit("ばかり", .544), hit("に違いない", .567)]
    assert [h["title"] for h in filter_hits(q1, 0.45, 0.85)] == ["わけではない"]

    nonsense = [hit("ついでに", .385), hit("習慣", .334), hit("禁止", .312)]
    assert filter_hits(nonsense, 0.45, 0.85) == []  # pertanyaan tak bermakna: tanpa referensi

    comparison = [hit("せいで", .61), hit("おかげで", .60), hit("ばかり", .45)]
    assert [h["title"] for h in filter_hits(comparison, 0.45, 0.85)] == ["せいで", "おかげで"]


def test_filter_ignores_floor_without_semantic_scores():
    """Saat embedding tidak tersedia, batas bawah semantic tidak boleh mematikan RAG."""
    lexical_only = [{"title": "たびに", "semantic": None, "lexical": 0.3}]
    assert len(filter_hits(lexical_only, 0.5, 0.85)) == 1


def test_lexical_search_finds_expected_documents():
    top = lambda q, **kw: retriever.search(q, k=1, mode="lexical", **kw)[0]
    assert "たびに" in top("setiap kali")["title"]
    assert "わけではない" in top("bukan berarti saya tidak suka")["title"]
    assert "せいで" in top("雨のせいで遅れた")["title"]


def test_entity_filter_and_empty_query():
    hits = retriever.search("bekerja", k=3, mode="lexical", entity="kanji")
    assert hits and all(h["entity"] == "kanji" for h in hits)
    assert retriever.search("   ", k=3) == []


def test_missing_embeddings_fall_back_to_lexical():
    # Indeks pengujian dibuat tanpa embedding, jadi mode semantic harus turun ke lexical
    hits = retriever.search("setiap kali", k=1, mode="semantic")
    assert hits[0]["via"] == "lexical (cadangan)"
