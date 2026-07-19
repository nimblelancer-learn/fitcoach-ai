# Cloudflare Migration Guide

## Purpose

This guide defines the production target for the public FitCoach AI MVP after
the Render-era deployment assumptions are retired. It is intentionally narrow:

- one public workout-plan flow
- persistent feedback capture
- documented Cloudflare deployment steps
- retained external integrations for OpenAI and Qdrant

Phase 2 now implements the narrowest runnable public path on top of that
architecture.

Phase 4 adds the first operator-facing review loop on top of that path:

- runtime metadata is threaded from generation into feedback persistence
- feedback review can distinguish fallback outcomes from weak retrieval cases
- stable request IDs remain the primary join key for later tracing and eval creation

Phase 5 adds Langfuse on top of that existing join path:

- the Worker uses the same `request_id` as the Langfuse `trace_id`
- `generation_runs.trace_id` preserves the generation-to-trace join explicitly
- `plan_feedback.runtime_metadata_json` keeps the same `trace_id` plus whether tracing was enabled
- trace submission stays fail-open and does not block generation or feedback persistence

## Recommended Public Runtime

Use a Cloudflare Worker as the only public runtime for the MVP.

Target request shape:

- `GET /` serves the public workout-plan UI
- `POST /api/workout-plans` generates one structured workout plan
- `POST /api/feedback` persists user feedback linked to the generation request
- `GET /health` returns a lightweight health response

Do not preserve the current same-stack FastAPI plus Jinja deployment shape for
production. That path depends on local process state and SQLite file semantics
that do not map cleanly onto Cloudflare.

## UI Serving Strategy

Serve the public UI as static assets attached to the Worker.

Why:

- keeps the MVP delivery shape to one Cloudflare deployment unit
- removes the need for server-side Jinja rendering in production
- keeps form/UI changes decoupled from Python framework constraints
- fits the MVP scope better than preserving server-rendered templates

Phase 2 implements a small static frontend in `public/` and lets the Worker
handle:

- asset serving
- JSON form submission endpoints
- request ID issuance
- D1 writes
- OpenAI and Qdrant orchestration

## Current Code Audit

### Reusable with little or no product-level change

- `backend/app/services/workout_plan_generator.py`
  - generation flow shape is reusable
  - retrieval-before-generation sequence is reusable
  - debug context concept is reusable
- `backend/app/llm/**`
  - prompt-building and OpenAI contract patterns are reusable in concept
- `backend/app/rag/**`
  - retrieval query intent and chunk usage are reusable in concept
- `backend/app/schemas/**`
  - workout-plan and user-profile contracts should remain the source model to
    mirror during the Worker migration
- `knowledge_base/**`
  - corpus and chunk artifact remain valid

### Tightly coupled to the current runtime

- `backend/app/main.py`
  - tied to FastAPI app lifecycle, app state, and router mounting
- `backend/app/api/routes_generate.py`
  - tied to FastAPI request/response objects and response headers
- `backend/app/api/routes_web.py`
  - tied to form posts, Jinja templates, and FastAPI request handling
- `backend/app/feedback/store.py`
  - tied to SQLite file paths, `sqlite3`, and synchronous local-disk writes
- `backend/app/web/templates/**`
  - tied to Jinja server rendering
- `render.yaml`
  - tied to Render Blueprint, persistent disk, and same-stack hosting

### Migration boundary for Phase 2

Keep the Python codebase as a reference implementation and local engineering
surface until the public Worker path is complete. Do not spread Cloudflare
conditionals through the current FastAPI modules. Build explicit adapters in the
new Worker runtime instead.

## D1 Storage Plan

Use D1 as the production persistence target for feedback and lightweight runtime
metadata.

Initial tables:

1. `generation_runs`
2. `plan_feedback`

Rationale:

- `generation_runs` stores the generation context once
- `plan_feedback` stores user feedback separately and links back to the run
- feedback remains queryable even when later review/reporting screens are added
- runtime metadata is available before Langfuse is introduced

### `generation_runs`

Purpose:

- one row per generated workout plan
- attaches request metadata and generation snapshot to a stable request ID

Fields:

- `request_id TEXT PRIMARY KEY`
- `created_at TEXT NOT NULL`
- `app_runtime TEXT NOT NULL`
- `app_version TEXT`
- `request_locale TEXT`
- `provider TEXT NOT NULL`
- `model TEXT NOT NULL`
- `rag_provider TEXT`
- `rag_collection TEXT`
- `rag_chunk_ids_json TEXT NOT NULL`
- `chunk_count INTEGER NOT NULL DEFAULT 0`
- `profile_json TEXT NOT NULL`
- `workout_plan_json TEXT NOT NULL`
- `generation_status TEXT NOT NULL`
- `error_code TEXT`
- `latency_ms INTEGER`
- `used_fallback INTEGER NOT NULL DEFAULT 0`
- `trace_id TEXT`
- `trace_enabled INTEGER NOT NULL DEFAULT 0`

Notes:

- keep `profile_json` and `workout_plan_json` denormalized
- store retrieved chunk IDs as JSON text
- keep fallback and latency metadata on the generation row so feedback review
  can reuse one stable request ID
