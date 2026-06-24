---
phase: 2
title: Implement chunking pipeline
status: completed
priority: P1
effort: ''
dependencies:
  - 1
---

# Phase 2: Implement chunking pipeline

## Overview

Build the actual chunk processor and check in processed sample output. The
implementation should be runnable locally without network access and should fit
the current backend package structure so later RAG modules can import the same
chunking logic instead of duplicating it in standalone scripts.

## Requirements

- Functional: Provide a local command that processes the raw knowledge base and
  writes chunk artifacts with deterministic metadata.
- Non-functional: Avoid third-party parsing dependencies unless the standard
  library is insufficient.

## Architecture

Add a small `backend/app/rag/chunking.py` module with:

- front-matter parsing
- markdown section tracking
- chunk boundary logic
- JSON serialization helpers
- a `main()` entrypoint for CLI execution

Processed output should land in `knowledge_base/processed/` in a predictable
filename such as `chunks-v1.json`.

## Related Code Files

- Create: `backend/app/rag/__init__.py`
- Create: `backend/app/rag/chunking.py`
- Modify: `knowledge_base/processed/README.md`
- Create or modify: `knowledge_base/processed/chunks-v1.json`

## Implementation Steps

1. Implement helpers to enumerate raw markdown files and parse their front
   matter/body split.
2. Add deterministic chunk splitting that prefers heading-aware grouping and a
   bounded chunk size target.
3. Serialize chunk records to a stable JSON artifact in
   `knowledge_base/processed/`.
4. Add a documented command, ideally `uv run python -m app.rag.chunking` from
   the `backend/` directory, and generate the checked-in sample output file.

## Success Criteria

- [ ] A local command produces chunk artifacts from the current raw corpus.
- [ ] Chunk IDs and ordering are stable across repeated runs on unchanged
      input.
- [ ] The repository includes sample processed output derived from the current
      raw documents.

## Risk Assessment

The largest risk is brittle chunk splitting that depends on markdown quirks.
Mitigation: prefer simple heading and paragraph/list boundaries, then test
against all current source documents.
