from __future__ import annotations

from dataclasses import dataclass

from app.core.settings import Settings
from app.rag.embeddings import EmbeddingClient
from app.rag.qdrant_client import QdrantClient
from app.schemas import UserProfile


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: str
    document_id: str
    title: str
    topic: str
    text: str
    score: float | None = None
    source_path: str | None = None
    section_path: list[str] | None = None


class KnowledgeRetriever:
    def __init__(
        self,
        settings: Settings,
        *,
        embedding_client: EmbeddingClient | None = None,
        qdrant_client: QdrantClient | None = None,
    ) -> None:
        self._settings = settings
        self._embedding_client = embedding_client or EmbeddingClient(settings)
        self._qdrant_client = qdrant_client or QdrantClient(settings)

    def retrieve(self, query_text: str, *, limit: int | None = None) -> list[RetrievedChunk]:
        effective_limit = limit or self._settings.rag_retrieval_limit
        if effective_limit <= 0 or not query_text.strip():
            return []

        query_vector = self._embedding_client.embed_texts([query_text])[0]
        matches = self._qdrant_client.search_points(query_vector, limit=effective_limit)

        retrieved: list[RetrievedChunk] = []
        for match in matches:
            payload = match.get("payload")
            if not isinstance(payload, dict):
                continue

            text = payload.get("text")
            chunk_id = payload.get("chunk_id")
            document_id = payload.get("document_id")
            title = payload.get("title")
            topic = payload.get("topic")
            if not all(
                isinstance(value, str) and value
                for value in [text, chunk_id, document_id, title, topic]
            ):
                continue

            section_path = payload.get("section_path")
            normalized_section_path = (
                [item for item in section_path if isinstance(item, str)]
                if isinstance(section_path, list)
                else None
            )
            score = match.get("score")
            retrieved.append(
                RetrievedChunk(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    title=title,
                    topic=topic,
                    text=text,
                    score=float(score) if isinstance(score, (int, float)) else None,
                    source_path=payload.get("source_path")
                    if isinstance(payload.get("source_path"), str)
                    else None,
                    section_path=normalized_section_path,
                )
            )
        return retrieved


def build_retrieval_query(profile: UserProfile) -> str:
    return "\n".join(
        [
            f"goal: {profile.goal.value}",
            f"experience_level: {profile.experience_level.value}",
            f"training_days_per_week: {profile.training_days_per_week}",
            f"session_duration_minutes: {profile.session_duration_minutes}",
            f"equipment: {', '.join(item.value for item in profile.equipment) or 'none'}",
            f"training_location: {profile.training_location.value}",
            f"injuries_or_limitations: {', '.join(profile.injuries_or_limitations) or 'none'}",
            f"exercise_preferences: {', '.join(profile.exercise_preferences) or 'none'}",
        ]
    )
