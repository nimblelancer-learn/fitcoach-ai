import logging
from time import perf_counter
from typing import Any

from pydantic import ValidationError

try:
    from openai import APITimeoutError, AsyncOpenAI, OpenAIError
except ModuleNotFoundError:

    class OpenAIError(Exception):
        pass

    class APITimeoutError(TimeoutError):
        pass

    class AsyncOpenAI:  # type: ignore[no-redef]
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            raise ModuleNotFoundError("openai package is required for workout generation")


from app.core.errors import AppError
from app.core.settings import Settings
from app.llm.pricing import (
    estimate_request_cost_from_pricing_usd,
    estimate_request_cost_usd,
)
from app.schemas import (
    ExperienceLevel,
    FitnessGoal,
    WorkoutPlan,
)
from app.schemas.workout_plan import (
    ExerciseCategory,
    Intensity,
    PrescriptionType,
    SafetyWarningCode,
    WarningSeverity,
)

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
        max_attempts = self._settings.openai_invalid_output_retries + 1

        logger.info(
            "openai_workout_plan_request model=%s goal=%s training_days_per_week=%s",
            self._settings.openai_model,
            _extract_prompt_field(messages, "goal"),
            _extract_prompt_field(messages, "training_days_per_week"),
        )

        last_invalid_output_error: AppError | None = None

        for attempt in range(1, max_attempts + 1):
            started_at = perf_counter()

            try:
                response = await client.responses.parse(
                    model=self._settings.openai_model,
                    input=messages,
                    text_format=WorkoutPlan,
                    timeout=self._settings.openai_timeout_seconds,
                )
            except APITimeoutError as exc:
                latency_ms = _elapsed_ms(started_at)
                logger.warning(
                    (
                        "openai_workout_plan_timeout model=%s attempt=%s latency_ms=%s "
                        "timeout_seconds=%s"
                    ),
                    self._settings.openai_model,
                    attempt,
                    latency_ms,
                    self._settings.openai_timeout_seconds,
                )
                raise AppError(
                    status_code=504,
                    code="OPENAI_TIMEOUT",
                    message="The workout generation service timed out.",
                ) from exc
            except TimeoutError as exc:
                latency_ms = _elapsed_ms(started_at)
                logger.warning(
                    (
                        "openai_workout_plan_timeout model=%s attempt=%s latency_ms=%s "
                        "timeout_seconds=%s"
                    ),
                    self._settings.openai_model,
                    attempt,
                    latency_ms,
                    self._settings.openai_timeout_seconds,
                )
                raise AppError(
                    status_code=504,
                    code="OPENAI_TIMEOUT",
                    message="The workout generation service timed out.",
                ) from exc
            except OpenAIError as exc:
                latency_ms = _elapsed_ms(started_at)
                logger.warning(
                    (
                        "openai_workout_plan_request_failed model=%s attempt=%s latency_ms=%s "
                        "error_type=%s"
                    ),
                    self._settings.openai_model,
                    attempt,
                    latency_ms,
                    type(exc).__name__,
                )
                raise AppError(
                    status_code=502,
                    code="OPENAI_REQUEST_FAILED",
                    message="The workout generation service request failed.",
                ) from exc

            latency_ms = _elapsed_ms(started_at)
            usage = _extract_usage(response)
            estimated_cost = _estimate_cost_from_settings_or_table(
                settings=self._settings,
                input_tokens=usage["input_tokens"],
                output_tokens=usage["output_tokens"],
            )

            logger.info(
                (
                    "openai_workout_plan_response model=%s attempt=%s latency_ms=%s "
                    "input_tokens=%s output_tokens=%s total_tokens=%s estimated_cost_usd=%s"
                ),
                self._settings.openai_model,
                attempt,
                latency_ms,
                usage["input_tokens"],
                usage["output_tokens"],
                usage["total_tokens"],
                _format_estimated_cost(estimated_cost),
            )

            refusal = _extract_refusal(response)
            if refusal is not None:
                logger.warning(
                    "openai_workout_plan_refusal model=%s attempt=%s",
                    self._settings.openai_model,
                    attempt,
                )
                raise AppError(
                    status_code=502,
                    code="OPENAI_REFUSAL",
                    message="The workout generation service did not return a workout plan.",
                )

            try:
                return _validate_parsed_workout_plan(response)
            except AppError as exc:
                last_invalid_output_error = exc
                logger.warning(
                    (
                        "openai_workout_plan_invalid_output model=%s attempt=%s "
                        "max_attempts=%s code=%s"
                    ),
                    self._settings.openai_model,
                    attempt,
                    max_attempts,
                    exc.code,
                )

                if attempt < max_attempts:
                    continue

        logger.warning(
            "openai_workout_plan_fallback model=%s attempts=%s reason=%s",
            self._settings.openai_model,
            max_attempts,
            last_invalid_output_error.code if last_invalid_output_error else "unknown",
        )
        return _build_fallback_workout_plan(messages)


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


def _validate_parsed_workout_plan(response: Any) -> WorkoutPlan:
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
            getattr(response, "model", None),
            len(exc.errors()),
        )
        raise AppError(
            status_code=502,
            code="OPENAI_INVALID_OUTPUT",
            message="The workout generation service returned invalid output.",
        ) from exc


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


def _extract_usage(response: Any) -> dict[str, int | None]:
    usage = getattr(response, "usage", None)
    if usage is None:
        return {
            "input_tokens": None,
            "output_tokens": None,
            "total_tokens": None,
        }

    input_tokens = getattr(usage, "input_tokens", None)
    output_tokens = getattr(usage, "output_tokens", None)
    total_tokens = getattr(usage, "total_tokens", None)

    if total_tokens is None and (isinstance(input_tokens, int) or isinstance(output_tokens, int)):
        total_tokens = (input_tokens or 0) + (output_tokens or 0)

    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
    }


