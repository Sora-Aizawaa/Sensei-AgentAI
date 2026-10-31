import { Button, PageIntro } from "../components/ui";

const EXAMPLES = [
  [
    "Koreksi kalimat",
    "日本語シャベルわけでわないし、今は勉強しっています",
    "Periksa kalimat Jepang dan tampilkan kesalahan, bacaan, serta level.",
  ],
  [
    "Ngobrol",
    "lets talk with japanese",
    "Ngobrol dalam bahasa Jepang dengan Sensei yang ingat konteks.",
  ],
  [
    "Kuis",
    "Buat 5 soal kuis N3 tentang kerja",
    "Soal pilihan ganda dari database.",
  ],
  [
    "Kosakata",
    "Berikan 10 kosakata N3 tentang perasaan",
    "Daftar kosakata dari database.",
  ],
  ["Arti kata", "Apa arti 迷惑?", "Cari satu kata di database."],
  [
    "Tata bahasa",
    "jelaskan 〜わけではない",
    "Penjelasan satu pola dari database.",
  ],
  ["Kanji", "Apa arti kanji 働", "On'yomi, kun'yomi, dan contoh kata."],
  [
    "Pertanyaan bebas",
    "Bagaimana cara bilang 'setiap kali' dalam bahasa Jepang?",
    "Dijawab dari database (RAG) lengkap dengan sumber.",
  ],
  [
    "Reading",
    "Buat teks reading N3 tentang kerja",
    "Bacaan pendek dengan soal pemahaman.",
  ],
];

const MENUS = [
  [
    "Sensei Chat",
    "Pintu utama. Router membaca maksud pesanmu lalu memilih koreksi, ngobrol, kuis, kosakata, kanji, grammar, pertanyaan bebas, atau reading.",
  ],
  [
    "Kosakata, Kanji, Tata Bahasa",
    "Menelusuri database dengan pencarian dan filter level atau topik.",
  ],
  ["Kuis", "Membuat kuis dengan pilihan jenis, level, topik, dan jumlah soal."],
  ["Reading", "Membuat bacaan N4 sampai N3 beserta soal pemahaman."],
  [
    "Progress",
    "Ringkasan hasil kuis dan reading, serta daftar yang sering salah.",
  ],
];

export default function HelpPage({ onTry }) {
  return (
    <div className="space-y-6">
      <PageIntro>Klik "Coba" untuk mengirim contoh ke Sensei Chat.</PageIntro>

      <section>
        <h3 className="mb-2 font-semibold">Contoh pesan</h3>
        <ul className="space-y-2">
          {EXAMPLES.map(([title, text, desc]) => (
            <li
              key={title}
              className="flex items-center justify-between gap-3 rounded-lg border border-slate-100 p-3 dark:border-slate-800"
            >
              <div className="min-w-0">
                <p className="text-sm font-semibold">{title}</p>
                <p className="truncate text-sm text-slate-600 dark:text-slate-300">
                  {text}
                </p>
                <p className="text-xs text-slate-400">{desc}</p>
              </div>
              <Button onClick={() => onTry(text)}>Coba</Button>
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h3 className="mb-2 font-semibold">Fungsi tiap menu</h3>
        <ul className="space-y-2 text-sm">
          {MENUS.map(([name, desc]) => (
            <li key={name}>
              <span className="font-semibold">{name}</span>
              <span className="text-slate-500">: {desc}</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="space-y-1 text-sm text-slate-500">
        <h3 className="font-semibold text-inherit">Perlu diingat</h3>
        <p>
          Sensei memakai model bahasa lokal yang bisa keliru. Cek ulang tata
          bahasa penting ke sumber resmi JLPT.
        </p>
        <p>
          Data awal berukuran kecil. Tambahkan materi sendiri lewat file CSV,
          lalu bangun ulang database dan indeks.
        </p>
      </section>
    </div>
  );
}
