---
phase: 2
title: Implement indexing pipeline
status: in-progress
priority: P1
effort: 2h
dependencies:
  - 1
---

# Phase 2: Implement indexing pipeline

## Overview

Build the embedding and Qdrant modules plus the CLI indexing entrypoint. The
result should be able to create the collection and upsert chunk vectors into a
running local Qdrant instance with a single command.

## Requirements

- Functional: Support local-hash and OpenAI embedding providers, ensure the
  Qdrant collection exists, and upsert vectors with payload metadata.
- Non-functional: Avoid unnecessary third-party Qdrant dependencies; use the
  current dependency set when possible.

## Architecture

The implementation should separate concerns:

- `embeddings.py` handles provider-specific vector generation
- `qdrant_client.py` handles REST calls to Qdrant
- `index.py` orchestrates chunk loading, embedding, collection setup, and
  upsert

The Makefile should expose a single `reindex-kb` command that routes to the
indexer entrypoint.

## Related Code Files

- Create: `backend/app/rag/embeddings.py`
- Create: `backend/app/rag/qdrant_client.py`
- Create: `backend/app/rag/index.py`
- Create: `backend/tests/rag/test_embeddings.py`
- Create: `backend/tests/rag/test_index.py`
- Modify: `backend/app/core/settings.py`
- Modify: `Makefile`

## Implementation Steps

1. Add embedding-provider settings and implement the local hash embedder plus
   the OpenAI provider path.
2. Add a small Qdrant REST client that can create or inspect the configured
   collection and upsert points.
3. Add the indexing entrypoint and Makefile target, then verify the command
   against a live local Qdrant instance.

## Success Criteria

- [ ] A local command creates or reuses the Qdrant collection.
- [ ] The command stores vectors and metadata for every chunk in the corpus.
- [ ] The implementation is covered by focused unit tests.

## Risk Assessment

The main risk is request-shape mismatch with Qdrant. The mitigation is to
validate the exact request against a live local instance and keep point IDs in a
Qdrant-safe format.
