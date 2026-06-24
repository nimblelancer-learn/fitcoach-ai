from typing import Protocol

from app.schemas import UserProfile


class GroundingChunk(Protocol):
    chunk_id: str
    document_id: str
    title: str
    topic: str
    text: str
    section_path: list[str] | None


WORKOUT_PLAN_SYSTEM_INSTRUCTION = "".join(
    [
        "You generate structured workout plans for general fitness only. ",
        "Do not diagnose, treat, or interpret medical conditions. ",
        "Do not provide rehabilitation protocols, return-to-sport advice, "
        "or injury-treatment plans. ",
        "Do not replace a doctor, physical therapist, or other licensed medical professional. ",
        "If the user reports red-flag symptoms such as chest pain, fainting, severe dizziness, "
        "sudden severe shortness of breath, or sharp worsening pain, do not coach through the "
        "risk as if it were normal training. ",
        "When medical risk or clearance needs are present, keep the output "
        "conservative and use structured safety warnings to recommend "
        "professional assessment instead of medical advice. ",
        "If the user has limitations but no red-flag symptoms, prefer lower-risk substitutions, "
        "reduced complexity, and pain-free ranges of motion. ",
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
        "Use retrieved knowledge context when it is relevant to the user profile and safety "
        "constraints. ",
        "Do not output prose outside the structured response.",
    ]
)


def _format_list(values: list[object]) -> str:
    if not values:
        return "none"

    return ", ".join(str(value) for value in values)


def _format_grounding_context(retrieved_chunks: list[GroundingChunk]) -> str:
    lines: list[str] = ["Retrieved knowledge context:"]
    for index, chunk in enumerate(retrieved_chunks, start=1):
        location = " > ".join(chunk.section_path or [])
        header = (
            f"[{index}] chunk_id={chunk.chunk_id}; title={chunk.title}; topic={chunk.topic}; "
            f"document_id={chunk.document_id}"
        )
        if location:
            header = f"{header}; section_path={location}"
        lines.extend([header, chunk.text])
    return "\n".join(lines)


def build_workout_plan_prompt(
    profile: UserProfile,
    *,
    retrieved_chunks: list[GroundingChunk] | None = None,
) -> list[dict]:
    prompt_lines = [
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
    if retrieved_chunks:
        prompt_lines.extend(["", _format_grounding_context(retrieved_chunks)])
    user_prompt = "\n".join(prompt_lines)

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
