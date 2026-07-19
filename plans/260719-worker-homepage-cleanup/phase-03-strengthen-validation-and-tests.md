---
phase: 3
title: "Strengthen validation and tests"
status: completed
priority: P1
effort: "3-5h"
dependencies: [2]
---

# Phase 3: Strengthen validation and tests

## Overview

Add regression coverage around the cleaned homepage and tighten validation so
the public Worker surface fails predictably instead of silently drifting.

## Requirements

- Functional: extend tests to verify the new language switch and the removal of
  unwanted project/process copy from the public homepage.
- Functional: tighten request validation assertions where the public Worker
  currently accepts ambiguous or weak input.
- Functional: verify preserved success paths for `/api/workout-plans` and
  `/api/feedback`.
- Non-functional: tests should be deterministic, local, and cheap to run.

## Architecture

Validation remains split across:

- static UI assertions in `cloudflare/public_ui_copy.test.mjs`
- Worker endpoint tests in `cloudflare/worker.test.mjs`
- optional backend reference tests only when shared behavior is touched

The public Worker path is the priority. Do not expand test scope into unrelated
legacy FastAPI surfaces unless the implementation changes them directly.

## Related Code Files

- Modify: `cloudflare/public_ui_copy.test.mjs`
- Modify: `cloudflare/worker.test.mjs`
- Review: `public/index.html`
- Optional modify: `backend/tests/api/test_web_home.py`

## Implementation Steps

1. Replace brittle copy assertions with ones aligned to the new public wording.
2. Add assertions for language-toggle controls and bilingual UI state.
3. Inspect Worker validation branches and add coverage for any tightened input
   rules introduced during the UI cleanup.
4. Re-run focused Worker tests after each meaningful change.

## Success Criteria

- [ ] UI tests assert the new simplified public copy and language controls.
- [ ] Worker tests cover the tightened validation behavior introduced by the
  implementation.
- [ ] Public Worker smoke tests pass locally after the changes.

## Risk Assessment

Main risk: asserting too much exact copy and making the suite fragile.
Mitigation: assert the important product contract and language-switch presence,
not every cosmetic sentence.
