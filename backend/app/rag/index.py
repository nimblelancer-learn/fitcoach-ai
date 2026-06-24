from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from app.core.settings import get_settings
from app.rag.chunking import build_chunk_artifact
from app.rag.embeddings import EmbeddingClient
from app.rag.qdrant_client import QdrantClient, QdrantPoint


@dataclass(frozen=True)
class IndexingSummary:
    collection_name: str
    document_count: int
    chunk_count: int
    embedding_provider: str
    vector_size: int


def build_qdrant_points(
    chunks: list[dict[str, Any]],
    vectors: list[list[float]],
) -> list[QdrantPoint]:
    if len(chunks) != len(vectors):
        raise ValueError("chunk and vector counts must match")

    points: list[QdrantPoint] = []
    for chunk, vector in zip(chunks, vectors, strict=True):
        payload = dict(chunk)
        points.append(
            QdrantPoint(
                point_id=str(uuid.uuid5(uuid.NAMESPACE_URL, chunk["chunk_id"])),
                vector=vector,
                payload=payload,
            )
        )
    return points


def run_indexing() -> IndexingSummary:
    settings = get_settings()
    artifact = build_chunk_artifact()
    chunks = artifact["chunks"]
    if not chunks:
        raise ValueError("no knowledge-base chunks available for indexing")

    embedding_client = EmbeddingClient(settings)
    vectors = embedding_client.embed_texts([chunk["text"] for chunk in chunks])
    qdrant_client = QdrantClient(settings)
    qdrant_client.ensure_collection(vector_size=len(vectors[0]))
    qdrant_client.upsert_points(build_qdrant_points(chunks, vectors))

    return IndexingSummary(
        collection_name=settings.qdrant_collection,
        document_count=artifact["document_count"],
        chunk_count=artifact["chunk_count"],
        embedding_provider=settings.rag_embedding_provider,
        vector_size=len(vectors[0]),
    )


def main() -> None:
    summary = run_indexing()
    print(
        "Indexed "
        f"{summary.chunk_count} chunks from {summary.document_count} documents into "
        f"{summary.collection_name} using {summary.embedding_provider} "
        f"({summary.vector_size} dimensions)"
    )


if __name__ == "__main__":
    main()
