import pytest

from app.agents import reading_agent as ra

GOOD = {
    "title": "朝の習慣",
    "passage": "私は毎朝六時に起きます。それから公園を散歩します。歩きながら一日の準備を考えます。",
    "translation": "Saya bangun jam enam setiap pagi.",
    "questions": [
        {"question": "Jam berapa penulis bangun?", "choices": ["Jam lima", "Jam enam", "Jam tujuh", "Jam delapan"],
         "answer": "B", "explanation": "Bacaan menyebut 六時."},
        {"question": "Ke mana penulis pergi setelah bangun?", "choices": ["Kantor", "Sekolah", "Taman", "Toko"],
         "answer": "C", "explanation": "Bacaan menyebut 公園."},
    ],
}


@pytest.mark.parametrize("answer,expected", [
    ("B", 1), ("b", 1), ("B.", 1), (2, 1), ("2", 1),
    ("Jam enam", 1), ("E", None), (9, None), (0, None), ("tidak ada", None), (True, None),
])
def test_answer_index_formats(answer, expected):
    assert ra._answer_index(answer, ["Jam lima", "Jam enam", "Jam tujuh", "Jam delapan"]) == expected


def test_clean_accepts_good_output_and_strips_letter_labels():
    data = {**GOOD, "questions": [{**GOOD["questions"][0], "choices": ["A. Jam lima", "B. Jam enam", "C. Jam tujuh", "D. Jam delapan"]}, GOOD["questions"][1]]}
    out = ra.clean(data)
    assert out["questions"][0]["choices"][1] == "Jam enam"
    assert out["questions"][0]["answer"] == 1 and out["questions"][0]["kind"] == "reading"


@pytest.mark.parametrize("bad", [
    {**GOOD, "passage": ""},
    {**GOOD, "passage": "This passage has no Japanese characters at all."},
    {**GOOD, "questions": "bukan daftar"},
    {**GOOD, "questions": [GOOD["questions"][0]]},  # hanya satu soal valid
    {**GOOD, "questions": [{**GOOD["questions"][0], "choices": ["x", "x", "y"]}] * 2},  # pilihan kembar
    {**GOOD, "questions": [{**GOOD["questions"][0], "answer": "Z"}] * 2},  # jawaban tidak dikenal
])
def test_clean_rejects_bad_output(bad):
    with pytest.raises(ValueError):
        ra.clean(bad)


def test_run_builds_full_reading_exercise(fake_llm):
    calls = fake_llm(GOOD)
    res = ra.run("kerja", "id")
    d = res.dokkai
    assert res.type == "reading" and d["hiragana"] and d["romaji"]
    assert len(d["questions"]) == 2 and d["topic"] == "kerja"
    assert "kerja" in calls[0][0]["content"]  # topik ikut ke prompt
    assert "Gunakan beberapa kata" in calls[0][0]["content"]  # kosakata dari database ikut sebagai bahan


def test_run_retries_once_then_succeeds(fake_llm):
    replies = iter([{"title": "x", "passage": "", "questions": []}, GOOD])
    calls = fake_llm(lambda messages: next(replies))
    assert ra.run(None, "id").type == "reading" and len(calls) == 2


def test_run_gives_up_after_two_invalid_replies(fake_llm):
    calls = fake_llm({"title": "x", "passage": "", "questions": []})
    with pytest.raises(ValueError):
        ra.run("kerja", "id")
    assert len(calls) == 2


def test_free_text_topic_is_accepted(fake_llm):
    calls = fake_llm(GOOD)
    assert ra.run("musim panas", "id").dokkai["topic"] == "musim panas"
    assert "musim panas" in calls[0][0]["content"]
