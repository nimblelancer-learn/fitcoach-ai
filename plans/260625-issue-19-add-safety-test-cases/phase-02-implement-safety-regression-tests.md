---
phase: 2
title: Implement safety regression tests
status: completed
priority: P2
effort: 45m
dependencies:
  - 1
---

# Phase 2: Implement safety regression tests

## Overview

Add or refine automated tests that cover the missing safety cases from phase 1.

## Requirements
- Functional: add injury-related, medical-risk, beginner-overload, and fallback
  behavior test cases aligned with issue 19
- Non-functional: keep the assertions deterministic and local to the current
  client/service contracts

## Architecture
The tests should exercise behavior at the smallest reliable layer:
- use `OpenAIWorkoutPlanClient` tests for guardrail and fallback logic
- avoid full integration coverage unless needed to prove the API contract
- validate fallback payload shape through the returned `WorkoutPlan` object

## Related Code Files
- Modify: `backend/tests/llm/test_openai_client.py`

## Implementation Steps

1. Add a mild injury-input test that proves normal generation is not blocked for
   non-medical limitations.
2. Add or tighten medical-risk tests to confirm immediate safety fallback and no
   upstream OpenAI request when trigger keywords are present.
3. Add beginner-overload coverage for unsafe generated plans, including fallback
   warnings and replacement behavior.
4. Add a direct fallback-shape assertion for the safety fallback output.

## Success Criteria

- [ ] The issue checklist is represented by concrete automated tests.
- [ ] New tests fail if safety guardrails regress.
