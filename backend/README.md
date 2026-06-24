## Running the backend

```bash
cd backend
uv sync
uv run fastapi dev app/main.py
```

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

The repo's safety boundary and medical-scope policy lives in `../docs/safety-policy.md`.

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

Run the local backend test suite:

```bash
cd backend
uv run pytest tests -q
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
