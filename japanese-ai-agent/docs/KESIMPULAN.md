# Kesimpulan proyek: JLPT N3 AI Study Partner (Sensei AI)

Dokumen ini merangkum seluruh proyek dari awal sampai akhir: apa yang dibangun, dataset yang dipakai,
arsitektur, semua model dan komponen, fungsi tiap menu, hasil yang terukur, dan keterbatasannya.
Angka yang diukur dibedakan dari angka yang belum diukur.

## 1. Ringkasan

Sensei AI adalah asisten belajar bahasa Jepang untuk persiapan JLPT N3. Pengguna bisa mengobrol, meminta koreksi
kalimat, menelusuri kosakata, kanji, dan tata bahasa, mengerjakan kuis, membaca teks pendek dengan soal, dan
melihat progres belajar. Semuanya berjalan **di laptop, gratis, tanpa token**.

Gagasan utama sistem ini: **fakta diambil dari database dan komponen yang bisa dipastikan, sedangkan LLM dipakai
untuk bahasa natural.** Model bahasa kecil sering keliru pada bacaan kanji, koreksi, dan arti, jadi bagian yang
bisa dihitung secara deterministik (bacaan, kunci kuis, pencarian, pemeriksa kesalahan umum) tidak diserahkan kepadanya.

## 2. Perjalanan pembangunan

| Tahap | Hasil |
|---|---|
| 1 sampai 5 | Antarmuka React + Vite + Tailwind: sidebar, area chat, panel kanan, mode gelap |
| 6 | Backend FastAPI dan komunikasi JSON dengan frontend (CORS, validasi Pydantic) |
| 7 | LLM lokal lewat Ollama. Hugging Face Inference ditinggalkan karena kredit gratis cepat habis |
| 7B | Classifier level JLPT buatan sendiri (TF-IDF karakter + Logistic Regression) beserta evaluasi dan grafik |
| 8 | Database SQLite (kosakata, kanji, grammar, terjemahan) yang dibangun dari file CSV |
| 9 | Router Agent, Vocabulary/Kanji/Grammar Tool, Quiz Agent, mode ngobrol dengan riwayat |
| (di antara) | Pemeriksa aturan kesalahan umum dan bacaan hiragana/romaji dari analisis morfologi (fugashi) |
| 10 | RAG: embedding bge-m3, pencarian lexical/semantic/hybrid, evaluasi, kalibrasi ambang |
| 11 | Pengujian otomatis, konfigurasi bersih dari rahasia, README final, catatan deploy |
| 12 | Semua menu sidebar berfungsi, Reading Agent, halaman Progress, Pengaturan, dan Bantuan |

## 3. Dataset

| Data | Isi | Ukuran awal | Dipakai oleh | Keandalan |
|---|---|---|---|---|
| `sentences.csv` | Kalimat Jepang berlabel level N5 sampai N1 | 50 kalimat (10 per level), bisa ditambah | Melatih classifier level | Label perkiraan, perlu diverifikasi |
| `vocabulary.csv` | Kata, bacaan, romaji, level, jenis kata, topik, contoh, arti (id, en) | 20 kata | Kosakata, kuis, RAG, Reading | Level dan arti perlu diverifikasi |
| `kanji.csv` | Kanji, on'yomi, kun'yomi, goresan, contoh kata, arti (id, en) | 10 kanji | Kanji, kuis, RAG | Perlu diverifikasi |
| `grammar.csv` | Pola, bentuk, contoh, bacaan contoh, arti (id, en) | 10 pola | Tata bahasa, kuis, RAG | Perlu diverifikasi |
| tabel `translations` | Arti dan terjemahan contoh per bahasa | 140 baris | Semua fitur yang menampilkan arti | Mengikuti CSV |
| tabel `rag_chunks` | Dokumen teks gabungan + vektor 1024 dimensi | 40 dokumen | Pencarian RAG | Dibangun ulang dari database |
| Set uji pencarian | Pertanyaan dengan jawaban yang benar | 35 pertanyaan (23 mudah, 12 parafrase) + 10 di luar topik | Evaluasi dan kalibrasi RAG | Sebagian ditulis pengembang |

Kesimpulan tentang dataset:

- Datanya **kecil dan awal**. Cukup untuk membuktikan seluruh alur bekerja, **belum cukup untuk klaim yang berlaku umum**.
- Kualitas data adalah tuas terbesar. Perbaikan data (lebih banyak contoh, deskripsi pola yang jelas) hampir selalu
  lebih berpengaruh daripada mengganti model atau mengatur ambang.
- Level, bacaan, dan arti di CSV awal adalah **perkiraan**. Tidak ada daftar resmi tata bahasa per level JLPT, jadi
  satu sumber acuan sebaiknya dipakai secara konsisten.
- Menambah materi cukup dengan mengedit CSV lalu menjalankan seed dan membangun ulang indeks. Menambah bahasa terjemahan
  cukup dengan menambah kolom (misalnya `meaning_zh`), tanpa mengubah kode.
