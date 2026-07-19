## Running the backend

```bash
cd backend
uv sync
uv run fastapi dev app/main.py
```

The same-stack MVP web demo is currently served from the same FastAPI
application at `/`. After a plan is generated, the same web surface can also
post user feedback to `/feedback`, storing the request context and generated
plan snapshot for later review.

This remains useful for local development, but it is now a legacy production
shape. The production target is a Cloudflare Worker plus D1 path documented in
[`../docs/cloudflare-migration-guide.md`](../docs/cloudflare-migration-guide.md).

## Cloudflare Public MVP

The public MVP no longer deploys this FastAPI app directly.

- runtime entrypoint: [`../cloudflare/worker.mjs`](../cloudflare/worker.mjs)
- static UI: [`../public/index.html`](../public/index.html)
- D1 schema: [`../cloudflare/d1/migrations/0001_feedback_runtime_metadata.sql`](../cloudflare/d1/migrations/0001_feedback_runtime_metadata.sql)
- Worker config: [`../wrangler.toml`](../wrangler.toml)

Use this local validation flow for the public path from the repo root:

```bash
cp .dev.vars.example .dev.vars
npx wrangler d1 create fitcoach-ai
npx wrangler d1 migrations apply FITCOACH_DB --local
npx wrangler dev
```

The Worker serves:

- `GET /`
- `POST /api/workout-plans`
- `POST /api/feedback`
- `GET /health`

## Environment

Set these values in the project `.env` file before testing the live OpenAI path:

```bash
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4.1-mini
OPENAI_TIMEOUT_SECONDS=20
OPENAI_INVALID_OUTPUT_RETRIES=2
OPENAI_INPUT_COST_PER_MILLION_TOKENS_USD=
OPENAI_OUTPUT_COST_PER_MILLION_TOKENS_USD=
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
QDRANT_COLLECTION=fitcoach_knowledge
RAG_EMBEDDING_PROVIDER=local-hash
RAG_EMBEDDING_MODEL=text-embedding-3-small
RAG_EMBEDDING_DIMENSIONS=256
RAG_RETRIEVAL_LIMIT=3
```

For local indexing without external credentials, the default
`RAG_EMBEDDING_PROVIDER=local-hash` uses a deterministic hash-based embedder.
Switch to `RAG_EMBEDDING_PROVIDER=openai` when `OPENAI_API_KEY` is configured
and you want real provider embeddings.

For the legacy Render deployment path in issue `#42`, the repository uses:

- `render.yaml` for the Blueprint definition
- a persistent disk mounted at `/var/data`
- `DATABASE_URL=sqlite:////var/data/fitcoach_ai.db` for the legacy MVP app database
- a managed Qdrant endpoint supplied through `QDRANT_URL` and `QDRANT_API_KEY`
- `OPENAI_MODEL=gpt-4.1-mini` for generation
- `RAG_EMBEDDING_PROVIDER=openai` with
  `RAG_EMBEDDING_MODEL=text-embedding-3-small` for retrieval embeddings

The repo's safety boundary and medical-scope policy lives in `../docs/safety-policy.md`.

## Cloudflare Production Target

The public MVP target is no longer same-stack FastAPI hosting.

- public runtime: Cloudflare Worker
- public UI: static assets served by Cloudflare
- public persistence: D1
- local FastAPI app: engineering and migration reference surface

Do not add new production assumptions that depend on Jinja rendering or
SQLite file persistence.

## Runtime safety guardrails

The current backend also applies a lightweight safety layer at the OpenAI client
boundary.

- high-risk medical or rehabilitation keywords in the prompt can short-circuit
  into a conservative structured fallback plan
- beginner plans are rejected if they contain `high` intensity prescriptions
- beginner plans are rejected if they contain a small denylist of clearly risky
  exercise names such as Olympic-lift or max-sprint patterns
- safety trigger events are logged with stable trigger codes for debugging

These are intentionally basic v1 guardrails. They do not replace clinical
screening or comprehensive policy enforcement.

## Local Qdrant indexing

