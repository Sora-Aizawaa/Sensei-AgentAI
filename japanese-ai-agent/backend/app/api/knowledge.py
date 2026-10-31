from typing import Annotated, Literal, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.agents import quiz
from app.database import repository as repo
from app.nlp.reading import reading as japanese_reading
from app.rag import retriever

router = APIRouter(prefix="/api", tags=["knowledge"])

LangQ = Annotated[str, Query(pattern="^[a-z]{2,8}$")]
LevelQ = Annotated[Optional[str], Query(pattern="^N[1-5]$")]
LimitQ = Annotated[int, Query(ge=1, le=100)]


class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1000)
    language: str = "id"


class ReadingRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1000)


@router.get("/vocabulary")
def vocabulary(
    q: Optional[str] = None,
    level: LevelQ = None,
    topic: Optional[str] = None,
    lang: LangQ = "id",
    limit: LimitQ = 20,
):
    items = repo.search_vocabulary(q, level, topic, lang, limit)
    return {"count": len(items), "items": items}


@router.get("/vocabulary/random")
def vocabulary_random(
    n: Annotated[int, Query(ge=1, le=50)] = 10,
    level: LevelQ = None,
    topic: Optional[str] = None,
    lang: LangQ = "id",
):
    items = repo.random_vocabulary(n, level, topic, lang)
    return {"count": len(items), "items": items}


@router.get("/topics")
def topics():
    return {"items": repo.list_topics()}


@router.get("/kanji")
def kanji(q: Optional[str] = None, level: LevelQ = None, lang: LangQ = "id", limit: LimitQ = 20):
    items = repo.search_kanji(q, level, lang, limit)
    return {"count": len(items), "items": items}


@router.get("/grammar")
def grammar(q: Optional[str] = None, level: LevelQ = None, lang: LangQ = "id", limit: LimitQ = 20):
    items = repo.search_grammar(q, level, lang, limit)
    return {"count": len(items), "items": items}


@router.post("/analyze")
def analyze(req: AnalyzeRequest):
    return repo.analyze_text(req.text, req.language)


@router.post("/reading")
def reading_endpoint(req: ReadingRequest):
    hiragana, romaji = japanese_reading(req.text)
    return {"hiragana": hiragana, "romaji": romaji}


# ---------- RAG ----------
@router.get("/search")
def search(
    q: Annotated[str, Query(min_length=1, max_length=300)],
    k: Annotated[int, Query(ge=1, le=20)] = 5,
    mode: Optional[Literal["lexical", "semantic", "hybrid"]] = None,
    entity: Optional[Literal["vocabulary", "grammar", "kanji"]] = None,
):
    """Pencarian semantik atas database (untuk menguji RAG tanpa LLM)."""
    hits = retriever.search(q, k=k, mode=mode, entity=entity)
    return {"count": len(hits), "items": hits}


@router.post("/rag/reload")
def rag_reload():
    """Muat ulang indeks setelah menjalankan: python -m app.rag.index"""
    retriever.reload()
    return {"status": "ok"}


# ---------- Kuis (untuk halaman Kuis) ----------
@router.get("/quiz")
def quiz_endpoint(
    n: Annotated[int, Query(ge=1, le=10)] = 5,
    focus: Optional[Literal["vocabulary", "grammar", "kanji"]] = None,
    level: LevelQ = None,
    topic: Optional[str] = None,
    lang: LangQ = "id",
):
    res = quiz.generate({"n": n, "focus": focus, "level": level, "topic": topic}, lang)
    return {"type": res.type, "message": res.message, "quiz": res.quiz}
