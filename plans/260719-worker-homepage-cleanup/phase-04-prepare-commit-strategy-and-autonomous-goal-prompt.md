---
phase: 4
title: "Prepare commit strategy and autonomous goal prompt"
status: completed
priority: P2
effort: "1-2h"
dependencies: [1, 2, 3]
---

# Phase 4: Prepare commit strategy and autonomous goal prompt

## Overview

Finish the branch in a way that is easy to review later: define commit grouping,
capture deployment caveats, and generate a reusable `/goal` prompt for
autonomous execution.

## Requirements

- Functional: propose the exact commit grouping for the cleaned branch.
- Functional: document what should remain uncommitted if any purely local files
  still exist.
- Functional: generate one copy-paste-ready `/goal` prompt that can drive the
  full implementation autonomously.
- Non-functional: the prompt must constrain scope, enforce validation loops,
  and avoid feature creep.

## Architecture

This phase is handoff-oriented:

- no new product scope
- one concise execution prompt
- one clear commit strategy tied to the existing repo structure

## Related Code Files

- Modify: `plans/260719-worker-homepage-cleanup/plan.md`
- Create: `plans/260719-worker-homepage-cleanup/goal-prompt.md`
- Review: `.gitignore`
- Review: `public/index.html`
- Review: `cloudflare/**`

## Implementation Steps

1. Summarize the final commit boundaries after cleanup and test changes settle.
2. Confirm whether deployment remains manual or if any CI/CD auto-deploy path
   has been introduced.
3. Generate a `/goal` prompt using the plan artifacts as the source contract.
4. Make the prompt explicit about skills, validation loops, non-goals, and
   completion criteria.

## Success Criteria

- [ ] A clear commit strategy exists for the branch.
- [ ] Local-only artifacts are explicitly excluded from commit.
- [ ] A reusable autonomous `/goal` prompt is checked in alongside the plan.

## Risk Assessment

Main risk: generating a vague prompt that re-opens product decisions.
Mitigation: pin the prompt to the Cloudflare Worker surface, current file set,
and current MVP boundaries only.
