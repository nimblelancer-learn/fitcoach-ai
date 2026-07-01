---
title: GitHub issue 42 deploy MVP backend and frontend
description: ''
status: in-progress
priority: P2
branch: main
tags: []
blockedBy: []
blocks: []
created: '2026-06-30T15:09:49.445Z'
createdBy: 'ck:plan'
source: skill
---

# GitHub issue 42 deploy MVP backend and frontend

## Overview

Issue `#42` requires a public backend and frontend, documented environment
variables, a deployed app database and vector store, end-to-end validation of
the main workout-plan flow, and a public demo link in `README.md`.

The repository already contains a deployable FastAPI backend, Jinja template
support, and Docker packaging, but it does not contain a standalone frontend
application. That makes the deployment/frontend choice the primary decision
gate for this issue.

Recommended path:

- build a minimal MVP frontend inside the existing FastAPI app
- deploy a single backend-plus-UI service
- use the existing request/response contract at `/generate/workout-plan`

Alternative path:

- add a separate frontend app now and deploy backend/frontend independently

The recommended path is lower-risk for `M4` because it avoids creating a new
frontend stack, build pipeline, and deployment surface during the deployment
milestone itself.

## Phases

| Phase | Name | Status |
|-------|------|--------|
| 1 | [Review deployment surface](./phase-01-review-deployment-surface.md) | Completed |
| 2 | [Implement deployment path](./phase-02-implement-deployment-path.md) | Completed |
| 3 | [Validate deployed MVP](./phase-03-validate-deployed-mvp.md) | In Progress |

## Dependencies

- Depends on the milestone execution queue in
  `plans/260630-github-milestone-execution/`
- Must preserve the API, safety, and retrieval contracts already implemented in
  `backend/app`
- Must produce public URLs that later issues `#43` and `#44` can consume

## Decision Checkpoint

Before Phase 2 starts, confirm one of:

1. Same-stack MVP frontend inside the FastAPI app
2. New standalone frontend app

If option 1 is selected, the issue stays inside current repo architecture and
targets a single deployable service plus external stateful dependencies.

If option 2 is selected, the issue expands to include frontend scaffolding,
frontend build/deploy config, CORS/API wiring, and an additional validation
surface.
