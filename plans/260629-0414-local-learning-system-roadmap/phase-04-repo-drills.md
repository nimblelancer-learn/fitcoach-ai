---
phase: 4
title: "Repo Drills"
status: complete
priority: P2
effort: "3h"
dependencies:
  - 3
---

# Phase 4: Repo Drills

## Overview

Add the deepest exercise mode: repo drills that connect learning content to
real code paths, tests, and change-impact reasoning.

## Requirements

- Functional: define drill format for call-flow tracing, file impact analysis,
  test prediction, and small repo-task prompts; support script- or pytest-based
  validation where appropriate
- Non-functional: preserve safe local execution; keep drills bounded and
  beginner-readable

## Architecture

Repo drills should not be framed as open-ended coding agents. They should be
small, constrained tasks with explicit artifacts and validation paths, such as:

- trace the call flow for a request
- identify which tests should fail after a specific change
- map a concept to the exact module/function that enforces it
- complete a tiny local edit or answer file that can be checked by script

This phase may add a separate drill runner or reuse the quiz CLI with a
different mode. Validation should prefer deterministic scripts or focused
pytest targets instead of complex grading heuristics.

## Related Code Files

- Modify: `backend/app/learning/quiz/cli.py`
- Create: `backend/app/learning/drills/__init__.py`
- Create: `backend/app/learning/drills/runner.py`
- Create: `backend/app/learning/exercises/repo-drills.toml`
- Create: `backend/tests/learning/test_repo_drills.py`
- Modify: `backend/README.md`

## Implementation Steps

1. Define the repo-drill content contract and decide whether to integrate it
   into the existing CLI or a sibling runner.
2. Add initial drill categories:
   - call-flow tracing
   - impact prediction
   - test selection
   - constrained repo task
3. Implement deterministic validation hooks where feasible, such as:
   - checking an answer file
   - checking selected test IDs
   - running a focused pytest target
4. Seed the first drills from real repo topics:
   - startup lifecycle
   - learning portal loader validation
   - workout plan generation flow
5. Add tests for drill parsing and validation behavior.
6. Document how drills differ from ordinary quizzes and when to use them before
   a milestone.

## Success Criteria

- [x] Repo drills exist as a distinct learning mode, not just longer quiz
  prompts.
- [x] At least one drill is validated by a deterministic script or pytest path.
- [x] Drill topics cover real backend flows already documented in the repo.
- [x] The resulting system gives a clear progression from recall to applied
  reasoning.

## Risk Assessment

- Risk: drills become mini feature work and bloat scope.
  Mitigation: constrain each drill to one learning objective and one validation
  path.
- Risk: validation becomes brittle if it relies on too much repo state.
  Mitigation: keep drill fixtures local and focused.
- Risk: users confuse drills with production workflows.
  Mitigation: document the local-only purpose and keep entry points clearly
  separated from app runtime commands.
