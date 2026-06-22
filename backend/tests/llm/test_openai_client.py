import importlib
from collections.abc import Sequence
from types import SimpleNamespace

import pytest
from openai import APITimeoutError, OpenAIError

from app.core.errors import AppError
from app.core.settings import Settings
from app.llm.openai_client import OpenAIWorkoutPlanClient
from app.main import create_app
from app.schemas import WorkoutPlan


def valid_plan_payload() -> dict:
    return {
        "title": "3-Day Beginner Home Strength Plan",
        "summary": "A low-impact three-day plan for general fitness and fat loss.",
        "goal": "fat_loss",
        "experience_level": "beginner",
        "training_days_per_week": 1,
        "duration_weeks": 4,
        "weekly_schedule": [
            {
                "day_index": 1,
                "title": "Day 1 - Full Body A",
                "focus": "Full-body strength",
                "estimated_duration_minutes": 45,
                "warm_up": [
                    "Walk in place for 5 minutes",
                ],
                "exercises": [
                    {
                        "name": "Goblet Squat",
                        "category": "strength",
                        "prescription_type": "repetitions",
                        "sets": 3,
                        "reps_min": 8,
                        "reps_max": 10,
                        "duration_seconds": None,
                        "rest_seconds": 90,
                        "intensity": "moderate",
                        "target_muscles": [
                            "quadriceps",
                            "glutes",
                        ],
                        "instructions": [
                            "Keep your chest tall.",
                            "Stop if knee pain occurs.",
                        ],
                        "safety_notes": [
                            "Use a pain-free range of motion.",
                        ],
                        "alternatives": [
                            "Box squat",
                        ],
                    }
                ],
                "cool_down": [
                    "Easy stretching for 5 minutes",
                ],
                "intensity_note": "Choose a load that leaves about two reps in reserve.",
            }
        ],
        "progression_suggestion": (
            "When all sets feel comfortable with good form, add one repetition "
            "per set before increasing load."
        ),
        "safety_warnings": [
            {
                "code": "form_priority",
                "severity": "caution",
                "message": "Keep controlled form; stop the movement if sharp pain occurs.",
                "recommended_action": "Reduce range of motion or choose the listed alternative.",
                "applies_to_exercise": None,
                "requires_professional_clearance": False,
            }
        ],
    }


def sample_messages() -> list[dict]:
    return [
        {
            "role": "system",
            "content": "Follow the WorkoutPlan schema exactly.",
        },
        {
            "role": "user",
            "content": (
                "goal: fat_loss\n"
                "experience_level: beginner\n"
                "training_days_per_week: 3\n"
                "session_duration_minutes: 45\n"
                "equipment: bodyweight, dumbbells"
            ),
        },
    ]


class FakeResponses:
    def __init__(
        self,
        result=None,
        error: Exception | None = None,
        sequence: Sequence[object] | None = None,
    ) -> None:
        self._result = result
        self._error = error
        self._sequence = list(sequence) if sequence is not None else None
        self.calls: list[dict] = []

    async def parse(self, **kwargs):
        self.calls.append(kwargs)
        if self._sequence is not None:
            item = self._sequence.pop(0)
            if isinstance(item, Exception):
                raise item
            return item

        if self._error is not None:
            raise self._error
        return self._result


class FakeAsyncClient:
    def __init__(
        self,
        result=None,
        error: Exception | None = None,
        sequence: Sequence[object] | None = None,
    ) -> None:
        self.responses = FakeResponses(result=result, error=error, sequence=sequence)


def test_openai_client_module_import_is_safe_without_env() -> None:
    module = importlib.import_module("app.llm.openai_client")
    settings = Settings(_env_file=None)

    client = module.OpenAIWorkoutPlanClient(settings)

    assert client is not None


def test_create_app_import_is_safe_without_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)

    app = create_app()

    assert app.state.workout_plan_generator is not None


def test_get_client_requires_api_key() -> None:
    client = OpenAIWorkoutPlanClient(
        Settings(
            _env_file=None,
            openai_api_key=None,
            openai_model="gpt-4.1-mini",
        )
    )

    with pytest.raises(AppError) as exc_info:
        client._get_client()

    assert exc_info.value.status_code == 503
    assert exc_info.value.code == "OPENAI_CONFIG_MISSING"


def test_get_client_requires_model() -> None:
    client = OpenAIWorkoutPlanClient(
        Settings(
            _env_file=None,
            openai_api_key="test-key",
            openai_model=None,
        )
    )

    with pytest.raises(AppError) as exc_info:
        client._get_client()

    assert exc_info.value.status_code == 503
    assert exc_info.value.code == "OPENAI_CONFIG_MISSING"


