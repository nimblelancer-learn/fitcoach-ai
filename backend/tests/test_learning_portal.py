from __future__ import annotations

from pathlib import Path

import httpx
import pytest

from app.core.settings import get_settings
from app.learning.loader import LearningContentError, load_learning_portal
from app.main import create_app, startup


@pytest.fixture(autouse=True)
def clear_settings_cache() -> None:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.mark.anyio
async def test_learning_portal_disabled_returns_explanatory_404(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENABLE_DEV_LEARNING_PORTAL", "false")

    response = await _get(create_app(), "/__learn")

    assert response.status_code == 404
    assert "Learning portal unavailable" in response.text
    assert "ENABLE_DEV_LEARNING_PORTAL=true" in response.text


@pytest.mark.anyio
async def test_learning_overview_renders_when_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENABLE_DEV_LEARNING_PORTAL", "true")

    response = await _get(create_app(), "/__learn")

    assert response.status_code == 200
    assert "FitCoach AI backend learning portal" in response.text
    assert "app.main" in response.text
    assert "app.core.settings" in response.text
    assert "app.api.routes_generate" in response.text
    assert "app.rag.retriever" in response.text
    assert "app.llm.openai_client" in response.text
    assert "app.evals.runner" in response.text
    assert "Startup lifecycle" in response.text
    assert "Request lifecycle" in response.text
    assert "Workout plan generation" in response.text
    assert "Eval runner" in response.text
    assert 'href="/__learn/flows/workout-plan-generation"' in response.text
    assert 'href="/__learn/flows/eval-runner"' in response.text
    assert 'href="/__learn/flows/startup-lifecycle"' in response.text
    assert "Open flow" in response.text
    assert "Glossary" in response.text


@pytest.mark.anyio
async def test_learning_module_detail_renders_when_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENABLE_DEV_LEARNING_PORTAL", "true")

    response = await _get(create_app(), "/__learn/modules/app-main")

    assert response.status_code == 200
    assert "Builds the FastAPI application" in response.text
    assert "create_app" in response.text
    assert "/__learn/flows/startup-lifecycle" in response.text
    assert "request lifecycle" in response.text.lower()
    assert "Related terms" in response.text
    assert "/__learn/glossary#startup" in response.text


@pytest.mark.anyio
async def test_learning_core_settings_module_detail_renders_when_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENABLE_DEV_LEARNING_PORTAL", "true")

    response = await _get(create_app(), "/__learn/modules/core-settings")

    assert response.status_code == 200
    assert "environment-backed Settings object" in response.text
    assert "app.core.settings.get_settings" in response.text
    assert "/__learn/glossary#feature-flag" in response.text
    assert "/__learn/glossary#app-state" in response.text
    assert "/__learn/glossary#retry" in response.text


@pytest.mark.anyio
async def test_learning_workout_generation_flow_renders_when_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENABLE_DEV_LEARNING_PORTAL", "true")

    response = await _get(create_app(), "/__learn/flows/workout-plan-generation")

    assert response.status_code == 200
    assert "Workout plan generation" in response.text
    assert "responses.parse()" in response.text
    assert "text_format=WorkoutPlan" in response.text
    assert "OPENAI_INVALID_OUTPUT" in response.text
    assert "input_tokens" in response.text
    assert "openai_invalid_output_retries" in response.text
    assert "openai_workout_plan_fallback" in response.text
    assert "KnowledgeRetriever.retrieve()" in response.text
    assert "X-RAG-Chunk-Count" in response.text
    assert "Safety-First Fallback Plan" in response.text


@pytest.mark.anyio
async def test_learning_rag_retriever_module_detail_renders_when_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENABLE_DEV_LEARNING_PORTAL", "true")

    response = await _get(create_app(), "/__learn/modules/rag-retriever")

    assert response.status_code == 200
    assert "vector search details" in response.text
    assert "app.rag.retriever.KnowledgeRetriever" in response.text
    assert "/__learn/flows/workout-plan-generation" in response.text
    assert "/__learn/glossary#grounding" in response.text


@pytest.mark.anyio
async def test_learning_eval_runner_flow_renders_when_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENABLE_DEV_LEARNING_PORTAL", "true")

    response = await _get(create_app(), "/__learn/flows/eval-runner")

    assert response.status_code == 200
    assert "Eval runner" in response.text
    assert "workout_plan_eval_dataset_v1.json" in response.text
    assert "generate_plan_live()" in response.text
    assert "score_case()" in response.text


@pytest.mark.anyio
async def test_learning_evals_runner_module_detail_renders_when_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENABLE_DEV_LEARNING_PORTAL", "true")

    response = await _get(create_app(), "/__learn/modules/evals-runner")

    assert response.status_code == 200
    assert "local eval entry point" in response.text
    assert "app.evals.runner.score_case" in response.text
    assert "/__learn/flows/eval-runner" in response.text
    assert "/__learn/glossary#rubric" in response.text


@pytest.mark.anyio
async def test_learning_llm_openai_client_module_detail_renders_when_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENABLE_DEV_LEARNING_PORTAL", "true")

    response = await _get(create_app(), "/__learn/modules/llm-openai-client")

    assert response.status_code == 200
    assert "structured parsing, runtime safety guardrails, reliability handling" in response.text
    assert "app.llm.openai_client.OpenAIWorkoutPlanClient" in response.text
    assert "/__learn/flows/workout-plan-generation" in response.text
    assert "/__learn/glossary#structured-output" in response.text
    assert "/__learn/glossary#token-usage" in response.text


@pytest.mark.anyio
async def test_learning_startup_flow_renders_when_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENABLE_DEV_LEARNING_PORTAL", "true")

    response = await _get(create_app(), "/__learn/flows/startup-lifecycle")

    assert response.status_code == 200
    assert "Startup lifecycle" in response.text
    assert "app.core.settings.get_settings" in response.text
    assert "load_learning_portal()" in response.text
    assert "request.app.state.learning_portal" in response.text
    assert "Current flow walkthrough" in response.text


@pytest.mark.anyio
async def test_learning_routes_are_hidden_from_openapi(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENABLE_DEV_LEARNING_PORTAL", "true")

    response = await _get(create_app(), "/openapi.json")

    assert response.status_code == 200
    assert "/__learn" not in response.text


@pytest.mark.anyio
async def test_learning_glossary_renders_when_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENABLE_DEV_LEARNING_PORTAL", "true")

    response = await _get(create_app(), "/__learn/glossary")

    assert response.status_code == 200
    assert "Backend terms used in this repo" in response.text
    assert "Middleware" in response.text
    assert "Request ID" in response.text
    assert "Feature flag" in response.text
    assert "App state" in response.text
    assert "Lifespan" in response.text
    assert "Structured output" in response.text
    assert "Retry" in response.text
    assert "Token usage" in response.text
    assert "Fallback plan" in response.text
    assert "Grounding" in response.text
    assert "Safety guardrail" in response.text
    assert "Rubric" in response.text
    assert "Why this matters here:" in response.text


def test_invalid_module_reference_fails_clearly(
    tmp_path: Path,
) -> None:
    content_dir = _write_learning_fixture(
        tmp_path,
        module_path="app.missing_module",
    )

    with pytest.raises(LearningContentError) as exc_info:
        load_learning_portal(content_dir)

    assert "Unknown module path 'app.missing_module'" in str(exc_info.value)


def test_invalid_function_reference_fails_clearly(
    tmp_path: Path,
) -> None:
    content_dir = _write_learning_fixture(
        tmp_path,
        function_path="app.api.routes_health.missing_function",
    )

    with pytest.raises(LearningContentError) as exc_info:
        load_learning_portal(content_dir)

    assert "Unknown function path 'app.api.routes_health.missing_function'" in str(
        exc_info.value,
    )


def _write_learning_fixture(
    root: Path,
    *,
    module_path: str = "app.api.routes_health",
    function_path: str = "app.api.routes_health.health_check",
) -> Path:
    (root / "modules").mkdir()
    (root / "flows").mkdir()
    (root / "glossary").mkdir()

    (root / "overview.toml").write_text(
        """
title = "Fixture portal"
intro = "Fixture intro."
high_level_notes = ["Read the fixture."]
featured_modules = ["fixture-module"]
featured_flows = ["fixture-flow"]
""".strip()
        + "\n",
        encoding="utf-8",
    )

    (root / "modules" / "fixture-module.toml").write_text(
        f"""
slug = "fixture-module"
title = "Fixture module"
module_path = "{module_path}"
summary = "Fixture summary."
why_it_exists = "Fixture why."
when_it_runs = "Fixture when."
dependencies = ["FastAPI"]
used_by = ["Fixture route"]
safe_edit_notes = ["Keep it simple."]
related_modules = []
related_flows = ["fixture-flow"]

[[key_functions]]
name = "fixture_function"
python_path = "{function_path}"
summary = "Fixture function summary."
why_it_matters = "Fixture function why."
""".strip()
        + "\n",
        encoding="utf-8",
    )

    (root / "flows" / "fixture-flow.toml").write_text(
        f"""
slug = "fixture-flow"
title = "Fixture flow"
summary = "Fixture flow summary."
why_it_matters = "Fixture flow why."
when_to_read = "Any time."
related_modules = ["fixture-module"]

[[steps]]
title = "Fixture step"
description = "Fixture flow step."
module_path = "{module_path}"
python_path = "{function_path}"
""".strip()
        + "\n",
        encoding="utf-8",
    )

    (root / "glossary" / "fixture-term.toml").write_text(
        """
slug = "fixture-term"
term = "Fixture term"
definition = "Fixture definition."
why_it_matters_in_repo = "Fixture why."
related_modules = ["fixture-module"]
""".strip()
        + "\n",
        encoding="utf-8",
    )

    return root


async def _get(app, path: str) -> httpx.Response:
    await startup(app)

    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        return await client.get(path)