- Model bawaan (LLM, bge-m3, kamus unidic-lite) dilatih pihak lain dengan data yang tidak kita kendalikan.

## 4. Arsitektur

```
React + Vite (frontend)
   │ menu: Chat, Kosakata, Kanji, Tata Bahasa, Kuis, Reading, Progress, Pengaturan, Bantuan
   ▼
FastAPI
   ├─ /api/chat ──► Router ─┬─ quiz ───────► Quiz Agent ───────────┐
   │                        ├─ vocabulary/kanji/grammar ► Tools ───┤
   │                        ├─ ask ────────► Retriever ► LLM        ├─► SQLite
   │                        ├─ reading ────► Reading Agent ► LLM    │   (CSV → seed)
   │                        └─ correction/chat ► Pemeriksa aturan   │
   │                                            + RAG + LLM ────────┘
   │                                            + fugashi (bacaan) + model ML (level)
   ├─ /api/vocabulary, /kanji, /grammar, /topics, /quiz, /search   (tanpa LLM)
   └─ /api/dokkai, /api/reading, /api/analyze, /api/difficulty, /api/health
```

Prinsip rancangan: **tiap komponen punya satu tugas**, ada **cadangan** bila komponen gagal (embedding mati: turun ke lexical,
LLM mati: tetap tampilkan hasil pencarian), dan **LLM tidak dipercaya mentah**: keluarannya diparse, dinormalisasi, dan divalidasi.

## 5. Model dan komponen

| Komponen | Jenis | Siapa yang melatih | Fungsi | Kekuatan | Kelemahan |
|---|---|---|---|---|---|
| LLM chat (Llama atau Qwen via Ollama) | Model bahasa pra-latih, inferensi lokal | Pihak lain | Koreksi, ngobrol, jawaban RAG, bacaan, router cadangan | Fleksibel, gratis, privat | Model kecil bisa keliru pada bacaan, koreksi, dan arti; bisa menyalin referensi yang tidak relevan |
| bge-m3 | Model embedding multibahasa (1024 dimensi) | Pihak lain | Pencarian semantik lintas bahasa | Memahami parafrase | Skor tidak sama dengan peluang benar; skor dokumen salah dan benar bertumpuk |
| TF-IDF + Logistic Regression | ML klasik, **dilatih sendiri** | Kita | Menebak level JLPT kalimat | Ringan, di CPU, bisa dijelaskan | Mengenali pola karakter, bukan makna; data sedikit |
| fugashi + unidic-lite | Analisis morfologi | Pihak lain | Bacaan hiragana dan romaji, pemisah kata | Deterministik, tahu kelas kata (partikel dibaca wa, o, e) | Kamus lama; bacaan yang bergantung konteks bisa meleset |
| pykakasi | Konversi kana ke romaji | Pihak lain | Romaji | Sederhana | Tidak mengenal partikel (karena itu hanya dipakai setelah fugashi) |
| Pemeriksa aturan | Aturan regex dan daftar | Kita | Menangkap kesalahan umum (でわ, こんにちわ, しっ, シャベル) | Pasti dan cepat | Hanya mencakup aturan yang ditulis |
| Router | Aturan kata kunci + LLM cadangan | Kita | Memilih agent dari maksud pesan | Bisa ditebak, gratis | Hanya mengenali kata kunci yang terdaftar |
| Quiz Agent | Pembuat soal dari database | Kita | Soal arti, bacaan, isi kosong | Kunci jawaban pasti benar | Terbatas pada isi database |
| Retriever | Lexical, semantic, hybrid (RRF) + penyaring relevansi | Kita | Menemukan dokumen relevan | Teruji secara terukur | Set uji kecil |
| Reading Agent | LLM + validasi ketat | Kita (kode), pihak lain (LLM) | Bacaan N4 sampai N3 dengan soal | Memakai kosakata database; keluaran divalidasi | Isi bacaan dan soal bisa keliru; kualitas bergantung model |

## 6. Hasil yang terukur

**Pencarian RAG** (35 pertanyaan uji, hasil dari menjalankan `python -m app.rag.eval`):

| Mode | Hit@1 semua | Hit@1 parafrase (n=12) | MRR |
|---|---|---|---|
| lexical (TF-IDF) | 77% | 42% | 0,83 |
| semantic (bge-m3) | 94% | 92% | 0,97 |
| hybrid (bobot sama) | 86% | 67% | 0,90 |

Temuan: pencarian semantik jauh lebih baik pada parafrase; hybrid dengan bobot sama justru lebih buruk daripada semantic
saja. Selang kepercayaan 95% masih lebar (semantic semua sekitar 81 sampai 98%, parafrase sekitar 65 sampai 99%) karena
sampelnya kecil. Ambang penyaring referensi dipilih dari set yang sama dengan evaluasi, sehingga cenderung optimistis.

