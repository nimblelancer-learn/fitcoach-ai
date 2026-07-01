---
title: GitHub milestone execution loop
description: ''
status: in-progress
priority: P2
branch: main
tags: []
blockedBy: []
blocks: []
created: '2026-06-30T15:07:35.435Z'
createdBy: 'ck:plan'
source: skill
---

# GitHub milestone execution loop

## Overview

Execute the current open GitHub backlog in milestone order using the
repository issue workflow as the contract. The primary sequencing rule is
milestone order (`M4` then `M5` then `M6`). Within each milestone, issue
dependencies override raw creation-date order when the two conflict.

The live backlog on 2026-06-30 matches the expected milestone membership but
not the supplied within-milestone ordering by created date. This plan preserves
the milestone order while using dependency analysis to choose the executable
sequence. The first hard gate is issue `#42`, where the repository lacks a
dedicated frontend app and the deployment path requires an explicit product and
hosting decision before implementation.

## Phases

| Phase | Name | Status |
|-------|------|--------|
| 1 | [Reconcile live backlog](./phase-01-reconcile-live-backlog.md) | Pending |
| 2 | [Execute M4](./phase-02-execute-m4.md) | In Progress |
| 3 | [Execute M5](./phase-03-execute-m5.md) | Pending |
| 4 | [Execute M6](./phase-04-execute-m6.md) | Pending |

## Dependencies

- Existing repository workflow contract in `docs/github-issue-goal-workflow.md`
- Product and safety constraints in:
  - `docs/eval-design.md`
  - `docs/local-learning-system-overview.md`
  - `docs/safety-policy.md`
  - `docs/learning-portal-maintenance.md`
- Current repo primitives:
  - FastAPI backend in `backend/app`
  - server-rendered Jinja template surface in `backend/app/learning/templates`
  - deployment primitives in `backend/Dockerfile`, `docker-compose.yml`, and
    `Makefile`
- Open issue queue as of 2026-06-30:
  - `M4`: `#41`, `#42`, `#43`, `#44`
  - `M5`: `#45`, `#46`, `#47`, `#48`, `#49`, `#52`
  - `M6`: `#50`, `#51`, `#53`, `#54`, `#55`

## Execution Notes

- `M4` executable dependency order is:
  1. `#42` deploy MVP backend and frontend
  2. `#44` add user feedback collection flow
  3. `#43` add public demo link and changelog
  4. `#41` collect first real user feedback
- `#41` likely contains an external-world completion dependency because it
  requires real users and actual feedback collection volume. Treat it as a
  likely blocker candidate only after the product and collection path are live.
- `M5` and `M6` should not begin until `M4` issues are either completed or
  explicitly blocked with evidence.
