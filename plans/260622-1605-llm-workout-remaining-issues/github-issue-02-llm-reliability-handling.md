# Issue 2: Add LLM reliability handling

## Summary
Implemented bounded retry, fallback, and timeout handling around malformed or slow
OpenAI responses while preserving the existing API contract.

## Current State
- Implemented: malformed structured output is retried using
  `OPENAI_INVALID_OUTPUT_RETRIES`
- Implemented: request timeout uses `OPENAI_TIMEOUT_SECONDS`
- Implemented: timeout failures map to `OPENAI_TIMEOUT` with HTTP 504 semantics
- Implemented: refusals still fail fast as `OPENAI_REFUSAL`
- Implemented: provider SDK failures still map to `OPENAI_REQUEST_FAILED`
- Implemented: retry exhaustion returns a conservative schema-valid fallback `WorkoutPlan`

## Scope
- Retry only malformed or schema-invalid output
- Add explicit timeout policy
- Add deterministic fallback behavior
- Keep refusal and hard provider failures as fail-fast paths unless policy says otherwise

## Delivered
- [x] Added `OPENAI_INVALID_OUTPUT_RETRIES` policy for malformed output
- [x] Added `OPENAI_TIMEOUT_SECONDS` configuration for OpenAI requests
- [x] Retry when `output_parsed` is missing
- [x] Retry when parsed payload fails `WorkoutPlan` validation
- [x] Added fallback behavior after retry exhaustion
- [x] Kept refusal and non-retryable provider errors clearly separated
- [x] Added tests for retry success, retry exhaustion, and timeout mapping

## Acceptance Criteria
- [x] Malformed output is retried a bounded number of times
- [x] Timeout behavior is explicit and tested
- [x] Final fallback behavior is deterministic
- [x] Logs distinguish retryable invalid output from provider hard failures

## Implementation Notes
- The retry loop lives inside `OpenAIWorkoutPlanClient.generate_workout_plan()`. That is
  the right boundary because malformed output is an SDK-response concern, not an HTTP
  route concern.
- Only invalid structured output is retried. Refusals and hard SDK errors still fail
  immediately. This keeps retry logic narrow and avoids hiding real provider failures.
- Timeout handling is explicit through `timeout=self._settings.openai_timeout_seconds` on
  the OpenAI request path. The client maps timeout failures to a stable application error
  instead of leaking provider exceptions upward.
- Fallback behavior returns a schema-valid `WorkoutPlan` rather than changing the API
  shape. That keeps downstream callers simpler and prevents fallback mode from becoming a
  second response contract.
- The fallback plan is intentionally conservative. It favors low-intensity movement,
  safety notes, and minimal assumptions because its purpose is graceful degradation, not
  personalization quality.

## Verification
- Unit tests for invalid output then success
- Unit tests for invalid output then fallback/error after max attempts
- Unit tests for timeout mapping
- Automated validation: `cd backend && uv run pytest tests -q`
