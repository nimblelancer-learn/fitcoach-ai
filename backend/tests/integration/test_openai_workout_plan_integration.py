import os

import pytest

from app.core.settings import Settings
from app.llm.openai_client import OpenAIWorkoutPlanClient
from app.schemas import UserProfile, WorkoutPlan
from app.services import WorkoutPlanGenerator


def valid_profile_payload() -> dict:
    return {
        "goal": "general_fitness",
        "experience_level": "beginner",
        "training_days_per_week": 2,
        "session_duration_minutes": 30,
        "equipment": ["bodyweight", "resistance_bands"],
        "training_location": "home",
        "injuries_or_limitations": [],
        "exercise_preferences": ["Low-impact cardio", "Strength training"],
    }


pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_openai_workout_plan_generation_integration() -> None:
    if os.environ.get("RUN_OPENAI_INTEGRATION") != "1":
        pytest.skip("Set RUN_OPENAI_INTEGRATION=1 to enable OpenAI integration tests.")

    if not os.environ.get("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY is required for OpenAI integration tests.")

    if not os.environ.get("OPENAI_MODEL"):
        pytest.skip("OPENAI_MODEL is required for OpenAI integration tests.")

    settings = Settings()
    generator = WorkoutPlanGenerator(OpenAIWorkoutPlanClient(settings))

    profile = UserProfile.model_validate(valid_profile_payload())
    plan = await generator.generate(profile)

    assert isinstance(plan, WorkoutPlan)
    assert plan.training_days_per_week == len(plan.weekly_schedule)

    for day in plan.weekly_schedule:
        assert day.exercises
        for exercise in day.exercises:
            dumped = exercise.model_dump()
            assert "alternatives" in dumped
            assert "duration_seconds" in dumped
            assert "reps_min" in dumped
            assert "reps_max" in dumped
