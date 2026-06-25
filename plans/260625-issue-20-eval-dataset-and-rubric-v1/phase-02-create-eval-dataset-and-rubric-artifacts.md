---
phase: 2
title: Create eval dataset and rubric artifacts
status: completed
priority: P2
effort: 1h
dependencies:
  - 1
---

# Phase 2: Create eval dataset and rubric artifacts

## Overview

Author the checked-in dataset and scoring rubric files for workout-plan evals.

## Requirements
- Functional: create 30 cases with expected behavior and risk tags; create a
  rubric with scoring dimensions and failure rules
- Non-functional: keep the files deterministic, explicit, and versioned

## Architecture
The dataset should store:
- case metadata
- `UserProfile`-compatible input
- expected behavior bullets
- risk tags

The rubric should store:
- rubric metadata and version
- scoring dimensions with descriptions and weights
- hard-fail conditions for medical-risk or contract-violation cases

## Related Code Files
- Create: `backend/app/evals/workout_plan_eval_dataset_v1.json`
- Create: `backend/app/evals/workout_plan_eval_rubric_v1.json`
- Create: `backend/app/evals/README.md`

## Implementation Steps

1. Write 30 representative cases spanning baseline, equipment constraints, mild
   limitations, medical-risk prompts, and beginner-overload expectations.
2. Add expected behavior bullets to every case.
3. Add risk tags to every case from a controlled vocabulary.
4. Define a scoring rubric that future runner code can apply consistently.

## Success Criteria

- [ ] The dataset contains 30 complete cases.
- [ ] The rubric defines clear scoring and hard-fail expectations.
