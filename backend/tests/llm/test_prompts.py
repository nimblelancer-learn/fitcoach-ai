from app.llm.prompts import (
    WORKOUT_PLAN_SYSTEM_INSTRUCTION,
    build_workout_plan_prompt,
)
from app.rag.retriever import RetrievedChunk
from app.schemas import UserProfile


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


def test_build_workout_plan_prompt_is_deterministic() -> None:
    profile = UserProfile.model_validate(valid_profile_payload())

    first_prompt = build_workout_plan_prompt(profile)
    second_prompt = build_workout_plan_prompt(profile)

    assert first_prompt == second_prompt


def test_system_instruction_covers_required_output_rules() -> None:
    assert "All fields must be present." in WORKOUT_PLAN_SYSTEM_INSTRUCTION
    assert "reps_min and reps_max" in WORKOUT_PLAN_SYSTEM_INSTRUCTION
    assert "duration_seconds" in WORKOUT_PLAN_SYSTEM_INSTRUCTION
    assert "Use [] for empty lists." in WORKOUT_PLAN_SYSTEM_INSTRUCTION
    assert "Use null for nullable fields" in WORKOUT_PLAN_SYSTEM_INSTRUCTION


def test_system_instruction_defines_medical_boundary_and_fallback() -> None:
    assert "general fitness only" in WORKOUT_PLAN_SYSTEM_INSTRUCTION
    assert "Do not provide rehabilitation protocols" in WORKOUT_PLAN_SYSTEM_INSTRUCTION
    assert "red-flag symptoms such as chest pain" in WORKOUT_PLAN_SYSTEM_INSTRUCTION
    assert "structured safety warnings" in WORKOUT_PLAN_SYSTEM_INSTRUCTION
    assert "professional assessment" in WORKOUT_PLAN_SYSTEM_INSTRUCTION


def test_build_workout_plan_prompt_maps_all_profile_fields() -> None:
    profile = UserProfile.model_validate(valid_profile_payload())

    prompt = build_workout_plan_prompt(profile)

    assert prompt == [
        {
            "role": "system",
            "content": WORKOUT_PLAN_SYSTEM_INSTRUCTION,
        },
        {
            "role": "user",
            "content": (
                "Create a workout plan from this user profile.\n"
                "goal: fat_loss\n"
                "experience_level: beginner\n"
                "training_days_per_week: 3\n"
                "session_duration_minutes: 45\n"
                "equipment: bodyweight, dumbbells, resistance_bands\n"
                "training_location: home\n"
                "injuries_or_limitations: Occasional knee discomfort when squatting deeply\n"
                "exercise_preferences: Strength training, Low-impact cardio"
            ),
        },
    ]


def test_build_workout_plan_prompt_uses_none_for_empty_lists() -> None:
    payload = valid_profile_payload()
    payload["injuries_or_limitations"] = []
    payload["exercise_preferences"] = []
    profile = UserProfile.model_validate(payload)

    prompt = build_workout_plan_prompt(profile)

    assert "injuries_or_limitations: none" in prompt[1]["content"]
    assert "exercise_preferences: none" in prompt[1]["content"]


def test_build_workout_plan_prompt_appends_grounding_context() -> None:
    profile = UserProfile.model_validate(valid_profile_payload())

    prompt = build_workout_plan_prompt(
        profile,
        retrieved_chunks=[
            RetrievedChunk(
                chunk_id="doc-1::chunk-000",
                document_id="doc-1",
                title="Warm-up basics",
                topic="warmup",
                text="Start with 5 minutes of easy movement before lifting.",
                section_path=["Warm-up", "Basics"],
            )
        ],
    )

    assert "Retrieved knowledge context:" in prompt[1]["content"]
    assert "chunk_id=doc-1::chunk-000" in prompt[1]["content"]
    assert "section_path=Warm-up > Basics" in prompt[1]["content"]
    assert "Start with 5 minutes of easy movement before lifting." in prompt[1]["content"]
