# Issue 3: Add basic LLM usage metrics

## Summary
Implemented lightweight request-level metrics for the OpenAI workout-plan generation
call. The goal is not full observability yet. The goal is to make local and backend
behavior measurable enough to answer basic operational questions quickly.

## Current State
- Implemented: request logs include model name
- Implemented: response logs include model name, attempt number, latency, token usage,
  and estimated cost
- Implemented: token usage extraction from `response.usage`
- Implemented: total-token fallback when the provider omits `total_tokens`
- Implemented: estimated cost helper via `backend/app/llm/pricing.py`
- Implemented: optional env-based pricing override for runtime cost estimation
- Implemented: unknown pricing logs as `estimated_cost_usd=unavailable`

## Scope
- Add latency timing
- Extract token usage when available
- Estimate cost from model pricing
- Emit structured logs without adding a full observability platform

## Why This Matters

Basic LLM metrics answer the first layer of production questions:

- Is the request slow because of the provider or because of our own app?
- Are we sending or receiving more tokens than expected?
- Did a prompt or retry change cost materially?
- Are fallback and retry paths hiding an expensive failure mode?

Without these metrics, debugging LLM behavior becomes guesswork. With them, even plain
application logs become useful for profiling, regression checks, and later cost reviews.

## Delivered
- [x] Measured elapsed time for each OpenAI generation request
- [x] Extracted usage metadata from OpenAI response
- [x] Added helper for model pricing and cost estimation
- [x] Added env-configurable pricing override for runtime cost estimation
- [x] Logged model name, latency, token counts, and estimated cost
- [x] Logged `estimated_cost_usd=unavailable` when pricing cannot be computed
- [x] Added unit tests for usage extraction and cost estimation behavior

## Acceptance Criteria
- [x] Every request logs model name and latency
- [x] Token usage is logged when returned by the SDK
- [x] Estimated cost is computed or explicitly unavailable
- [x] Metrics logic is testable without real OpenAI calls

## Implementation Notes
- Metric collection stays at the OpenAI client boundary in
  `backend/app/llm/openai_client.py`. This is the cleanest place because the client has
  the provider response, retry attempt number, timing window, and model name in one
  place.
- Latency is measured with `perf_counter()` around the provider call. This avoids mixing
  provider latency with unrelated app work before or after the SDK request.
- Token usage is read defensively from `response.usage`. If the provider returns
  `input_tokens` and `output_tokens` but omits `total_tokens`, the client reconstructs
  total tokens locally.
- Cost estimation is intentionally separated into `backend/app/llm/pricing.py`. That
  keeps pricing assumptions out of the orchestration code and makes future updates easier.
- Runtime cost estimation can be driven from settings with
  `OPENAI_INPUT_COST_PER_MILLION_TOKENS_USD` and
  `OPENAI_OUTPUT_COST_PER_MILLION_TOKENS_USD`. This avoids hardcoding mutable pricing
  data into the request path.
- The current pricing helper is conservative: if the model is not present in the local
  pricing table, the code logs `estimated_cost_usd=unavailable` instead of guessing.
  That is a deliberate design choice. Wrong cost is worse than missing cost for early
  observability.
- Response-side metric logs include:
  - model name
  - retry attempt number
  - latency in milliseconds
  - input tokens
  - output tokens
  - total tokens
  - estimated cost in USD or `unavailable`

## How It Helps Later

- Performance debugging: latency spikes become visible immediately in logs.
- Prompt tuning: token growth can be correlated with prompt changes.
- Retry analysis: repeated invalid-output attempts can be compared against token and time
  cost.
- Cost hygiene: even a rough estimate helps catch runaway usage early before adding a
  dedicated observability platform.
- Migration readiness: when moving to Langfuse or another tracing stack later, the team
  already knows which dimensions matter.

## Verification
- Unit tests for latency and usage extraction paths
- Unit tests for known-model and unknown-model cost cases
- Manual log inspection from a local request if desired
- Automated validation: `cd backend && uv run pytest tests -q`
- Static validation: `cd backend && uv run ruff check app tests`
