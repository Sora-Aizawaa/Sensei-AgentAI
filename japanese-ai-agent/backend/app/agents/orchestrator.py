"""Orchestrator: Router memilih agent, lalu agent yang dipilih bekerja."""
import traceback

from app import llm
from app.agents import quiz, tools
from app.agents.router import route
from app.database.repository import analyze_text
from app.ml.difficulty import predict_level
from app.nlp.checks import check_text
from app.nlp.reading import reading as japanese_reading
from app.schemas import ChatRequest, ChatResponse


def _history(req: ChatRequest) -> list[dict]:
    """Ambil 8 pesan terakhir, dipotong supaya prompt tidak membengkak."""
    return [{"role": h.role, "content": h.content[:300]} for h in req.history[-8:] if h.content.strip()]


def _enrich(result: ChatResponse, req: ChatRequest, hints: list[dict]) -> None:
    """Tambahkan pemeriksa aturan, bacaan, level ML, dan data database ke jawaban LLM."""
    result.rule_hints = hints
    if any(h["wrong"] in result.japanese for h in hints):
        result.warning = (
            "Pemeriksa otomatis menemukan kesalahan yang belum diperbaiki di jawaban AI. "
            "Pegang koreksi dari pemeriksa otomatis, jangan terjemahan dan penjelasan AI."
        )

    # Hiragana dan romaji dihitung oleh analisis morfologi, bukan tebakan LLM
    try:
        result.hiragana, result.romaji = japanese_reading(result.japanese)
    except Exception:
        print("READING ERROR (bacaan dari LLM tidak dipakai):")
        traceback.print_exc()

    pred = predict_level(result.japanese)
    if pred:
        result.jlpt_ml = f"JLPT {pred['level']} ({int(pred['confidence'] * 100)}%)"

    try:
        found = analyze_text(f"{req.message} {result.japanese}", req.language)
        result.db_vocabulary = found["vocabulary"]
        result.db_grammar = found["grammar"]
    except Exception:
        print("DB ERROR (chat tetap jalan tanpa kartu database):")
        traceback.print_exc()


def _run_language(req: ChatRequest, intent: str) -> ChatResponse:
    hints = check_text(req.message)
    if intent == "chat":
        data = llm.ask_partner(req.message, req.language, _history(req), hints)
    else:
        data = llm.ask_sensei(req.message, req.language, hints)
    result = ChatResponse.model_validate({**data, "type": intent})
    _enrich(result, req, hints)
    return result


def handle_message(req: ChatRequest) -> ChatResponse:
    decision = route(req.message, req.mode, req.previous_type)
    print(f"ROUTER: {decision.intent} via {decision.via} params={decision.params}")

    if decision.intent == "quiz":
        response = quiz.run(decision.params, req.language)
    elif decision.intent in ("vocabulary", "kanji", "grammar"):
        response = tools.run(decision.intent, decision.params, req.language)
    elif decision.intent == "reading":
        response = ChatResponse(
            type="info",
            message="Latihan reading belum tersedia, ini rencana tahap berikutnya. "
            "Sementara itu kamu bisa mencoba kuis, kosakata, atau mengobrol dengan Sensei.",
        )
    else:  # chat atau correction
        response = _run_language(req, decision.intent)

    response.route = f"{decision.intent} · {decision.via}"
    return response