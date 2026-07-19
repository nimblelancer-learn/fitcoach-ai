import httpx
import pytest

from app.core.errors import AppError
from app.core.settings import get_settings
from app.feedback.store import StoredFeedback
from app.main import create_app
from app.rag.retriever import RetrievedChunk
from app.schemas import FeedbackRuntimeMetadata, PlanFeedback, UserProfile, WorkoutPlan
from app.services import GenerationDebugContext, GenerationRuntimeContext


def valid_form_payload() -> dict[str, object]:
    return {
        "goal": "fat_loss",
        "experience_level": "beginner",
        "training_days_per_week": "3",
        "session_duration_minutes": "45",
        "equipment": ["bodyweight", "dumbbells"],
        "training_location": "home",
        "injuries_or_limitations_text": "Occasional knee discomfort",
        "exercise_preferences_text": "Strength training\nLow-impact cardio",
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
                        "instructions": ["Keep your chest tall.", "Stop if knee pain occurs."],
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
        self._runtime_context = GenerationRuntimeContext(
            metadata=FeedbackRuntimeMetadata(
                generated_at="2026-07-14T17:00:00+00:00",
                model_name="gpt-4.1-mini",
                latency_ms=231,
                used_fallback=False,
                retrieved_chunk_count=0,
                retrieved_chunk_ids=[],
                safety_trigger_codes=[],
                trace_id=None,
                trace_enabled=False,
                langfuse_host=None,
            )
        )

    async def generate(self, profile):
        if self._error is not None:
            raise self._error
        return self._result

    def get_last_debug_context(self) -> GenerationDebugContext:
        return self._debug_context

    def get_last_runtime_context(self) -> GenerationRuntimeContext:
        return self._runtime_context


class FakeFeedbackStore:
    def __init__(self) -> None:
        self.saved_payload: dict[str, object] | None = None
        self.recent_feedback: list[StoredFeedback] = []

    def save_feedback(
        self,
        *,
        request_id: str,
        profile: UserProfile,
        workout_plan: WorkoutPlan,
        feedback: PlanFeedback,
        runtime_metadata: FeedbackRuntimeMetadata,
    ) -> None:
        self.saved_payload = {
            "request_id": request_id,
            "profile": profile,
            "workout_plan": workout_plan,
            "feedback": feedback,
            "runtime_metadata": runtime_metadata,
        }

    def list_recent_feedback(self, *, limit: int = 20) -> list[StoredFeedback]:
        return self.recent_feedback[:limit]


@pytest.fixture(autouse=True)
def clear_settings_cache() -> None:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.mark.anyio
async def test_home_page_renders_demo_form() -> None:
    response = await _request("GET", "/")

    assert response.status_code == 200
    assert "Tạo kế hoạch tập luyện trong một luồng đơn giản." in response.text
    assert "Nhập hồ sơ tập luyện" in response.text
    assert "Tạo kế hoạch tập luyện" in response.text
    assert "Nhập bằng tiếng Anh ngắn gọn." in response.text
    assert "Occasional knee discomfort" in response.text
    assert "Strength training" in response.text


@pytest.mark.anyio
async def test_home_form_submission_renders_generated_plan() -> None:
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
        response = await client.post("/", data=valid_form_payload())

    assert response.status_code == 200
    assert "Kế hoạch đã sẵn sàng." in response.text
    assert "3-Day Beginner Home Strength Plan" in response.text
    assert "doc-1::chunk-000" in response.text
    assert "Day 1 - Full Body A" in response.text
    assert "Lưu phản hồi" in response.text
    assert "Nội dung kế hoạch hiện vẫn ở tiếng Anh" in response.text
    assert 'name="runtime_metadata_json"' in response.text


@pytest.mark.anyio
async def test_home_form_submission_renders_validation_errors() -> None:
    payload = valid_form_payload()
    payload["equipment"] = []
    payload["training_days_per_week"] = "0"

    response = await _request("POST", "/", data=payload)

    assert response.status_code == 200
    assert "Vui lòng kiểm tra lại các thông tin bên dưới." in response.text
    assert "training_days_per_week: Input should be greater than or equal to 1" in response.text
    assert "equipment: List should have at least 1 item after validation, not 0" in response.text


@pytest.mark.anyio
async def test_home_form_submission_renders_service_error() -> None:
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
        response = await client.post("/", data=valid_form_payload())

    assert response.status_code == 200
    assert "Hiện chưa thể tạo kế hoạch." in response.text
    assert "The workout generation service is not configured." in response.text


@pytest.mark.anyio
async def test_feedback_submission_persists_feedback_and_renders_confirmation() -> None:
    app = create_app()
    feedback_store = FakeFeedbackStore()
    app.state.feedback_store = feedback_store

    profile = UserProfile.model_validate(
        {
            "goal": "fat_loss",
            "experience_level": "beginner",
            "training_days_per_week": 3,
            "session_duration_minutes": 45,
            "equipment": ["bodyweight", "dumbbells"],
            "training_location": "home",
            "injuries_or_limitations": ["Occasional knee discomfort"],
            "exercise_preferences": ["Strength training", "Low-impact cardio"],
        }
    )
    plan = WorkoutPlan.model_validate(valid_plan_payload())

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/feedback",
            data={
                "request_id": "req-123",
                "profile_snapshot_json": profile.model_dump_json(),
                "generated_plan_json": plan.model_dump_json(),
                "runtime_metadata_json": FeedbackRuntimeMetadata(
                    generated_at="2026-07-14T17:00:00+00:00",
                    model_name="gpt-4.1-mini",
                    latency_ms=231,
                    used_fallback=False,
                    retrieved_chunk_count=1,
                    retrieved_chunk_ids=["doc-1::chunk-000"],
                    safety_trigger_codes=[],
                    trace_id="req-123",
                    trace_enabled=True,
                    langfuse_host="https://cloud.langfuse.com",
                ).model_dump_json(),
                "usefulness_rating": "5",
                "difficulty_feedback": "about_right",
                "felt_safe": "true",
                "would_follow_plan": "true",
                "feedback_text": "The plan felt realistic and easy to follow.",
            },
        )

    assert response.status_code == 200
    assert "Đã ghi nhận phản hồi." in response.text
    assert "bằng chứng người dùng thật" in response.text
    assert feedback_store.saved_payload is not None
    assert feedback_store.saved_payload["request_id"] == "req-123"
    assert feedback_store.saved_payload["profile"] == profile
    assert feedback_store.saved_payload["workout_plan"] == plan
    assert feedback_store.saved_payload["feedback"] == PlanFeedback.model_validate(
        {
            "usefulness_rating": 5,
            "difficulty_feedback": "about_right",
            "felt_safe": True,
            "would_follow_plan": True,
            "feedback_text": "The plan felt realistic and easy to follow.",
        }
    )
    assert feedback_store.saved_payload["runtime_metadata"] == FeedbackRuntimeMetadata(
        generated_at="2026-07-14T17:00:00+00:00",
        model_name="gpt-4.1-mini",
        latency_ms=231,
        used_fallback=False,
        retrieved_chunk_count=1,
        retrieved_chunk_ids=["doc-1::chunk-000"],
        safety_trigger_codes=[],
        trace_id="req-123",
        trace_enabled=True,
        langfuse_host="https://cloud.langfuse.com",
    )


