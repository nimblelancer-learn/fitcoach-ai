---
phase: 3
title: Validate safety policy docs and tests
status: completed
priority: P2
effort: 20m
dependencies:
  - 2
---

# Phase 3: Validate safety policy docs and tests

## Overview

Run focused prompt and schema-adjacent tests, then document where the safety
policy lives and how it relates to the backend behavior.

## Requirements

- Functional: validate the prompt contract with focused tests.
- Functional: expose the policy doc from repo entry points.
- Non-functional: keep validation narrow and fast.

## Architecture

Validate only the prompt layer and docs touched by this issue. Use README links
so future contributors can find the policy before touching safety work.

## Related Code Files

- Modify: `README.md`
- Modify: `backend/README.md`
- Modify: `plans/260624-issue-17-safety-policy-and-medical-boundaries/plan.md`

## Implementation Steps

1. Run focused prompt tests.
2. Link the safety policy from the main repo docs.
3. Capture validation results for the GitHub issue comment.

## Success Criteria

- [ ] Focused tests pass.
- [ ] The policy doc is discoverable from the repo docs.
