# Processed Knowledge Base Outputs

This directory stores normalized chunk outputs and later retrieval-ready assets.

Current artifact:

- `chunks-v1.json`: deterministic chunk records derived from
  `knowledge_base/raw/`

Each chunk record preserves document metadata and adds:

- `chunk_id`
- `chunk_index`
- `section_path`
- `word_count`
- `text`

Regenerate the file with:

```bash
cd backend
uv run python -m app.rag.chunking
```
