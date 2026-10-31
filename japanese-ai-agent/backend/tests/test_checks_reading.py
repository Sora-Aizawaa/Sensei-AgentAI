import pytest

from app.nlp.checks import check_text
from app.nlp.reading import reading


def test_rules_detect_typical_mistakes():
    wrong = {h["wrong"] for h in check_text("日本語シャベルわけでわないし、今は勉強しっています")}
    assert wrong == {"でわ", "しっ", "シャベル"}


@pytest.mark.parametrize("text", [
    "日本語が話せないわけではありません。今は勉強しています。",
    "彼のことを知っています。",  # 知っています tidak boleh dianggap salah ketik
    "毎朝七時に起きます。",
])
def test_rules_have_no_false_alarm(text):
    assert check_text(text) == []


@pytest.mark.parametrize("text,hiragana,romaji", [
    ("今日は何を食べますか？", "きょうは なにを たべますか？", "Kyou wa nani o tabemasu ka?"),
    ("私は学生です。", "わたしは がくせいです。", "Watashi wa gakusei desu."),
    ("日本人の友達がいます。", "にほんじんの ともだちが います。", "Nihonjin no tomodachi ga imasu."),
])
def test_reading(text, hiragana, romaji):
    assert reading(text) == (hiragana, romaji)
