---
phase: 2
title: Execute M4
status: in-progress
priority: P1
effort: 1-2d
dependencies:
  - 1
---

# Phase 2: Execute M4

## Overview

Finish all executable `M4` work before starting `M5`, using one branch per
issue and the GitHub issue workflow for each lifecycle. Issue `#42` is the
first implementation gate because the repo currently has no separate frontend
application, so deployment requires a user-approved frontend/deployment
approach before code changes begin.

## Requirements

- Functional: complete `#42`, `#44`, `#43`, and `#41` in dependency order when
  possible
- Functional: use a dedicated branch, validation loop, commit, push, PR,
  comment, and closure flow for each issue
- Functional: reassess remaining `M4` queue after each issue
- Non-functional: avoid adding a speculative new frontend stack unless the user
  explicitly chooses that direction
- Non-functional: preserve existing product language and keep UI changes lean

## Architecture

Planned `M4` sequence:

1. `#42` Deployment
   Decision gate: same-stack FastAPI-served MVP frontend vs new standalone
   frontend app.
2. `#44` Feedback flow
   Depends on the live product surface from `#42`.
3. `#43` Demo link and changelog
   Depends on the public demo URL from `#42` and should reflect actual shipped
   behavior.
4. `#41` First real-user feedback
   Depends on deployed product plus feedback collection and may be partially
   blocked by external user availability.

## Related Code Files

- Modify: `backend/app/**` as needed for `#42` and `#44`
- Modify: `backend/tests/**` for new backend or UI route coverage
- Modify: `README.md`
- Modify: `.env.example`
- Modify: deployment config files introduced or updated for the chosen hosting path

## Implementation Steps

1. Resolve the `#42` deployment/frontend decision with the user.
2. Create a dedicated issue plan for `#42`, implement, validate, and ship it.
3. Reassess codebase and deployment output, then plan and execute `#44`.
4. Update public docs and changelog in `#43` using the actual deployed URLs and
   known limitations.
5. Attempt `#41` only after deployment and feedback collection are live; if the
   issue cannot be completed without external user activity, document the exact
   blocker and evidence.

## Success Criteria

- [ ] `#42` is completed through deployed public URLs and GitHub workflow.
- [ ] `#44` is completed through collection, persistence, traceability, and a
      review surface.
- [ ] `#43` is completed with accurate public docs and changelog content.
- [ ] `#41` is either completed with real-user evidence or explicitly blocked by
      external-world constraints after the prerequisites are live.
