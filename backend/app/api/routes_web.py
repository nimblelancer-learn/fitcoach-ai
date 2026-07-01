from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Form, Request
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from app.core.errors import AppError
from app.schemas import Equipment, ExperienceLevel, FitnessGoal, TrainingLocation, UserProfile
from app.services import GenerationDebugContext, WorkoutPlanGenerator

router = APIRouter(tags=["Web"])

templates = Jinja2Templates(
    directory=str(
        Path(__file__).resolve().parent.parent / "web" / "templates",
    ),
)


def _format_label(value: str) -> str:
    return value.replace("_", " ").title()


def _build_choice_items(
    enum_cls: type[FitnessGoal | ExperienceLevel | TrainingLocation | Equipment],
) -> list[dict[str, str]]:
    return [{"value": item.value, "label": _format_label(item.value)} for item in enum_cls]


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
        },
    )


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
    )
