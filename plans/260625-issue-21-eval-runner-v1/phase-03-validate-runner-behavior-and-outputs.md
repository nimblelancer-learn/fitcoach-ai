---
phase: 3
title: Validate runner behavior and outputs
status: completed
priority: P2
effort: 30m
dependencies:
  - 2
---

# Phase 3: Validate runner behavior and outputs

## Overview

Validate the runner with focused local tests.

## Requirements
- Functional: verify scoring, loader behavior, and report rendering
- Non-functional: keep tests fully local and deterministic

## Architecture
Tests should cover both a normal-plan case and a medical-risk fallback case, so
the runner proves it can distinguish the two major eval outcomes.

## Related Code Files
- Create: `backend/tests/evals/test_runner.py`
- Modify: `plans/260625-issue-21-eval-runner-v1/plan.md`

## Implementation Steps

1. Add unit tests for loader functions.
2. Add unit tests for normal-plan and safety-fallback scoring.
3. Add report rendering tests for markdown and CSV output.
4. Run focused pytest targets for the new runner tests and eval asset tests.

## Success Criteria

- [ ] Runner tests pass locally.
- [ ] The runner proves the required report formats and score categories.
