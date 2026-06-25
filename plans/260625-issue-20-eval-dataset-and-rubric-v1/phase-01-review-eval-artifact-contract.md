---
phase: 1
title: Review eval artifact contract
status: completed
priority: P2
effort: 30m
dependencies: []
---

# Phase 1: Review eval artifact contract

## Overview

Define the minimum artifact shape needed for a reusable eval dataset and rubric.

## Requirements
- Functional: choose stable fields for 30 cases, expected behavior, and risk
  tags
- Non-functional: keep artifacts readable by both humans and a later automated
  runner

## Architecture
The repo currently has no eval implementation code, but it already has stable
contracts for:
- `UserProfile` request payload shape
- safety-policy and safety-fallback behavior
- retrieval-grounded workout generation

That makes JSON artifacts under `backend/app/evals/` the narrowest useful
surface for v1.

## Related Code Files
- Create: `backend/app/evals/workout_plan_eval_dataset_v1.json`
- Create: `backend/app/evals/workout_plan_eval_rubric_v1.json`
- Create: `backend/tests/test_eval_assets.py`

## Implementation Steps

1. Review the issue checklist and current backend contracts.
2. Choose a dataset schema that a future runner can read without code changes.
3. Choose rubric dimensions and risk-tag vocabulary aligned with current repo
   capabilities.

## Success Criteria

- [ ] The eval artifact structure is defined before asset creation starts.
- [ ] The chosen fields map cleanly to current backend behavior.
