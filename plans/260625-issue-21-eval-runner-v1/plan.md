---
title: GitHub issue 21 implement eval runner v1
description: >-
  Implement a local-first eval runner that reads the checked-in dataset and
  rubric, scores schema/safety/personalization/clarity heuristics, and writes
  markdown or CSV reports.
status: completed
priority: P2
branch: issue-21-implement-eval-runner-v1
tags: []
blockedBy: []
blocks: []
created: '2026-06-25T03:46:15.741Z'
createdBy: 'ck:plan'
source: skill
---

# GitHub issue 21 implement eval runner v1

## Overview

Issue 21 turns the eval artifacts from issue 20 into an executable local tool.
The narrowest useful v1 is a runner that:

- loads the dataset and rubric JSON files
- generates plans through the existing workout-plan path when live credentials
  are available
- scores the response for schema validity, safety behavior, personalization, and
  clarity with deterministic heuristics
- writes a markdown or CSV report for later review

## Phases

| Phase | Name | Status |
|-------|------|--------|
| 1 | [Review eval runner contract](./phase-01-review-eval-runner-contract.md) | Completed |
| 2 | [Implement local eval runner and reports](./phase-02-implement-local-eval-runner-and-reports.md) | Completed |
| 3 | [Validate runner behavior and outputs](./phase-03-validate-runner-behavior-and-outputs.md) | Completed |

## Dependencies

- Depends directly on `backend/app/evals/workout_plan_eval_dataset_v1.json` and
  `backend/app/evals/workout_plan_eval_rubric_v1.json`.
- Should avoid requiring a live provider call during tests, so scoring logic
  must be injectable and testable with local fixtures.
