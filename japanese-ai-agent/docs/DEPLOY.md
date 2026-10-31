# Catatan deploy

## Kenyataan arsitektur

Model bahasa (LLM) dan model embedding berjalan di **Ollama di laptop**. Hosting seperti Vercel atau
server cloud **tidak bisa** memanggil laptopmu. Jadi "deploy" ada tiga tingkat, dengan biaya dan risiko berbeda.

| Opsi | Isi | Biaya | Risiko |
|---|---|---|---|
| **A. Demo lokal** (disarankan untuk portofolio) | Jalankan di laptop. Tampilkan lewat screenshot, video singkat, dan README | Gratis | Tidak ada, tapi pengunjung tidak bisa mencoba sendiri |
| **B. Demo sementara lewat tunnel** | Frontend dan backend tetap di laptop, dibuka ke internet lewat layanan tunnel selama demo | Cek syarat layanan tunnel | Laptopmu terbuka ke internet dan API belum punya login atau pembatas laju. Matikan setelah demo |
| **C. Cloud penuh** | Frontend di Vercel, backend (Docker) di layanan hosting, LLM dan embedding dari penyedia API | Cek halaman harga tiap layanan | Biaya LLM, penyalahgunaan API publik, perlu langkah keamanan di bawah |

Untuk portofolio, opsi A dengan video demo 1 sampai 2 menit biasanya cukup dan paling aman.

## Opsi C: langkah kasar

1. **Backend sebagai container.** `backend/Dockerfile` sudah disiapkan (belum diuji di Docker). Jalankan di layanan
   yang mendukung Docker (misalnya Render, Railway, Fly.io, atau Hugging Face Spaces). Layanan itu biasanya
   mengisi variabel `PORT` otomatis, dan Dockerfile sudah membacanya.
2. **LLM dari penyedia API.** Kode memakai klien OpenAI-compatible, jadi cukup mengganti tiga variabel di
   pengaturan environment hosting (bukan di Git): `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`.
   Set `LLM_JSON_MODE=0` jika penyedia menolak parameter `response_format`.
3. **Embedding.** Pencarian semantik butuh model embedding yang bisa dijangkau server. `app/rag/embeddings.py`
   memakai `LLM_BASE_URL` dan `LLM_API_KEY` yang sama dengan LLM. Jika embedding berasal dari penyedia lain,
   tambahkan variabel `EMBED_BASE_URL` dan `EMBED_API_KEY` di kode. Tanpa embedding, sistem otomatis turun ke
   pencarian lexical, yang di pertanyaan parafrase jauh lebih lemah (lihat bagian RAG di README).
4. **CORS.** Isi `CORS_ORIGINS` dengan alamat frontend produksi, misalnya `https://nama-proyek.vercel.app`.
5. **Frontend di Vercel.** Impor repository GitHub, atur **Root Directory** ke `frontend`. Vercel mengenali Vite
   (perintah build `npm run build`, output `dist`). Tambahkan environment variable `VITE_API_URL` berisi alamat
   backend, lalu deploy ulang (variabel `VITE_` dibaca saat build).
6. **Uji asap.** Buka `https://ALAMAT-BACKEND/api/health`, lalu coba satu kuis dan satu koreksi dari frontend.

## Checklist keamanan sebelum membuka ke publik

- [ ] Tidak ada rahasia di Git: `git ls-files` tidak memuat `.env`, dan token yang pernah tersimpan sudah dicabut.
- [ ] API key hanya ada di environment hosting.
- [ ] `CORS_ORIGINS` hanya berisi alamat frontend kamu.
- [ ] **Pembatas laju (rate limiting) belum ada.** Tanpa itu, siapa pun bisa menghabiskan kuota atau biaya LLM-mu.
      Tambahkan pembatas (misalnya library slowapi) atau taruh di belakang layanan yang menyediakannya.
- [ ] Atur batas pengeluaran di dashboard penyedia LLM.
- [ ] Pertimbangkan menonaktifkan `/docs` untuk produksi.
- [ ] Tampilkan peringatan bahwa jawaban AI bisa keliru (sudah ada di antarmuka, pertahankan).

## Yang belum diuji

- Build Docker (Dockerfile ditulis berdasarkan pemeriksaan paket, belum dijalankan).
- Seluruh alur di hosting cloud.
