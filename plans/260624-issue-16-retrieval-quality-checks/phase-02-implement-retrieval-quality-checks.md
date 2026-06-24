---
phase: 2
title: Implement retrieval quality checks
status: completed
priority: P2
effort: 1h
dependencies:
  - 1
---

# Phase 2: Implement retrieval quality checks

## Overview

Implement the code needed to exercise retrieval quality locally and expose an
optional metadata-filtering hook without changing default request behavior.

## Requirements

- Functional: add a reusable metadata filter parameter from retriever to Qdrant
  search.
- Functional: add tests that run representative queries against the processed
  chunk corpus and verify relevant topics/chunks rank at the top.
- Non-functional: keep tests deterministic by using local embeddings and an
  in-memory fake search layer.

## Architecture

Thread a simple `metadata_filter: dict[str, str] | None` argument through
`KnowledgeRetriever.retrieve()` into `QdrantClient.search_points()`. In tests,
simulate Qdrant search by computing cosine-style similarity over chunk vectors
and applying the same payload filtering rules in memory.

## Related Code Files

- Modify: `backend/app/rag/retriever.py`
- Modify: `backend/app/rag/qdrant_client.py`
- Create: `backend/tests/rag/test_retrieval_quality.py`

## Implementation Steps

1. Extend the retriever and Qdrant client search contract for optional metadata
   filtering.
2. Build retrieval quality tests around the processed chunk artifact and
   representative user questions.
3. Add assertions for both relevance and filter behavior.

## Success Criteria

- [ ] Retrieval accepts an optional metadata filter without breaking current
  callers.
- [ ] Quality tests cover multiple query intents and pass locally.
- [ ] Filtering tests prove payload constraints narrow results correctly.
