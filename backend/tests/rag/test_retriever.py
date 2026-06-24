from app.core.settings import Settings
from app.rag.retriever import KnowledgeRetriever, RetrievedChunk, build_retrieval_query
from app.schemas import UserProfile


class FakeEmbeddingClient:
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        assert texts == ["goal: fat_loss"]
        return [[0.25, 0.75]]


class FakeQdrantClient:
    def search_points(self, query_vector: list[float], *, limit: int) -> list[dict]:
        assert query_vector == [0.25, 0.75]
        assert limit == 2
        return [
            {
                "score": 0.88,
                "payload": {
                    "chunk_id": "doc-1::chunk-000",
                    "document_id": "doc-1",
                    "title": "Warm-up basics",
                    "topic": "warmup",
                    "text": "Start with 5 minutes of easy movement.",
                    "source_path": "raw/warmup.md",
                    "section_path": ["Warm-up", "Basics"],
                },
            },
            {"payload": {"chunk_id": "missing-required"}},
        ]


def valid_profile() -> UserProfile:
    return UserProfile.model_validate(
        {
            "goal": "fat_loss",
            "experience_level": "beginner",
            "training_days_per_week": 3,
            "session_duration_minutes": 45,
            "equipment": ["bodyweight", "dumbbells"],
            "training_location": "home",
            "injuries_or_limitations": ["knee pain"],
            "exercise_preferences": ["strength training"],
        }
    )


def test_knowledge_retriever_maps_qdrant_payloads() -> None:
    retriever = KnowledgeRetriever(
        Settings(rag_retrieval_limit=2),
        embedding_client=FakeEmbeddingClient(),  # type: ignore[arg-type]
        qdrant_client=FakeQdrantClient(),  # type: ignore[arg-type]
    )

    chunks = retriever.retrieve("goal: fat_loss")

    assert chunks == [
        RetrievedChunk(
            chunk_id="doc-1::chunk-000",
            document_id="doc-1",
            title="Warm-up basics",
            topic="warmup",
            text="Start with 5 minutes of easy movement.",
            score=0.88,
            source_path="raw/warmup.md",
            section_path=["Warm-up", "Basics"],
        )
    ]


def test_build_retrieval_query_flattens_profile_fields() -> None:
    query = build_retrieval_query(valid_profile())

    assert "goal: fat_loss" in query
    assert "equipment: bodyweight, dumbbells" in query
    assert "injuries_or_limitations: knee pain" in query
