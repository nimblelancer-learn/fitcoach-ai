---
title: GitHub issue 18 basic safety guardrails
description: >-
  Add prompt-risk detection, safety fallback templates, beginner/unsafe-plan
  validation, and trigger logging around workout generation.
status: pending
priority: P2
branch: issue-18-basic-safety-guardrails
tags: []
blockedBy: []
blocks: []
created: '2026-06-24T19:09:54.827Z'
createdBy: 'ck:plan'
source: skill
---

# GitHub issue 18 basic safety guardrails

## Overview

Issue 18 turns the documented safety policy into lightweight runtime guardrails.
The safest insertion point is the OpenAI client boundary, where prompt fields,
parsed output, fallback generation, and event logging already converge.

## Phases

| Phase | Name | Status |
|-------|------|--------|
| 1 | [Review generation and safety guardrail insertion points](./phase-01-review-generation-and-safety-guardrail-insertion-points.md) | Pending |
| 2 | [Implement safety trigger detection and fallback validation](./phase-02-implement-safety-trigger-detection-and-fallback-validation.md) | Completed |
| 3 | [Validate safety guardrails and docs](./phase-03-validate-safety-guardrails-and-docs.md) | Pending |

## Dependencies

- Builds directly on issue 17's policy document and prompt boundary rules.
