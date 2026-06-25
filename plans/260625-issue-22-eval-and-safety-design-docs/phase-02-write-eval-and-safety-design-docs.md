---
phase: 2
title: Write eval and safety design docs
status: completed
priority: P2
effort: 45m
dependencies:
  - 1
---

# Phase 2: Write eval and safety design docs

## Overview

Author the eval design doc and expand the safety doc with concrete examples and
limitations.

## Requirements
- Functional: add eval design, safety policy details, known limitations, and
  pass/fail examples
- Non-functional: keep docs easy to scan and grounded in the current codebase

## Architecture
The eval doc should explain:
- dataset structure
- rubric dimensions
- runner execution path
- report outputs

The safety doc should explain:
- policy boundary
- runtime guardrail behavior
- current limitations
- pass/fail examples that match the existing implementation

## Related Code Files
- Create: `docs/eval-design.md`
- Modify: `docs/safety-policy.md`
- Modify: `README.md`

## Implementation Steps

1. Write an eval design doc that references the checked-in assets and runner.
2. Extend the safety doc with runtime guardrail notes, limitations, and
   examples.
3. Add lightweight discovery links from the repo README.

## Success Criteria

- [ ] The required docs exist and cover the issue checklist concretely.
