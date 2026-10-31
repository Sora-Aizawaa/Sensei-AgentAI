import os

from dotenv import load_dotenv

load_dotenv()  # baca file .env

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "ollama")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.1:8b")
LLM_JSON_MODE = os.getenv("LLM_JSON_MODE", "0") == "1"

# --- RAG (Tahap 10) ---
EMBED_MODEL = os.getenv("EMBED_MODEL", "bge-m3")  # model embedding di Ollama
RAG_MODE = os.getenv("RAG_MODE", "hybrid")  # lexical | semantic | hybrid
RAG_IN_CHAT = os.getenv("RAG_IN_CHAT", "1") == "1"  # suntik referensi ke mode koreksi dan ngobrol
RAG_MIN_SCORE = float(os.getenv("RAG_MIN_SCORE", "0"))  # batas bawah skor semantic (0 = tidak ada batas)
RAG_KEEP_RATIO = float(os.getenv("RAG_KEEP_RATIO", "0.85"))  # buang referensi yang skornya < rasio x skor tertinggi

# --- Deploy (Tahap 11) ---
# Alamat frontend yang boleh memanggil API, dipisah koma. Contoh produksi: https://sensei-ai.vercel.app
CORS_ORIGINS = [
    o.strip()
    for o in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if o.strip()
]