from app.core.settings import Settings
from app.rag.retriever import KnowledgeRetriever, RetrievedChunk, build_retrieval_query
from app.schemas import UserProfile


class FakeEmbeddingClient:
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        assert texts == ["goal: fat_loss"]
        return [[0.25, 0.75]]


class FakeQdrantClient:
    def __init__(self) -> None:
        self.received_metadata_filter: dict[str, str] | None = None

    def search_points(
        self,
        query_vector: list[float],
        *,
        limit: int,
        metadata_filter: dict[str, str] | None = None,
    ) -> list[dict]:
        assert query_vector == [0.25, 0.75]
        assert limit == 2
        self.received_metadata_filter = metadata_filter
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
    qdrant_client = FakeQdrantClient()
    retriever = KnowledgeRetriever(
        Settings(rag_retrieval_limit=2),
        embedding_client=FakeEmbeddingClient(),  # type: ignore[arg-type]
        qdrant_client=qdrant_client,  # type: ignore[arg-type]
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
    assert qdrant_client.received_metadata_filter is None


def test_knowledge_retriever_passes_metadata_filter() -> None:
    qdrant_client = FakeQdrantClient()
    retriever = KnowledgeRetriever(
        Settings(rag_retrieval_limit=2),
        embedding_client=FakeEmbeddingClient(),  # type: ignore[arg-type]
        qdrant_client=qdrant_client,  # type: ignore[arg-type]
    )

    retriever.retrieve("goal: fat_loss", metadata_filter={"topic": "mobility"})

    assert qdrant_client.received_metadata_filter == {"topic": "mobility"}


def test_build_retrieval_query_flattens_profile_fields() -> None:
    query = build_retrieval_query(valid_profile())

    assert "goal: fat_loss" in query
    assert "equipment: bodyweight, dumbbells" in query
    assert "injuries_or_limitations: knee pain" in query
