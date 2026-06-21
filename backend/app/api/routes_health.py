from fastapi import APIRouter

router = APIRouter(tags=["System"])


@router.get(
    "/health",
    summary="Check API health",
    description="Returns the current availability of the API.",
)
async def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "fitcoach-ai-api",
    }
