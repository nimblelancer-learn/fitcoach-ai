# Knowledge Base

This directory contains the starter retrieval corpus for FitCoach AI.

The v1 goal is narrow on purpose:

- cover low-risk beginner fitness topics
- keep documents easy to chunk in later RAG issues
- make provenance and document status explicit

Current layout:

- `raw/`: authored markdown documents that are ready for chunking
- `processed/`: reserved for normalized chunk outputs in later issues
- `source-policy.md`: rules for what content may enter the corpus
- `sources.md`: inventory of the current documents and their provenance status

Each raw document should include metadata front matter with a stable
`document_id`, a `topic`, and a `status` so downstream indexing code can attach
predictable metadata without guesswork.
