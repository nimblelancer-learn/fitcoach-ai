from app.core.settings import Settings
from app.rag.embeddings import EmbeddingClient


def test_local_hash_embeddings_are_deterministic() -> None:
    settings = Settings(rag_embedding_provider="local-hash", rag_embedding_dimensions=32)
    client = EmbeddingClient(settings)

    first = client.embed_texts(["Beginner full-body plan"])
    second = client.embed_texts(["Beginner full-body plan"])

    assert first == second
    assert len(first[0]) == 32


def test_openai_provider_requires_api_key() -> None:
    settings = Settings(
        rag_embedding_provider="openai",
        rag_embedding_model="text-embedding-3-small",
        rag_embedding_dimensions=8,
        openai_api_key=None,
    )
    client = EmbeddingClient(settings)

    try:
        client.embed_texts(["hello"])
    except ValueError as exc:
        assert "OPENAI_API_KEY" in str(exc)
    else:
        raise AssertionError("expected missing API key validation error")
