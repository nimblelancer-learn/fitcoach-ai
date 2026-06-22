---
phase: 3
title: Add basic LLM usage metrics
status: completed
priority: P2
effort: 0.75d
dependencies:
  - 1
  - 2
---

# Phase 3: Add basic LLM usage metrics

## Overview
This phase adds lightweight observability around each generation call: latency, token
usage, estimated cost, and model name. The goal is not full tracing. The goal is
operational visibility through consistent structured logs.

## Requirements
- Functional: Log model name for every generation attempt.
- Functional: Track latency per request.
- Functional: Read token usage from the OpenAI response when available.
- Functional: Estimate request cost from token usage and configured model pricing.
- Functional: Keep logs useful even when usage data is absent.
- Non-functional: Do not add an external observability dependency in this phase.
- Non-functional: Keep metric emission local to the OpenAI client boundary.

## Architecture
Recommended implementation:

```text
start = monotonic()
response = await call_openai(...)
latency_ms = elapsed_ms(start)
usage = response.usage or None
cost = estimate_cost(model, usage) or None
logger.info(
  "openai_workout_plan_response model=%s latency_ms=%s input_tokens=%s output_tokens=%s estimated_cost_usd=%s",
  ...
)
```

Use a small pricing table inside the app for the configured model family, or return
`None` when the model is unknown. Unknown cost is acceptable as long as the log makes
that explicit.

## Related Code Files
- Modify: `backend/app/llm/openai_client.py`
- Create or Modify: `backend/app/llm/pricing.py`
- Modify: `backend/tests/llm/test_openai_client.py`
- Modify: `README.md`
- Modify: `backend/README.md`

## Implementation Steps
1. Add monotonic timing around the provider call.
2. Extract usage fields from the OpenAI response in a defensive way.
3. Centralize model pricing and cost estimation in a tiny helper module.
4. Log model, latency, token counts, retry count if available, and estimated cost.
5. Document the meaning and limits of these metrics in README.

## Success Criteria
- [x] Each generation request emits latency and model name.
- [x] Token usage is logged when the provider returns usage metadata.
- [x] Cost estimation is logged or explicitly marked unavailable.
- [x] Metric-related behavior is unit-tested without real network calls.

## Risk Assessment
The main risk is misleading cost reporting if pricing assumptions are buried in the
client. Mitigation: isolate pricing constants, document them, and make unknown-model
behavior explicit instead of guessing.
