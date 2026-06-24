---
title: "GitHub issue 15 retrieval and prompt grounding"
description: "Implement Qdrant retrieval, prompt grounding, and endpoint debug evidence for workout generation."
status: completed
priority: P2
branch: "issue-15-retrieval-prompt-grounding"
tags: []
blockedBy: []
blocks: []
created: "2026-06-24T17:29:44.826Z"
createdBy: "ck:plan"
source: skill
---

# GitHub issue 15 retrieval and prompt grounding

## Overview

Issue 15 connects the existing Qdrant index to the workout generation flow.
The backend now retrieves top-k knowledge chunks from the indexed fitness corpus,
injects them into the prompt, logs retrieval evidence, and exposes lightweight
debug headers on the generation endpoint.

## Phases

| Phase | Name | Status |
|-------|------|--------|
| 1 | [Review retrieval integration contract](./phase-01-review-retrieval-integration-contract.md) | Completed |
| 2 | [Implement retriever and grounded generation](./phase-02-implement-retriever-and-grounded-generation.md) | Completed |
| 3 | [Validate retrieval behavior and docs](./phase-03-validate-retrieval-behavior-and-docs.md) | Completed |

## Dependencies

- Issue 14 completed the Qdrant indexing path and collection contract consumed here.

## Outcome

- Added `KnowledgeRetriever` for embedding-backed Qdrant lookup with top-k retrieval.
- Grounded workout prompts with retrieved chunk text and metadata.
- Logged retrieval chunk IDs and exposed `X-RAG-Chunk-Count` / `X-RAG-Chunk-Ids`
  on `/generate/workout-plan`.
- Validated with focused RAG, prompt, service, and API tests.
