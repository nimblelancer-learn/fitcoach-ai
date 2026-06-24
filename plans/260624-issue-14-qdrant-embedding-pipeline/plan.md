---
title: GitHub issue 14 qdrant and embedding pipeline
description: >-
  Plan for adding a local Qdrant indexing pipeline, embedding-provider
  configuration, a re-index command, and validation that knowledge-base chunks
  are stored with metadata in the vector collection.
status: in-progress
priority: P1
branch: issue-14-qdrant-embedding-pipeline
tags:
  - rag
  - qdrant
  - github-issues
blockedBy: []
blocks: []
created: '2026-06-24T17:16:51.312Z'
createdBy: 'ck:plan'
source: skill
---

# GitHub issue 14 qdrant and embedding pipeline

## Overview

The repository already has chunked knowledge-base output and a Docker Compose
service for Qdrant, but it lacks the actual indexing path that creates a
collection, produces embeddings, and stores chunk metadata. This plan keeps the
scope narrow by adding a deterministic local hash embedder for credential-free
development while still allowing OpenAI embeddings through environment config.
It also adds a single re-index command and validates the flow against a live
local Qdrant instance.

## Phases

| Phase | Name | Status |
|-------|------|--------|
| 1 | [Review Qdrant and embedding contract](./phase-01-review-qdrant-and-embedding-contract.md) | Completed |
| 2 | [Implement indexing pipeline](./phase-02-implement-indexing-pipeline.md) | In Progress |
| 3 | [Validate local commands and docs](./phase-03-validate-local-commands-and-docs.md) | In Progress |

## Dependencies

- Existing chunk artifact generation in `backend/app/rag/chunking.py`
- Existing local Qdrant service definition in `docker-compose.yml`
- Existing environment configuration surface in `.env.example` and
  `backend/app/core/settings.py`
- No linked GitHub Project item was present for issue `#14`, so there is no
  `Evidence` field dependency for this issue

## Success Criteria

- [ ] Qdrant collection creation is automated from the indexing command
- [ ] Knowledge-base chunks can be embedded with a configured provider
- [ ] Embeddings and chunk metadata are written to Qdrant
- [ ] Re-indexing is available through a documented local command
- [ ] Tests and docs cover the local pipeline and provider configuration
