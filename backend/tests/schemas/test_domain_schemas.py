from copy import deepcopy

import pytest
from pydantic import ValidationError

from app.schemas import ExerciseItem, FitnessGoal, UserProfile, WorkoutPlan


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


def valid_exercise_payload() -> dict:
    return {
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


def valid_duration_exercise_payload() -> dict:
    return {
        "name": "March in Place",
        "category": "cardio",
        "prescription_type": "duration",
        "sets": 2,
        "reps_min": None,
        "reps_max": None,
        "duration_seconds": 180,
        "rest_seconds": None,
        "intensity": "low",
        "target_muscles": [
            "calves",
            "hip flexors",
        ],
        "instructions": [
            "Keep a steady pace.",
        ],
        "safety_notes": [],
        "alternatives": [],
    }


def valid_plan_payload() -> dict:
    return {
        "title": "3-Day Beginner Home Strength Plan",
        "summary": ("A low-impact three-day plan for general fitness and fat loss."),
        "goal": "fat_loss",
        "experience_level": "beginner",
        "training_days_per_week": 1,
        "duration_weeks": 4,
        "weekly_schedule": [
            {
                "day_index": 1,
                "title": "Day 1 — Full Body A",
                "focus": "Full-body strength",
                "estimated_duration_minutes": 45,
                "warm_up": [
                    "Walk in place for 5 minutes",
                ],
                "exercises": [
                    valid_exercise_payload(),
                ],
                "cool_down": [
                    "Easy stretching for 5 minutes",
                ],
                "intensity_note": ("Choose a load that leaves about two reps in reserve."),
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
                "message": ("Keep controlled form; stop the movement if sharp pain occurs."),
                "recommended_action": ("Reduce range of motion or choose the listed alternative."),
                "applies_to_exercise": None,
                "requires_professional_clearance": False,
            }
        ],
    }


def test_user_profile_accepts_valid_input() -> None:
    profile = UserProfile.model_validate(valid_profile_payload())

    assert profile.goal is FitnessGoal.FAT_LOSS
    assert profile.training_days_per_week == 3
    assert profile.equipment[0].value == "bodyweight"


@pytest.mark.parametrize("invalid_days", [0, 8])
def test_user_profile_rejects_invalid_training_days(
    invalid_days: int,
) -> None:
    payload = valid_profile_payload()
    payload["training_days_per_week"] = invalid_days

    with pytest.raises(ValidationError):
        UserProfile.model_validate(payload)


def test_user_profile_rejects_unknown_fields() -> None:
    payload = valid_profile_payload()
    payload["unexpected_key"] = "must not be accepted"

    with pytest.raises(ValidationError):
        UserProfile.model_validate(payload)


def test_exercise_item_rejects_invalid_rep_range() -> None:
    payload = valid_exercise_payload()
    payload["reps_min"] = 12
    payload["reps_max"] = 8

    with pytest.raises(ValidationError):
        ExerciseItem.model_validate(payload)


def test_exercise_item_rejects_mixed_prescription_fields() -> None:
    payload = valid_exercise_payload()
    payload["duration_seconds"] = 300

    with pytest.raises(ValidationError):
        ExerciseItem.model_validate(payload)


def test_workout_plan_accepts_valid_nested_data() -> None:
    plan = WorkoutPlan.model_validate(valid_plan_payload())

    assert plan.weekly_schedule[0].exercises[0].name == "Goblet Squat"
    assert plan.safety_warnings[0].code.value == "form_priority"


def test_workout_plan_rejects_schedule_count_mismatch() -> None:
    payload = valid_plan_payload()
    payload["training_days_per_week"] = 2

    with pytest.raises(ValidationError):
        WorkoutPlan.model_validate(payload)


def test_workout_plan_rejects_duplicate_day_indexes() -> None:
    payload = valid_plan_payload()

    second_day = deepcopy(payload["weekly_schedule"][0])
    second_day["title"] = "Day 1 — Full Body B"

    payload["weekly_schedule"].append(second_day)
    payload["training_days_per_week"] = 2

    with pytest.raises(ValidationError):
        WorkoutPlan.model_validate(payload)


def test_medical_referral_warning_requires_clearance() -> None:
    payload = valid_plan_payload()

    payload["safety_warnings"] = [
        {
            "code": "medical_referral",
            "severity": "stop",
            "message": ("A clinician should assess this issue before training."),
            "recommended_action": ("Pause the plan and seek professional guidance."),
            "applies_to_exercise": None,
            "requires_professional_clearance": False,
        }
    ]

    with pytest.raises(ValidationError):
        WorkoutPlan.model_validate(payload)


def test_duration_exercise_accepts_required_null_keys() -> None:
    exercise = ExerciseItem.model_validate(valid_duration_exercise_payload())

    assert exercise.reps_min is None
    assert exercise.reps_max is None
    assert exercise.rest_seconds is None


def test_workout_plan_schema_marks_structured_output_fields_as_required() -> None:
    schema = WorkoutPlan.model_json_schema()
    required = set(schema["required"])

    assert "duration_weeks" in required
    assert "safety_warnings" in required


def test_exercise_item_schema_marks_structured_output_fields_as_required() -> None:
    schema = ExerciseItem.model_json_schema()
    required = set(schema["required"])

    assert "duration_seconds" in required
    assert "rest_seconds" in required
    assert "safety_notes" in required
    assert "alternatives" in required


def test_workout_plan_rejects_missing_required_structured_output_fields() -> None:
    payload = valid_plan_payload()
    del payload["safety_warnings"]

    with pytest.raises(ValidationError):
        WorkoutPlan.model_validate(payload)


def test_safety_warning_rejects_unknown_fields() -> None:
    payload = valid_plan_payload()
    payload["safety_warnings"][0]["unexpected_key"] = "must not be accepted"

    with pytest.raises(ValidationError):
        WorkoutPlan.model_validate(payload)


def test_workout_plan_rejects_whitespace_only_strings_after_stripping() -> None:
    payload = valid_plan_payload()
    payload["summary"] = "   "

    with pytest.raises(ValidationError):
        WorkoutPlan.model_validate(payload)
