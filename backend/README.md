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
```

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
