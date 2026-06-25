---
phase: 3
title: Validate eval assets and tests
status: completed
priority: P2
effort: 30m
dependencies:
  - 2
---

# Phase 3: Validate eval assets and tests

## Overview

Validate the new eval artifacts with focused contract tests.

## Requirements
- Functional: prove the dataset and rubric exist, are parseable, and satisfy
  the v1 contract
- Non-functional: catch structural drift without depending on a future eval
  runner implementation

## Architecture
Validation should mirror the existing checked-in asset tests used for the
knowledge base: load files locally and assert required fields, case counts, and
controlled vocabularies.

## Related Code Files
- Create: `backend/tests/test_eval_assets.py`
- Modify: `plans/260625-issue-20-eval-dataset-and-rubric-v1/plan.md`

## Implementation Steps

1. Add local tests that validate dataset structure, case count, and uniqueness.
2. Validate rubric dimensions, weights, and hard-fail rule presence.
3. Run focused pytest coverage for the new eval asset tests.

## Success Criteria

- [ ] Eval artifacts parse successfully and satisfy the local contract tests.
- [ ] Focused validation passes without requiring external services.
