# Learning Content Maintenance Guide

This guide is the repo-specific source of truth for maintaining curated learning
content under `backend/app/learning/`.

It covers both local learning surfaces:

- learning portal reference content in `backend/app/learning/content/`
- practice content in `backend/app/learning/exercises/` consumed by:
  - `backend/app/learning/quiz/`
  - `backend/app/learning/drills/`

The rule is simple: when source knowledge changes, review both surfaces. Do not
assume updating only the portal or only practice content is enough.

## Surfaces

### Portal

Use the portal for stable explanation:

- architecture overview
- module purpose
- execution flows
- glossary terms

Main files:

- `backend/app/learning/content/overview.toml`
- `backend/app/learning/content/modules/*.toml`
- `backend/app/learning/content/flows/*.toml`
- `backend/app/learning/content/glossary/*.toml`

Validation/runtime:

- `backend/app/learning/loader.py`
- `backend/app/learning/models.py`
- `backend/app/api/routes_learning.py`
- `backend/tests/test_learning_portal.py`

### Practice content

Use practice content for active retrieval and bounded applied reasoning:

- quiz recall and distinction prompts
- explain-back prompts
- prediction prompts
- repo drills

Main files:

- `backend/app/learning/exercises/*.toml`
- `backend/app/learning/quiz/models.py`
- `backend/app/learning/quiz/loader.py`
- `backend/app/learning/drills/runner.py`
- `backend/tests/learning/test_quiz_cli.py`
- `backend/tests/learning/test_repo_drills.py`

## When To Update What

Update the portal when the learner needs a new or corrected explanation of:

- architecture
- ownership or purpose of a module
- request or startup flow
- important repo vocabulary

Update practice content when the learner should now practice:

- a new fact or distinction
- a changed explanation
- a changed prediction outcome
- a changed validation choice or repo task

Update both when a code or knowledge change affects both explanation and
practice. Common cases:

- startup/runtime wiring changes
- router or shared service behavior changes
- source-of-truth workflow changes such as dependency or validation flow
- renamed modules/functions/flags that appear in portal prose and exercise packs

Update neither when the change is purely internal and does not improve a
beginner's understanding of the current repo.

## Source-Change Workflow

Run this workflow whenever source knowledge changes:

1. Read the real source first: code, docs, tests, or configs.
2. List what changed:
   - facts
   - explanations
   - likely outcomes
   - bounded tasks or validation paths
3. Decide surface impact:
   - portal
   - practice content
   - both
   - neither
4. Update the smallest content files that restore truth.
5. Recheck nearby content for drift:
   - portal references
   - quiz answers
   - explain-back expected points
   - prediction outcomes and follow-up checks
   - drill validators and target tests
6. Run validation before finishing.

## Authoring Rules

Portal rules:

- explain the current repo, not a desired future design
- keep pages curated and beginner-readable
- prefer key functions and important flow steps only

Practice rules:

- keep packs tied to real repo files and workflows
- keep `expected_points` short and concrete
- keep prediction scenarios file-specific
- prefer self-review for nuanced explanation
- prefer deterministic drill validation such as:
  - answer-file substring checks
  - exact test selection
  - focused pytest targets

Do not:

- dump implementation details into portal pages
- add generic theory not anchored to this repo
- hardcode knowledge into CLI Python instead of TOML
- pretend heuristic AI grading is authoritative
- create broad or network-dependent drills

## Anti-Drift Checklist

Check these before considering the update complete:

- [ ] Portal prose still matches current code paths and naming.
- [ ] Every `module_path` and `python_path` still resolves.
- [ ] Every related portal slug still exists.
- [ ] Every exercise topic slug still matches its file name.
- [ ] Every source file path in packs or drills still exists.
- [ ] Every expected answer, expected point, and prediction outcome is still true.
- [ ] Every drill validator still matches the current best local validation path.
- [ ] Workflow changes updated practice content, not only portal prose.

## Validation Commands

Run from repo root:

```bash
cd backend && UV_CACHE_DIR=/tmp/uv-cache uv run ruff check app/learning tests/learning tests/test_learning_portal.py
cd backend && UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_learning_portal.py tests/learning/test_quiz_cli.py tests/learning/test_repo_drills.py -q
cd backend && UV_CACHE_DIR=/tmp/uv-cache uv run python - <<'PY'
from app.learning.loader import load_learning_portal
portal = load_learning_portal()
print("modules", len(portal.modules))
print("flows", len(portal.flows))
print("glossary", len(portal.glossary))
PY
cd backend && UV_CACHE_DIR=/tmp/uv-cache uv run python -m app.learning.quiz.cli --topic pyproject-and-uv-lock
cd backend && UV_CACHE_DIR=/tmp/uv-cache uv run python -m app.learning.quiz.cli --topic app-main-and-learning-portal
cd backend && UV_CACHE_DIR=/tmp/uv-cache uv run python -m app.learning.quiz.cli --topic runtime-and-workflow-predictions
```

If you changed drill content or drill contracts, also run:

```bash
cd backend && UV_CACHE_DIR=/tmp/uv-cache uv run python -m app.learning.drills.runner --topic repo-drills
```

Prepare any required files under `/tmp/fitcoach-learning-drills/repo-drills/`
before the drill smoke test.

## Fast Decision Table

- New module/flow/glossary concept:
  update portal first, then decide whether practice should reinforce it.
- Changed answer, reasoning, or expected repo outcome:
  update practice content.
- Changed workflow that learners should both understand and rehearse:
  update both.
- Refactor with no learner-facing knowledge change:
  likely update neither, but still verify references did not drift.
