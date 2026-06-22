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
```
