import httpx
import pytest

from app.core.errors import AppError
from app.core.settings import get_settings
from app.main import create_app
from app.rag.retriever import RetrievedChunk
from app.schemas import WorkoutPlan
from app.services import GenerationDebugContext


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


class FakeGenerator:
    def __init__(self, result: WorkoutPlan | None = None, error: Exception | None = None) -> None:
        self._result = result
        self._error = error
        self._debug_context = GenerationDebugContext(retrieval_query="", retrieved_chunks=[])

    async def generate(self, profile):
        if self._error is not None:
            raise self._error
        return self._result

    def get_last_debug_context(self) -> GenerationDebugContext:
        return self._debug_context


@pytest.fixture(autouse=True)
def clear_settings_cache() -> None:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.mark.anyio
async def test_generate_workout_plan_returns_weekly_schedule() -> None:
    app = create_app()
    app.state.workout_plan_generator = FakeGenerator(
        result=WorkoutPlan.model_validate(valid_plan_payload())
    )

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post("/generate/workout-plan", json=valid_profile_payload())

    assert response.status_code == 200
    body = response.json()
    assert body["training_days_per_week"] == 3
    assert len(body["weekly_schedule"]) == 3


@pytest.mark.anyio
async def test_generate_workout_plan_maps_app_error_to_common_envelope() -> None:
    app = create_app()
    app.state.workout_plan_generator = FakeGenerator(
        error=AppError(
            status_code=503,
            code="OPENAI_CONFIG_MISSING",
            message="The workout generation service is not configured.",
        )
    )

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post("/generate/workout-plan", json=valid_profile_payload())

    assert response.status_code == 503
    body = response.json()
    assert body["error"]["code"] == "OPENAI_CONFIG_MISSING"
    assert body["request_id"]


@pytest.mark.anyio
async def test_generate_workout_plan_validates_request_body() -> None:
    app = create_app()

    invalid_payload = valid_profile_payload()
    invalid_payload["training_days_per_week"] = 0

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post("/generate/workout-plan", json=invalid_payload)

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "REQUEST_VALIDATION_ERROR"
    assert body["request_id"]


@pytest.mark.anyio
async def test_generate_workout_plan_sets_retrieval_debug_headers() -> None:
    app = create_app()
    generator = FakeGenerator(result=WorkoutPlan.model_validate(valid_plan_payload()))
    generator._debug_context = GenerationDebugContext(
        retrieval_query="goal: fat_loss",
        retrieved_chunks=[
            RetrievedChunk(
                chunk_id="doc-1::chunk-000",
                document_id="doc-1",
                title="Warm-up basics",
                topic="warmup",
                text="Start with 5 minutes of easy movement.",
            )
        ],
    )
    app.state.workout_plan_generator = generator

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post("/generate/workout-plan", json=valid_profile_payload())

    assert response.status_code == 200
    assert response.headers["X-RAG-Chunk-Count"] == "1"
    assert response.headers["X-RAG-Chunk-Ids"] == "doc-1::chunk-000"
