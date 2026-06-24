from fastapi import APIRouter, Request, Response

from app.schemas import UserProfile, WorkoutPlan
from app.services import WorkoutPlanGenerator

router = APIRouter(prefix="/generate", tags=["Generation"])


@router.post("/workout-plan", response_model=WorkoutPlan)
async def generate_workout_plan(
    profile: UserProfile,
    request: Request,
    response: Response,
) -> WorkoutPlan:
    generator: WorkoutPlanGenerator = request.app.state.workout_plan_generator
    plan = await generator.generate(profile)
    get_debug_context = getattr(generator, "get_last_debug_context", None)
    if callable(get_debug_context):
        debug_context = get_debug_context()
        response.headers["X-RAG-Chunk-Count"] = str(len(debug_context.retrieved_chunks))
        if debug_context.retrieved_chunks:
            response.headers["X-RAG-Chunk-Ids"] = ",".join(
                chunk.chunk_id for chunk in debug_context.retrieved_chunks[:3]
            )
    return plan
