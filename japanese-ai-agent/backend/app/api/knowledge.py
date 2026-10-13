from typing import Annotated, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.database import repository as repo

router = APIRouter(prefix="/api", tags=["knowledge"])

LangQ = Annotated[str, Query(pattern="^[a-z]{2,8}$")]
LevelQ = Annotated[Optional[str], Query(pattern="^N[1-5]$")]
LimitQ = Annotated[int, Query(ge=1, le=100)]

from app.nlp.reading import reading as japanese_reading

class ReadingRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1000)


@router.post("/reading")
def reading_endpoint(req: ReadingRequest):
    hiragana, romaji = japanese_reading(req.text)
    return {"hiragana": hiragana, "romaji": romaji}


class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1000)
    language: str = "id"


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