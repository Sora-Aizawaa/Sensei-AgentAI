import os
from dotenv import load_dotenv

load_dotenv()  # baca file .env

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "ollama")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2:3b")
LLM_JSON_MODE = os.getenv("LLM_JSON_MODE", "0") == "1"