Start Qdrant:

```bash
make qdrant-up
```

Build or refresh the knowledge-base collection:

```bash
make reindex-kb
```

Workout generation now queries the indexed knowledge base before calling the
LLM. The `/generate/workout-plan` response includes:

- `X-RAG-Chunk-Count`: how many chunks were injected into the grounded prompt
- `X-RAG-Chunk-Ids`: up to the first three retrieved chunk IDs for debugging

## Test Commands

Run the Cloudflare Worker smoke tests:

```bash
node --test cloudflare/worker.test.mjs
```

Run the local backend test suite:

```bash
cd backend
uv run pytest tests -q
```

Focused validation for the same-stack MVP web surface:

```bash
cd backend
UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/api/test_web_home.py tests/api/test_generate_workout_plan.py tests/test_learning_portal.py -q
```

Run the focused retrieval quality checks:

```bash
cd backend
uv run pytest tests/rag/test_retriever.py tests/rag/test_retrieval_quality.py tests/rag/test_index.py -q
```

Run the opt-in OpenAI integration test only when you want a real provider call:

```bash
cd backend
RUN_OPENAI_INTEGRATION=1 OPENAI_API_KEY=... OPENAI_MODEL=gpt-4.1-mini uv run pytest tests/integration/test_openai_workout_plan_integration.py -q
```

## Local Learning Quiz CLI

System overview:

- `../docs/local-learning-system-overview.md`

Run the local-only quiz CLI against one curated exercise pack:

```bash
cd backend
uv run python -m app.learning.quiz.cli --topic pyproject-and-uv-lock
```

This local-only CLI is intentionally isolated from FastAPI runtime wiring and
the `ENABLE_DEV_LEARNING_PORTAL` feature flag. It reads one TOML pack from
`app/learning/exercises/`, renders one question at a time in the terminal, and
prints a compact summary at the end.

Supported question modes:

- `multiple_choice`
- `short_answer`
- `self_check`
- `explain_back` with self-marked expected-point coverage
- `prediction` with repo-specific scenarios, expected outcomes, and manual follow-up checks

Current starter topics:

- `pyproject-and-uv-lock`
- `app-main-and-learning-portal`
- `runtime-and-workflow-predictions`

Focused validation for the quiz package:

```bash
cd backend
uv run ruff check app/learning/quiz tests/learning/test_quiz_cli.py
uv run pytest tests/learning/test_quiz_cli.py -q
```

## Local Repo Drills

Run the separate drill runner when you want bounded repo tasks instead of
ordinary quiz prompts:

```bash
cd backend
uv run python -m app.learning.drills.runner --topic repo-drills
```

Repo drills differ from quizzes in one important way: quizzes stop at answer
reveal and self-review, while drills ask you to produce a local artifact,
choose a focused regression target, or run one bounded validation hook.

Current drill set:

- `repo-drills`

Focused validation for the drill runner:

```bash
cd backend
uv run ruff check app/learning/drills tests/learning/test_repo_drills.py
uv run pytest tests/learning/test_repo_drills.py -q
```

## Retrieval quality notes

The retrieval quality harness uses the checked-in `knowledge_base/processed/chunks-v1.json`
artifact plus the deterministic `local-hash` embedder. It is intended to catch
obvious regressions in query-to-chunk relevance without requiring a live Qdrant
instance.

Known early failure cases:

- Broad or ambiguous queries can still rank a nearby chunk above the best chunk.
  For example, safety wording may overlap with the shorter foundations safety
  chunk unless a metadata filter narrows the search.
- `local-hash` embeddings are only a local approximation. Passing tests do not
  guarantee the same ranking quality when `RAG_EMBEDDING_PROVIDER=openai`.
- The checks only cover the current curated corpus. Missing or weak source
  documents will still produce weak retrieval even when the harness passes.
- Empty query strings or `RAG_RETRIEVAL_LIMIT <= 0` return no chunks by design.
- Metadata filtering is exact-match only. A wrong filter key or value can
  silently over-constrain retrieval and produce empty results.
