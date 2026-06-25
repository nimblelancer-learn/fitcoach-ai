---
title: GitHub issue 20 create eval dataset and rubric v1
description: >-
  Create a first machine-readable evaluation dataset and scoring rubric for
  workout-plan generation, including expected behavior and risk tags for each
  case so later eval-runner work can consume the assets directly.
status: pending
priority: P2
branch: issue-20-create-eval-dataset-and-rubric-v1
tags: []
blockedBy: []
blocks: []
created: '2026-06-25T03:33:58.892Z'
createdBy: 'ck:plan'
source: skill
---

# GitHub issue 20 create eval dataset and rubric v1

## Overview

Issue 20 is an asset-definition task. The repo roadmap already mentions evals,
but there is no checked-in dataset or rubric yet. The implementation should
prefer deterministic checked-in JSON artifacts plus validation tests so issue 21
can focus on execution logic instead of debating file shape.

The output should include:

- a dataset with exactly 30 eval cases
- expected behavior for every case
- risk tags for every case
- a rubric that explains how future eval runs should score groundedness,
  personalization, safety, and fallback behavior

## Phases

| Phase | Name | Status |
|-------|------|--------|
| 1 | [Review eval artifact contract](./phase-01-review-eval-artifact-contract.md) | Pending |
| 2 | [Create eval dataset and rubric artifacts](./phase-02-create-eval-dataset-and-rubric-artifacts.md) | Completed |
| 3 | [Validate eval assets and tests](./phase-03-validate-eval-assets-and-tests.md) | Completed |

## Dependencies

- Builds on the current workout-plan schema, prompt contract, retrieval
  grounding, and safety guardrails already implemented in the backend.
- Should stay machine-readable so issue 21 can implement an eval runner without
  reformatting the assets first.
