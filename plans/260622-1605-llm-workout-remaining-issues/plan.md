---
title: LLM workout generation remaining issues
description: >-
  Implementation plan for the remaining OpenAI generation, reliability, metrics,
  and local test coverage issues.
status: completed
priority: P1
branch: feature/domain-schemas
tags:
  - llm
  - openai
  - workout-plan
  - github-issues
blockedBy: []
blocks: []
created: '2026-06-22T16:05:46.385Z'
createdBy: 'ck:plan'
source: skill
---

# LLM workout generation remaining issues

## Overview

The repository already contains a direct `AsyncOpenAI` wrapper, prompt builder, route,
service layer, and several schema and client tests. The missing work is concentrated in
four gaps: closing the direct structured-generation issue with clearer documentation and
verification, adding reliability controls around malformed or slow model responses,
adding basic usage metrics, and finishing local test and README coverage.

This plan keeps the scope narrow. It does not redesign the API surface, add third-party
observability, or expand into RAG. It completes the MVP-quality LLM feature set already
started in `backend/app/llm`, `backend/app/services`, and `backend/tests`.

## Phases

| Phase | Name | Status |
|-------|------|--------|
| 1 | [Implement direct OpenAI structured generation](./phase-01-implement-direct-openai-structured-generation.md) | Completed |
| 2 | [Add LLM reliability handling](./phase-02-add-llm-reliability-handling.md) | Completed |
| 3 | [Add basic LLM usage metrics](./phase-03-add-basic-llm-usage-metrics.md) | Completed |
| 4 | [Add basic tests for local AI feature](./phase-04-add-basic-tests-for-local-ai-feature.md) | Completed |

## Dependencies

- Existing baseline implementation in `backend/app/llm/openai_client.py`,
  `backend/app/llm/prompts.py`, `backend/app/services/workout_plan_generator.py`,
  and `backend/app/api/routes_generate.py`
- Existing schema contract in `backend/app/schemas/profile.py` and
  `backend/app/schemas/workout_plan.py`
- Existing tests in `backend/tests/schemas`, `backend/tests/llm`, `backend/tests/api`,
  and `backend/tests/services`
- Prior exploratory plan in `plans/260622-1535-workout-plan-generation/`

## Success Criteria

- [x] The remaining four GitHub issues are broken into implementation-ready phases with
      scope, architecture, files, risks, and verification steps.
- [x] Four issue-ready markdown docs exist in this plan directory and can be copied into
      GitHub issues with minimal editing.
- [x] The plan clearly distinguishes already-complete work from still-missing work so
      implementation does not duplicate current code.
