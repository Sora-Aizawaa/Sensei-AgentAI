import re

KANJI = "\u4e00-\u9fff"

# (pola, salah, benar, alasan)
RULES = [
    (re.compile(r"でわ"), "でわ", "では",
     "Partikel は dibaca 'wa' tetapi tetap ditulis は: ～では, bukan ～でわ."),
    (re.compile(r"こんにちわ"), "こんにちわ", "こんにちは",
     "Salam ditulis こんにちは (は, bukan わ)."),
    (re.compile(r"こんばんわ"), "こんばんわ", "こんばんは",
     "Salam ditulis こんばんは (は, bukan わ)."),
    (re.compile(rf"(?<=[{KANJI}])しっ(?=ています|ていた|ていない|ている)"), "しっ", "し",
     "Kemungkinan salah ketik: っ kecil berlebih. Contoh: 勉強しています."),
]

# Kata katakana yang sering tertukar dengan kata kerja / kata lain
CONFUSABLE = {
    "シャベル": ("しゃべる",
                "シャベル berarti 'sekop' (shovel). Untuk 'berbicara' tulis しゃべる atau 話す."),
}


def check_text(text):
    hints = []
    for pattern, wrong, right, reason in RULES:
        if pattern.search(text):
            hints.append({"wrong": wrong, "right": right, "reason": reason})
    for wrong, (right, reason) in CONFUSABLE.items():
        if wrong in text:
            hints.append({"wrong": wrong, "right": right, "reason": reason})
    return hints