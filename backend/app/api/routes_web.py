from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Form, Query, Request
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from app.core.errors import AppError
from app.feedback import FeedbackStore, StoredFeedback
from app.schemas import (
    DifficultyFeedback,
    Equipment,
    ExperienceLevel,
    FeedbackRuntimeMetadata,
    FitnessGoal,
    PlanFeedback,
    TrainingLocation,
    UserProfile,
    WorkoutPlan,
)
from app.services import GenerationDebugContext, WorkoutPlanGenerator

router = APIRouter(tags=["Web"])

templates = Jinja2Templates(
    directory=str(
        Path(__file__).resolve().parent.parent / "web" / "templates",
    ),
)


def _format_label(value: str) -> str:
    return value.replace("_", " ").title()


UI_LABELS = {
    FitnessGoal.FAT_LOSS.value: "Giảm mỡ",
    FitnessGoal.MUSCLE_GAIN.value: "Tăng cơ",
    FitnessGoal.GENERAL_FITNESS.value: "Thể lực tổng quát",
    FitnessGoal.ENDURANCE.value: "Sức bền",
    ExperienceLevel.BEGINNER.value: "Người mới",
    ExperienceLevel.INTERMEDIATE.value: "Trung cấp",
    TrainingLocation.HOME.value: "Ở nhà",
    TrainingLocation.GYM.value: "Phòng gym",
    TrainingLocation.OUTDOORS.value: "Ngoài trời",
    TrainingLocation.MIXED.value: "Kết hợp",
    Equipment.BODYWEIGHT.value: "Trọng lượng cơ thể",
    Equipment.DUMBBELLS.value: "Tạ tay",
    Equipment.RESISTANCE_BANDS.value: "Dây kháng lực",
    Equipment.KETTLEBELL.value: "Kettlebell",
    Equipment.BARBELL.value: "Barbell",
    Equipment.MACHINES.value: "Machines",
    Equipment.FULL_GYM.value: "Phòng gym đầy đủ",
    DifficultyFeedback.TOO_EASY.value: "Quá dễ",
    DifficultyFeedback.ABOUT_RIGHT.value: "Vừa sức",
    DifficultyFeedback.TOO_HARD.value: "Quá khó",
}


def _build_choice_items(
    enum_cls: type[FitnessGoal | ExperienceLevel | TrainingLocation | Equipment],
) -> list[dict[str, str]]:
    return [
        {"value": item.value, "label": UI_LABELS.get(item.value, _format_label(item.value))}
        for item in enum_cls
    ]


GOAL_CHOICES = _build_choice_items(FitnessGoal)
EXPERIENCE_CHOICES = _build_choice_items(ExperienceLevel)
LOCATION_CHOICES = _build_choice_items(TrainingLocation)
EQUIPMENT_CHOICES = _build_choice_items(Equipment)


def _default_form_state() -> dict[str, object]:
    return {
        "goal": FitnessGoal.GENERAL_FITNESS.value,
        "experience_level": ExperienceLevel.BEGINNER.value,
        "training_days_per_week": 3,
        "session_duration_minutes": 45,
        "equipment": [Equipment.BODYWEIGHT.value, Equipment.DUMBBELLS.value],
        "training_location": TrainingLocation.HOME.value,
        "injuries_or_limitations_text": "",
        "exercise_preferences_text": "Strength training\nLow-impact cardio",
    }


def _form_state_from_profile(profile: UserProfile) -> dict[str, object]:
    return {
        "goal": profile.goal.value,
        "experience_level": profile.experience_level.value,
        "training_days_per_week": profile.training_days_per_week,
        "session_duration_minutes": profile.session_duration_minutes,
        "equipment": [item.value for item in profile.equipment],
        "training_location": profile.training_location.value,
        "injuries_or_limitations_text": "\n".join(profile.injuries_or_limitations),
        "exercise_preferences_text": "\n".join(profile.exercise_preferences),
    }


def _parse_multiline_text(raw_text: str) -> list[str]:
    return [line.strip() for line in raw_text.splitlines() if line.strip()]


def _field_errors_from_validation(exc: ValidationError) -> list[str]:
    messages: list[str] = []
    for error in exc.errors():
        location = " -> ".join(str(item) for item in error["loc"])
        messages.append(f"{location}: {error['msg']}")
    return messages


