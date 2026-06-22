---
phase: 4
title: Add basic tests for local AI feature
status: completed
priority: P1
effort: 0.75d
dependencies:
  - 1
  - 2
  - 3
---

# Phase 4: Add basic tests for local AI feature

## Overview
The repository already has strong baseline schema, API, and client tests. This phase
finishes the local AI feature test story by covering the remaining reliability and
metrics branches and by adding a documented test command to the README.

## Requirements
- Functional: Keep schema tests for valid and invalid profile input.
- Functional: Add tests for malformed LLM output retry/fallback handling.
- Functional: Add tests for timeout handling and metrics logging/cost estimation helpers.
- Functional: Add a clear local test run command to README.
- Non-functional: Keep tests isolated from real OpenAI calls by default.
- Non-functional: Preserve the existing opt-in integration test gate.

## Architecture
Test coverage should remain layered:

```text
schemas -> pure Pydantic validation
llm client -> retry, timeout, fallback, usage extraction, cost estimation
service -> prompt delegation
api -> request validation and error envelope
integration -> opt-in real OpenAI path only
```

Avoid duplicating the same assertion at every layer. The client tests should own most of
the reliability and metrics branches.

## Related Code Files
- Modify: `backend/tests/schemas/test_domain_schemas.py`
- Modify: `backend/tests/llm/test_openai_client.py`
- Modify: `backend/tests/api/test_generate_workout_plan.py`
- Modify: `backend/tests/services/test_workout_plan_generator.py`
- Modify: `README.md`
- Modify: `backend/README.md`

## Implementation Steps
1. Keep the current valid/invalid profile schema coverage as the base contract.
2. Add LLM client tests for retry-on-invalid-output, fallback after retry exhaustion, and
   timeout mapping.
3. Add tests for metrics extraction and cost estimation helpers.
4. Add or update README with the exact local unit test command.
5. Run the relevant test subset and record the canonical command in the issue doc.

## Success Criteria
- [x] Schema tests remain green for valid and invalid profile payloads.
- [x] LLM client tests cover malformed output retry and timeout paths.
- [x] Metrics helpers are unit-tested.
- [x] README contains a copy-paste local test command.

## Risk Assessment
The risk is bloated overlapping tests. Mitigation: keep branch-specific assertions at the
lowest useful layer and reserve API tests for envelope behavior, not client internals.
