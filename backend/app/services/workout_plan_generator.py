from app.llm.openai_client import OpenAIWorkoutPlanClient
from app.llm.prompts import build_workout_plan_prompt
from app.schemas import UserProfile, WorkoutPlan


class WorkoutPlanGenerator:
    def __init__(self, client: OpenAIWorkoutPlanClient) -> None:
        self._client = client

    async def generate(self, profile: UserProfile) -> WorkoutPlan:
        messages = build_workout_plan_prompt(profile)
        return await self._client.generate_workout_plan(messages)
