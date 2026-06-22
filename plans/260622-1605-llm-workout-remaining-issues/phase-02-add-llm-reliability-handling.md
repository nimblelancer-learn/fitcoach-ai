---
phase: 2
title: Add LLM reliability handling
status: completed
priority: P1
effort: 1d
dependencies:
  - 1
---

# Phase 2: Add LLM reliability handling

## Overview
This phase adds the missing runtime controls for malformed output and slow or failed
provider responses. Current code validates output and maps errors, but it does not retry
malformed responses, does not provide a fallback after retry exhaustion, and does not set
an explicit timeout policy.

## Requirements
- Functional: Retry when parsed output is missing or schema validation fails.
- Functional: Stop retrying after a small bounded number of attempts.
- Functional: Return a deterministic fallback response or fallback error path when retries
  fail, consistent with product expectations.
- Functional: Handle timeout failures explicitly and map them to stable app-level errors.
- Non-functional: Keep retry scope narrow to malformed/invalid model output, not every
  failure category.
- Non-functional: Avoid infinite retries or silent swallowing of provider failures.

## Architecture
Recommended control flow inside `OpenAIWorkoutPlanClient.generate_workout_plan()`:

```text
for attempt in 1..max_attempts:
  call OpenAI responses.parse with timeout
  if refusal -> fail fast
  if parsed payload valid -> return WorkoutPlan
  if parsed payload invalid -> log + retry

if retries exhausted:
  either return a schema-valid fallback WorkoutPlan
  or raise a dedicated fallback AppError, depending on product choice
```

Implementation should keep timeout, retry count, and fallback strategy in settings or
client-level constants so tests can control them. If a fallback `WorkoutPlan` is chosen,
it must be obviously conservative and machine-valid.

## Related Code Files
- Modify: `backend/app/llm/openai_client.py`
- Modify: `backend/app/core/settings.py`
- Modify: `.env.example`
- Create or Modify: `backend/app/llm/__init__.py`
- Modify: `backend/tests/llm/test_openai_client.py`
- Modify: `backend/tests/api/test_generate_workout_plan.py`

## Implementation Steps
1. Decide a concrete policy for `max_attempts`, timeout seconds, and fallback behavior.
2. Add explicit timeout configuration to the OpenAI request path.
3. Wrap malformed-output handling in a bounded retry loop.
4. Fail fast on refusal and non-retryable provider errors.
5. Add a dedicated fallback branch after retry exhaustion and document whether it returns
   a fallback plan or a stable error.
6. Extend tests to prove retry count, timeout mapping, and fallback behavior.

## Success Criteria
- [x] Malformed or missing parsed output triggers bounded retries.
- [x] Timeout failures are surfaced as explicit app-level behavior.
- [x] Retry exhaustion results in deterministic fallback handling.
- [x] Tests cover success-after-retry and failure-after-retries scenarios.

## Risk Assessment
The biggest risk is turning the client into a grab bag of policies. Mitigation: keep the
retryable conditions explicit, isolate helper methods for validation/fallback, and avoid
retrying refusals or hard SDK failures unless there is a strong product reason.
