---
phase: 1
title: Review deployment surface
status: completed
priority: P1
effort: 1h
dependencies: []
---

# Phase 1: Review deployment surface

## Overview

Review the current repository surface for deployment readiness, identify the
minimal code and infrastructure changes needed for a public MVP, and reduce the
frontend/deployment decision to a concrete approval boundary.

## Requirements

- Functional: inventory current backend, template, Docker, env, and test
  surfaces
- Functional: map issue acceptance criteria to current repo artifacts and gaps
- Functional: identify the narrowest deployment path that satisfies both
  backend and frontend requirements
- Non-functional: avoid speculative infrastructure or a new frontend stack
  unless explicitly chosen

## Architecture

Current deployable assets:

- FastAPI app factory in `backend/app/main.py`
- JSON generation endpoint in `backend/app/api/routes_generate.py`
- server-rendered Jinja infrastructure already used by
  `backend/app/api/routes_learning.py`
- Docker image definition in `backend/Dockerfile`
- local Qdrant container definition in `docker-compose.yml`
- runtime env surface in `.env.example`

Current gap:

- no user-facing MVP route for workout-plan generation exists yet
- no production deployment config is committed yet
- no public URLs or maintenance docs exist yet

## Related Code Files

- Inspect: `backend/app/main.py`
- Inspect: `backend/app/api/routes_generate.py`
- Inspect: `backend/app/api/routes_learning.py`
- Inspect: `backend/Dockerfile`
- Inspect: `.env.example`
- Inspect: `Makefile`

## Implementation Steps

1. Verify the current repo and GitHub issue acceptance criteria.
2. Inspect the application surface for deployable backend and reusable UI
   primitives.
3. Compare same-stack and standalone-frontend approaches against current repo
   structure.
4. Record the recommended option and why it is the smallest viable `M4` path.

## Success Criteria

- [ ] Current deployment surface and gaps are documented.
- [ ] The frontend/deployment choice is reduced to a single explicit user
      approval.
- [ ] Phase 2 can start immediately once the user confirms the option.
