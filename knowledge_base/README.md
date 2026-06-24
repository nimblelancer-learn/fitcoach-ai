# Knowledge Base

This directory contains the starter retrieval corpus for FitCoach AI.

The v1 goal is narrow on purpose:

- cover low-risk beginner fitness topics
- keep documents easy to chunk in later RAG issues
- make provenance and document status explicit

Current layout:

- `raw/`: authored markdown documents that are ready for chunking
- `processed/`: normalized chunk outputs for downstream RAG work
- `source-policy.md`: rules for what content may enter the corpus
- `sources.md`: inventory of the current documents and their provenance status

Each raw document should include metadata front matter with a stable
`document_id`, a `topic`, and a `status` so downstream indexing code can attach
predictable metadata without guesswork.

## Chunking Output

The current processor writes `processed/chunks-v1.json`.

The chunking strategy is intentionally simple:

- parse raw markdown front matter as document-level metadata
- keep heading context while splitting body content into paragraph or list-based
  units
- merge adjacent units into bounded chunks so the corpus stays readable and
  deterministic
- emit stable `chunk_id` values in document order

Regenerate the processed artifact with:

```bash
cd backend
uv run python -m app.rag.chunking
```
