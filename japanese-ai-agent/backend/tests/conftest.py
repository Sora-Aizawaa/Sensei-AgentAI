import pytest

from app import llm
from app.database import connection


@pytest.fixture(scope="session", autouse=True)
def test_database(tmp_path_factory):
    """Database sementara dari file CSV di data/. Tes tidak menyentuh data/sensei.db milikmu."""
    connection.DB_PATH = tmp_path_factory.mktemp("db") / "test.db"

    from app.database import seed
    from app.rag import index, retriever

    seed.main()
    index.build(with_embeddings=False)  # indeks lexical saja, tidak butuh Ollama
    retriever.reload()
    yield connection.DB_PATH


@pytest.fixture
def fake_llm(monkeypatch):
    """Ganti pemanggilan LLM dengan jawaban palsu, jadi tes tidak butuh Ollama.
    Pemakaian: fake_llm(nama_fungsi_atau_dict)."""

    def install(reply):
        calls = []

        def fake(messages, max_tokens=900, temperature=0.2):
            calls.append(messages)
            if isinstance(reply, Exception):
                raise reply
            return reply(messages) if callable(reply) else reply

        monkeypatch.setattr(llm, "chat_json", fake)
        return calls

    return install
