---
phase: 3
title: Validate deployed MVP
status: in-progress
priority: P1
effort: 2-4h
dependencies:
  - 2
---

# Phase 3: Validate deployed MVP

## Overview

Verify that the deployed service actually satisfies the issue acceptance
criteria and leaves the repo in a state where `#43` and `#44` can proceed
without reinterpretation.

## Requirements

- Functional: confirm public backend and frontend URLs are reachable
- Functional: confirm workout-plan generation works end to end in the deployed
  environment
- Functional: confirm required services and environment variables are documented
- Functional: add the public demo link to `README.md`
- Non-functional: capture validation evidence suitable for issue comment and PR

## Architecture

Validation should include both local and deployed checks:

- local: lint, tests, container build, route smoke tests
- deployed: health check, public page load, workout generation request, Qdrant
  connectivity where observable, and documentation review

## Related Code Files

- Modify: `README.md`
- Modify: issue comment draft file if needed
- Inspect: deployed URLs and PR status

## Implementation Steps

1. Run local validation commands before PR creation.
2. Deploy the chosen stack and verify public URLs.
3. Run end-to-end workout generation against the deployed app.
4. Add the public demo URL to `README.md` and any maintenance notes required by
   the issue.
5. Complete git/GitHub workflow: commit, push, PR, merge if allowed, issue
   comment, close.

## Success Criteria

- [ ] Public backend and frontend URLs are verified.
- [ ] End-to-end deployed workout generation is verified.
- [ ] `README.md` contains the public demo link.
- [ ] The issue can be closed with evidence.
