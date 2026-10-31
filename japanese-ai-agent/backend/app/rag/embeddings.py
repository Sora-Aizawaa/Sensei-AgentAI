"""Mengubah teks menjadi vektor lewat Ollama (endpoint /v1/embeddings)."""
import numpy as np
from openai import OpenAI

from app.config import EMBED_MODEL, LLM_API_KEY, LLM_BASE_URL

_client = OpenAI(base_url=LLM_BASE_URL, api_key=LLM_API_KEY, timeout=120)


def embed(texts: list[str]) -> np.ndarray:
    """Matriks (n x d) yang sudah dinormalisasi, sehingga dot product = cosine similarity."""
    vectors = []
    for i in range(0, len(texts), 16):  # kirim per 16 teks
        resp = _client.embeddings.create(model=EMBED_MODEL, input=texts[i : i + 16])
        vectors += [item.embedding for item in resp.data]
    m = np.asarray(vectors, dtype=np.float32)
    norms = np.linalg.norm(m, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return m / norms