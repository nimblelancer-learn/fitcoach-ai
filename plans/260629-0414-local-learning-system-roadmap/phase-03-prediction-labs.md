---
phase: 3
title: "Prediction Labs"
status: complete
priority: P2
effort: "2h"
dependencies:
  - 2
---

# Phase 3: Prediction Labs

## Overview

Add prediction-oriented exercises that force the learner to anticipate repo
behavior before running commands, changing config, or touching code.

## Requirements

- Functional: support prediction question types tied to real files, commands,
  and workflows; reveal actual expected outcomes after user input
- Non-functional: keep labs deterministic; avoid executing arbitrary commands
  during the learning session

## Architecture

Prediction labs should introduce a new question shape with fields such as:

- `scenario`
- `target_files`
- `expected_outcome`
- `why`
- `follow_up_check`

The learner predicts what will happen, then reviews the expected outcome and
the reasoning. `follow_up_check` can suggest a command or file to inspect after
the answer, but the CLI should keep execution manual in v1.

## Related Code Files

- Modify: `backend/app/learning/quiz/models.py`
- Modify: `backend/app/learning/quiz/cli.py`
- Create: `backend/app/learning/exercises/runtime-and-workflow-predictions.toml`
- Modify: `backend/tests/learning/test_quiz_cli.py`
- Modify: `backend/README.md`

## Implementation Steps

1. Add a prediction-lab question type to the schema.
2. Implement the CLI interaction for:
   - scenario display
   - freeform prediction capture
   - reveal of expected outcome and reasoning
   - optional follow-up verification hint
3. Seed scenarios from real repo behavior, for example:
   - editing `backend/pyproject.toml`
   - `uv sync` implications for `backend/uv.lock`
   - toggling `ENABLE_DEV_LEARNING_PORTAL`
   - renaming a referenced learning module slug
4. Add tests to ensure prediction-lab rendering and content validation work.

## Success Criteria

- [x] Prediction questions are supported as a first-class mode.
- [x] Scenarios point to real files and workflows in this repo.
- [x] Expected outcomes explain both what happens and why.
- [x] Tests protect schema and CLI behavior for the new mode.

## Risk Assessment

- Risk: scenarios become hypothetical instead of repo-specific.
  Mitigation: require each scenario to reference concrete files or commands.
- Risk: temptation to auto-run commands and blur learning with automation.
  Mitigation: keep verification hints manual in v1.
- Risk: duplicate overlap with explain-back questions.
  Mitigation: reserve prediction labs for future-state reasoning, not static
  definitions.
