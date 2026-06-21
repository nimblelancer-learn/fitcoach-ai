from pydantic import Field, field_validator

from .common import (
    Equipment,
    ExperienceLevel,
    FitnessGoal,
    SchemaBase,
    ShortText,
    TrainingLocation,
)


class UserProfile(SchemaBase):
    """
    Input contract for workout-plan generation.

    This is not a database user entity.
    Do not add email, password, authentication fields, or persistence IDs here.
    """

    goal: FitnessGoal
    experience_level: ExperienceLevel

    training_days_per_week: int = Field(
        ge=1,
        le=7,
        description="Number of training days available each week.",
    )

    session_duration_minutes: int = Field(
        ge=15,
        le=180,
        description="Preferred maximum duration for one workout session.",
    )

    equipment: list[Equipment] = Field(
        min_length=1,
        max_length=8,
    )

    training_location: TrainingLocation

    injuries_or_limitations: list[ShortText] = Field(
        default_factory=list,
        max_length=5,
        description=(
            "User-reported limitations only. This field must not be treated as a medical diagnosis."
        ),
    )

    exercise_preferences: list[ShortText] = Field(
        default_factory=list,
        max_length=5,
    )

    @field_validator("equipment")
    @classmethod
    def equipment_must_be_unique(
        cls,
        value: list[Equipment],
    ) -> list[Equipment]:
        if len(value) != len(set(value)):
            raise ValueError("equipment must not contain duplicates")

        return value

    @field_validator("injuries_or_limitations", "exercise_preferences")
    @classmethod
    def text_items_must_be_unique(
        cls,
        value: list[str],
    ) -> list[str]:
        normalized = [item.casefold() for item in value]

        if len(normalized) != len(set(normalized)):
            raise ValueError("list items must not contain duplicates")

        return value