**Classifier level JLPT:** isi dengan hasil `python -m app.ml.train` terbarumu (akurasi persis dan dalam ±1 level,
jumlah data latih). Pada tahap awal dengan 50 kalimat, akurasi persis berada sekitar 42% dan dalam ±1 level sekitar 86%
(tebakan acak: 20% dan sekitar 52%). Model menangkap arah kesulitan, tetapi belum membedakan level bersebelahan.

**Pengujian perangkat lunak** (dijalankan di lingkungan pengembangan tanpa Ollama): 73 tes backend (Router, Quiz,
pemeriksa aturan, bacaan, RAG, Reading Agent, endpoint, penanganan error, CORS) dan 28 pemeriksaan alur frontend
dengan API tiruan (semua menu, kuis sampai skor, penyimpanan progres, pengaturan, perpindahan menu).

**Belum diukur:** kualitas jawaban LLM sebenarnya (koreksi, penjelasan, bacaan, terjemahan), uji dengan pengguna nyata,
Docker, dan deploy cloud.

## 7. Fungsi tiap menu di sidebar

| Menu | Fungsi | Sumber data | Butuh LLM | Endpoint |
|---|---|---|---|---|
| Sensei Chat | Pintu utama. Router memilih koreksi, ngobrol, kuis, kosakata, kanji, grammar, pertanyaan bebas, atau reading | Semua | Bergantung rute | `/api/chat` |
| Kosakata | Cari kata (kanji, bacaan, romaji, arti), filter level dan topik, tombol Acak 10 | Database | Tidak | `/api/vocabulary`, `/random`, `/topics` |
| Kanji | Cari kanji, lihat bacaan, goresan, dan contoh kata | Database | Tidak | `/api/kanji` |
| Tata Bahasa | Cari pola, lihat bentuk, arti, dan contoh | Database | Tidak | `/api/grammar` |
| Kuis | Atur jenis, level, topik, dan jumlah soal; jawab dengan umpan balik; skor dicatat | Database | Tidak | `/api/quiz` |
| Reading | Bacaan N4 sampai N3 dengan soal; tampilkan hiragana, romaji, terjemahan; kosakata database yang muncul | LLM + database | Ya | `/api/dokkai` |
| Progress | Jumlah kuis, akurasi total dan per jenis soal, daftar yang sering salah, riwayat | Browser (localStorage) | Tidak | tidak ada |
| Pengaturan | Bahasa terjemahan, mode chat, tema, hapus catatan, status backend | Browser + backend | Tidak | `/api/health` |
| Bantuan | Contoh pesan (tombol Coba mengisi chat), penjelasan menu, hal yang perlu diingat | Statis | Tidak | tidak ada |

Yang masih **placeholder**: kotak "Cari..." di sidebar dan panel "Riwayat" di sisi kanan chat (isinya contoh statis,
bukan riwayat sungguhan).

## 8. Pelajaran utama

1. **Ukur dulu sebelum percaya.** Hybrid terlihat "pasti lebih baik" tetapi ternyata lebih buruk dari semantic saja.
2. **Skor bukan peluang benar.** Skor kemiripan harus dikalibrasi ke data sendiri dan dipakai sebagai penyaring.
3. **Konteks yang tidak relevan lebih buruk daripada tanpa konteks.** Model kecil menyalin referensi yang disuntikkan.
4. **Jangan serahkan fakta kepada LLM kecil.** Bacaan, kunci kuis, dan pencarian dibuat deterministik.
5. **Rancang kegagalan.** Setiap komponen punya cadangan, dan pesan error dibuat spesifik.
6. **Urutan `except` penting** (bug penanganan error di awal yang menyamarkan masalah sebenarnya).
7. **Uji komponen yang deterministik** dengan tes otomatis, dan LLM diganti jawaban palsu agar tes cepat dan stabil.

## 9. Keterbatasan

- LLM ukuran kecil bisa keliru; hasilnya perlu dicek ke sumber resmi.
- Data awal sangat kecil dan berlabel perkiraan.
- Kunci jawaban kuis dikirim ke browser; progres hanya tersimpan di browser ini.
- Belum ada autentikasi dan pembatas laju, sehingga belum layak dibuka ke publik (lihat `docs/DEPLOY.md`).
- Reading Agent bergantung pada kualitas model; bacaan dan soal dibuat AI dan divalidasi bentuknya, bukan kebenaran isinya.

## 10. Rencana lanjutan

- Menambah data dan memvalidasi ambang RAG dengan pertanyaan baru yang ditulis sendiri.
- Riwayat chat sungguhan di panel kanan dan pencarian di sidebar.
- Kuis dari daftar yang sering salah (memakai data di Progress).
- Fitur morfologi untuk classifier level, dan membandingkan model embedding lain.
- Deploy cloud dengan pembatas laju dan autentikasi.
