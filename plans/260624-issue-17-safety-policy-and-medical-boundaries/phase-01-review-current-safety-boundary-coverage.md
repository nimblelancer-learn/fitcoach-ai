---
phase: 1
title: Review current safety boundary coverage
status: completed
priority: P2
effort: 20m
dependencies: []
---

# Phase 1: Review current safety boundary coverage

## Overview

Map where safety and medical-boundary language already exists so the new policy
document does not drift from current repo behavior.

## Requirements

- Functional: identify current safety boundary coverage in prompts, schemas,
  knowledge-base policy, and README docs.
- Non-functional: keep the issue scoped to policy and prompt alignment, not
  runtime enforcement.

## Architecture

Treat the safety policy doc as the canonical written contract, then align the
LLM system instruction and tests to that contract. Leave runtime blocking logic
for follow-on work.

## Related Code Files

- Modify: `backend/app/llm/prompts.py`
- Modify: `backend/tests/llm/test_prompts.py`
- Create: `docs/safety-policy.md`
- Modify: `README.md`
- Modify: `backend/README.md`

## Implementation Steps

1. Review the current prompt instruction, source policy, and safety corpus.
2. Identify missing explicit boundaries for medical, rehabilitation, and acute
   symptom scenarios.
3. Define the minimal artifact set needed for a policy-first implementation.

## Success Criteria

- [x] Current safety coverage and gaps are identified.
- [x] The issue remains limited to policy and prompt boundary definition.
