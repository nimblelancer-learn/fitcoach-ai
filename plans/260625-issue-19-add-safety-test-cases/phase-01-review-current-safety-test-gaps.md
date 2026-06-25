---
phase: 1
title: Review current safety test gaps
status: completed
priority: P2
effort: 30m
dependencies: []
---

# Phase 1: Review current safety test gaps

## Overview

Inspect the current safety-policy, guardrail implementation, and existing test
coverage to identify what issue 19 still requires.

## Requirements
- Functional: map the issue checklist to concrete test scenarios
- Non-functional: keep scope limited to tests unless a missing assertion exposes
  a real implementation bug

## Architecture
The main behavior lives in `backend/app/llm/openai_client.py`:
- pre-request prompt scanning for medical-risk keywords
- post-validation scanning for unsafe beginner outputs
- construction of a structured safety fallback `WorkoutPlan`

Coverage review should compare those branches against current tests in
`backend/tests/llm/test_openai_client.py`.

## Related Code Files
- Modify: `backend/tests/llm/test_openai_client.py`
- Review: `backend/app/llm/openai_client.py`
- Review: `docs/safety-policy.md`

## Implementation Steps

1. Read the issue body and enumerate the missing safety scenarios.
2. Compare current tests against prompt-trigger, plan-trigger, and fallback-plan
   branches.
3. Decide whether the issue can be solved with tests only or if an uncovered bug
   requires a production fix.

## Success Criteria

- [ ] Missing safety scenarios are translated into explicit test targets.
- [ ] Planned edits stay scoped to regression coverage unless a bug is proven.