@pytest.mark.anyio
async def test_feedback_review_page_renders_attention_metadata() -> None:
    app = create_app()
    feedback_store = FakeFeedbackStore()
    app.state.feedback_store = feedback_store

    feedback_store.recent_feedback = [
        StoredFeedback(
            feedback_id=7,
            created_at="2026-07-14T17:15:00+00:00",
            request_id="req-review-7",
            profile=UserProfile.model_validate(
                {
                    "goal": "fat_loss",
                    "experience_level": "beginner",
                    "training_days_per_week": 3,
                    "session_duration_minutes": 45,
                    "equipment": ["bodyweight"],
                    "training_location": "home",
                    "injuries_or_limitations": ["Occasional knee discomfort"],
                    "exercise_preferences": ["Strength training"],
                }
            ),
            workout_plan=WorkoutPlan.model_validate(valid_plan_payload()),
            feedback=PlanFeedback.model_validate(
                {
                    "usefulness_rating": 2,
                    "difficulty_feedback": "too_hard",
                    "felt_safe": False,
                    "would_follow_plan": False,
                    "feedback_text": "Too hard and not confidence-inspiring.",
                }
            ),
            runtime_metadata=FeedbackRuntimeMetadata(
                generated_at="2026-07-14T17:10:00+00:00",
                model_name="gpt-4.1-mini",
                latency_ms=544,
                used_fallback=True,
                retrieved_chunk_count=0,
                retrieved_chunk_ids=[],
                safety_trigger_codes=["medical_keyword:chest pain"],
                trace_id="req-review-7",
                trace_enabled=True,
                langfuse_host="https://cloud.langfuse.com",
            ),
        )
    ]

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get("/feedback/review?signal=attention")

    assert response.status_code == 200
    assert "req-review-7" in response.text
    assert "Too hard and not confidence-inspiring." in response.text
    assert "weak_retrieval" in response.text
    assert "medical_keyword:chest pain" in response.text
    assert "Fallback" in response.text
    assert "req-review-7" in response.text
    assert "Langfuse configured via https://cloud.langfuse.com" in response.text


async def _request(method: str, path: str, data: dict[str, object] | None = None) -> httpx.Response:
    app = create_app()
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        return await client.request(method, path, data=data)
