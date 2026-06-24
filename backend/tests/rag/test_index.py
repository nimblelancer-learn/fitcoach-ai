import uuid

from app.rag.index import build_qdrant_points
from app.rag.qdrant_client import QdrantPoint


def test_build_qdrant_points_preserves_payload_metadata() -> None:
    chunks = [
        {
            "chunk_id": "doc-1::chunk-000",
            "document_id": "doc-1",
            "chunk_index": 0,
            "topic": "strength",
            "text": "sample text",
            "section_path": ["Doc", "Intro"],
        }
    ]

    points = build_qdrant_points(chunks, [[0.5, 0.5]])

    assert points == [
        QdrantPoint(
            point_id=str(uuid.uuid5(uuid.NAMESPACE_URL, "doc-1::chunk-000")),
            vector=[0.5, 0.5],
            payload={
                "document_id": "doc-1",
                "chunk_id": "doc-1::chunk-000",
                "chunk_index": 0,
                "topic": "strength",
                "text": "sample text",
                "section_path": ["Doc", "Intro"],
            },
        )
    ]


def test_build_qdrant_points_requires_matching_lengths() -> None:
    try:
        build_qdrant_points([], [[1.0]])
    except ValueError as exc:
        assert "counts must match" in str(exc)
    else:
        raise AssertionError("expected mismatch validation error")
