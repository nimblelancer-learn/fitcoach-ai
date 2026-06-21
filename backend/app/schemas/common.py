from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

ShortText = Annotated[str, Field(min_length=1, max_length=200)]


class SchemaBase(BaseModel):
    """
    Shared base model for all domain schemas.

    - extra="forbid": reject unknown fields from API clients or LLM output.
    - str_strip_whitespace=True: normalize text input.
    - validate_assignment=True: revalidate when a field is changed later.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class FitnessGoal(StrEnum):
    FAT_LOSS = "fat_loss"
    MUSCLE_GAIN = "muscle_gain"
    GENERAL_FITNESS = "general_fitness"
    ENDURANCE = "endurance"


class ExperienceLevel(StrEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"


class TrainingLocation(StrEnum):
    HOME = "home"
    GYM = "gym"
    OUTDOORS = "outdoors"
    MIXED = "mixed"


class Equipment(StrEnum):
    BODYWEIGHT = "bodyweight"
    DUMBBELLS = "dumbbells"
    RESISTANCE_BANDS = "resistance_bands"
    KETTLEBELL = "kettlebell"
    BARBELL = "barbell"
    MACHINES = "machines"
    FULL_GYM = "full_gym"
