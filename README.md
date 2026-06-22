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

## Roadmap

- Setup FastAPI backend skeleton
- Define domain schemas
- Implement structured workout plan generation
- Add retrieval with Qdrant
- Add safety validation
- Add eval dataset and runner
- Add observability and feedback collection
