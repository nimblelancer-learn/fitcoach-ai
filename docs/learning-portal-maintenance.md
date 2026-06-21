# Learning Portal Maintenance Guide

This guide is the source of truth for updating the dev-only learning portal under `backend/app/learning`.

## Purpose

The portal is intentionally curated, small, and beginner-readable.

That means updates should optimize for:

- accurate explanations tied to the current code
- explicit module and function references
- early validation failures when curated content drifts
- small, understandable content files instead of automation-heavy generation

## Portal structure

The learning portal has four content types:

- `overview`
  - file: `backend/app/learning/content/overview.toml`
- `module pages`
  - directory: `backend/app/learning/content/modules/`
- `flow pages`
  - directory: `backend/app/learning/content/flows/`
- `glossary entries`
  - directory: `backend/app/learning/content/glossary/`

Typed contracts live in:

- `backend/app/learning/models.py`

Loading and validation live in:

- `backend/app/learning/loader.py`

Routes and rendering live in:

- `backend/app/api/routes_learning.py`
- `backend/app/learning/templates/`

## Update policy

When new code or a new feature is added, update portal content only if it improves a beginner's understanding of the current architecture.

Good candidates:

- new top-level FastAPI wiring in `app.main`
- new routers
- new middleware
- new shared core modules
- new request flows that are important to understanding behavior
- repeated vocabulary that a beginner would not know yet

Do not add:

- every function in a module
- raw implementation dumps
- speculative content for code that does not exist yet
- generic definitions that are not tied back to this repo

## Required workflow for portal updates

Follow this sequence every time:

1. Read the real code first.
2. Decide whether the change belongs in `overview`, a `module page`, a `flow page`, `glossary`, or a combination.
3. Update the smallest number of TOML files needed.
4. Make sure every Python reference in TOML points to a real importable module or attribute.
5. Run validation commands.
6. If behavior changed, update tests or add one focused test.

## How to add or update a module page

Create or edit one file in `backend/app/learning/content/modules/<slug>.toml`.

Every module page should explain:

- what the module does
- why it exists
- when it runs
- dependencies
- what uses it
- safe edit notes
- related modules
- related flows
- key functions only

Keep `key_functions` limited to high-signal functions a beginner should inspect first.

## How to add or update a flow page

Create or edit one file in `backend/app/learning/content/flows/<slug>.toml`.

Use a flow page when understanding depends on execution order, such as:

- request lifecycle
- startup initialization
- validation pipeline
- background processing flow

Each step should describe the current behavior, not a desired future architecture.

## How to add or update glossary entries

Create or edit one file in `backend/app/learning/content/glossary/<slug>.toml`.

Each glossary entry must include:

- `term`
- `definition`
- `why_it_matters_in_repo`
- `related_modules`

Use these rules:

- `definition` explains the term in plain language
- `why_it_matters_in_repo` explains why the term matters in FitCoach AI specifically
- `related_modules` should point to the best next pages to read

If a term is generic but not actually important in this repo yet, do not add it.

## How to avoid content mismatch

Before finalizing an update, check these explicitly:

- every `module_path` imports successfully
- every `python_path` resolves to a real attribute
- every `related_modules` slug exists
- every `related_flows` slug exists
- every glossary entry has repo-specific meaning, not only a dictionary definition
- the request flow still matches the current app wiring

If a code refactor renamed a function or moved a module:

1. update the TOML reference
2. update the narrative text
3. rerun loader validation and tests

## Validation commands

Run from repo root:

```bash
cd backend && .venv/bin/python -m ruff check .
cd backend && .venv/bin/python -m pytest -q
cd backend && .venv/bin/python - <<'PY'
from app.learning.loader import load_learning_portal
portal = load_learning_portal()
print("modules", sorted(portal.modules))
print("flows", sorted(portal.flows))
print("glossary", sorted(portal.glossary))
PY
```

## Prompting guide for future Codex updates

When asking for portal updates later, include these instructions:

1. Read the relevant backend code before editing portal content.
2. Follow `docs/learning-portal-maintenance.md`.
3. Keep the change set small and beginner-readable.
4. Update curated TOML content, not hardcoded route HTML.
5. Run `ruff`, `pytest`, and the loader validation snippet before finishing.
6. If the code changed request flow or startup behavior, review the flow and glossary entries for drift.

## Review checklist

Use this checklist before considering the update done:

- [ ] The explanation matches the real code as it exists now.
- [ ] New content is curated and not over-documented.
- [ ] Every new reference validates cleanly.
- [ ] At least one rendered page or related test covers the change.
- [ ] Glossary text includes both definition and repo-specific relevance.
- [ ] No unrelated architecture or UI changes were introduced.
