from pathlib import Path

from app.feedback.store import LocalFeedbackStore
from app.schemas import FeedbackRuntimeMetadata, PlanFeedback, UserProfile, WorkoutPlan


def valid_profile() -> UserProfile:
    return UserProfile.model_validate(
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


def valid_plan() -> WorkoutPlan:
    return WorkoutPlan.model_validate(
        {
            "title": "3-Day Beginner Home Strength Plan",
            "summary": "A low-impact three-day plan for general fitness and fat loss.",
            "goal": "fat_loss",
            "experience_level": "beginner",
            "training_days_per_week": 1,
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
                            "instructions": ["Keep your chest tall."],
                            "safety_notes": ["Use a pain-free range of motion."],
                            "alternatives": ["Box squat"],
                        }
                    ],
                    "cool_down": ["Easy stretching for 5 minutes"],
                    "intensity_note": "Choose a load that leaves about two reps in reserve.",
                }
            ],
            "progression_suggestion": "Add one repetition before increasing load.",
            "safety_warnings": [
                {
                    "code": "form_priority",
                    "severity": "caution",
                    "message": "Keep controlled form; stop if sharp pain occurs.",
                    "recommended_action": (
                        "Reduce range of motion or choose the listed alternative."
                    ),
                    "applies_to_exercise": None,
                    "requires_professional_clearance": False,
                }
            ],
        }
    )


def valid_feedback() -> PlanFeedback:
    return PlanFeedback.model_validate(
        {
            "usefulness_rating": 2,
            "difficulty_feedback": "too_hard",
            "felt_safe": False,
            "would_follow_plan": False,
            "feedback_text": "Too hard and not confidence-inspiring.",
        }
    )


def valid_runtime_metadata() -> FeedbackRuntimeMetadata:
    return FeedbackRuntimeMetadata(
        generated_at="2026-07-14T17:10:00+00:00",
        model_name="gpt-4.1-mini",
        latency_ms=544,
        used_fallback=True,
        retrieved_chunk_count=0,
        retrieved_chunk_ids=[],
        safety_trigger_codes=["medical_keyword:chest pain"],
        trace_id="req-store-1",
        trace_enabled=True,
        langfuse_host="https://cloud.langfuse.com",
    )


def test_local_feedback_store_round_trips_runtime_metadata(tmp_path: Path) -> None:
    store = LocalFeedbackStore(f"sqlite:///{tmp_path / 'feedback.db'}")
    store.initialize()

    saved = store.save_feedback(
        request_id="req-store-1",
        profile=valid_profile(),
        workout_plan=valid_plan(),
        feedback=valid_feedback(),
        runtime_metadata=valid_runtime_metadata(),
    )

    recent = store.list_recent_feedback(limit=5)

    assert saved.request_id == "req-store-1"
    assert saved.runtime_metadata == valid_runtime_metadata()
    assert len(recent) == 1
    assert recent[0].request_id == "req-store-1"
    assert recent[0].runtime_metadata == valid_runtime_metadata()
    assert recent[0].feedback.feedback_text == "Too hard and not confidence-inspiring."