def _render_home(
    request: Request,
    *,
    form_state: dict[str, object],
    validation_errors: list[str] | None = None,
    service_error: str | None = None,
    generated_plan=None,
    debug_context: GenerationDebugContext | None = None,
    feedback_success: str | None = None,
    feedback_error: str | None = None,
    profile_snapshot_json: str | None = None,
    runtime_metadata_json: str | None = None,
):
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "goal_choices": GOAL_CHOICES,
            "experience_choices": EXPERIENCE_CHOICES,
            "location_choices": LOCATION_CHOICES,
            "equipment_choices": EQUIPMENT_CHOICES,
            "form_state": form_state,
            "validation_errors": validation_errors or [],
            "service_error": service_error,
            "generated_plan": generated_plan,
            "debug_context": debug_context or GenerationDebugContext("", []),
            "difficulty_feedback_choices": [
                {
                    "value": DifficultyFeedback.TOO_EASY.value,
                    "label": UI_LABELS[DifficultyFeedback.TOO_EASY.value],
                },
                {
                    "value": DifficultyFeedback.ABOUT_RIGHT.value,
                    "label": UI_LABELS[DifficultyFeedback.ABOUT_RIGHT.value],
                },
                {
                    "value": DifficultyFeedback.TOO_HARD.value,
                    "label": UI_LABELS[DifficultyFeedback.TOO_HARD.value],
                },
            ],
            "feedback_success": feedback_success,
            "feedback_error": feedback_error,
            "profile_snapshot_json": profile_snapshot_json,
            "runtime_metadata_json": runtime_metadata_json,
        },
    )


def _feedback_attention_reasons(item: StoredFeedback) -> list[str]:
    reasons: list[str] = []
    if item.runtime_metadata.used_fallback:
        reasons.append("fallback")
    if item.runtime_metadata.retrieved_chunk_count == 0:
        reasons.append("weak_retrieval")
    if item.feedback.usefulness_rating <= 2:
        reasons.append("low_rating")
    if not item.feedback.felt_safe:
        reasons.append("unsafe")
    if not item.feedback.would_follow_plan:
        reasons.append("won't_follow")
    return reasons


def _build_feedback_review_items(records: list[StoredFeedback]) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    for item in records:
        attention_reasons = _feedback_attention_reasons(item)
        items.append(
            {
                "feedback_id": item.feedback_id,
                "created_at": item.created_at,
                "request_id": item.request_id,
                "plan_title": item.workout_plan.title,
                "profile_summary": (
                    f"{UI_LABELS.get(item.profile.goal.value, item.profile.goal.value)} · "
                    f"{item.profile.training_days_per_week} buổi/tuần · "
                    f"{item.profile.session_duration_minutes} phút"
                ),
                "feedback": item.feedback,
                "runtime_metadata": item.runtime_metadata,
                "attention_reasons": attention_reasons,
            }
        )
    return items


def _filter_feedback_review_items(
    items: list[dict[str, object]],
    *,
    signal: str,
) -> list[dict[str, object]]:
    if signal == "fallback":
        return [item for item in items if item["runtime_metadata"].used_fallback]
    if signal == "weak_retrieval":
        return [item for item in items if item["runtime_metadata"].retrieved_chunk_count == 0]
    if signal == "attention":
        return [item for item in items if item["attention_reasons"]]
    return items


@router.get("/", include_in_schema=False)
async def home(request: Request):
    return _render_home(
        request,
        form_state=_default_form_state(),
    )


