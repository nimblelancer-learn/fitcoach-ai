---
phase: 1
title: Review retrieval quality contract
status: completed
priority: P2
effort: 20m
dependencies: []
---

# Phase 1: Review retrieval quality contract

## Overview

Define what "basic retrieval quality" means in this repo and identify the
smallest implementation that gives signal without requiring a live Qdrant
instance or external embedding API.

## Requirements

- Functional: add representative retrieval queries and assert top results are
  relevant to the intended topic.
- Functional: support an optional metadata filter path so future call sites can
  narrow retrieval by payload attributes.
- Functional: document failure cases that will still happen with the current
  lightweight embedding strategy.
- Non-functional: keep checks deterministic and cheap enough for local pytest.

## Architecture

Use the existing processed chunk artifact plus `local-hash` embeddings to build
an in-memory retrieval harness inside tests. Extend the retriever/Qdrant
interface with an optional metadata filter that forwards payload constraints to
search. Keep production behavior unchanged when no filter is passed.

## Related Code Files

- Modify: `backend/app/rag/retriever.py`
- Modify: `backend/app/rag/qdrant_client.py`
- Create: `backend/tests/rag/test_retrieval_quality.py`
- Modify: `backend/README.md`
- Modify: `plans/260624-issue-16-retrieval-quality-checks/plan.md`

## Implementation Steps

1. Review current retriever, embeddings, and processed chunk assets.
2. Choose a deterministic relevance-check strategy that does not depend on
   running Qdrant.
3. Define representative queries and expected topic/chunk outcomes.

## Success Criteria

- [x] The scope is limited to deterministic, local retrieval quality checks.
- [x] The implementation path covers tests, optional filtering, and docs.
