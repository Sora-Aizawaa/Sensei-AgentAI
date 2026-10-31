# BELUM DIUJI di Docker. Lihat docs/DEPLOY.md sebelum memakainya.
FROM python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY data ./data

# Bangun database, model klasifikasi level, dan indeks pencarian saat image dibuat.
# Indeks dibuat TANPA embedding (butuh model embedding yang bisa dijangkau saat build).
# Untuk pencarian semantik di server, jalankan "python -m app.rag.index" setelah
# EMBED_MODEL, LLM_BASE_URL, dan LLM_API_KEY mengarah ke penyedia embedding.
RUN python -m app.database.seed \
 && python -m app.ml.train \
 && python -m app.rag.index --no-embed

EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
