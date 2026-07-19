import pytest

from app.rag.retriever import RetrievedChunk
from app.schemas import FeedbackRuntimeMetadata, UserProfile, WorkoutPlan
from app.services import WorkoutPlanGenerator


def valid_profile_payload() -> dict:
    return {
        "goal": "fat_loss",
        "experience_level": "beginner",
        "training_days_per_week": 3,
        "session_duration_minutes": 45,
        "equipment": [
            "bodyweight",
            "dumbbells",
            "resistance_bands",
        ],
        "training_location": "home",
        "injuries_or_limitations": [
            "Occasional knee discomfort when squatting deeply",
        ],
        "exercise_preferences": [
            "Strength training",
            "Low-impact cardio",
        ],
    }


def valid_plan_payload() -> dict:
    return {
        "title": "3-Day Beginner Home Strength Plan",
        "summary": "A low-impact three-day plan for general fitness and fat loss.",
        "goal": "fat_loss",
        "experience_level": "beginner",
        "training_days_per_week": 3,
        "duration_weeks": 4,
        "weekly_schedule": [
            {
                "day_index": 1,
                "title": "Day 1 - Full Body A",
                "focus": "Full-body strength",
                "estimated_duration_minutes": 45,
                "warm_up": ["Walk in place for 5 minutes"],
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
                        "target_muscles": ["quadriceps", "glutes"],
                        "instructions": [
                            "Keep your chest tall.",
                            "Stop if knee pain occurs.",
                        ],
                        "safety_notes": ["Use a pain-free range of motion."],
                        "alternatives": ["Box squat"],
                    }
                ],
                "cool_down": ["Easy stretching for 5 minutes"],
                "intensity_note": "Choose a load that leaves about two reps in reserve.",
            },
            {
                "day_index": 3,
                "title": "Day 2 - Upper Body",
                "focus": "Upper-body strength",
                "estimated_duration_minutes": 45,
                "warm_up": ["Arm circles for 2 minutes"],
                "exercises": [
                    {
                        "name": "Dumbbell Row",
                        "category": "strength",
                        "prescription_type": "repetitions",
                        "sets": 3,
                        "reps_min": 10,
                        "reps_max": 12,
                        "duration_seconds": None,
                        "rest_seconds": 75,
                        "intensity": "moderate",
                        "target_muscles": ["back", "biceps"],
                        "instructions": ["Keep the spine neutral."],
                        "safety_notes": [],
                        "alternatives": ["Resistance band row"],
                    }
                ],
                "cool_down": ["Gentle shoulder stretches"],
                "intensity_note": "Use a controlled tempo.",
            },
            {
                "day_index": 5,
                "title": "Day 3 - Conditioning",
                "focus": "Low-impact conditioning",
                "estimated_duration_minutes": 40,
                "warm_up": ["March in place for 3 minutes"],
                "exercises": [
                    {
                        "name": "Brisk Walk",
                        "category": "cardio",
                        "prescription_type": "duration",
                        "sets": 1,
                        "reps_min": None,
                        "reps_max": None,
                        "duration_seconds": 1200,
                        "rest_seconds": None,
                        "intensity": "low",
                        "target_muscles": ["cardiovascular system"],
                        "instructions": ["Maintain a pace that allows conversation."],
                        "safety_notes": [],
                        "alternatives": [],
                    }
                ],
                "cool_down": ["Easy walking for 5 minutes"],
                "intensity_note": "Stay below breathless effort.",
            },
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


class FakeClient:
    def __init__(self, result: WorkoutPlan) -> None:
        self._result = result
        self.calls: list[list[dict]] = []
        self._last_generation_metadata = FeedbackRuntimeMetadata(
            generated_at="2026-07-14T17:00:00+00:00",
            model_name="gpt-4.1-mini",
            latency_ms=231,
            used_fallback=False,
            retrieved_chunk_count=0,
            retrieved_chunk_ids=[],
            safety_trigger_codes=[],
        )

    async def generate_workout_plan(self, messages: list[dict]) -> WorkoutPlan:
        self.calls.append(messages)
        return self._result

    def get_last_generation_metadata(self) -> FeedbackRuntimeMetadata:
        return self._last_generation_metadata


class FakeRetriever:
    def __init__(
        self, chunks: list[RetrievedChunk] | None = None, error: Exception | None = None
    ) -> None:
        self._chunks = chunks or []
        self._error = error
        self.calls: list[str] = []

    def retrieve(self, query_text: str, *, limit: int | None = None) -> list[RetrievedChunk]:
        self.calls.append(query_text)
        if self._error is not None:
            raise self._error
        return self._chunks


