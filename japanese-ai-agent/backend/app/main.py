# import json
# import sqlite3

# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from openai import APIConnectionError, APIStatusError
# from pydantic import ValidationError

# from app.api.knowledge import router as knowledge_router
# from app.config import LLM_BASE_URL, LLM_MODEL
# from app.database.repository import analyze_text
# from app.llm import ask_sensei
# from app.ml.difficulty import predict_level
# from app.schemas import ChatRequest, ChatResponse, DifficultyRequest
# import traceback
# from app.nlp.reading import reading as japanese_reading

# app = FastAPI(title="Japanese AI Agent API")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.include_router(knowledge_router)


# @app.get("/api/health")
# def health():
#     return {"status": "ok", "model": LLM_MODEL, "base_url": LLM_BASE_URL}


# @app.post("/api/difficulty")
# def difficulty(req: DifficultyRequest):
#     pred = predict_level(req.text)
#     if pred is None:
#         raise HTTPException(status_code=503, detail="Model belum dilatih. Jalankan: python -m app.ml.train")
#     return pred


# @app.post("/api/chat", response_model=ChatResponse)
# def chat(req: ChatRequest):
#     try:
#         data = ask_sensei(req.message, req.language)
#         result = ChatResponse.model_validate(data)

#         try:
#             result.hiragana, result.romaji = japanese_reading(result.japanese)
#         except Exception:
#             print("READING ERROR (memakai bacaan dari LLM):")
#             traceback.print_exc()

#         # Level dari model ML buatan sendiri
#         pred = predict_level(result.japanese)
#         if pred:
#             result.jlpt_ml = f"JLPT {pred['level']} ({int(pred['confidence'] * 100)}%)"

#         # Kosakata dan grammar dari database (cari di pesan pengguna + jawaban Sensei)
#         try:
#             found = analyze_text(f"{req.message} {result.japanese}", req.language)
#             result.db_vocabulary = found["vocabulary"]
#             result.db_grammar = found["grammar"]
#         except Exception:
#             # Apa pun masalah databasenya, chat tetap jalan tanpa kartu database
#             print("DB ERROR:")
#             traceback.print_exc()

#         return result

#     except APIStatusError as e:
#         print("LLM STATUS ERROR:", e.status_code, repr(e))
#         if e.status_code == 404:
#             detail = f"Model '{LLM_MODEL}' tidak ditemukan. Jalankan: ollama pull {LLM_MODEL}"
#         elif e.status_code == 401:
#             detail = "API key tidak valid (401). Cek LLM_API_KEY di .env."
#         elif e.status_code == 429:
#             detail = "Terlalu banyak request (429). Tunggu sebentar."
#         else:
#             detail = f"LLM mengembalikan error (kode {e.status_code})."
#         raise HTTPException(status_code=502, detail=detail)

#     except APIConnectionError as e:
#         print("LLM CONNECTION ERROR:", repr(e))
#         raise HTTPException(
#             status_code=502,
#             detail=f"Tidak bisa terhubung ke LLM di {LLM_BASE_URL}. Pastikan Ollama sedang berjalan.",
#         )

#     except (ValueError, json.JSONDecodeError, ValidationError) as e:
#         print("PARSE ERROR:", repr(e))
#         raise HTTPException(status_code=502, detail="Sensei membalas dengan format tidak valid. Coba kirim ulang.")

#     except Exception:
#         print("UNKNOWN ERROR:")
#         traceback.print_exc()
#         raise HTTPException(status_code=502, detail="Terjadi kesalahan pada server AI. Lihat terminal backend.")

import traceback

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import APIConnectionError, APIStatusError
from pydantic import ValidationError

from app.agents.orchestrator import handle_message
from app.api.knowledge import router as knowledge_router
from app.config import LLM_BASE_URL, LLM_MODEL
from app.ml.difficulty import predict_level
from app.schemas import ChatRequest, ChatResponse, DifficultyRequest

app = FastAPI(title="Japanese AI Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(knowledge_router)


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

    except APIStatusError as e:
        print("LLM STATUS ERROR:", e.status_code, repr(e))
        if e.status_code == 404:
            detail = f"Model '{LLM_MODEL}' tidak ditemukan. Jalankan: ollama pull {LLM_MODEL}"
        elif e.status_code == 401:
            detail = "API key tidak valid (401). Cek LLM_API_KEY di .env."
        elif e.status_code == 429:
            detail = "Terlalu banyak request (429). Tunggu sebentar."
        else:
            detail = f"LLM mengembalikan error (kode {e.status_code})."
        raise HTTPException(status_code=502, detail=detail)

    except APIConnectionError as e:
        print("LLM CONNECTION ERROR:", repr(e))
        raise HTTPException(
            status_code=502,
            detail=f"Tidak bisa terhubung ke LLM di {LLM_BASE_URL}. Pastikan Ollama sedang berjalan.",
        )

    except (ValueError, ValidationError) as e:
        print("PARSE ERROR:", repr(e))
        raise HTTPException(status_code=502, detail="Sensei membalas dengan format tidak valid. Coba kirim ulang.")

    except Exception:
        print("UNKNOWN ERROR:")
        traceback.print_exc()
        raise HTTPException(status_code=502, detail="Terjadi kesalahan pada server AI. Lihat terminal backend.")