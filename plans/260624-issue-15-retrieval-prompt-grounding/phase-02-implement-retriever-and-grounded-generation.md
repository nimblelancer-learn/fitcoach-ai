---
phase: 2
title: "Implement retriever and grounded generation"
status: completed
effort: "2h"
---

# Phase 2: Implement retriever and grounded generation

## Overview

Implemented the retrieval path from Qdrant into prompt construction and the
generation endpoint.

## Implementation Steps

1. Added `app.rag.retriever.KnowledgeRetriever` plus `RetrievedChunk` and
   `build_retrieval_query`.
2. Extended `QdrantClient` with a `search_points()` call that reads top-k
   matches from the existing collection.
3. Updated `WorkoutPlanGenerator` to:
   - build a retrieval query from `UserProfile`
   - retrieve top-k chunks before prompt construction
   - log retrieved chunk IDs
   - preserve debug state for the request lifecycle
   - degrade gracefully when retrieval fails
4. Updated `build_workout_plan_prompt()` to inject retrieved knowledge context
   while keeping the original profile field lines stable for existing logging
   and fallback behavior in `OpenAIWorkoutPlanClient`.
5. Wired `KnowledgeRetriever` into app startup.
6. Exposed retrieval debug headers on `/generate/workout-plan` without changing
   the JSON response body.

## Success Criteria

- [x] The backend retrieves top-k relevant chunks from Qdrant before generation.
- [x] Grounded context is injected into the workout plan prompt.
- [x] Retrieval evidence is visible in logs and endpoint debug headers.
- [x] Generation still returns the existing structured `WorkoutPlan` schema.
