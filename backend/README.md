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

Run the opt-in OpenAI integration test only when you want a real provider call:

```bash
cd backend
RUN_OPENAI_INTEGRATION=1 OPENAI_API_KEY=... OPENAI_MODEL=gpt-4.1-mini uv run pytest tests/integration/test_openai_workout_plan_integration.py -q
```
