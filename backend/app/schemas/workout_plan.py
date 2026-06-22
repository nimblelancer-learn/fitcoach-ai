from enum import StrEnum

from pydantic import Field, model_validator

from .common import ExperienceLevel, FitnessGoal, SchemaBase, ShortText


class ExerciseCategory(StrEnum):
    STRENGTH = "strength"
    CARDIO = "cardio"
    MOBILITY = "mobility"


class PrescriptionType(StrEnum):
    REPETITIONS = "repetitions"
    DURATION = "duration"


class Intensity(StrEnum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class SafetyWarningCode(StrEnum):
    STOP_IF_PAIN = "stop_if_pain"
    FORM_PRIORITY = "form_priority"
    INJURY_MODIFICATION = "injury_modification"
    BEGINNER_INTENSITY = "beginner_intensity"
    MEDICAL_REFERRAL = "medical_referral"
    EQUIPMENT_SUBSTITUTION = "equipment_substitution"


class WarningSeverity(StrEnum):
    INFO = "info"
    CAUTION = "caution"
    STOP = "stop"


class SafetyWarning(SchemaBase):
    """
    A structured warning attached to a plan or exercise.

    It represents a warning. It does not itself detect medical risk.
    """

    code: SafetyWarningCode
    severity: WarningSeverity

    message: str = Field(
        min_length=1,
        max_length=300,
    )

    recommended_action: str = Field(
        min_length=1,
        max_length=300,
    )

    applies_to_exercise: str | None = Field(
        min_length=1,
        max_length=120,
    )

    requires_professional_clearance: bool

    @model_validator(mode="after")
    def medical_referral_requires_clearance(self) -> "SafetyWarning":
        if (
            self.code == SafetyWarningCode.MEDICAL_REFERRAL
            and not self.requires_professional_clearance
        ):
            raise ValueError("medical_referral warnings must require professional clearance")

        return self


class ExerciseItem(SchemaBase):
    """
    One exercise in one workout day.

    A prescription must be either:
    - repetitions-based, or
    - duration-based.

    It cannot contain both.
    """

    name: str = Field(
        min_length=1,
        max_length=120,
    )

    category: ExerciseCategory
    prescription_type: PrescriptionType

    sets: int = Field(
        ge=1,
        le=8,
    )

    reps_min: int | None = Field(
        ge=1,
        le=100,
    )

    reps_max: int | None = Field(
        ge=1,
        le=100,
    )

    duration_seconds: int | None = Field(
        ge=15,
        le=3600,
    )

    rest_seconds: int | None = Field(
        ge=0,
        le=600,
    )

    intensity: Intensity

    target_muscles: list[ShortText] = Field(
        min_length=1,
        max_length=6,
    )

    instructions: list[ShortText] = Field(
        min_length=1,
        max_length=6,
    )

    safety_notes: list[ShortText] = Field(
        max_length=5,
    )

    alternatives: list[ShortText] = Field(
        max_length=3,
    )

    @model_validator(mode="after")
    def validate_prescription(self) -> "ExerciseItem":
        if self.prescription_type == PrescriptionType.REPETITIONS:
            if self.reps_min is None or self.reps_max is None:
                raise ValueError("repetitions prescription requires reps_min and reps_max")

            if self.duration_seconds is not None:
                raise ValueError("repetitions prescription must not include duration_seconds")

            if self.reps_min > self.reps_max:
                raise ValueError("reps_min must be less than or equal to reps_max")

        if self.prescription_type == PrescriptionType.DURATION:
            if self.duration_seconds is None:
                raise ValueError("duration prescription requires duration_seconds")

            if self.reps_min is not None or self.reps_max is not None:
                raise ValueError("duration prescription must not include reps_min or reps_max")

        return self


class WorkoutDay(SchemaBase):
    """
    Supporting nested model for one scheduled training day.
    """

    day_index: int = Field(
        ge=1,
        le=7,
    )

    title: str = Field(
        min_length=1,
        max_length=120,
    )

    focus: ShortText

    estimated_duration_minutes: int = Field(
        ge=15,
        le=180,
    )

    warm_up: list[ShortText] = Field(
        min_length=1,
        max_length=5,
    )

    exercises: list[ExerciseItem] = Field(
        min_length=1,
        max_length=12,
    )

    cool_down: list[ShortText] = Field(
        min_length=1,
        max_length=5,
    )

    intensity_note: str = Field(
        min_length=1,
        max_length=240,
    )


class WorkoutPlan(SchemaBase):
    """
    Structured output contract for the generated workout plan.
    """

    title: str = Field(
        min_length=1,
        max_length=120,
    )

    summary: str = Field(
        min_length=1,
        max_length=500,
    )

    goal: FitnessGoal
    experience_level: ExperienceLevel

    training_days_per_week: int = Field(
        ge=1,
        le=7,
    )

    duration_weeks: int = Field(
        ge=1,
        le=12,
    )

    weekly_schedule: list[WorkoutDay] = Field(
        min_length=1,
        max_length=7,
    )

    progression_suggestion: str = Field(
        min_length=1,
        max_length=400,
    )

    safety_warnings: list[SafetyWarning] = Field(
        max_length=10,
    )

    @model_validator(mode="after")
    def validate_schedule(self) -> "WorkoutPlan":
        if len(self.weekly_schedule) != self.training_days_per_week:
            raise ValueError("weekly_schedule length must equal training_days_per_week")

        day_indices = [day.day_index for day in self.weekly_schedule]

        if len(day_indices) != len(set(day_indices)):
            raise ValueError("weekly_schedule must not contain duplicate day_index values")

        return self
