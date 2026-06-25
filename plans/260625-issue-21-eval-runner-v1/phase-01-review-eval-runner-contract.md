---
phase: 1
title: Review eval runner contract
status: completed
priority: P2
effort: 25m
dependencies: []
---

# Phase 1: Review eval runner contract

## Overview

Define the runner interface, artifact loading contract, and the minimum scoring
dimensions for v1.

## Requirements
- Functional: load dataset and rubric assets; support report output
- Non-functional: keep the runner locally testable without requiring OpenAI

## Architecture
The runner should live under `backend/app/evals/` beside the dataset and rubric.
Core scoring functions should accept a generated `WorkoutPlan` plus an eval case
so tests can inject fake outputs instead of making provider calls.

## Related Code Files
- Create: `backend/app/evals/runner.py`
- Create: `backend/tests/evals/test_runner.py`

## Implementation Steps

1. Review issue 21 requirements and the issue 20 artifact shapes.
2. Define runner result objects and score categories.
3. Separate live plan generation from deterministic scoring/report rendering.

## Success Criteria

- [ ] The runner contract is clear enough to implement without live dependencies.
