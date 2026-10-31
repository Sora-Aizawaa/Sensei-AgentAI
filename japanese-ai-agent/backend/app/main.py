import traceback

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import APIConnectionError, APIStatusError
from pydantic import ValidationError

from app.agents import reading_agent
from app.agents.orchestrator import handle_message
from app.api.knowledge import router as knowledge_router
from app.config import CORS_ORIGINS, LLM_BASE_URL, LLM_MODEL
from app.ml.difficulty import predict_level
from app.schemas import ChatRequest, ChatResponse, DifficultyRequest, DokkaiRequest

app = FastAPI(title="Japanese AI Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(knowledge_router)


def translate_error(e: Exception) -> HTTPException:
    """Ubah error LLM atau parsing menjadi pesan yang jelas untuk pengguna."""
    if isinstance(e, HTTPException):
        return e
    if isinstance(e, APIStatusError):
        print("LLM STATUS ERROR:", e.status_code, repr(e))
        if e.status_code == 404:
            detail = f"Model '{LLM_MODEL}' tidak ditemukan. Jalankan: ollama pull {LLM_MODEL}"
        elif e.status_code == 401:
            detail = "API key tidak valid (401). Cek LLM_API_KEY di .env."
        elif e.status_code == 429:
            detail = "Terlalu banyak request (429). Tunggu sebentar."
        else:
            detail = f"LLM mengembalikan error (kode {e.status_code})."
        return HTTPException(status_code=502, detail=detail)
    if isinstance(e, APIConnectionError):
        print("LLM CONNECTION ERROR:", repr(e))
        return HTTPException(
            status_code=502,
            detail=f"Tidak bisa terhubung ke LLM di {LLM_BASE_URL}. Pastikan Ollama sedang berjalan.",
        )
    if isinstance(e, (ValueError, ValidationError)):
        print("PARSE ERROR:", repr(e))
        return HTTPException(status_code=502, detail="Sensei membalas dengan format tidak valid. Coba kirim ulang.")
    print("UNKNOWN ERROR:")
    traceback.print_exception(e)
    return HTTPException(status_code=502, detail="Terjadi kesalahan pada server AI. Lihat terminal backend.")


@app.get("/api/health")
def health():
    return {"status": "ok", "model": LLM_MODEL, "base_url": LLM_BASE_URL}


@app.post("/api/difficulty")
def difficulty(req: DifficultyRequest):
    pred = predict_level(req.text)
    if pred is None:
        raise HTTPException(status_code=503, detail="Model belum dilatih. Jalankan: python -m app.ml.train")
    return pred


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        return handle_message(req)  # Router memilih agent, lalu agent bekerja
    except Exception as e:
        raise translate_error(e) from e


@app.post("/api/dokkai", response_model=ChatResponse)
def dokkai(req: DokkaiRequest):
    """Latihan reading untuk halaman Reading."""
    try:
        return reading_agent.run(req.topic, req.language)
    except Exception as e:
        raise translate_error(e) from e
