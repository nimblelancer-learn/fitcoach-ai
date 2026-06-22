from app.schemas import UserProfile

WORKOUT_PLAN_SYSTEM_INSTRUCTION = "".join(
    [
        "You generate structured workout plans for general fitness only. ",
        "Do not diagnose, treat, or interpret medical conditions. ",
        "Do not replace a doctor, physical therapist, or other licensed medical professional. ",
        "Be conservative for beginner users. ",
        "Respect the user's stated limitations, exercise preferences, equipment, "
        "and training location. ",
        "Follow the WorkoutPlan schema exactly. ",
        "All fields must be present. ",
        "Use [] for empty lists. ",
        "Use null for nullable fields that do not apply. ",
        "For repetitions prescriptions, include reps_min and reps_max, set "
        "duration_seconds to null, and ensure reps_min <= reps_max. ",
        "For duration prescriptions, include duration_seconds and set reps_min and reps_max to "
        "null. ",
        "Do not output prose outside the structured response.",
    ]
)


def _format_list(values: list[object]) -> str:
    if not values:
        return "none"

    return ", ".join(str(value) for value in values)


def build_workout_plan_prompt(profile: UserProfile) -> list[dict]:
    user_prompt = "\n".join(
        [
            "Create a workout plan from this user profile.",
            f"goal: {profile.goal.value}",
            f"experience_level: {profile.experience_level.value}",
            f"training_days_per_week: {profile.training_days_per_week}",
            f"session_duration_minutes: {profile.session_duration_minutes}",
            f"equipment: {_format_list([item.value for item in profile.equipment])}",
            f"training_location: {profile.training_location.value}",
            f"injuries_or_limitations: {_format_list(profile.injuries_or_limitations)}",
            f"exercise_preferences: {_format_list(profile.exercise_preferences)}",
        ]
    )

    return [
        {
            "role": "system",
            "content": WORKOUT_PLAN_SYSTEM_INSTRUCTION,
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ]
