---
phase: 1
title: Review current eval and safety documentation gaps
status: completed
priority: P2
effort: 20m
dependencies: []
---

# Phase 1: Review current eval and safety documentation gaps

## Overview

Identify what is already documented and what issue 22 still requires.

## Requirements
- Functional: map the issue checklist to concrete doc sections
- Non-functional: avoid duplicating code comments or rewriting the whole README

## Architecture
The current repo already has:
- `docs/safety-policy.md`
- `backend/app/evals/README.md`
- the eval dataset, rubric, and runner source files

What is missing is a design-level doc that ties those pieces together and adds
known limitations plus pass/fail examples.

## Related Code Files
- Create: `docs/eval-design.md`
- Modify: `docs/safety-policy.md`
- Modify: `README.md`

## Implementation Steps

1. Review current safety and eval artifacts.
2. Decide which content belongs in the eval doc versus the safety doc.
3. Keep the updates repository-specific and implementation-aware.

## Success Criteria

- [ ] Missing documentation sections are clearly identified before writing.