- keep `trace_id` explicit so operators can move from D1 review to Langfuse
  without recomputing the join

### `plan_feedback`

Purpose:

- stores one or more feedback submissions tied to a generated plan

Fields:

- `id INTEGER PRIMARY KEY AUTOINCREMENT`
- `request_id TEXT NOT NULL`
- `created_at TEXT NOT NULL`
- `usefulness_rating INTEGER NOT NULL`
- `difficulty_feedback TEXT NOT NULL`
- `felt_safe INTEGER NOT NULL`
- `would_follow_plan INTEGER NOT NULL`
- `feedback_text TEXT`
- `feedback_channel TEXT NOT NULL DEFAULT 'public_mvp'`
- `feedback_json TEXT NOT NULL`
- `runtime_metadata_json TEXT NOT NULL DEFAULT '{}'`

Notes:

- `request_id` references `generation_runs.request_id`
- `runtime_metadata_json` is the escape hatch for light metadata attachment in
  the MVP without premature schema expansion
- keep booleans as integer `0/1` values for SQLite/D1 compatibility
- `feedback_json` keeps the saved user response snapshot explicit even though
  the individual columns remain queryable
- Phase 5 runtime metadata remains intentionally small:
  - `generated_at`
  - `model_name`
  - `latency_ms`
  - `used_fallback`
  - `retrieved_chunk_count`
  - `retrieved_chunk_ids`
  - `safety_trigger_codes`
  - `trace_id`
  - `trace_enabled`
  - `langfuse_host`

## Feedback Review Surface

The first review surface should stay operator-focused and lightweight.

Current local reference endpoint:

- `GET /feedback/review`

Design constraints:

- newest feedback first
- simple debugging filters only
- direct visibility into request ID, qualitative feedback, fallback status,
  retrieval strength, and safety-trigger context
- no broad analytics or BI layer

This page is intentionally a thin review adapter, not a separate reporting
subsystem.

## Future Tracing Connection

Phase 4 does not add Langfuse yet. It prepares for Phase 5 by preserving:

- one stable `request_id` per generation
- one linked `request_id` per feedback submission
- enough runtime metadata to create trace links and eval cases without changing
  the feedback contract again

When Langfuse is added, the intended join path is:

1. generation request/trace uses the existing `request_id`
2. feedback row already stores that same `request_id`
3. operator review can move from local metadata inspection to direct trace
   correlation without a persistence redesign

## Environment Variables and Bindings

### Required Cloudflare binding

- `FITCOACH_DB`
  - D1 database binding used for generation metadata and feedback persistence

### Required Worker environment variables

- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `QDRANT_URL`
- `QDRANT_API_KEY`
- `QDRANT_COLLECTION`

### Optional Worker environment variables for Langfuse tracing

- `LANGFUSE_PUBLIC_KEY`
- `LANGFUSE_SECRET_KEY`
- `LANGFUSE_BASE_URL`
  - default: `https://cloud.langfuse.com`
  - override this for self-hosted Langfuse or a different regional host

### Recommended Worker environment variables

- `APP_ENV`
- `APP_VERSION`
- `OPENAI_TIMEOUT_MS`
- `RAG_EMBEDDING_PROVIDER`
- `RAG_EMBEDDING_MODEL`
- `RAG_EMBEDDING_DIMENSIONS`
- `RAG_RETRIEVAL_LIMIT`
- `PUBLIC_APP_NAME`

### Deferred but reserved for later phases

Langfuse is now part of Phase 5 for the public Worker path. The local FastAPI
reference app can display trace metadata if present in saved feedback, but
trace creation itself happens in the Cloudflare Worker flow used by `wrangler dev`
and production deploys.

## Langfuse Tracing Contract

The first tracing schema is intentionally small.

Per public generation request:

- one Langfuse trace keyed by the existing `request_id`
- one retrieval span with:
  - retrieval query
  - retrieved chunk IDs
  - retrieved chunk count
  - retrieval degraded/failed indicator
- one generation observation with:
  - model name
  - structured prompt input
  - output plan or error code
  - token usage when OpenAI returns usage
  - fallback indicator
  - refusal indicator
  - safety trigger codes

Why this shape:

- operators already debug from feedback rows and request IDs
- the trace should answer "what did retrieval return, what model path ran, and did fallback/refusal happen?"
- broader analytics and prompt-experiment infrastructure are deliberately out of scope

## Fail-Open Policy

Langfuse must never become a hard dependency for the public MVP.

Current behavior:

- if Langfuse keys are absent, generation and feedback continue normally
- if Langfuse ingestion fails, generation still returns and feedback still saves
- trace submission is scheduled asynchronously from the Worker via `waitUntil`
- persistence happens before trace submission so operator evidence is not lost during an observability outage

## Canonical Debug Workflow

When a tester leaves poor feedback:

1. Open the feedback review surface and locate the row by time or rating.
2. Copy the saved `request_id`.
3. Check the same row for:
   - fallback status
   - retrieved chunk count and chunk IDs
   - safety trigger codes
   - `trace_id`
