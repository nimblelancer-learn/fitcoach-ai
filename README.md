# FitCoach AI

FitCoach AI is a portfolio project for building a production-minded AI fitness coaching assistant.

## Goal

Build a backend-first LLM application that demonstrates:

- FastAPI
- Direct LLM SDK usage
- Structured output
- RAG-based grounding
- Safety guardrails
- Evals
- Observability
- User feedback loops

## Problem Statement

Many fitness beginners do not know how to create a workout plan that matches their goals, schedule, equipment, and current ability. Generic plans are often too vague, too intense, or not personalized enough.

FitCoach AI explores how an LLM-powered assistant can generate structured and safer workout plans grounded in a curated fitness knowledge base.

The current repo-level safety boundary is documented in [docs/safety-policy.md](docs/safety-policy.md).
The current eval stack is documented in [docs/eval-design.md](docs/eval-design.md).

## Target Users

- Fitness beginners
- Busy people who want simple weekly workout plans
- Users training at home or in a gym
- People with general fitness goals such as fat loss, muscle gain, endurance, and overall health

## Planned Tech Stack

- Backend: Python, FastAPI, Pydantic
- LLM: OpenAI SDK directly
- Vector DB: Qdrant
- Observability: Langfuse
- App DB: SQLite for MVP, PostgreSQL later

## Local Setup

Current setup steps:

1. Create a virtual environment.
2. Install backend dependencies with `uv sync --project backend`.
3. Copy `.env.example` to `.env`.
4. Set `OPENAI_API_KEY` and `OPENAI_MODEL`.
5. Run the FastAPI backend locally.

```bash
cd backend
uv sync
uv run fastapi dev app/main.py
```

The same-stack MVP demo route is available at:

- `GET /` for the server-rendered public interface
- `POST /` for form-based workout-plan generation
- `GET /generate/workout-plan` for the JSON API contract

## Current Backend LLM Flow

The local workout-plan generation path is:

1. `POST /generate/workout-plan`
2. `WorkoutPlanGenerator.generate(profile)`
3. `build_workout_plan_prompt(profile)`
4. `OpenAIWorkoutPlanClient.generate_workout_plan(messages)`
5. `AsyncOpenAI.responses.parse(..., text_format=WorkoutPlan)`
6. `WorkoutPlan.model_validate(...)`

The app calls the OpenAI SDK directly. It does not hide the provider call behind a
framework wrapper.

## Reliability Handling

The current backend adds a few basic runtime protections around the LLM call:

- Invalid structured output is retried a bounded number of times
- Timeouts are mapped to an explicit app error
- Refusals fail fast
- Retry exhaustion returns a conservative schema-valid fallback workout plan

The fallback preserves the API contract by still returning a valid `WorkoutPlan`, which
keeps local development and downstream consumers simpler.

## Basic LLM Usage Metrics

Each generation request logs:

- model name
- latency in milliseconds
- input tokens when available
- output tokens when available
- total tokens when available
- estimated cost when pricing is known, otherwise `unavailable`

This is intentionally lightweight. The purpose is to make local behavior observable
before adding a full tracing or analytics stack.

If you want runtime cost estimates without editing code, set:

- `OPENAI_INPUT_COST_PER_MILLION_TOKENS_USD`
- `OPENAI_OUTPUT_COST_PER_MILLION_TOKENS_USD`

## Local Testing

Run the backend test suite with:

```bash
cd backend
uv run pytest tests -q
```

The real OpenAI integration test is opt-in and guarded by environment variables.

## Render Deployment Path

Issue `#42` uses a same-stack Render deployment path:

- one Render web service for the FastAPI API plus the public MVP UI
- one persistent Render disk for SQLite at `sqlite:////var/data/fitcoach_ai.db`
- one managed Qdrant instance referenced through `QDRANT_URL` and `QDRANT_API_KEY`

The Blueprint file is:

- [`render.yaml`](./render.yaml)

Current deployment intent:

- `GET /` is the public MVP page
- `GET /health` is the Render health check
- the learning portal is disabled in public deployment with
  `ENABLE_DEV_LEARNING_PORTAL=false`

To deploy on Render:

1. Create a new Blueprint-backed service from this repository.
2. Let Render read `render.yaml`.
3. Fill the prompted secret or environment values:
   - `OPENAI_API_KEY`
   - `QDRANT_URL`
   - `QDRANT_API_KEY`
4. After the first deploy succeeds, open the shell or run a one-off command to
   index the knowledge base:

```bash
cd /app && python -m app.rag.index
```

Notes:

- The Blueprint provisions a persistent disk for the app database requirement
  even though the current MVP does not yet write generation data to SQLite.
- The deployed default AI path is:
  - `OPENAI_MODEL=gpt-4.1-mini`
  - `RAG_EMBEDDING_PROVIDER=openai`
  - `RAG_EMBEDDING_MODEL=text-embedding-3-small`
- Grounded retrieval depends on loading the Qdrant collection before public
  demo validation.
- The final public demo URL should be added here after the first successful
  deployment is live.

## Safety Boundary

Safety policy v1 lives in `docs/safety-policy.md`.

- General fitness coaching is in scope.
- Medical advice, diagnosis, treatment, and rehabilitation programming are out of scope.
- Red-flag symptom scenarios should route toward conservative output and professional clearance, not improvised coaching.

## Knowledge Base Assets

The starter retrieval corpus lives in `knowledge_base/`.

- `knowledge_base/raw/` stores chunk-ready markdown documents grouped by topic.
- `knowledge_base/processed/chunks-v1.json` stores the current normalized chunk
  artifact checked into the repo.
- `knowledge_base/source-policy.md` defines what sources may enter the corpus.
- `knowledge_base/sources.md` tracks document provenance for later RAG work.

To regenerate the processed chunk artifact locally:

```bash
cd backend
uv run python -m app.rag.chunking
```

The chunking pass is deterministic and heading-aware. It preserves each raw
document's front-matter metadata, emits stable `chunk_id` values, and stores
the resulting JSON in a predictable location so later embedding and retrieval
steps can consume it without extra normalization work.

## Roadmap

- Setup FastAPI backend skeleton
- Define domain schemas
- Implement structured workout plan generation
- Add retrieval with Qdrant
- Add safety validation
- Add eval dataset and runner
- Add observability and feedback collection
