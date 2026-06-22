# Issue 4: Add basic tests for local AI feature

## Summary
Completed the local test story for the AI workout-plan feature and documented the
canonical test commands in the repo README files.

## Current State
- Implemented: schema tests exist
- Implemented: valid profile input test exists
- Implemented: invalid profile input tests exist
- Implemented: malformed output handling tests cover retry and fallback behavior
- Implemented: timeout handling tests exist
- Implemented: metrics-helper tests exist
- Implemented: README and backend README include test commands

## Scope
- Extend local unit and API tests only
- Preserve opt-in integration tests for real OpenAI calls
- Add test documentation to README

## Delivered
- [x] Preserved current schema tests
- [x] Added retry/fallback tests to the LLM client suite
- [x] Added timeout-handling tests
- [x] Added metrics-helper tests
- [x] Added local test commands to `README.md` and `backend/README.md`
- [x] Documented the opt-in integration path separately from default local tests

## Acceptance Criteria
- [x] Local tests cover valid and invalid profile inputs
- [x] Local tests cover malformed output retry/fallback behavior
- [x] Local tests cover timeout behavior
- [x] README contains a copy-paste test command

## Implementation Notes
- Test layering stayed intentional:
  - schema tests own pure Pydantic contract checks
  - LLM client tests own retry, timeout, fallback, and metrics branches
  - API tests continue to own envelope behavior and request validation
  - integration tests remain opt-in for real provider calls
- The main growth happened in `backend/tests/llm/test_openai_client.py`, where the suite
  now covers:
  - retry after invalid parsed output
  - fallback after retry exhaustion
  - timeout mapping
  - usage logging
  - unavailable cost logging
  - cost helper behavior for unknown models
- The canonical local command is:
  `cd backend && uv run pytest tests -q`

## Verification
- Run the documented unit-test command locally
- Keep integration tests opt-in via env guard
- Final validation run: `48 passed, 1 skipped`
