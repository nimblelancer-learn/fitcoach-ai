import logging
from dataclasses import dataclass

from app.llm.openai_client import OpenAIWorkoutPlanClient
from app.llm.prompts import build_workout_plan_prompt
from app.rag.retriever import KnowledgeRetriever, RetrievedChunk, build_retrieval_query
from app.schemas import UserProfile, WorkoutPlan

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GenerationDebugContext:
    retrieval_query: str
    retrieved_chunks: list[RetrievedChunk]


class WorkoutPlanGenerator:
    def __init__(
        self,
        client: OpenAIWorkoutPlanClient,
        retriever: KnowledgeRetriever | None = None,
    ) -> None:
        self._client = client
        self._retriever = retriever
        self._last_debug_context = GenerationDebugContext(retrieval_query="", retrieved_chunks=[])

    async def generate(self, profile: UserProfile) -> WorkoutPlan:
        retrieval_query = build_retrieval_query(profile)
        retrieved_chunks: list[RetrievedChunk] = []
        if self._retriever is not None:
            try:
                retrieved_chunks = self._retriever.retrieve(retrieval_query)
            except Exception as exc:
                logger.warning(
                    "workout_plan_retrieval_failed error_type=%s",
                    type(exc).__name__,
                )

        self._last_debug_context = GenerationDebugContext(
            retrieval_query=retrieval_query,
            retrieved_chunks=retrieved_chunks,
        )
        logger.info(
            "workout_plan_retrieval count=%s chunk_ids=%s",
            len(retrieved_chunks),
            [chunk.chunk_id for chunk in retrieved_chunks],
        )
        messages = build_workout_plan_prompt(profile, retrieved_chunks=retrieved_chunks)
        return await self._client.generate_workout_plan(messages)

    def get_last_debug_context(self) -> GenerationDebugContext:
        return self._last_debug_context
