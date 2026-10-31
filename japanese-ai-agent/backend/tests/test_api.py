import httpx
import pytest
from fastapi.testclient import TestClient
from openai import APIConnectionError

from app.main import app

client = TestClient(app)

CORRECTION = {
    "errors": ["でわ -> では"], "japanese": "日本語が嫌いなわけではない。",
    "translation": "x", "jlpt": "JLPT N3", "feedback": "f",
}


def test_health():
    assert client.get("/api/health").json()["status"] == "ok"


def test_database_endpoints():
    items = client.get("/api/vocabulary", params={"q": "働", "lang": "id"}).json()["items"]
    assert items and items[0]["meaning"] == "bekerja"
    assert client.get("/api/vocabulary", params={"level": "N9"}).status_code == 422
    assert client.get("/api/kanji", params={"q": "働"}).json()["count"] >= 1
    assert client.get("/api/grammar", params={"q": "わけ"}).json()["count"] >= 1
    assert client.get("/api/topics").json()["items"]


def test_analyze_finds_word_and_kanji():
    res = client.post("/api/analyze", json={"text": "彼は銀行で働いています。"}).json()
    assert [v["word"] for v in res["vocabulary"]] == ["働く"]
    assert [k["character"] for k in res["kanji"]] == ["働"]


def test_search_endpoint_validates_mode():
    assert client.get("/api/search", params={"q": "setiap kali", "mode": "lexical"}).status_code == 200
    assert client.get("/api/search", params={"q": "x", "mode": "bogus"}).status_code == 422


def test_quiz_via_chat_needs_no_llm(fake_llm):
    calls = fake_llm(RuntimeError("LLM tidak boleh dipanggil"))
    res = client.post("/api/chat", json={"message": "Buat 3 soal kuis N3", "language": "id"}).json()
    assert res["type"] == "quiz" and len(res["quiz"]["questions"]) == 3
    assert res["route"].startswith("quiz") and calls == []


def test_correction_flow(fake_llm):
    calls = fake_llm(CORRECTION)
    res = client.post("/api/chat", json={"message": "彼は日本語が嫌いなわけでわない。", "language": "id"}).json()
    assert res["type"] == "correction"
    assert res["hiragana"] and res["romaji"]  # dihitung oleh modul bacaan, bukan oleh LLM
    assert [h["wrong"] for h in res["rule_hints"]] == ["でわ"]
    assert "[Catatan pemeriksa otomatis]" in calls[-1][-1]["content"]  # petunjuk ikut dikirim ke LLM


def test_chat_mode_sends_history(fake_llm):
    calls = fake_llm(CORRECTION)
    body = {
        "message": "はい、元気です。", "language": "id", "mode": "chat",
        "history": [{"role": "user", "content": "こんにちは"}, {"role": "assistant", "content": "元気ですか。"}],
    }
    assert client.post("/api/chat", json=body).json()["type"] == "chat"
    roles = [m["role"] for m in calls[-1]]
    assert roles == ["system", "user", "assistant", "user"]


def test_ask_uses_rag_and_survives_llm_failure(fake_llm):
    fake_llm(RuntimeError("Ollama mati"))
    res = client.post("/api/chat", json={"message": "apa bedanya せいで dan おかげで", "language": "id"}).json()
    assert res["type"] == "ask" and res["sources"]  # tetap menampilkan hasil pencarian


def test_llm_connection_error_becomes_clear_502(fake_llm):
    err = APIConnectionError(request=httpx.Request("POST", "http://localhost:11434"))
    fake_llm(err)
    res = client.post("/api/chat", json={"message": "彼は日本語が嫌いなわけではない。", "language": "id"})
    assert res.status_code == 502 and "Ollama" in res.json()["detail"]


def test_invalid_request_is_rejected():
    assert client.post("/api/chat", json={"message": "", "language": "id"}).status_code == 422
    assert client.post("/api/chat", json={"message": "x" * 1001, "language": "id"}).status_code == 422


def test_cors_allows_local_frontend():
    res = client.options(
        "/api/chat",
        headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST"},
    )
    assert res.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_quiz_endpoint_for_quiz_page():
    res = client.get("/api/quiz", params={"n": 4, "focus": "grammar", "lang": "id"}).json()
    assert res["type"] == "quiz" and len(res["quiz"]["questions"]) == 4
    assert client.get("/api/quiz", params={"level": "N1"}).json()["type"] == "info"
    assert client.get("/api/quiz", params={"n": 99}).status_code == 422
    assert client.get("/api/quiz", params={"focus": "bogus"}).status_code == 422


def test_dokkai_endpoint(fake_llm):
    from tests.test_reading_agent import GOOD

    fake_llm(GOOD)
    res = client.post("/api/dokkai", json={"topic": "kerja", "language": "id"}).json()
    assert res["type"] == "reading" and res["dokkai"]["questions"]


def test_dokkai_invalid_llm_output_becomes_502(fake_llm):
    fake_llm({"title": "x", "passage": "", "questions": []})
    res = client.post("/api/dokkai", json={"topic": None, "language": "id"})
    assert res.status_code == 502 and "format tidak valid" in res.json()["detail"]


def test_chat_reading_intent_uses_reading_agent(fake_llm):
    from tests.test_reading_agent import GOOD

    calls = fake_llm(GOOD)
    res = client.post("/api/chat", json={"message": "Buat teks reading N3 tentang kerja", "language": "id"}).json()
    assert res["type"] == "reading" and res["route"].startswith("reading")
    assert "kerja" in calls[0][0]["content"]
