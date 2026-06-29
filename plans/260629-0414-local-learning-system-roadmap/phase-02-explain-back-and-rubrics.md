---
phase: 2
title: "Explain-Back and Rubrics"
status: complete
priority: P2
effort: "2h"
dependencies:
  - 1
---

# Phase 2: Explain-Back and Rubrics

## Overview

Upgrade the CLI so self-explanation becomes a first-class learning mode instead
of just freeform text entry.

## Requirements

- Functional: support explain-back prompts; expected answer points; short
  rubrics; user-visible self-review flow
- Non-functional: remain local-only; avoid AI grading; keep scoring transparent
  and lightweight

## Architecture

Extend the question model with:

- `expected_points`: key ideas the learner should mention
- `rubric`: short checklist or partial-credit criteria
- `reflection_prompt`: optional prompt for self-evaluation after reveal

The CLI should not pretend to auto-grade nuanced prose in v1. Instead, it
should collect the user's answer, reveal expected points, and let the learner
mark whether they covered each point. This keeps the system honest and avoids
false precision.

## Related Code Files

- Modify: `backend/app/learning/quiz/models.py`
- Modify: `backend/app/learning/quiz/loader.py`
- Modify: `backend/app/learning/quiz/cli.py`
- Modify: `backend/app/learning/exercises/pyproject-and-uv-lock.toml`
- Create: `backend/app/learning/exercises/app-main-and-learning-portal.toml`
- Modify: `backend/tests/learning/test_quiz_cli.py`
- Modify: `backend/README.md`

## Implementation Steps

1. Extend the question schema to represent explain-back prompts and rubrics.
2. Add CLI flow for:
   - show prompt
   - collect answer
   - reveal expected points
   - optionally let the learner self-mark covered points
3. Add at least one topic pack that exercises repo-architecture explanation,
   such as `app.main`, `routes_learning.py`, and `app.learning.loader`.
4. Ensure the session summary can display:
   - how many explain-back questions were attempted
   - which expected points were missed
5. Add tests for rubric parsing and explain-back interaction flow.

## Success Criteria

- [x] Explain-back prompts can reveal expected points and rubrics cleanly.
- [x] The learner can self-check answers without any external grader.
- [x] At least one repo-architecture pack exists beyond dependency-management
  questions.
- [x] Tests cover schema validation and explain-back CLI branches.

## Risk Assessment

- Risk: rubrics become too verbose and kill learning flow.
  Mitigation: cap expected points per question to 3-5 concise bullets.
- Risk: fake scoring confidence from crude automation.
  Mitigation: keep v1 self-assessed and explicitly non-authoritative.
- Risk: content drift as code changes.
  Mitigation: mirror the portal discipline and prefer small curated packs with
  focused tests.
