---
phase: 2
title: Implement deployment path
status: completed
priority: P1
effort: 4-8h
dependencies:
  - 1
---

# Phase 2: Implement deployment path

## Overview

Implement the chosen deployment path, keeping the diff small and biased toward
shipping a working public MVP rather than introducing a broader application
architecture.

## Requirements

- Functional: provide a public backend URL
- Functional: provide a public frontend/demo URL
- Functional: connect the frontend to the deployed generation API
- Functional: document required environment variables and services
- Functional: provision deployed app database and vector database integration
- Non-functional: preserve existing product language and safety constraints
- Non-functional: keep new infrastructure and code paths minimal

## Architecture

Recommended implementation if same-stack is chosen:

- add a small MVP UI route inside FastAPI for entering a profile and rendering a
  generated workout plan
- reuse Jinja templates rather than introducing a new build system
- keep generation requests server-side or same-origin to avoid extra CORS work
- introduce only the minimal persistence required for feedback-ready `M4`
  follow-up issues

Alternative implementation if standalone frontend is chosen:

- add a new frontend app directory and package manager surface
- create API integration for `/generate/workout-plan`
- add separate frontend deployment configuration and environment wiring
- update backend CORS and deployment docs

## Related Code Files

- Modify: `backend/app/main.py`
- Create or modify: `backend/app/api/routes_web.py`
- Create: `backend/app/templates/*` or equivalent template directory
- Modify: `backend/Dockerfile`
- Modify: `.env.example`
- Modify: `README.md`
- Modify or create: deployment config files for the chosen host
- Modify: `backend/tests/api/*`

## Implementation Steps

1. Create `issue-42-...` branch.
2. Implement the chosen MVP frontend/deployment path.
3. Add or update deployment config, runtime env docs, and service wiring.
4. Add regression tests for the new user-facing surface and any deployment
   behavior that is testable locally.
5. Run lint, tests, build/image validation, and issue-specific smoke checks.

## Success Criteria

- [ ] The repo contains the chosen frontend and deployment implementation.
- [ ] Local validation passes for code and the new user-facing flow.
- [ ] Deployment documentation is sufficient to reproduce the public MVP.
