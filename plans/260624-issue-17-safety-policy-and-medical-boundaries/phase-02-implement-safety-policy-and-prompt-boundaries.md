---
phase: 2
title: Implement safety policy and prompt boundaries
status: completed
priority: P2
effort: 1h
dependencies:
  - 1
---

# Phase 2: Implement safety policy and prompt boundaries

## Overview

Write the safety policy v1 and update the LLM prompt so the generation path
explicitly follows the same medical-boundary and fallback rules.

## Requirements

- Functional: define in-scope coaching behavior versus out-of-scope medical
  behavior.
- Functional: define refusal or fallback scenarios for red-flag symptoms,
  diagnosis/treatment requests, and rehabilitation-style requests.
- Functional: add prompt regression tests so future edits do not weaken the
  boundary language.

## Architecture

Create a repo-level safety policy doc under `docs/`, then mirror its rules in
`WORKOUT_PLAN_SYSTEM_INSTRUCTION`. Validate the contract through prompt tests
rather than full generation tests.

## Related Code Files

- Create: `docs/safety-policy.md`
- Modify: `backend/app/llm/prompts.py`
- Modify: `backend/tests/llm/test_prompts.py`
- Modify: `README.md`
- Modify: `backend/README.md`

## Implementation Steps

1. Author the safety policy with scope, out-of-scope cases, and fallback rules.
2. Strengthen the workout-plan system prompt to reflect those boundaries.
3. Add or update prompt tests to lock the policy language in place.

## Success Criteria

- [ ] A safety policy v1 exists in repo docs.
- [ ] The system prompt explicitly encodes medical boundaries and fallback
  behavior.
- [ ] Prompt tests cover the new boundary language.
