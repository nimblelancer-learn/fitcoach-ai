import json
from pathlib import Path

import pytest

from app.core.settings import Settings
from app.rag.embeddings import EmbeddingClient
from app.rag.retriever import KnowledgeRetriever

CHUNK_ARTIFACT_PATH = (
    Path(__file__).resolve().parents[3] / "knowledge_base" / "processed" / "chunks-v1.json"
)


class InMemorySearchClient:
    def __init__(self, chunks: list[dict], vectors: list[list[float]]) -> None:
        self._chunks = chunks
        self._vectors = vectors

    def search_points(
        self,
        query_vector: list[float],
        *,
        limit: int,
        metadata_filter: dict[str, str] | None = None,
    ) -> list[dict]:
        matches: list[dict] = []
        for chunk, vector in zip(self._chunks, self._vectors, strict=True):
            if metadata_filter and any(
                chunk.get(key) != value for key, value in metadata_filter.items()
            ):
                continue
            matches.append(
                {
                    "score": sum(
                        left * right for left, right in zip(query_vector, vector, strict=True)
                    ),
                    "payload": chunk,
                }
            )
        matches.sort(key=lambda item: item["score"], reverse=True)
        return matches[:limit]


def build_quality_retriever() -> KnowledgeRetriever:
    artifact = json.loads(CHUNK_ARTIFACT_PATH.read_text())
    chunks = artifact["chunks"]
    settings = Settings(rag_embedding_provider="local-hash", rag_embedding_dimensions=256)
    embedding_client = EmbeddingClient(settings)
    vectors = embedding_client.embed_texts([chunk["text"] for chunk in chunks])
    search_client = InMemorySearchClient(chunks, vectors)
    return KnowledgeRetriever(
        settings,
        embedding_client=embedding_client,
        qdrant_client=search_client,  # type: ignore[arg-type]
    )


@pytest.mark.parametrize(
    ("query_text", "expected_top_chunk_id"),
    [
        (
            "bodyweight dumbbells resistance bands home plan 2 to 4 sets 6 to 12 repetitions",
            "kb-strength-full-body-strength-for-beginners-v1::chunk-000",
        ),
        (
            "warm up before workout and cool down after training",
            "kb-mobility-warm-up-and-cool-down-basics-v1::chunk-000",
        ),
        (
            "rest day sleep persistent soreness workload too high",
            "kb-recovery-recovery-sleep-and-rest-days-v1::chunk-000",
        ),
        (
            "full body training 2 to 4 days per week beginner",
            "kb-foundations-beginner-training-principles-v1::chunk-000",
        ),
    ],
)
def test_retrieval_quality_queries_return_relevant_top_chunk(
    query_text: str,
    expected_top_chunk_id: str,
) -> None:
    retriever = build_quality_retriever()

    chunks = retriever.retrieve(query_text, limit=3)

    assert chunks
    assert chunks[0].chunk_id == expected_top_chunk_id


def test_retrieval_quality_can_narrow_results_with_metadata_filter() -> None:
    retriever = build_quality_retriever()

    chunks = retriever.retrieve(
        "sharp pain dizziness chest pain stop exercise",
        limit=3,
        metadata_filter={"topic": "safety"},
    )

    assert [chunk.topic for chunk in chunks] == ["safety"]
    assert chunks[0].chunk_id == "kb-safety-exercise-safety-and-red-flags-v1::chunk-000"


def test_retrieval_quality_exposes_early_failure_case_without_filter() -> None:
    retriever = build_quality_retriever()

    chunks = retriever.retrieve("sharp pain dizziness chest pain stop exercise", limit=3)

    assert chunks
    assert chunks[0].topic == "foundations"
    assert {chunk.topic for chunk in chunks[:2]} == {"foundations", "safety"}
