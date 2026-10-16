"""Vocabulary, Kanji, dan Grammar Tool: mengambil data dari database, tanpa LLM."""
from app.database import repository as repo
from app.schemas import ChatResponse

TEXT = {
    "id": {
        "vocabulary": "Berikut {n} kosakata{extra}:",
        "kanji": "Berikut {n} kanji{extra}:",
        "grammar": "Berikut {n} pola tata bahasa{extra}:",
        "none": "Tidak ada hasil yang cocok di database.",
        "topics": "Topik kosakata yang tersedia: {topics}.",
        "level": "level {level}",
        "topic": "topik {topic}",
        "search": "pencarian \"{q}\"",
    },
    "en": {
        "vocabulary": "Here are {n} vocabulary items{extra}:",
        "kanji": "Here are {n} kanji{extra}:",
        "grammar": "Here are {n} grammar patterns{extra}:",
        "none": "No matching results in the database.",
        "topics": "Available vocabulary topics: {topics}.",
        "level": "level {level}",
        "topic": "topic {topic}",
        "search": "search \"{q}\"",
    },
}


def run(intent: str, params: dict, lang: str = "id") -> ChatResponse:
    t = TEXT.get(lang, TEXT["id"])
    level, topic, q = params.get("level"), params.get("topic"), params.get("q")
    n = params.get("n", 10 if intent == "vocabulary" else 5)

    if intent == "vocabulary":
        if q:
            items = repo.search_vocabulary(q=q, level=level, topic=topic, lang=lang, limit=n)
        else:
            items = repo.random_vocabulary(n, level, topic, lang)
    elif intent == "kanji":
        items = repo.search_kanji(q=q, level=level, lang=lang, limit=n)
    else:  # grammar
        items = repo.search_grammar(q=q, level=level, lang=lang, limit=n)

    if not items:
        message = t["none"]
        if intent == "vocabulary":
            topics = ", ".join(x["topic"] for x in repo.list_topics())
            if topics:
                message += " " + t["topics"].format(topics=topics)
        return ChatResponse(type="info", message=message)

    parts = []
    if level:
        parts.append(t["level"].format(level=level))
    if topic and intent == "vocabulary":
        parts.append(t["topic"].format(topic=topic))
    if q:
        parts.append(t["search"].format(q=q))
    extra = f" ({', '.join(parts)})" if parts else ""

    return ChatResponse(type=intent, message=t[intent].format(n=len(items), extra=extra), items=items)