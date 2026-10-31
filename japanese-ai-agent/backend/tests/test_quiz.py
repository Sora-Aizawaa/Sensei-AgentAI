from app.agents import quiz


def test_questions_are_valid():
    """Pilihan unik, indeks jawaban di dalam daftar pilihan, dan ada penjelasan."""
    for _ in range(100):
        res = quiz.run({"n": 10}, "id")
        assert res.type == "quiz"
        for q in res.quiz["questions"]:
            assert len(q["choices"]) == len(set(q["choices"]))
            assert 3 <= len(q["choices"]) <= 4
            assert 0 <= q["answer"] < len(q["choices"])
            assert q["prompt"] and q["explanation"]


def test_requested_count_is_respected():
    assert len(quiz.run({"n": 3}, "id").quiz["questions"]) == 3


def test_topic_restricts_to_vocabulary():
    res = quiz.run({"n": 4, "topic": "kerja"}, "id")
    assert all(q["kind"].startswith("vocab") for q in res.quiz["questions"])


def test_focus_grammar():
    res = quiz.run({"n": 4, "focus": "grammar"}, "id")
    assert all(q["kind"].startswith("grammar") for q in res.quiz["questions"])


def test_english_prompts():
    res = quiz.run({"n": 2, "focus": "vocabulary"}, "en")
    assert any("What does" in q["prompt"] or "How do you read" in q["prompt"] or "Choose" in q["prompt"]
               for q in res.quiz["questions"])


def test_no_data_gives_info_message():
    res = quiz.run({"n": 3, "level": "N1"}, "id")  # data awal hanya N3 dan N4
    assert res.type == "info" and res.quiz is None


def test_every_question_carries_a_subject():
    for q in quiz.run({"n": 10}, "id").quiz["questions"]:
        assert q["subject"]
