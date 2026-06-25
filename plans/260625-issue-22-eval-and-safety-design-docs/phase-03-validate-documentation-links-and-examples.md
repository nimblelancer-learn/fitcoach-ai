---
phase: 3
title: Validate documentation links and examples
status: completed
priority: P2
effort: 15m
dependencies:
  - 2
---

# Phase 3: Validate documentation links and examples

## Overview

Validate links, examples, and internal references after the doc updates.

## Requirements
- Functional: ensure the new docs are linked and examples match current code
- Non-functional: keep validation lightweight and local

## Architecture
Validation is a consistency pass across docs and file references. The goal is
to catch stale paths or examples that no longer match the implemented guardrail
and eval behavior.

## Related Code Files
- Modify: `plans/260625-issue-22-eval-and-safety-design-docs/plan.md`
- Review: `docs/eval-design.md`
- Review: `docs/safety-policy.md`
- Review: `README.md`

## Implementation Steps

1. Re-read the updated docs for stale references.
2. Confirm file paths and commands exist.
3. Prepare the issue summary for the GitHub handoff.

## Success Criteria

- [ ] Docs are internally consistent and reference real repo artifacts.
