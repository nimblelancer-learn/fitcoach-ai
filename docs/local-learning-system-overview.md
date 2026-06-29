# Local Learning System Overview

This repo now has two complementary learning surfaces under `backend/app/learning/`:

- `content/`
  Dev learning portal reference content for architecture, flows, and glossary.
- `exercises/` plus local CLIs
  Active practice content for recall, explain-back, prediction, and repo drills.

## What was added

The local-first practice system adds:

- quiz CLI runtime in `backend/app/learning/quiz/`
- drill runner in `backend/app/learning/drills/`
- curated packs in `backend/app/learning/exercises/`
- focused tests in `backend/tests/learning/`
- portable skill package in `docs/skills/ck-learnloop/`

## Learning modes

- `multiple_choice`
  Fast recognition and distinction checks.
- `short_answer`
  Compact retrieval without open-ended grading.
- `self_check`
  Reveal-based recall for quick review.
- `explain_back`
  Self-reviewed explanation against expected points.
- `prediction`
  Repo-specific outcome forecasting before verification.
- `repo drills`
  Bounded applied tasks with deterministic local validation.

## Entry points

From `backend/`:

```bash
uv run python -m app.learning.quiz.cli --topic pyproject-and-uv-lock
uv run python -m app.learning.quiz.cli --topic app-main-and-learning-portal
uv run python -m app.learning.quiz.cli --topic runtime-and-workflow-predictions
uv run python -m app.learning.drills.runner --topic repo-drills
```

Installed script entry points from `backend/pyproject.toml`:

```bash
learning-quiz --topic pyproject-and-uv-lock
learning-drills --topic repo-drills
```

## Design constraints

- local-first and low-friction
- data-first content in TOML, not hardcoded prompt logic
- no fake authoritative AI grading
- drills must have a bounded validation path
- practice content must be reviewed when source knowledge changes

## Maintenance

Use [learning-portal-maintenance.md](./learning-portal-maintenance.md) as the
source of truth for updating both portal content and practice content.

If this framework is reused in another project, start from
`docs/skills/ck-learnloop/`.
