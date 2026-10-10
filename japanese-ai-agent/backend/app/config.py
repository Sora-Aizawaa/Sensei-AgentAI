import os
from dotenv import load_dotenv

load_dotenv()  # baca file .env

HF_TOKEN = os.getenv("HF_TOKEN")
HF_MODEL = os.getenv("HF_MODEL", "Qwen/Qwen2.5-7B-Instruct")