from functools import lru_cache

import pykakasi
from fugashi import Tagger

# Partikel yang ditulis は / を / へ tetapi dibaca wa / o / e
PARTICLE_PRON = {"は": "ワ", "を": "オ", "へ": "エ"}

# Perbaikan bacaan yang sering meleset di kamus unidic-lite (tambah sendiri sesuai kebutuhan)
SURFACE_OVERRIDE = {"日本": "ニホン", "私": "ワタシ"}

# 何 dibaca "nani" sebelum partikel ini, selain itu "nan"
NANI_NEXT = {"を", "が", "は", "に", "か", "も"}

# Kopula yang ditulis terpisah dalam romaji ("gakusei desu")
COPULA = {"です", "でし", "でしょ", "だ", "だっ"}

PUNCT = {"、": ",", "。": ".", "？": "?", "！": "!", "「": '"', "」": '"', "　": " "}


@lru_cache(maxsize=1)
def _tagger():
    return Tagger()


@lru_cache(maxsize=1)
def _kks():
    return pykakasi.kakasi()


def _has_kanji(s):
    return any("\u4e00" <= c <= "\u9fff" for c in s)


def _is_kana(s):
    return bool(s) and all("\u3040" <= c <= "\u30ff" for c in s)


def _to_hiragana(s):
    return "".join(chr(ord(c) - 0x60) if "\u30a1" <= c <= "\u30f6" else c for c in s)


def _romaji_of(kana):
    if not _is_kana(kana):
        return kana  # huruf latin, angka, dan sebagainya dibiarkan
    return "".join(item["hepburn"] for item in _kks().convert(kana))


def _base_kana(words):
    """Bacaan dasar tiap kata (katakana) + perbaikan untuk kasus yang sering salah."""
    kanas = []
    for w in words:
        k = getattr(w.feature, "kana", None)
        kanas.append(k if k and k != "*" else w.surface)

    for i, w in enumerate(words):
        s = w.surface
        nxt = words[i + 1].surface if i + 1 < len(words) else ""
        prev = words[i - 1] if i > 0 else None

        if s == "何":
            kanas[i] = "ナニ" if nxt in NANI_NEXT else "ナン"
        elif s in SURFACE_OVERRIDE:
            kanas[i] = SURFACE_OVERRIDE[s]
        elif s == "人" and w.feature.pos1 == "接尾辞" and prev is not None:
            if prev.surface == "一":
                kanas[i - 1], kanas[i] = "ヒト", "リ"
            elif prev.surface == "二":
                kanas[i - 1], kanas[i] = "フタ", "リ"
            elif prev.feature.pos2 != "数詞":
                kanas[i] = "ジン"  # 日本人, 外国人, ...
    return kanas


def _is_counter(w, prev):
    """Kata bantu bilangan (時, 円, 週間...) dirapatkan ke angkanya: 十時, 何時."""
    if prev is None or w.feature.pos3 != "助数詞可能":
        return False
    return prev.feature.pos2 == "数詞" or prev.surface == "何"


def reading(text):
    words = list(_tagger()(text))
    kanas = _base_kana(words)

    hira_chunks, roma_chunks = [], []  # hiragana: partikel menempel; romaji: partikel terpisah

    for i, w in enumerate(words):
        s = w.surface
        pos1, pos2 = w.feature.pos1, w.feature.pos2
        prev = words[i - 1] if i > 0 else None

        if s in PUNCT:
            hira, roma = s, PUNCT[s]
            h_attach = r_attach = True
        else:
            # Kata tanpa kanji (kana / katakana) ditulis apa adanya di baris hiragana
            hira = _to_hiragana(kanas[i]) if _has_kanji(s) else s
            if pos1 == "助詞" and s in PARTICLE_PRON:
                roma = _romaji_of(PARTICLE_PRON[s])
            else:
                roma = _romaji_of(kanas[i])

            suffix_like = pos1 == "接尾辞" or s == "語" or _is_counter(w, prev)
            h_attach = pos1 in {"助詞", "助動詞"} or suffix_like
            r_attach = (
                (pos1 == "助動詞" and s not in COPULA)
                or (pos1 == "助詞" and pos2 == "接続助詞")  # te, ba, nagara menempel ke kata kerja
                or suffix_like
            )

        if h_attach and hira_chunks:
            hira_chunks[-1] += hira
        else:
            hira_chunks.append(hira)

        if r_attach and roma_chunks:
            roma_chunks[-1] += roma
        else:
            roma_chunks.append(roma)

    hiragana = " ".join(hira_chunks)
    romaji = " ".join(roma_chunks)
    if romaji and romaji[0].islower() and not text[:1].isascii():
        romaji = romaji[0].upper() + romaji[1:]
    # rapikan spasi sebelum tanda baca
    for p in (",", ".", "?", "!"):
        romaji = romaji.replace(f" {p}", p)
    for p in ("、", "。", "？", "！"):
        hiragana = hiragana.replace(f" {p}", p)
    hiragana = hiragana.replace("、 ", "、")
    return hiragana, romaji