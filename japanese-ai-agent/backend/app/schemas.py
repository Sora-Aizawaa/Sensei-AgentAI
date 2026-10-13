from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    language: str = "id"  # id / en


class ChatResponse(BaseModel):
    japanese: str
    hiragana: str = ""
    romaji: str = ""
    translation: str = ""
    jlpt: str = ""
    feedback: str = ""
    jlpt_ml: str = ""  # prediksi dari model ML buatan sendiri
    db_vocabulary: list[dict] = Field(default_factory=list)  # kosakata yang ada di database
    db_grammar: list[dict] = Field(default_factory=list)  # pola grammar yang ada di database


class DifficultyRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1000)