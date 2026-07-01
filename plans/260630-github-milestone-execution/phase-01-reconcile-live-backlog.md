---
phase: 1
title: Reconcile live backlog
status: completed
priority: P1
effort: 1h
dependencies: []
---

# Phase 1: Reconcile live backlog

## Overview

Confirm the live repository and GitHub state, compare the current open issue
queue against the supplied milestone ordering, and translate the result into an
execution-ready queue with explicit dependency notes and decision checkpoints.

## Requirements

- Functional: confirm remote, branch, worktree cleanliness, and GitHub auth
- Functional: fetch live open issues with milestone, labels, created date, and
  URLs
- Functional: identify exact differences between live issue ordering and the
  supplied target ordering
- Functional: derive milestone-local execution order from dependencies when it
  differs from raw created date
- Non-functional: use the repository workflow docs as the execution contract
- Non-functional: do not start implementation until the first issue plan and
  decision boundary are clear

## Architecture

This phase is control-plane only. It does not change runtime application code.
Its outputs are:

1. a verified live issue queue
2. an execution order per milestone
3. identified blockers or decision gates
4. a repository plan artifact that later issue execution can reference

## Related Code Files

- Modify: `plans/260630-github-milestone-execution/plan.md`
- Modify: `plans/260630-github-milestone-execution/phase-01-reconcile-live-backlog.md`
- Modify: `plans/260630-github-milestone-execution/phase-02-execute-m4.md`

## Implementation Steps

1. Read the required repository docs and validate workflow constraints.
2. Confirm `origin`, `gh auth status`, current branch, and worktree state.
3. Fetch the live open issues and compare milestone membership and created-date
   order to the supplied target queue.
4. Derive dependency-aware ordering for `M4` and note where external blockers
   are likely.
5. Capture the results in the project plan and set the first decision checkpoint
   on issue `#42`.

## Success Criteria

- [x] Repo and GitHub readiness are verified from current state.
- [x] Live milestone membership and ordering differences are documented.
- [x] `M4` dependency-aware execution order is identified.
- [x] The first gating decision for `#42` is explicit.
