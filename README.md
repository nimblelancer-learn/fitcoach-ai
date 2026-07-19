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
- App DB: Cloudflare D1 for the public MVP, SQLite only for local legacy paths

## Deployment Direction

The main deployment path is now Cloudflare-native.

- public runtime: Cloudflare Worker
- public UI: static assets served on Cloudflare
- public persistence: Cloudflare D1
- external providers: OpenAI and Qdrant

The Render plus persistent-disk path is now legacy documentation only. The
Phase 1 architecture guide lives in
[docs/cloudflare-migration-guide.md](docs/cloudflare-migration-guide.md).

## Cloudflare Local Setup

Use this path when you want the public MVP runtime, static UI, and D1-backed
feedback flow locally.

1. Create the D1 database once and copy the returned `database_id` into `wrangler.toml`.

```bash
npx wrangler d1 create fitcoach-ai
```

2. Copy `.dev.vars.example` to `.dev.vars` and set:

```bash
OPENAI_API_KEY=...
QDRANT_URL=...
QDRANT_API_KEY=...
LANGFUSE_PUBLIC_KEY=...   # optional
LANGFUSE_SECRET_KEY=...   # optional
LANGFUSE_BASE_URL=https://cloud.langfuse.com
```

3. Apply the local D1 migration.

```bash
npx wrangler d1 migrations apply FITCOACH_DB --local
```

4. Start the Worker locally.

```bash
npx wrangler dev
```

The Cloudflare MVP path serves:

- `GET /` for the static public interface in [`public/index.html`](public/index.html)
- `POST /api/workout-plans` for JSON generation
- `POST /api/feedback` for D1-backed feedback persistence
- `GET /health` for runtime health

Current public UX note:

- the public form UI is Vietnamese-first
- the two free-text inputs still require short English text for best retrieval quality
- generated plan content may still appear in English in the current MVP

## Langfuse Tracing

Phase 5 adds Langfuse tracing to the public Cloudflare Worker flow.

Important scope boundaries:

- tracing is attached to the existing `request_id`; it does not replace D1 persistence
- the same `request_id` is used as the Langfuse `trace_id` when tracing is enabled
- tracing is fail-open: generation and feedback save still work if Langfuse is disabled, misconfigured, or temporarily down

### Required vs optional configuration

Required for the public MVP runtime:

- `FITCOACH_DB` D1 binding
- `OPENAI_API_KEY`
- `QDRANT_URL`
- `QDRANT_API_KEY`

Optional for tracing:

- `LANGFUSE_PUBLIC_KEY`
- `LANGFUSE_SECRET_KEY`
- `LANGFUSE_BASE_URL`

If the Langfuse keys are absent, the Worker skips trace submission and still returns a normal response.

### What gets traced

One trace per public generation request with:

- `request_id` / `trace_id`
- model name
- generation latency
- token usage when OpenAI returns it
- retrieval query, chunk count, and chunk IDs
- fallback and refusal indicators
- safety trigger codes

### Canonical operator workflow

1. Start from the feedback review row or D1 feedback record.
2. Copy `request_id`.
3. Use the same value as the Langfuse `trace_id`.
4. Check retrieval metadata first:
   - `retrieved_chunk_count`
   - `retrieved_chunk_ids`
5. Then inspect the Langfuse trace for:
   - retrieval span output
   - generation observation input/output
   - latency and token usage
   - fallback/refusal indicators

If tracing was disabled for that run, the D1 row remains the primary debugging source.

## Local FastAPI Reference Setup

The Python app remains available as a local engineering surface and migration
reference. It is not the production deployment path.

```bash
cd backend
uv sync
uv run fastapi dev app/main.py
```

The legacy same-stack routes are:

- `GET /`
- `POST /`
- `POST /feedback`
- `POST /generate/workout-plan`

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

## Feedback Capture

The public MVP feedback loop is now Cloudflare-native.

- `POST /api/workout-plans` writes a `generation_runs` row in D1 keyed by the
  returned request ID.
- `POST /api/feedback` writes a linked `plan_feedback` row with the user
  feedback payload plus runtime metadata needed for later review.
- The legacy FastAPI path still supports local SQLite-backed feedback storage,
  but that is now an engineering-only fallback rather than the main path.

The current local operator review surface is:

- `GET /feedback/review` on the FastAPI reference app

It keeps the scope intentionally narrow:

- newest feedback first
- simple filters for `attention`, `fallback`, and `weak_retrieval`
- request ID, free-text feedback, and runtime metadata shown together for fast diagnosis

The stored metadata fields are:

- `request_id` as the stable join key between generation, feedback, future traces, and eval cases
- `generated_at` to align feedback with a specific generation event
- `model_name` to identify which model produced the outcome
- `latency_ms` to separate quality issues from slow-path behavior
- `used_fallback` to spot reliability or safety fallback outcomes quickly
- `retrieved_chunk_count` and `retrieved_chunk_ids` to identify weak or missing grounding
- `safety_trigger_codes` to explain why a safety path short-circuited or replaced a normal plan

