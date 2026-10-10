from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    language: str = "id"


class ChatResponse(BaseModel):
    japanese: str
    hiragana: str = ""
    romaji: str = ""
    translation: str = ""
    jlpt: str = ""
    feedback: str = ""