@router.post("/", include_in_schema=False)
async def submit_home(
    request: Request,
    goal: Annotated[str, Form()],
    experience_level: Annotated[str, Form()],
    training_days_per_week: Annotated[int, Form()],
    session_duration_minutes: Annotated[int, Form()],
    training_location: Annotated[str, Form()],
    equipment: Annotated[list[str] | None, Form()] = None,
    injuries_or_limitations_text: Annotated[str, Form()] = "",
    exercise_preferences_text: Annotated[str, Form()] = "",
):
    selected_equipment = equipment or []
    form_state: dict[str, object] = {
        "goal": goal,
        "experience_level": experience_level,
        "training_days_per_week": training_days_per_week,
        "session_duration_minutes": session_duration_minutes,
        "equipment": selected_equipment,
        "training_location": training_location,
        "injuries_or_limitations_text": injuries_or_limitations_text,
        "exercise_preferences_text": exercise_preferences_text,
    }

    try:
        profile = UserProfile.model_validate(
            {
                "goal": goal,
                "experience_level": experience_level,
                "training_days_per_week": training_days_per_week,
                "session_duration_minutes": session_duration_minutes,
                "equipment": selected_equipment,
                "training_location": training_location,
                "injuries_or_limitations": _parse_multiline_text(injuries_or_limitations_text),
                "exercise_preferences": _parse_multiline_text(exercise_preferences_text),
            }
        )
    except ValidationError as exc:
        return _render_home(
            request,
            form_state=form_state,
            validation_errors=_field_errors_from_validation(exc),
        )

    generator: WorkoutPlanGenerator = request.app.state.workout_plan_generator

    try:
        generated_plan = await generator.generate(profile)
    except AppError as exc:
        return _render_home(
            request,
            form_state=form_state,
            service_error=exc.message,
        )

    return _render_home(
        request,
        form_state=form_state,
        generated_plan=generated_plan,
        debug_context=generator.get_last_debug_context(),
        profile_snapshot_json=profile.model_dump_json(),
        runtime_metadata_json=generator.get_last_runtime_context().metadata.model_dump_json(),
    )


@router.post("/feedback", include_in_schema=False)
async def submit_feedback(
    request: Request,
    request_id: Annotated[str, Form()],
    profile_snapshot_json: Annotated[str, Form()],
    generated_plan_json: Annotated[str, Form()],
    runtime_metadata_json: Annotated[str, Form()],
    usefulness_rating: Annotated[int, Form()],
    difficulty_feedback: Annotated[str, Form()],
    felt_safe: Annotated[bool, Form()],
    would_follow_plan: Annotated[bool, Form()],
    feedback_text: Annotated[str, Form()] = "",
):
    try:
        profile = UserProfile.model_validate_json(profile_snapshot_json)
        generated_plan = WorkoutPlan.model_validate_json(generated_plan_json)
        runtime_metadata = FeedbackRuntimeMetadata.model_validate_json(runtime_metadata_json)
        feedback = PlanFeedback.model_validate(
            {
                "usefulness_rating": usefulness_rating,
                "difficulty_feedback": difficulty_feedback,
                "felt_safe": felt_safe,
                "would_follow_plan": would_follow_plan,
                "feedback_text": feedback_text or None,
            }
        )
    except ValidationError:
        return _render_home(
            request,
            form_state=_default_form_state(),
            feedback_error=(
                "Không thể xác thực biểu mẫu phản hồi vì ảnh chụp kế hoạch đi kèm chưa đầy đủ. "
                "Hãy tạo lại kế hoạch mới rồi thử lại."
            ),
        )

    feedback_store: FeedbackStore = request.app.state.feedback_store
    feedback_store.save_feedback(
        request_id=request_id,
        profile=profile,
        workout_plan=generated_plan,
        feedback=feedback,
        runtime_metadata=runtime_metadata,
    )

    return _render_home(
        request,
        form_state=_form_state_from_profile(profile),
        generated_plan=generated_plan,
        feedback_success=(
            "Đã lưu phản hồi. Lần tạo kế hoạch này giờ có thể dùng làm bằng chứng người dùng thật "
            "cho iteration, eval case và trao đổi phỏng vấn."
        ),
        profile_snapshot_json=profile.model_dump_json(),
        runtime_metadata_json=runtime_metadata.model_dump_json(),
    )


@router.get("/feedback/review", include_in_schema=False)
async def review_feedback(
    request: Request,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    signal: Annotated[str, Query(pattern="^(all|attention|fallback|weak_retrieval)$")] = "all",
):
    feedback_store: FeedbackStore = request.app.state.feedback_store
    records = feedback_store.list_recent_feedback(limit=limit)
    review_items = _build_feedback_review_items(records)
    filtered_items = _filter_feedback_review_items(review_items, signal=signal)
    return templates.TemplateResponse(
        request=request,
        name="feedback_review.html",
        context={
            "items": filtered_items,
            "selected_signal": signal,
            "limit": limit,
            "total_count": len(records),
        },
    )
