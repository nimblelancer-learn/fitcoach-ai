import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes_generate import router as generate_router
from app.api.routes_health import router as health_router
from app.api.routes_learning import router as learning_router
from app.api.routes_web import router as web_router
from app.core.errors import register_exception_handlers
from app.core.logging import setup_logging
from app.core.settings import get_settings
from app.learning.loader import load_learning_portal
from app.llm.openai_client import OpenAIWorkoutPlanClient
from app.middleware.request_logging import request_logging_middleware
from app.rag.retriever import KnowledgeRetriever
from app.services import WorkoutPlanGenerator

logger = logging.getLogger(__name__)


async def startup(app: FastAPI) -> None:
    settings = app.state.settings

    if settings.enable_dev_learning_portal:
        app.state.learning_portal = load_learning_portal()

    logger.info(
        "application_started name=fitcoach-ai-api dev_learning_portal_enabled=%s",
        settings.enable_dev_learning_portal,
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await startup(app)
    yield


def create_app() -> FastAPI:
    setup_logging()

    settings = get_settings()

    app = FastAPI(
        title="FitCoach AI API",
        description="Backend API for the FitCoach AI application.",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.state.settings = settings
    app.state.workout_plan_generator = WorkoutPlanGenerator(
        OpenAIWorkoutPlanClient(settings),
        KnowledgeRetriever(settings),
    )

    app.middleware("http")(request_logging_middleware)
    register_exception_handlers(app)

    app.include_router(generate_router)
    app.include_router(health_router)
    app.include_router(learning_router)
    app.include_router(web_router)

    return app


app = create_app()
