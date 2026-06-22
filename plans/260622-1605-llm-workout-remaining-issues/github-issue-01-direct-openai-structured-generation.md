# Issue 1: Implement direct OpenAI structured generation

## Summary
Implemented the direct OpenAI structured generation flow for workout-plan creation and
documented how the request moves through the backend.

## Current State
- Implemented: `OpenAIWorkoutPlanClient` wraps `AsyncOpenAI`
- Implemented: `Settings` loads `OPENAI_API_KEY` and `OPENAI_MODEL` from environment
- Implemented: `build_workout_plan_prompt()` creates the first workout-plan prompt
- Implemented: `responses.parse(..., text_format=WorkoutPlan)` produces structured output
- Implemented: `WorkoutPlan.model_validate(...)` revalidates parsed output before returning
- Implemented: request example for `POST /generate/workout-plan`
- Implemented: README and backend README setup notes for local generation

## Scope
- Keep the direct SDK call path
- Keep the current route/service/client layering
- Document the local generation flow
- Verify route and sample request docs

## Delivered
- [x] Verified `POST /generate/workout-plan` as the documented generation entrypoint
- [x] Documented required env vars: `OPENAI_API_KEY`, `OPENAI_MODEL`
- [x] Documented the direct call path from route -> service -> prompt -> OpenAI client
- [x] Added a request example for local manual testing
- [x] Separated baseline generation from later reliability and metrics concerns

## Acceptance Criteria
- [x] Direct OpenAI structured generation is clearly documented
- [x] Structured output and Pydantic validation are explicitly called out
- [x] Local setup for generation is readable without code archaeology
- [x] This issue stays focused on the baseline generation path; retry, timeout, fallback,
      and metrics are handled in separate issues

## Implementation Notes
- The generation path is intentionally thin:
  `routes_generate.py` owns HTTP input/output, `WorkoutPlanGenerator` owns prompt
  delegation, and `OpenAIWorkoutPlanClient` owns the provider SDK call.
- The OpenAI call uses `responses.parse(..., text_format=WorkoutPlan)` so the provider is
  asked for structured output rather than free-form prose.
- The app revalidates the parsed result with `WorkoutPlan.model_validate(...)` before it
  returns the object to the API layer. This keeps the application schema as the final
  contract, not the SDK helper alone.
- Docs were updated in `README.md`, `backend/README.md`, and
  `backend/app/examples/requests.http` so the flow is visible without reading code first.

## Verification
- Confirm route wiring in FastAPI app
- Confirm sample request docs
- Confirm env config is present in `.env.example`
- Automated validation: `cd backend && uv run pytest tests -q`
