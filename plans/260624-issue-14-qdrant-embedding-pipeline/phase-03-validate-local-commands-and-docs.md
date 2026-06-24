---
phase: 3
title: Validate local commands and docs
status: in-progress
priority: P1
effort: 1h
dependencies:
  - 2
---

# Phase 3: Validate local commands and docs

## Overview

Lock in the local workflow with tests, docs, and one real indexing run. This
phase ensures the issue closes with concrete evidence instead of only unit-level
confidence.

## Requirements

- Functional: Document Qdrant startup, reindexing, and provider configuration.
- Non-functional: Keep the validation commands short and reproducible.

## Architecture

Validation should include:

- focused backend tests for embeddings and indexing helpers
- a live local `docker compose up -d qdrant` run
- a real `uv run python -m app.rag.index` or `make reindex-kb` execution

Docs should live in `backend/README.md` and `.env.example` so the local path is
discoverable near the backend setup instructions.

## Related Code Files

- Modify: `backend/README.md`
- Modify: `.env.example`
- Modify: `Makefile`

## Implementation Steps

1. Run targeted tests for the new RAG indexing modules.
2. Start local Qdrant and execute the indexing command.
3. Capture collection evidence such as point count and vector size.
4. Update issue-facing documentation and validation notes.

## Success Criteria

- [ ] The live local Qdrant collection contains indexed chunk points.
- [ ] The backend setup docs explain how to rerun the pipeline.
- [ ] Validation output is concrete enough to cite in the issue comment and PR.

## Risk Assessment

The main risk is local-environment drift between docs and commands. Mitigation:
validate against the actual Docker Compose service and the documented reindex
command before closing the issue.