4. If `trace_enabled` is true, search Langfuse for that `trace_id`.
5. Inspect:
   - retrieval span output for missing or weak grounding
   - generation observation for model, latency, usage, fallback, or refusal
6. If `trace_enabled` is false, use the persisted request metadata and feedback row as the source of truth; tracing was intentionally disabled for that run.

This is the intended operator join:

- `plan_feedback.request_id`
- `generation_runs.request_id`
- `generation_runs.trace_id`
- Langfuse `trace.id`

## Cloudflare Deployment Checks

Required before deploy:

1. Confirm the D1 binding name remains `FITCOACH_DB`.
2. Confirm `OPENAI_API_KEY` and `QDRANT_API_KEY` secrets are set.
3. If tracing is desired, also set:
   - `LANGFUSE_PUBLIC_KEY`
   - `LANGFUSE_SECRET_KEY`
4. Confirm `LANGFUSE_BASE_URL` in `wrangler.toml` or per-environment vars if not using the default host.

Suggested verification after deploy:

1. Submit one workout-plan request with a known `X-Request-ID`.
2. Submit feedback for that generated plan.
3. Confirm:
   - D1 contains the `generation_runs` row
   - D1 feedback metadata contains the same `request_id` and `trace_id`
   - Langfuse contains the matching trace when tracing is enabled

## External Provider Assumptions

- OpenAI remains the plan-generation provider
- Qdrant remains the external retrieval store
- D1 stores only feedback and lightweight runtime metadata
- the Cloudflare Worker is responsible for outbound provider calls

Do not introduce extra queues, background workers, or multi-service orchestration
in the MVP path unless a concrete Cloudflare limitation forces it later.

## Legacy Paths to Deprecate

Treat these as legacy after Phase 1:

- `render.yaml`
- Render Blueprint deployment instructions in the repo root docs
- any assumption that `DATABASE_URL=sqlite:///...` is the production default
- any assumption that Jinja server rendering is the preferred public UI model

Local FastAPI development remains useful, but it is no longer the production
deployment target.

## Phase 2 Implementation Boundary

Phase 2 should implement only:

1. a Worker-based public API surface
2. D1 write/read adapter for `generation_runs` and `plan_feedback`
3. static public UI served by Cloudflare
4. OpenAI and Qdrant calls from the Worker runtime

Phase 2 should not reopen these decisions unless one of these assumptions fails:

- Worker runtime can reach OpenAI and Qdrant directly
- the narrow workout-plan flow fits within Worker execution limits
- the required public UI can be served as static assets plus Worker APIs

## Executable Setup Steps

### 1. Create the D1 database

```bash
npx wrangler d1 create fitcoach-ai
```

Copy the resulting database ID into `wrangler.toml`.

### 2. Create local development secrets

Copy `.dev.vars.example` to `.dev.vars` and set:

```bash
OPENAI_API_KEY=...
QDRANT_URL=...
QDRANT_API_KEY=...
```

### 3. Apply the initial schema

```bash
npx wrangler d1 migrations apply FITCOACH_DB --local
npx wrangler d1 migrations apply FITCOACH_DB --remote
```

### 4. Set Cloudflare secrets for remote deploy

```bash
npx wrangler secret put OPENAI_API_KEY
npx wrangler secret put QDRANT_API_KEY
```

Set plain environment values in `wrangler.toml` or through the Cloudflare
dashboard for:

- `OPENAI_MODEL`
- `QDRANT_URL`
- `QDRANT_COLLECTION`
- `APP_ENV`
- `APP_VERSION`
- `OPENAI_TIMEOUT_MS`
- `RAG_EMBEDDING_PROVIDER`
- `RAG_EMBEDDING_MODEL`
- `RAG_EMBEDDING_DIMENSIONS`
- `RAG_RETRIEVAL_LIMIT`

### 5. Run the Worker locally

```bash
npx wrangler dev
```

### 6. Implemented public routes

The current Worker path serves:

- `GET /`
- `POST /api/workout-plans`
- `POST /api/feedback`
- `GET /health`

### 7. Deploy the Worker

```bash
npx wrangler deploy
```

### 8. Validate the public path

Minimum production checks:

- `GET /health` returns `200`
- one workout plan can be generated from the public form
- one feedback submission persists to D1
- the saved feedback row is linked to a generated `request_id`

Focused repo-level validation commands:

```bash
node --test cloudflare/worker.test.mjs
cd backend && UV_CACHE_DIR=/tmp/uv-cache uv run ruff check app/core/settings.py app/feedback/store.py tests/api/test_web_home.py tests/api/test_generate_workout_plan.py
cd backend && UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/api/test_web_home.py tests/api/test_generate_workout_plan.py -q
```

## Remaining Risks After Phase 2

- Worker-side OpenAI and Qdrant networking still need end-to-end validation
  with real secrets and a real D1 database in this environment.
- The Worker currently ports the minimal prompt, retrieval, validation, and
  fallback logic directly in JavaScript instead of reusing the Python service
  module at runtime.
- The public UI is intentionally narrow and English-only in this phase; the
  Vietnamese localization and richer review surfaces remain future work.
