---
phase: 3
title: "Validate retrieval behavior and docs"
status: completed
effort: "45m"
---

# Phase 3: Validate retrieval behavior and docs

## Overview

Validated the new retrieval path with focused automated tests and documented the
runtime knobs and debug outputs.

## Implementation Steps

1. Added tests for:
   - retriever mapping from Qdrant payloads
   - grounded prompt formatting
   - service-level retrieval orchestration and fallback
   - API debug headers
2. Documented `RAG_RETRIEVAL_LIMIT` and generation debug headers in
   `backend/README.md`.
3. Ran:
   - `uv run pytest backend/tests/llm/test_prompts.py backend/tests/services/test_workout_plan_generator.py backend/tests/api/test_generate_workout_plan.py backend/tests/rag/test_retriever.py -q`
   - `uv run pytest backend/tests/rag backend/tests/llm/test_prompts.py backend/tests/services/test_workout_plan_generator.py backend/tests/api/test_generate_workout_plan.py -q`
4. Recorded the remaining external blocker:
   - `backend/tests/llm/test_openai_client.py` cannot be collected in this
     environment because the `openai` package is not installed here.

## Success Criteria

- [x] Focused retrieval and generation tests pass.
- [x] Runtime configuration and debug behavior are documented.
- [x] The remaining validation gap is explicit and environment-specific.