@pytest.mark.asyncio
async def test_generate_returns_client_plan() -> None:
    profile = UserProfile.model_validate(valid_profile_payload())
    plan = WorkoutPlan.model_validate(valid_plan_payload())
    client = FakeClient(plan)
    service = WorkoutPlanGenerator(client)  # type: ignore[arg-type]

    result = await service.generate(profile)

    assert result == plan


@pytest.mark.asyncio
async def test_generate_builds_prompt_and_passes_messages(
    monkeypatch,
) -> None:
    profile = UserProfile.model_validate(valid_profile_payload())
    plan = WorkoutPlan.model_validate(valid_plan_payload())
    client = FakeClient(plan)
    service = WorkoutPlanGenerator(client)  # type: ignore[arg-type]
    expected_messages = [
        {"role": "system", "content": "system"},
        {"role": "user", "content": "user"},
    ]

    def fake_build_workout_plan_prompt(
        received_profile: UserProfile,
        *,
        retrieved_chunks: list[RetrievedChunk] | None = None,
    ) -> list[dict]:
        assert received_profile == profile
        assert retrieved_chunks == []
        return expected_messages

    monkeypatch.setattr(
        "app.services.workout_plan_generator.build_workout_plan_prompt",
        fake_build_workout_plan_prompt,
    )

    result = await service.generate(profile)

    assert result == plan
    assert client.calls == [expected_messages]


@pytest.mark.asyncio
async def test_generate_retrieves_context_and_exposes_debug_state(
    monkeypatch,
) -> None:
    profile = UserProfile.model_validate(valid_profile_payload())
    plan = WorkoutPlan.model_validate(valid_plan_payload())
    client = FakeClient(plan)
    retriever = FakeRetriever(
        chunks=[
            RetrievedChunk(
                chunk_id="doc-1::chunk-000",
                document_id="doc-1",
                title="Warm-up basics",
                topic="warmup",
                text="Start with 5 minutes of easy movement.",
            )
        ]
    )
    service = WorkoutPlanGenerator(client, retriever=retriever)  # type: ignore[arg-type]

    captured_kwargs: dict[str, object] = {}

    def fake_build_workout_plan_prompt(
        received_profile: UserProfile,
        *,
        retrieved_chunks: list[RetrievedChunk] | None = None,
    ) -> list[dict]:
        assert received_profile == profile
        captured_kwargs["retrieved_chunks"] = retrieved_chunks
        return [{"role": "system", "content": "system"}]

    monkeypatch.setattr(
        "app.services.workout_plan_generator.build_workout_plan_prompt",
        fake_build_workout_plan_prompt,
    )

    result = await service.generate(profile)

    assert result == plan
    assert retriever.calls
    assert captured_kwargs["retrieved_chunks"] == retriever._chunks
    debug_context = service.get_last_debug_context()
    assert debug_context.retrieved_chunks == retriever._chunks
    assert "goal: fat_loss" in debug_context.retrieval_query
    runtime_context = service.get_last_runtime_context()
    assert runtime_context.metadata.model_name == "gpt-4.1-mini"
    assert runtime_context.metadata.latency_ms == 231
    assert runtime_context.metadata.retrieved_chunk_count == 1
    assert runtime_context.metadata.retrieved_chunk_ids == ["doc-1::chunk-000"]


@pytest.mark.asyncio
async def test_generate_falls_back_to_prompt_without_context_when_retrieval_fails(
    monkeypatch,
) -> None:
    profile = UserProfile.model_validate(valid_profile_payload())
    plan = WorkoutPlan.model_validate(valid_plan_payload())
    client = FakeClient(plan)
    retriever = FakeRetriever(error=RuntimeError("qdrant unavailable"))
    service = WorkoutPlanGenerator(client, retriever=retriever)  # type: ignore[arg-type]

    captured_kwargs: dict[str, object] = {}

    def fake_build_workout_plan_prompt(
        received_profile: UserProfile,
        *,
        retrieved_chunks: list[RetrievedChunk] | None = None,
    ) -> list[dict]:
        assert received_profile == profile
        captured_kwargs["retrieved_chunks"] = retrieved_chunks
        return [{"role": "system", "content": "system"}]

    monkeypatch.setattr(
        "app.services.workout_plan_generator.build_workout_plan_prompt",
        fake_build_workout_plan_prompt,
    )

    result = await service.generate(profile)

    assert result == plan
    assert captured_kwargs["retrieved_chunks"] == []
    runtime_context = service.get_last_runtime_context()
    assert runtime_context.metadata.retrieved_chunk_count == 0
