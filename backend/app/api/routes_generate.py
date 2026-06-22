from fastapi import APIRouter, Request

from app.schemas import UserProfile, WorkoutPlan
from app.services import WorkoutPlanGenerator

router = APIRouter(prefix="/generate", tags=["Generation"])


@router.post("/workout-plan", response_model=WorkoutPlan)
async def generate_workout_plan(
    profile: UserProfile,
    request: Request,
) -> WorkoutPlan:
    generator: WorkoutPlanGenerator = request.app.state.workout_plan_generator
    return await generator.generate(profile)
