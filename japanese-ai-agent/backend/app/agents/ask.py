"""Ask Agent: menjawab pertanyaan bebas dengan RAG (cari di database, lalu LLM menjelaskan)."""
from app import llm
from app.prompts import build_ask_prompt
from app.rag import context as rag
from app.schemas import ChatResponse

TEXT = {
    "id": {
        "none": "Aku tidak menemukan data yang relevan di database. Coba tambahkan materinya di file CSV lalu bangun ulang indeks.",
        "fallback": "AI sedang tidak tersedia, jadi ini hasil pencarian yang paling relevan dari database:",
        "empty": "AI tidak memberi jawaban. Ini hasil pencarian yang paling relevan dari database:",
        "short": "Jawaban AI terlalu singkat, jadi ini isi database yang paling relevan:",
    },
    "en": {
        "none": "I could not find relevant data in the database. Add the material to the CSV files and rebuild the index.",
        "fallback": "The AI is unavailable, so here are the most relevant search results from the database:",
        "empty": "The AI gave no answer. Here are the most relevant search results from the database:",
        "short": "The AI answer was too short, so here is the most relevant database entry:",
    },
}


def run(question: str, lang: str = "id") -> ChatResponse:
    t = TEXT.get(lang, TEXT["id"])
    hits = rag.retrieve(question, k=4)
    if not hits:
        return ChatResponse(type="info", message=t["none"])

    language_name = llm.LANG_NAMES.get(lang, "Bahasa Indonesia")
    answer, used = "", None
    try:
        data = llm.chat_json(
            [
                {"role": "system", "content": build_ask_prompt(language_name, rag.numbered_references(hits))},
                {"role": "user", "content": question},
            ],
            max_tokens=700,
        )
        answer = llm._to_str(data.get("answer"))
        nums = data.get("sources", [])
        used = {int(n) for n in nums if str(n).strip().isdigit()} if isinstance(nums, list) else None
    except Exception as e:
        print("ASK LLM ERROR (memakai hasil pencarian saja):", repr(e))
        answer = ""
        message_if_empty = t["fallback"]
    else:
        message_if_empty = t["empty"]

    # Jawaban model kecil kadang hanya nama pola (contoh: "〜たびに"). Anggap itu gagal.
    if answer and len(answer) < 25:
        answer, message_if_empty = "", t["short"]

    if not answer:
        # Tampilkan isi database teratas langsung, supaya pengguna tidak perlu membuka daftar sumber
        answer = f"{message_if_empty}\n\n{hits[0]['text']}"

    return ChatResponse(type="ask", message=answer, sources=rag.to_sources(hits, used))