@pytest.mark.asyncio
async def test_generate_workout_plan_revalidates_parsed_model_instance() -> None:
    parsed_plan = WorkoutPlan.model_validate(valid_plan_payload())
    fake_client = FakeAsyncClient(
        result=SimpleNamespace(
            output=[],
            output_parsed=parsed_plan,
        )
    )

    client = OpenAIWorkoutPlanClient(
        Settings(
            _env_file=None,
            openai_api_key="test-key",
            openai_model="gpt-4.1-mini",
        )
    )
    client._client = fake_client

    plan = await client.generate_workout_plan(sample_messages())

    assert isinstance(plan, WorkoutPlan)
    assert plan.title == parsed_plan.title


@pytest.mark.asyncio
async def test_generate_workout_plan_rejects_refusal() -> None:
    fake_client = FakeAsyncClient(
        result=SimpleNamespace(
            output=[
                SimpleNamespace(
                    type="message",
                    content=[
                        SimpleNamespace(
                            type="refusal",
                            refusal="I can't comply.",
                        )
                    ],
                )
            ],
            output_parsed=None,
        )
    )

    client = OpenAIWorkoutPlanClient(
        Settings(
            _env_file=None,
            openai_api_key="test-key",
            openai_model="gpt-4.1-mini",
        )
    )
    client._client = fake_client

    with pytest.raises(AppError) as exc_info:
        await client.generate_workout_plan(sample_messages())

    assert exc_info.value.status_code == 502
    assert exc_info.value.code == "OPENAI_REFUSAL"


@pytest.mark.asyncio
async def test_generate_workout_plan_retries_invalid_output_then_returns_fallback() -> None:
    fake_client = FakeAsyncClient(
        sequence=[
            SimpleNamespace(output=[], output_parsed=None),
            SimpleNamespace(output=[], output_parsed=None),
            SimpleNamespace(output=[], output_parsed=None),
        ]
    )

    client = OpenAIWorkoutPlanClient(
        Settings(
            _env_file=None,
            openai_api_key="test-key",
            openai_model="gpt-4.1-mini",
        )
    )
    client._client = fake_client

    plan = await client.generate_workout_plan(sample_messages())

    assert plan.title == "Fallback General Fitness Plan"
    assert plan.training_days_per_week == 3
    assert len(plan.weekly_schedule) == 3


@pytest.mark.asyncio
async def test_generate_workout_plan_maps_sdk_errors_to_app_error() -> None:
    fake_client = FakeAsyncClient(error=OpenAIError("boom"))

    client = OpenAIWorkoutPlanClient(
        Settings(
            _env_file=None,
            openai_api_key="test-key",
            openai_model="gpt-4.1-mini",
        )
    )
    client._client = fake_client

    with pytest.raises(AppError) as exc_info:
        await client.generate_workout_plan(sample_messages())

    assert exc_info.value.status_code == 502
    assert exc_info.value.code == "OPENAI_REQUEST_FAILED"


@pytest.mark.asyncio
async def test_generate_workout_plan_retries_invalid_parsed_data_then_succeeds() -> None:
    invalid_payload = valid_plan_payload()
    del invalid_payload["title"]

    fake_client = FakeAsyncClient(
        sequence=[
            SimpleNamespace(output=[], output_parsed=invalid_payload),
            SimpleNamespace(
                output=[],
                output_parsed=WorkoutPlan.model_validate(valid_plan_payload()),
            ),
        ]
    )

    client = OpenAIWorkoutPlanClient(
        Settings(
            _env_file=None,
            openai_api_key="test-key",
            openai_model="gpt-4.1-mini",
        )
    )
    client._client = fake_client

    plan = await client.generate_workout_plan(sample_messages())

    assert plan.title == "3-Day Beginner Home Strength Plan"


@pytest.mark.asyncio
async def test_generate_workout_plan_maps_timeout_to_app_error() -> None:
    fake_client = FakeAsyncClient(error=APITimeoutError(request=None))

    client = OpenAIWorkoutPlanClient(
        Settings(
            _env_file=None,
            openai_api_key="test-key",
            openai_model="gpt-4.1-mini",
            openai_timeout_seconds=7.5,
        )
    )
    client._client = fake_client

    with pytest.raises(AppError) as exc_info:
        await client.generate_workout_plan(sample_messages())

    assert exc_info.value.status_code == 504
    assert exc_info.value.code == "OPENAI_TIMEOUT"
