import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from app.config import HF_TOKEN, HF_MODEL
from app.llm import ask_sensei
from app.schemas import ChatRequest, ChatResponse

from huggingface_hub.errors import HfHubHTTPError

app = FastAPI(title="Japanese AI Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    # Jangan pernah mengirim token itu sendiri, cukup status ada/tidaknya
    return {"status": "ok", "model": HF_MODEL, "token_set": bool(HF_TOKEN)}


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not HF_TOKEN:
        raise HTTPException(status_code=500, detail="HF_TOKEN belum diatur di backend/.env")

    try:
        data = ask_sensei(req.message, req.language)
        return ChatResponse.model_validate(data)

    except HfHubHTTPError as e:
        status = e.response.status_code if e.response is not None else "?"
        print("HF ERROR:", status, repr(e))
        if "model_not_supported" in str(e):
            detail = f"Model '{HF_MODEL}' tidak tersedia untuk akunmu. Ganti HF_MODEL di .env."
        elif status == 401:
            detail = "Token Hugging Face tidak valid (401). Cek HF_TOKEN di .env."
        elif status == 402:
            detail = "Kredit inference habis (402)."
        elif status == 403:
            detail = "Token tidak punya izin Inference Providers (403)."
        elif status == 429:
            detail = "Terlalu banyak request (429). Tunggu sebentar."
        else:
            detail = f"Gagal menghubungi model AI (kode {status})."
        raise HTTPException(status_code=502, detail=detail)
    
    except (ValueError, json.JSONDecodeError, ValidationError) as e:
        print("PARSE ERROR:", repr(e))
        raise HTTPException(status_code=502, detail="Sensei membalas dengan format tidak valid. Coba kirim ulang.")

    except Exception as e:
        print("UNKNOWN ERROR:", repr(e))
        raise HTTPException(status_code=502, detail="Terjadi kesalahan pada server AI.")