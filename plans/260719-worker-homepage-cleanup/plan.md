---
title: "Clean working tree and simplify public homepage"
description: "Stabilize the current Cloudflare deployment branch by removing generated clutter, simplifying the public homepage for desktop-first use, adding a clear English/Vietnamese language toggle, and tightening validation coverage before commit."
status: completed
priority: P2
branch: "main"
tags: [cloudflare, ui, cleanup, testing]
blockedBy: [260714-cloudflare-feedback-launch]
blocks: [260630-issue-42-deploy-mvp-backend-frontend, 260630-github-milestone-execution]
created: "2026-07-19T11:30:00.179Z"
createdBy: "ck:plan"
source: skill
---

# Clean working tree and simplify public homepage

## Overview

The current branch is functionally close to a commitable Cloudflare MVP, but the
working tree is still noisy and the public homepage is carrying too much
portfolio/process language. The public Worker entrypoint also needs a cleaner
desktop layout, a simple Vietnamese/English switch, and tighter regression
coverage so the next autonomous implementation pass can land without guessing.

## Phases

| Phase | Name | Status |
|-------|------|--------|
| 1 | [Audit and cleanup working tree](./phase-01-audit-and-cleanup-working-tree.md) | Completed |
| 2 | [Refactor public homepage UI](./phase-02-refactor-public-homepage-ui.md) | Completed |
| 3 | [Strengthen validation and tests](./phase-03-strengthen-validation-and-tests.md) | Completed |
| 4 | [Prepare commit strategy and autonomous goal prompt](./phase-04-prepare-commit-strategy-and-autonomous-goal-prompt.md) | Completed |

## Dependencies

- Depends on `plans/260714-cloudflare-feedback-launch/` because the public UI
  now runs on the Cloudflare Worker path introduced there.
- Blocks the final validation and close-out steps still open in:
  - `plans/260630-issue-42-deploy-mvp-backend-frontend/`
  - `plans/260630-github-milestone-execution/`

## Scope Boundaries

In scope:

- clean up generated or accidental working-tree noise so the branch can be
  committed without dragging local artifacts along
- simplify `public/index.html` into a user-facing landing page rather than a
  project showcase
- improve desktop-first layout balance and remove left-stacked hero behavior
- add a deterministic language switch for Vietnamese and English copy
- preserve the existing Worker request contract for `POST /api/workout-plans`
  and `POST /api/feedback`
- add or tighten tests around UI copy, language switching, and request
  validation boundaries

Out of scope:

- redesigning the workout-plan JSON schema
- changing D1 persistence schema
- replacing the Worker runtime with another framework
- expanding the public product scope beyond one workout-plan flow
- adding analytics, auth, dashboards, or admin tooling
