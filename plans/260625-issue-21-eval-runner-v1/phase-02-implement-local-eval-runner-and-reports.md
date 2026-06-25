---
phase: 2
title: Implement local eval runner and reports
status: completed
priority: P2
effort: 1h
dependencies:
  - 1
---

# Phase 2: Implement local eval runner and reports

## Overview

Implement the eval runner module, loader functions, score heuristics, and
report rendering.

## Requirements
- Functional: evaluate schema validity, safety behavior, personalization, and
  clarity; emit markdown or CSV
- Non-functional: keep scoring deterministic and small enough for unit tests

## Architecture
The runner should expose:
- dataset and rubric loaders
- an injectable async `run_eval_cases(...)` entry point
- report builders for markdown and CSV
- a CLI entry point for live runs using the existing OpenAI client

## Related Code Files
- Create: `backend/app/evals/__init__.py`
- Create: `backend/app/evals/runner.py`
- Modify: `backend/app/evals/README.md`

## Implementation Steps

1. Add dataclasses for cases, rubric, and per-case results.
2. Implement deterministic score heuristics for the required categories.
3. Implement markdown and CSV report rendering.
4. Add a CLI entry point that writes the chosen report format to disk.

## Success Criteria

- [ ] The runner can score eval cases and render reports from local artifacts.
