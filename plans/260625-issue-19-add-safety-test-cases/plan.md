---
title: GitHub issue 19 add safety test cases
description: >-
  Expand regression coverage for safety guardrails and fallback behavior around
  workout generation, especially injury-related prompts, medical-risk triggers,
  beginner-overload detection, and the resulting fallback payload shape.
status: completed
priority: P2
branch: issue-19-add-safety-test-cases
tags: []
blockedBy: []
blocks: []
created: '2026-06-25T03:16:45.602Z'
createdBy: 'ck:plan'
source: skill
---

# GitHub issue 19 add safety test cases

## Overview

Issue 19 is a test-coverage task, not a feature-expansion task. The current
backend already implements safety-policy prompt constraints and runtime
guardrails in `backend/app/llm/openai_client.py`, but the existing tests only
cover a subset of the expected safety branches. The safest implementation is to
add focused regression tests that lock down:

- mild injury-related input that should stay inside normal generation flow
- medical-risk input that should short-circuit to the safety fallback
- beginner-overload output that should be replaced by the safety fallback
- the structure and defaults of the safety fallback payload itself

## Phases

| Phase | Name | Status |
|-------|------|--------|
| 1 | [Review current safety test gaps](./phase-01-review-current-safety-test-gaps.md) | Completed |
| 2 | [Implement safety regression tests](./phase-02-implement-safety-regression-tests.md) | Completed |
| 3 | [Validate test coverage and docs](./phase-03-validate-test-coverage-and-docs.md) | Completed |

## Dependencies

- Reuses the guardrail behavior already present in the main branch.
- Conceptually follows issue 17 policy boundaries and issue 18 runtime
  guardrails, but does not need to modify those plan directories.
