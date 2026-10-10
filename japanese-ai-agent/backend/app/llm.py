import json
import re

from huggingface_hub import InferenceClient

from app.config import HF_TOKEN, HF_MODEL
from app.prompts import build_system_prompt

LANG_NAMES = {"id": "Bahasa Indonesia", "en": "English"}
EXPECTED = ["japanese", "hiragana", "romaji", "translation", "jlpt", "feedback"]

client = InferenceClient(api_key=HF_TOKEN, timeout=60)


def extract_json(text: str) -> dict:
    """Ambil objek JSON dari balasan model, walau dibungkus ```json atau teks lain."""
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    text = re.sub(r"```(?:json)?", "", text).strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("Balasan model tidak mengandung JSON")
    # strict=False: toleransi baris baru mentah di dalam string
    data = json.loads(text[start : end + 1], strict=False)
    if not isinstance(data, dict):
        raise ValueError("JSON bukan objek")
    return data


def normalize(data: dict) -> dict:
    """Samakan nama field (huruf kecil) dan paksa semua nilai jadi string."""
    data = {str(k).strip().lower(): v for k, v in data.items()}
    clean = {}
    for key in EXPECTED:
        value = data.get(key, "")
        if isinstance(value, (list, tuple)):
            value = " ".join(str(v) for v in value)
        elif isinstance(value, dict):
            value = json.dumps(value, ensure_ascii=False)
        clean[key] = str(value).strip()
    if not clean["japanese"]:
        raise ValueError("Field 'japanese' kosong atau tidak ada")
    return clean


def ask_sensei(message: str, language: str) -> dict:
    language_name = LANG_NAMES.get(language, "Bahasa Indonesia")

    completion = client.chat.completions.create(
        model=HF_MODEL,
        messages=[
            {"role": "system", "content": build_system_prompt(language_name)},
            {"role": "user", "content": message},
        ],
        max_tokens=900,
        temperature=0.2,
    )

    raw = completion.choices[0].message.content
    print("RAW:", raw)  # tetap berguna untuk debugging
    return normalize(extract_json(raw))