def _elapsed_ms(started_at: float) -> int:
    return int((perf_counter() - started_at) * 1000)


def _format_estimated_cost(cost: float | None) -> str:
    if cost is None:
        return "unavailable"

    return f"{cost:.8f}"


def _estimate_cost_from_settings_or_table(
    *,
    settings: Settings,
    input_tokens: int | None,
    output_tokens: int | None,
) -> float | None:
    if (
        settings.openai_input_cost_per_million_tokens_usd is not None
        and settings.openai_output_cost_per_million_tokens_usd is not None
    ):
        return estimate_request_cost_from_pricing_usd(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_per_million_tokens_usd=settings.openai_input_cost_per_million_tokens_usd,
            output_per_million_tokens_usd=settings.openai_output_cost_per_million_tokens_usd,
        )

    return estimate_request_cost_usd(
        settings.openai_model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )


def _build_fallback_workout_plan(messages: list[dict]) -> WorkoutPlan:
    goal = _parse_fitness_goal(_extract_prompt_field(messages, "goal"))
    experience_level = _parse_experience_level(_extract_prompt_field(messages, "experience_level"))
    training_days_per_week = _parse_training_days_per_week(
        _extract_prompt_field(messages, "training_days_per_week")
    )
    session_duration_minutes = _parse_session_duration_minutes(
        _extract_prompt_field(messages, "session_duration_minutes")
    )

    weekly_schedule = []
    for day_index in range(1, training_days_per_week + 1):
        weekly_schedule.append(
            {
                "day_index": day_index,
                "title": f"Day {day_index} - Fallback Full Body Session",
                "focus": "General fitness movement practice",
                "estimated_duration_minutes": session_duration_minutes,
                "warm_up": [
                    "Walk in place for 5 minutes",
                    "Perform gentle mobility for the hips and shoulders",
                ],
                "exercises": [
                    {
                        "name": "Bodyweight Sit-to-Stand",
                        "category": ExerciseCategory.STRENGTH,
                        "prescription_type": PrescriptionType.REPETITIONS,
                        "sets": 2,
                        "reps_min": 8,
                        "reps_max": 10,
                        "duration_seconds": None,
                        "rest_seconds": 60,
                        "intensity": Intensity.LOW,
                        "target_muscles": ["legs", "glutes"],
                        "instructions": [
                            "Move slowly and keep the range of motion pain free.",
                            "Stop the set early if sharp discomfort appears.",
                        ],
                        "safety_notes": [
                            "Use a chair or support if needed for balance.",
                        ],
                        "alternatives": [
                            "Supported squat to chair",
                        ],
                    },
                    {
                        "name": "Brisk Walk",
                        "category": ExerciseCategory.CARDIO,
                        "prescription_type": PrescriptionType.DURATION,
                        "sets": 1,
                        "reps_min": None,
                        "reps_max": None,
                        "duration_seconds": max((session_duration_minutes - 15) * 60, 900),
                        "rest_seconds": None,
                        "intensity": Intensity.LOW,
                        "target_muscles": ["cardiovascular system"],
                        "instructions": [
                            "Choose a pace that still allows easy conversation.",
                        ],
                        "safety_notes": [
                            "Reduce pace if breathing becomes difficult.",
                        ],
                        "alternatives": [
                            "Stationary cycling",
                        ],
                    },
                ],
                "cool_down": [
                    "Slow walking for 3 minutes",
                    "Gentle breathing and stretching for 2 minutes",
                ],
                "intensity_note": (
                    "Keep effort conservative because this fallback plan is intended to be safe "
                    "and broadly applicable."
                ),
            }
        )

    return WorkoutPlan.model_validate(
        {
            "title": "Fallback General Fitness Plan",
            "summary": (
                "A conservative temporary workout plan returned because the structured model "
                "response could not be validated after retries."
            ),
            "goal": goal,
            "experience_level": experience_level,
            "training_days_per_week": training_days_per_week,
            "duration_weeks": 2,
            "weekly_schedule": weekly_schedule,
            "progression_suggestion": (
                "If all sessions feel comfortable with steady form, add a small amount of time "
                "or one repetition per set in the following week."
            ),
            "safety_warnings": [
                {
                    "code": SafetyWarningCode.FORM_PRIORITY,
                    "severity": WarningSeverity.CAUTION,
                    "message": (
                        "This fallback plan is intentionally conservative and should be kept "
                        "comfortable and pain free."
                    ),
                    "recommended_action": (
                        "Reduce intensity, shorten the session, or stop if symptoms feel unusual."
                    ),
                    "applies_to_exercise": None,
                    "requires_professional_clearance": False,
                }
            ],
        }
    )


def _parse_fitness_goal(value: str | None) -> FitnessGoal:
    if value is None:
        return FitnessGoal.GENERAL_FITNESS

    try:
        return FitnessGoal(value)
    except ValueError:
        return FitnessGoal.GENERAL_FITNESS


def _parse_experience_level(value: str | None) -> ExperienceLevel:
    if value is None:
        return ExperienceLevel.BEGINNER

    try:
        return ExperienceLevel(value)
    except ValueError:
        return ExperienceLevel.BEGINNER


def _parse_training_days_per_week(value: str | None) -> int:
    try:
        parsed = int(value) if value is not None else 3
    except ValueError:
        parsed = 3

    return min(max(parsed, 1), 7)


def _parse_session_duration_minutes(value: str | None) -> int:
    try:
        parsed = int(value) if value is not None else 30
    except ValueError:
        parsed = 30

    return min(max(parsed, 15), 180)
