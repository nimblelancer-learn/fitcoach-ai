---
title: GitHub issue 17 safety policy and medical boundaries
description: >-
  Define the repo's safety policy v1, clarify medical boundaries, and anchor the
  LLM prompt to those rules.
status: pending
priority: P2
branch: issue-17-safety-policy-and-medical-boundaries
tags: []
blockedBy: []
blocks: []
created: '2026-06-24T19:05:15.566Z'
createdBy: 'ck:plan'
source: skill
---

# GitHub issue 17 safety policy and medical boundaries

## Overview

Issue 17 asks for a repository-level safety policy that separates general
fitness coaching from medical advice, identifies out-of-scope cases, and
defines refusal or fallback behavior. The repo already contains partial prompt
language and source-policy constraints, but there is no single policy document
or prompt regression coverage for these boundaries.

## Phases

| Phase | Name | Status |
|-------|------|--------|
| 1 | [Review current safety boundary coverage](./phase-01-review-current-safety-boundary-coverage.md) | Completed |
| 2 | [Implement safety policy and prompt boundaries](./phase-02-implement-safety-policy-and-prompt-boundaries.md) | Pending |
| 3 | [Validate safety policy docs and tests](./phase-03-validate-safety-policy-docs-and-tests.md) | Completed |

## Dependencies

- Uses the existing source-policy and safety corpus as boundary inputs.
- Must stay narrower than issue 18, which is reserved for runtime guardrails.