This metadata is deliberately small. It is the minimum useful bundle for
debugging poor outcomes today while preserving a clean path to Langfuse
correlation in Phase 5.

## Public Feedback Loop

Phase 6 closes the loop between public MVP usage, repeated failure review, eval
updates, and changelog evidence.

Repo-local assets for that loop now include:

- D1 export query: `cloudflare/d1/queries/export_feedback_review.sql`
- Review CLI: `backend/app/feedback/review_loop.py`
- Operator runbook: [docs/public-feedback-loop-runbook.md](docs/public-feedback-loop-runbook.md)
- Phase status note: [docs/evidence/phase-06-feedback-loop-status.md](docs/evidence/phase-06-feedback-loop-status.md)

Example review command:

```bash
cd backend
uv run python -m app.feedback.review_loop \
  --input ../artifacts/feedback-loop/feedback-export-YYYYMMDD.json \
  --output-dir ../artifacts/feedback-loop/review-YYYYMMDD \
  --campaign-label july-public-feedback \
  --min-pattern-count 2
```

Important honesty rule:

- do not add new eval cases until the exported real-user feedback shows a repeated negative pattern
- do not treat raw submission volume as the completion signal; the loop closes only after eval and changelog outputs exist

If you want runtime cost estimates without editing code, set:

- `OPENAI_INPUT_COST_PER_MILLION_TOKENS_USD`
- `OPENAI_OUTPUT_COST_PER_MILLION_TOKENS_USD`

## Local Testing

Run the focused Cloudflare Worker smoke coverage with:

```bash
node --test cloudflare/worker.test.mjs
```

Run the backend reference test suite with:

```bash
cd backend
uv run pytest tests -q
```

The real OpenAI integration test is opt-in and guarded by environment variables.

## Cloudflare Deployment

Deploy the public MVP Worker after local verification:

```bash
npx wrangler d1 migrations apply FITCOACH_DB --remote
npx wrangler secret put OPENAI_API_KEY
npx wrangler secret put QDRANT_API_KEY
npx wrangler secret put LANGFUSE_PUBLIC_KEY   # optional
npx wrangler secret put LANGFUSE_SECRET_KEY   # optional
npx wrangler deploy
```

`OPENAI_MODEL`, `QDRANT_COLLECTION`, `RAG_EMBEDDING_PROVIDER`,
`RAG_EMBEDDING_MODEL`, `RAG_EMBEDDING_DIMENSIONS`, `RAG_RETRIEVAL_LIMIT`, and
`LANGFUSE_BASE_URL` are configured in `wrangler.toml` and can be overridden per
environment there.

## GitHub Actions Deployment

This repo now includes [`cloudflare-worker.yml`](.github/workflows/cloudflare-worker.yml).

- pull requests into `main`: run the Worker test suite only
- pushes to `main`: run the Worker tests, then deploy the Worker to Cloudflare
- manual trigger: available through `workflow_dispatch`

Important operational boundary:

- the workflow deploys application code only
- it does not auto-apply remote D1 migrations on every push
- if you add a new D1 migration, apply it intentionally before or during release:

```bash
npx wrangler d1 migrations apply FITCOACH_DB --remote
```

### What you need to connect between GitHub and Cloudflare

You do not need to connect the GitHub repository from the Cloudflare dashboard
if you use this GitHub Actions path. The deployment link is:

1. GitHub Actions runs on push to `main`
2. the workflow authenticates to Cloudflare with an API token
3. `wrangler deploy` publishes the Worker

Add these two GitHub repository secrets in `Settings -> Secrets and variables -> Actions`:

- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`

Recommended API token scope:

- `Account`
- `Cloudflare Workers:Edit`
- `D1:Edit` only if you also want to run D1 commands from CI later

How to get them:

1. In Cloudflare, open `My Profile -> API Tokens`.
2. Create a custom token with `Cloudflare Workers:Edit`.
3. In Cloudflare dashboard, copy the Account ID from the right sidebar of any account overview page.
4. Save both values as GitHub Actions secrets.

### What still lives on Cloudflare, not on GitHub

Worker runtime secrets should stay in Cloudflare:

```bash
npx wrangler secret put OPENAI_API_KEY
npx wrangler secret put QDRANT_API_KEY
npx wrangler secret put LANGFUSE_PUBLIC_KEY
npx wrangler secret put LANGFUSE_SECRET_KEY
```

Also make sure the Worker account already has:

- the `FITCOACH_DB` D1 binding from `wrangler.toml`
- the remote D1 schema applied
- plain config values from `wrangler.toml` kept in sync with production intent

## Legacy Render Deployment Path

Deprecated: Render remains documented only as a legacy MVP path. It is no
longer the recommended production target for this repository.

If you need to inspect the older deployment contract, use:

- [`render.yaml`](./render.yaml)
- the legacy notes in [`backend/README.md`](backend/README.md)

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
- Expand observability and feedback review/reporting
