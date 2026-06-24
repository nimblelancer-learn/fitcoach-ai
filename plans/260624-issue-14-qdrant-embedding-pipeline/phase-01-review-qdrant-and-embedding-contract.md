---
phase: 1
title: Review Qdrant and embedding contract
status: completed
priority: P1
effort: 30m
dependencies: []
---

# Phase 1: Review Qdrant and embedding contract

## Overview

Define the minimum indexing contract needed for the next retrieval issue: how
chunks become vectors, which settings control the provider and collection, and
what metadata gets stored alongside each point in Qdrant.

## Requirements

- Functional: Create or reuse a Qdrant collection, generate vectors for each
  chunk, and preserve chunk metadata in payload fields.
- Non-functional: Keep local validation possible without external credentials.

## Architecture

The indexing pipeline should build on the existing chunking module rather than
reading ad hoc files. The contract is:

1. `build_chunk_artifact()` provides normalized chunk records
2. `EmbeddingClient` turns chunk text into vectors via either `local-hash` or
   `openai`
3. `QdrantClient` ensures the collection exists and upserts point records
4. a CLI entrypoint invokes the full flow

Point IDs should be stable and Qdrant-compatible, so they should be derived from
`chunk_id` rather than using the raw chunk ID directly.

## Related Code Files

- Create: `backend/app/rag/embeddings.py`
- Create: `backend/app/rag/qdrant_client.py`
- Create: `backend/app/rag/index.py`
- Modify: `backend/app/core/settings.py`
- Modify: `Makefile`
- Modify: `backend/README.md`
- Modify: `.env.example`

## Implementation Steps

1. Decide which settings govern provider selection, vector dimensions, and
   Qdrant collection details.
2. Define how point payloads should preserve chunk metadata for later prompt
   grounding.
3. Lock the local validation path so the issue can finish without requiring a
   real embedding API key.

## Success Criteria

- [ ] The embedding and Qdrant settings are explicit.
- [ ] The local default provider supports end-to-end indexing without secrets.
- [ ] Stable point-ID rules are defined before implementation.

## Risk Assessment

The largest risk is coupling issue completion to external credentials. The
mitigation is a deterministic local embedder that keeps the pipeline testable
while preserving an OpenAI path for higher-quality embeddings later.
