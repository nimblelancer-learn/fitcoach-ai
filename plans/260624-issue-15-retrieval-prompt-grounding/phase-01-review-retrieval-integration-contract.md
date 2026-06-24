---
phase: 1
title: "Review retrieval integration contract"
status: completed
effort: "30m"
---

# Phase 1: Review retrieval integration contract

## Overview

Reviewed the current generation flow, Qdrant indexing contract, and the issue
scope from the master plan to identify the smallest integration surface.

## Implementation Steps

1. Confirmed issues 12-14 were already merged on `main`, making issue 15 the
   next oldest unfinished issue in sequence.
2. Reviewed `app.services.workout_plan_generator`, `app.llm.prompts`,
   `app.rag.index`, `app.rag.qdrant_client`, and the generation route.
3. Derived the required contract:
   - retrieval query should be built from the existing `UserProfile`
   - retrieved Qdrant payloads should preserve chunk metadata and text
   - prompt grounding must not break the existing profile field extraction in
     `OpenAIWorkoutPlanClient`
   - endpoint debug output should not change the JSON schema
4. Chose response headers for lightweight debug output to avoid changing the
   `WorkoutPlan` response model.

## Success Criteria

- [x] Retrieval integration points are identified without changing the API body schema.
- [x] The Qdrant payload contract needed by generation is explicit.
- [x] A concrete implementation path is defined for phases 2 and 3.
