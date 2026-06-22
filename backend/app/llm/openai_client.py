import logging
from typing import Any

from openai import AsyncOpenAI, OpenAIError
from pydantic import ValidationError

from app.core.errors import AppError
from app.core.settings import Settings
from app.schemas import WorkoutPlan

logger = logging.getLogger(__name__)


class OpenAIWorkoutPlanClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: AsyncOpenAI | None = None

    def _get_client(self) -> AsyncOpenAI:
        if not self._settings.openai_api_key:
            raise AppError(
                status_code=503,
                code="OPENAI_CONFIG_MISSING",
                message="The workout generation service is not configured.",
            )

        if not self._settings.openai_model:
            raise AppError(
                status_code=503,
                code="OPENAI_CONFIG_MISSING",
                message="The workout generation service is not configured.",
            )

        if self._client is None:
            self._client = AsyncOpenAI(api_key=self._settings.openai_api_key)

        return self._client

    async def generate_workout_plan(self, messages: list[dict]) -> WorkoutPlan:
        client = self._get_client()

        logger.info(
            "openai_workout_plan_request model=%s goal=%s training_days_per_week=%s",
            self._settings.openai_model,
            _extract_prompt_field(messages, "goal"),
            _extract_prompt_field(messages, "training_days_per_week"),
        )

        try:
            response = await client.responses.parse(
                model=self._settings.openai_model,
                input=messages,
                text_format=WorkoutPlan,
            )
        except OpenAIError as exc:
            logger.warning(
                "openai_workout_plan_request_failed model=%s error_type=%s",
                self._settings.openai_model,
                type(exc).__name__,
            )
            raise AppError(
                status_code=502,
                code="OPENAI_REQUEST_FAILED",
                message="The workout generation service request failed.",
            ) from exc

        refusal = _extract_refusal(response)
        if refusal is not None:
            logger.warning(
                "openai_workout_plan_refusal model=%s",
                self._settings.openai_model,
            )
            raise AppError(
                status_code=502,
                code="OPENAI_REFUSAL",
                message="The workout generation service did not return a workout plan.",
            )

        parsed = getattr(response, "output_parsed", None)
        if parsed is None:
            raise AppError(
                status_code=502,
                code="OPENAI_INVALID_OUTPUT",
                message="The workout generation service returned invalid output.",
            )

        try:
            if isinstance(parsed, WorkoutPlan):
                return WorkoutPlan.model_validate(parsed.model_dump())

            return WorkoutPlan.model_validate(parsed)
        except ValidationError as exc:
            logger.warning(
                "openai_workout_plan_validation_failed model=%s error_count=%s",
                self._settings.openai_model,
                len(exc.errors()),
            )
            raise AppError(
                status_code=502,
                code="OPENAI_INVALID_OUTPUT",
                message="The workout generation service returned invalid output.",
            ) from exc


def _extract_prompt_field(messages: list[dict], field_name: str) -> str | None:
    prefix = f"{field_name}: "

    for message in messages:
        content = message.get("content")
        if not isinstance(content, str):
            continue

        for line in content.splitlines():
            if line.startswith(prefix):
                return line.removeprefix(prefix)

    return None


def _extract_refusal(response: Any) -> str | None:
    direct_refusal = getattr(response, "refusal", None)
    if isinstance(direct_refusal, str) and direct_refusal:
        return direct_refusal

    for output_item in getattr(response, "output", []):
        if getattr(output_item, "type", None) != "message":
            continue

        for content_item in getattr(output_item, "content", []):
            if getattr(content_item, "type", None) != "refusal":
                continue

            refusal = getattr(content_item, "refusal", None)
            if isinstance(refusal, str) and refusal:
                return refusal

    return None
