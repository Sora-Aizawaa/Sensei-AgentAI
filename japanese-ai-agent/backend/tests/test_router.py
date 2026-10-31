import pytest

from app.agents import router


@pytest.fixture(autouse=True)
def no_llm_router(monkeypatch):
    # Router cadangan (LLM) dimatikan: pesan yang tidak cocok aturan jatuh ke "chat · default"
    monkeypatch.setattr(router, "llm_route", lambda message: None)


CASES = [
    # (pesan, mode, previous_type, intent yang diharapkan)
    ("Buat 5 soal kuis N3 tentang kerja", "auto", None, "quiz"),
    ("buat soal kuis kanji", "chat", None, "quiz"),  # alat didahulukan walau mode ngobrol
    ("Berikan 10 kosakata N3 tentang perasaan", "auto", None, "vocabulary"),
    ("Apa arti 迷惑?", "auto", None, "vocabulary"),
    ("jelaskan 〜わけではない", "auto", None, "grammar"),
    ("Apa arti kanji 働", "auto", None, "kanji"),
    ("日本語シャベルわけでわないし、今は勉強しっています", "auto", None, "correction"),
    ("はい、元気です。", "auto", "chat", "chat"),  # melanjutkan obrolan
    ("Tolong koreksi kalimat saya: 私わ学生です", "auto", "chat", "correction"),
    ("Bagaimana cara bilang 'bukan berarti' dalam bahasa Jepang?", "auto", None, "ask"),
    ("apa bedanya 〜せいで dan 〜おかげで", "auto", None, "ask"),
    ("Buat teks reading N3 tentang kerja", "auto", None, "reading"),
    ("lets talk with japanese", "auto", None, "chat"),
    ("こんにちは", "chat", None, "chat"),
    ("こんにちは", "correction", None, "correction"),
]


@pytest.mark.parametrize("message,mode,previous,expected", CASES)
def test_route_intent(message, mode, previous, expected):
    assert router.route(message, mode, previous).intent == expected


def test_extract_params():
    p = router.extract_params("Buat 5 soal kuis N3 tentang kerja")
    assert p["n"] == 5  # angka di "N3" tidak dihitung
    assert p["level"] == "N3"
    assert p["topic"] == "kerja"


def test_extract_japanese_query():
    assert router.extract_params("jelaskan 〜わけではない")["q"] == "わけではない"
