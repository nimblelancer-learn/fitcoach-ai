---
title: "Local learning system roadmap"
description: >-
  Build a local-first learning system for FitCoach AI that starts with a quiz
  CLI and grows into explain-back prompts, prediction labs, and repo drills.
status: complete
priority: P2
branch: "main"
effort: 9h
tags: [feature, docs, backend, experimental]
blockedBy: []
blocks: []
created: "2026-06-29T04:14:09.600Z"
createdBy: "ck:plan"
source: skill
---

# Local learning system roadmap

## Overview

This plan defines a staged learning system for the repo so you can move from
passive reading into active recall, prediction, explanation, and application.
The narrowest useful v1 is a local CLI that reads curated exercise packs and
runs multiple question modes without touching production runtime paths.

The roadmap intentionally grows in four layers:

- Phase 1 builds the base quiz CLI with topic-based packs and basic answer
  modes.
- Phase 2 adds explain-back prompts and rubric-driven self-check so short
  freeform answers become useful instead of vague.
- Phase 3 adds prediction labs tied to real files, commands, and workflows in
  this repo.
- Phase 4 adds repo drills that point at code paths, tests, and change-impact
  exercises close to real engineering work.

Scope challenge:

- Existing code: the dev-only learning portal under `backend/app/learning/`
  already provides curated module, flow, and glossary content; its loader and
  tests show a clean pattern for validated educational content.
- Minimum changes: start with a local-only CLI and content schema; do not add
  production routes, scoring services, or external AI grading in v1.
- Complexity: likely 8-14 files with one new learning package area plus tests;
  four phases are justified because each learning mode adds a distinct
  interaction contract.
- Selected mode: HOLD SCOPE.

## Phases

| Phase | Name | Status |
|-------|------|--------|
| 1 | [Quiz CLI v1](./phase-01-quiz-cli-v1.md) | Complete |
| 2 | [Explain-Back and Rubrics](./phase-02-explain-back-and-rubrics.md) | Complete |
| 3 | [Prediction Labs](./phase-03-prediction-labs.md) | Complete |
| 4 | [Repo Drills](./phase-04-repo-drills.md) | Complete |

## Dependencies

- No direct cross-plan blockers were found in existing unfinished plans.
- Reuse these current sources of truth:
  - `backend/app/learning/content/` for curated topic material
  - `docs/learning-portal-maintenance.md` for fail-fast content discipline
  - `backend/pyproject.toml` and `backend/README.md` for local CLI/test command
    patterns
- Keep the learning system local-first. New commands may live under `backend/`
  but should not require enabling `/__learn` routes or deploying any new
  runtime surface.
