from enum import StrEnum

from pydantic import Field

from .common import SchemaBase


class DifficultyFeedback(StrEnum):
    TOO_EASY = "too_easy"
    ABOUT_RIGHT = "about_right"
    TOO_HARD = "too_hard"


class PlanFeedback(SchemaBase):
    usefulness_rating: int = Field(ge=1, le=5)
    difficulty_feedback: DifficultyFeedback
    felt_safe: bool
    would_follow_plan: bool
    feedback_text: str | None = Field(default=None, max_length=1000)


class FeedbackRuntimeMetadata(SchemaBase):
    generated_at: str | None = Field(default=None, min_length=1, max_length=64)
    model_name: str | None = Field(default=None, min_length=1, max_length=120)
    latency_ms: int | None = Field(default=None, ge=0)
    used_fallback: bool = False
    retrieved_chunk_count: int = Field(default=0, ge=0, le=100)
    retrieved_chunk_ids: list[str] = Field(default_factory=list, max_length=100)
    safety_trigger_codes: list[str] = Field(default_factory=list, max_length=20)
    trace_id: str | None = Field(default=None, min_length=1, max_length=120)
    trace_enabled: bool = False
    langfuse_host: str | None = Field(default=None, min_length=1, max_length=200)
