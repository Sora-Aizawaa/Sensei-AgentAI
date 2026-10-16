from typing import Literal, Optional

from pydantic import BaseModel, Field


class HistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=600)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    language: str = "id"  # id / en
    mode: Literal["auto", "chat", "correction"] = "auto"
    previous_type: Optional[str] = None  # jenis balasan Sensei sebelumnya (untuk melanjutkan obrolan)
    history: list[HistoryItem] = Field(default_factory=list, max_length=20)


class ChatResponse(BaseModel):
    type: str = "correction"  # correction | chat | vocabulary | kanji | grammar | quiz | info
    message: str = ""  # teks pengantar untuk jawaban dari tool
    route: str = ""  # keputusan Router, contoh: "quiz · rule"
    japanese: str = ""
    hiragana: str = ""
    romaji: str = ""
    translation: str = ""
    jlpt: str = ""
    feedback: str = ""
    jlpt_ml: str = ""  # prediksi dari model ML buatan sendiri
    errors: list[str] = Field(default_factory=list)  # kesalahan yang ditemukan LLM
    rule_hints: list[dict] = Field(default_factory=list)  # temuan pemeriksa aturan
    warning: str = ""
    db_vocabulary: list[dict] = Field(default_factory=list)
    db_grammar: list[dict] = Field(default_factory=list)
    items: list[dict] = Field(default_factory=list)  # hasil Vocabulary/Kanji/Grammar Tool
    quiz: Optional[dict] = None  # hasil Quiz Agent


class DifficultyRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1000)