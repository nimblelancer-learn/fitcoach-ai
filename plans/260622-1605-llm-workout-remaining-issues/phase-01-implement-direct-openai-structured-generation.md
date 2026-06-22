---
phase: 1
title: Implement direct OpenAI structured generation
status: completed
priority: P1
effort: 0.5d
dependencies: []
---

# Phase 1: Implement direct OpenAI structured generation

## Overview
Most of this issue is already present in the repo. This phase closes the gap between
"working code exists" and "issue can be marked done" by verifying the direct SDK path,
documenting configuration and request flow, and aligning acceptance criteria with the
actual implementation.

## Requirements
- Functional: Keep generation flowing through the direct OpenAI SDK wrapper, prompt
  builder, service, and `/generate/workout-plan` route.
- Functional: Ensure environment-based configuration is explicit and documented for
  `OPENAI_API_KEY` and `OPENAI_MODEL`.
- Functional: Preserve structured output via the `WorkoutPlan` schema contract.
- Non-functional: Avoid refactoring unrelated app layers or introducing framework
  abstractions over the OpenAI call.

## Architecture
The intended request path is:

```text
POST /generate/workout-plan
  -> routes_generate.generate_workout_plan()
  -> WorkoutPlanGenerator.generate(profile)
  -> build_workout_plan_prompt(profile)
  -> OpenAIWorkoutPlanClient.generate_workout_plan(messages)
  -> AsyncOpenAI.responses.parse(..., text_format=WorkoutPlan)
  -> WorkoutPlan.model_validate(...)
```

The current code already follows this architecture. Remaining work is largely issue
closure hygiene: verify the route contract, fill any missing README/setup details, and
ensure the issue doc states exactly what is already shipped versus what remains in later
phases.

## Related Code Files
- Modify: `README.md`
- Modify: `backend/README.md`
- Modify: `backend/app/examples/requests.http`
- Verify: `backend/app/llm/openai_client.py`
- Verify: `backend/app/llm/prompts.py`
- Verify: `backend/app/services/workout_plan_generator.py`
- Verify: `backend/app/api/routes_generate.py`

## Implementation Steps
1. Confirm the issue uses the existing direct SDK wrapper rather than introducing any new
   abstraction layer.
2. Add concise setup and usage documentation for the local generation flow, including the
   required environment variables.
3. Verify the route and sample request docs show the structured generation entrypoint.
4. Update the issue doc so its task list explicitly marks wrapper, env loading, prompt,
   structured output, and Pydantic validation as delivered.

## Success Criteria
- [x] Direct OpenAI structured generation is documented as a concrete request flow.
- [x] README and/or backend README explain the minimum env setup for local generation.
- [x] Sample request documentation points to `POST /generate/workout-plan`.
- [x] The issue can be closed without claiming work that belongs to retry, timeout, or
      metrics phases.

## Risk Assessment
The main risk is false closure: code exists, but the issue doc may hide missing setup or
verification details. Mitigation: keep this phase narrowly focused on baseline generation
and push reliability and metrics work into later phases instead of mixing concerns.
