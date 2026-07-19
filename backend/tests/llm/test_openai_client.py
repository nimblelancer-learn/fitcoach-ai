import importlib
from collections.abc import Sequence
from types import SimpleNamespace

import pytest

from app.core.errors import AppError
from app.core.settings import Settings
from app.llm import openai_client as openai_client_module
from app.llm.openai_client import OpenAIWorkoutPlanClient
from app.llm.pricing import (
    estimate_request_cost_from_pricing_usd,
    estimate_request_cost_usd,
)
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
                "goal: fat_loss\ntraining_days_per_week: 3\nequipment: bodyweight, dumbbells"
            ),
        },
    ]


def medical_risk_messages() -> list[dict]:
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
                "injuries_or_limitations: chest pain after exercise"
            ),
        },
    ]


def mild_injury_messages() -> list[dict]:
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
                "injuries_or_limitations: occasional knee discomfort when squatting deeply"
            ),
        },
    ]


def rehab_risk_messages() -> list[dict]:
    return [
        {
            "role": "system",
            "content": "Follow the WorkoutPlan schema exactly.",
        },
        {
            "role": "user",
            "content": (
                "goal: general_fitness\n"
                "experience_level: beginner\n"
                "training_days_per_week: 2\n"
                "injuries_or_limitations: need a rehabilitation plan after fracture"
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


def test_get_client_lazy_initializes_once(monkeypatch: pytest.MonkeyPatch) -> None:
    created_clients = []

    def fake_async_openai(*, api_key: str):
        created_clients.append(api_key)
        return SimpleNamespace(api_key=api_key)

    monkeypatch.setattr("app.llm.openai_client.AsyncOpenAI", fake_async_openai)

    client = OpenAIWorkoutPlanClient(
        Settings(
            _env_file=None,
            openai_api_key="test-key",
            openai_model="gpt-4.1-mini",
        )
    )

    first = client._get_client()
    second = client._get_client()

    assert first is second
    assert created_clients == ["test-key"]


@pytest.mark.asyncio
async def test_generate_workout_plan_revalidates_parsed_model_instance() -> None:
    parsed_plan = WorkoutPlan.model_validate(valid_plan_payload())
    fake_client = FakeAsyncClient(
        result=SimpleNamespace(
            model="gpt-4.1-mini",
            output=[],
            output_parsed=parsed_plan,
            usage=SimpleNamespace(input_tokens=120, output_tokens=240, total_tokens=360),
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
    metadata = client.get_last_generation_metadata()
    assert metadata.model_name == "gpt-4.1-mini"
    assert metadata.used_fallback is False
    assert metadata.safety_trigger_codes == []
    assert metadata.generated_at is not None
    assert metadata.latency_ms >= 0
    assert fake_client.responses.calls == [
        {
            "model": "gpt-4.1-mini",
            "input": sample_messages(),
            "text_format": WorkoutPlan,
            "timeout": 20.0,
        }
    ]


@pytest.mark.asyncio
async def test_generate_workout_plan_rejects_refusal() -> None:
    fake_client = FakeAsyncClient(
        result=SimpleNamespace(
            model="gpt-4.1-mini",
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
            usage=None,
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
async def test_generate_workout_plan_rejects_missing_parsed_output() -> None:
    fake_client = FakeAsyncClient(
        sequence=[
            SimpleNamespace(output=[], output_parsed=None, usage=None),
            SimpleNamespace(output=[], output_parsed=None, usage=None),
            SimpleNamespace(output=[], output_parsed=None, usage=None),
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
    assert len(fake_client.responses.calls) == 3
    metadata = client.get_last_generation_metadata()
    assert metadata.used_fallback is True
    assert metadata.safety_trigger_codes == []


@pytest.mark.asyncio
async def test_generate_workout_plan_short_circuits_medical_keyword_triggers(
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level("WARNING")
    fake_client = FakeAsyncClient(
        result=SimpleNamespace(
            model="gpt-4.1-mini",
            output=[],
            output_parsed=WorkoutPlan.model_validate(valid_plan_payload()),
            usage=None,
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

    plan = await client.generate_workout_plan(medical_risk_messages())

    assert plan.title == "Safety-First Fallback Plan"
    assert plan.safety_warnings[0].code.value == "medical_referral"
    assert plan.safety_warnings[0].requires_professional_clearance is True
    assert fake_client.responses.calls == []
    assert "workout_plan_safety_trigger" in caplog.text
    assert "medical_keyword:chest pain" in caplog.text
    metadata = client.get_last_generation_metadata()
    assert metadata.used_fallback is True
    assert metadata.safety_trigger_codes == ["medical_keyword:chest pain"]


@pytest.mark.asyncio
async def test_generate_workout_plan_allows_mild_injury_limitations() -> None:
    fake_client = FakeAsyncClient(
        result=SimpleNamespace(
            model="gpt-4.1-mini",
            output=[],
            output_parsed=WorkoutPlan.model_validate(valid_plan_payload()),
            usage=None,
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

    plan = await client.generate_workout_plan(mild_injury_messages())

    assert plan.title == "3-Day Beginner Home Strength Plan"
    assert len(fake_client.responses.calls) == 1


@pytest.mark.asyncio
async def test_generate_workout_plan_short_circuits_rehabilitation_medical_risk() -> None:
    fake_client = FakeAsyncClient(
        result=SimpleNamespace(
            model="gpt-4.1-mini",
            output=[],
            output_parsed=WorkoutPlan.model_validate(valid_plan_payload()),
            usage=None,
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

    plan = await client.generate_workout_plan(rehab_risk_messages())

    assert plan.title == "Safety-First Fallback Plan"
    assert plan.training_days_per_week == 2
    assert fake_client.responses.calls == []
    assert "medical_keyword:rehabilitation" in plan.safety_warnings[0].message
    assert "medical_keyword:fracture" in plan.safety_warnings[0].message


@pytest.mark.asyncio
async def test_generate_workout_plan_maps_sdk_errors_to_app_error() -> None:
    fake_client = FakeAsyncClient(error=openai_client_module.OpenAIError("boom"))

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
async def test_generate_workout_plan_maps_invalid_parsed_data_to_app_error() -> None:
    invalid_payload = valid_plan_payload()
    del invalid_payload["title"]

    fake_client = FakeAsyncClient(
        sequence=[
            SimpleNamespace(output=[], output_parsed=invalid_payload, usage=None),
            SimpleNamespace(
                output=[],
                output_parsed=WorkoutPlan.model_validate(valid_plan_payload()),
                usage=None,
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
    assert len(fake_client.responses.calls) == 2


@pytest.mark.asyncio
async def test_generate_workout_plan_maps_timeout_to_app_error() -> None:
    fake_client = FakeAsyncClient(error=TimeoutError("timeout"))

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


@pytest.mark.asyncio
async def test_generate_workout_plan_logs_usage_metrics(
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level("INFO")

    fake_client = FakeAsyncClient(
        result=SimpleNamespace(
            model="gpt-4.1-mini",
            output=[],
            output_parsed=WorkoutPlan.model_validate(valid_plan_payload()),
            usage=SimpleNamespace(input_tokens=1000, output_tokens=500, total_tokens=1500),
        )
    )
    client = OpenAIWorkoutPlanClient(
        Settings(
            _env_file=None,
            openai_api_key="test-key",
            openai_model="gpt-4.1-mini",
            openai_input_cost_per_million_tokens_usd=0.5,
            openai_output_cost_per_million_tokens_usd=1.5,
        )
    )
    client._client = fake_client

    await client.generate_workout_plan(sample_messages())

    assert "openai_workout_plan_response" in caplog.text
    assert "input_tokens=1000" in caplog.text
    assert "output_tokens=500" in caplog.text
    assert "estimated_cost_usd=0.00125000" in caplog.text


@pytest.mark.asyncio
async def test_generate_workout_plan_replaces_high_intensity_beginner_plan_with_safety_fallback(
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level("WARNING")
    unsafe_payload = valid_plan_payload()
    unsafe_payload["weekly_schedule"][0]["exercises"][0]["intensity"] = "high"
    fake_client = FakeAsyncClient(
        result=SimpleNamespace(
            model="gpt-4.1-mini",
            output=[],
            output_parsed=unsafe_payload,
            usage=None,
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

    assert plan.title == "Safety-First Fallback Plan"
    assert "beginner_intensity:high" in plan.safety_warnings[0].message
    assert "workout_plan_safety_trigger" in caplog.text
    metadata = client.get_last_generation_metadata()
    assert metadata.used_fallback is True
    assert metadata.safety_trigger_codes == ["beginner_intensity:high"]


@pytest.mark.asyncio
async def test_generate_workout_plan_keeps_non_beginner_high_intensity_plan() -> None:
    unsafe_payload = valid_plan_payload()
    unsafe_payload["experience_level"] = "intermediate"
    unsafe_payload["weekly_schedule"][0]["exercises"][0]["intensity"] = "high"
    unsafe_payload["weekly_schedule"][0]["exercises"][0]["name"] = "Barbell Snatch"
    fake_client = FakeAsyncClient(
        result=SimpleNamespace(
            model="gpt-4.1-mini",
            output=[],
            output_parsed=unsafe_payload,
            usage=None,
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

    assert plan.title == "3-Day Beginner Home Strength Plan"
    assert plan.experience_level.value == "intermediate"


@pytest.mark.asyncio
async def test_generate_workout_plan_replaces_unsafe_exercise_with_safety_fallback() -> None:
    unsafe_payload = valid_plan_payload()
    unsafe_payload["weekly_schedule"][0]["exercises"][0]["name"] = "Barbell Snatch"
    fake_client = FakeAsyncClient(
        result=SimpleNamespace(
            model="gpt-4.1-mini",
            output=[],
            output_parsed=unsafe_payload,
            usage=None,
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

    assert plan.title == "Safety-First Fallback Plan"
    assert "unsafe_exercise:barbell snatch" in plan.safety_warnings[0].message


@pytest.mark.asyncio
async def test_generate_workout_plan_safety_fallback_has_expected_placeholder_shape() -> None:
    fake_client = FakeAsyncClient(
        result=SimpleNamespace(
            model="gpt-4.1-mini",
            output=[],
            output_parsed=WorkoutPlan.model_validate(valid_plan_payload()),
            usage=None,
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

    plan = await client.generate_workout_plan(medical_risk_messages())

    assert plan.duration_weeks == 1
    assert len(plan.weekly_schedule) == 3
    assert plan.weekly_schedule[0].title == "Day 1 - Safety-First Recovery Session"
    assert plan.weekly_schedule[0].estimated_duration_minutes == 15
    assert plan.weekly_schedule[0].exercises[0].name == "Easy Walk"
    assert plan.safety_warnings[0].code.value == "medical_referral"
    assert plan.safety_warnings[0].recommended_action.startswith("Pause normal training")
    assert plan.progression_suggestion.startswith("Do not progress training")
    assert fake_client.responses.calls == []


@pytest.mark.asyncio
async def test_generate_workout_plan_logs_unavailable_cost_when_model_pricing_missing(
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level("INFO")

    fake_client = FakeAsyncClient(
        result=SimpleNamespace(
            model="custom-model",
            output=[],
            output_parsed=WorkoutPlan.model_validate(valid_plan_payload()),
            usage=SimpleNamespace(input_tokens=100, output_tokens=50, total_tokens=None),
        )
    )
    client = OpenAIWorkoutPlanClient(
        Settings(
            _env_file=None,
            openai_api_key="test-key",
            openai_model="custom-model",
        )
    )
    client._client = fake_client

    await client.generate_workout_plan(sample_messages())

    assert "estimated_cost_usd=unavailable" in caplog.text
    assert "total_tokens=150" in caplog.text


def test_estimate_request_cost_usd_returns_none_for_unknown_model() -> None:
    assert (
        estimate_request_cost_usd(
            "unknown-model",
            input_tokens=1000,
            output_tokens=500,
        )
        is None
    )


def test_estimate_request_cost_from_pricing_usd_uses_token_counts() -> None:
    cost = estimate_request_cost_from_pricing_usd(
        input_tokens=1000,
        output_tokens=500,
        input_per_million_tokens_usd=0.5,
        output_per_million_tokens_usd=1.5,
    )

    assert cost == pytest.approx(0.00125)
