---
phase: 1
title: "Quiz CLI v1"
status: complete
priority: P2
effort: "2h"
dependencies: []
---

# Phase 1: Quiz CLI v1

## Overview

Build the foundation: a local CLI that loads topic-based question packs and
runs multiple choice, short answer, and self-check prompts without touching the
FastAPI runtime.

## Requirements

- Functional: support topic-based packs; multiple choice; short answer;
  self-check answer reveal; basic session summary
- Non-functional: run locally in terminal; deterministic behavior; no network
  calls; no dependency on `ENABLE_DEV_LEARNING_PORTAL`

## Architecture

Create a small learning package under `backend/app/learning/quiz/` or a nearby
local-only package under `backend/app/learning/`. The v1 command should:

1. load a curated exercise pack from disk
2. render one question at a time in the terminal
3. capture user input
4. reveal the expected answer or rubric hints
5. print a compact session summary

Use a data-first design so content is not hardcoded in Python. A pack schema
should separate topic metadata from question items and allow per-question
levels such as `recognize`, `distinguish`, `predict`, `apply`, `critique`, and
`explain`.

## Related Code Files

- Create: `backend/app/learning/quiz/__init__.py`
- Create: `backend/app/learning/quiz/models.py`
- Create: `backend/app/learning/quiz/loader.py`
- Create: `backend/app/learning/quiz/cli.py`
- Create: `backend/app/learning/exercises/pyproject-and-uv-lock.toml`
- Create: `backend/tests/learning/test_quiz_cli.py`
- Modify: `backend/README.md`
- Modify: `backend/pyproject.toml`

## Implementation Steps

1. Define the exercise pack schema and question model.
2. Choose the CLI entry shape, for example `uv run python -m app.learning.quiz
   --topic pyproject-and-uv-lock`.
3. Implement pack loading and validation with clear failure messages for bad
   content.
4. Implement terminal flows for:
   - multiple choice
   - short answer capture
   - self-check reveal without automatic grading
5. Create the first pack covering `pyproject.toml` and `uv.lock` using the
   six-level question pattern already discussed.
6. Add focused tests for pack loading, question rendering decisions, and answer
   handling.
7. Document the local command in `backend/README.md`.

## Success Criteria

- [x] A local CLI can run one topic pack end-to-end.
- [x] Question content is loaded from files, not hardcoded in command logic.
- [x] The first pack includes multiple choice, short answer, and self-check
  questions for `pyproject.toml` and `uv.lock`.
- [x] Tests cover loader validation and core CLI flow logic.

## Risk Assessment

- Risk: over-designing the schema before the first pack exists.
  Mitigation: keep the v1 schema minimal and proven by one real topic pack.
- Risk: mixing learning logic into production app startup.
  Mitigation: keep entry points CLI-only and avoid app startup hooks.
- Risk: terminal UX becomes fragile if parsing is too clever.
  Mitigation: use plain line-based prompts and deterministic output.
