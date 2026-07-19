---
phase: 1
title: "Audit and cleanup working tree"
status: completed
priority: P2
effort: "1-2h"
dependencies: []
---

# Phase 1: Audit and cleanup working tree

## Overview

Separate commit-worthy product changes from local-only artifacts, then normalize
the working tree so later commits are deliberate instead of accidental.

## Requirements

- Functional: identify tracked vs untracked changes, classify them into
  deploy/runtime, public UI, backend reference, docs, tests, and local
  generated artifacts.
- Functional: remove or ignore files that should never be committed, including
  `.wrangler/` cache output and duplicate ignore entries.
- Non-functional: do not discard user changes blindly; preserve all intentional
  code/doc work already in progress.

## Architecture

This phase is bookkeeping, not feature work. The output is a clean map of the
branch:

- local-only artifacts get ignored or deleted safely
- intentional source changes stay visible
- commit boundaries become obvious before UI refactoring starts

## Related Code Files

- Modify: `.gitignore`
- Review: `wrangler.toml`
- Review: `README.md`
- Review: `backend/README.md`
- Review: `backend/app/**`
- Review: `cloudflare/**`
- Review: `public/index.html`

## Implementation Steps

1. Audit `git status --short` and `git diff --stat` to classify every change.
2. Add missing ignore rules for `.wrangler/` and de-duplicate `.deploy.env`.
3. Verify only deployment-safe config remains tracked, especially
   `wrangler.toml`, docs, and Worker source.
4. Produce a recommended commit grouping so the implementation phase can stage
   intentionally.

## Success Criteria

- [ ] `.wrangler/` and similar local artifacts are not candidates for commit.
- [ ] `.gitignore` is minimal, non-duplicated, and covers local deploy files.
- [ ] The branch has a clear file grouping for later commits.

## Risk Assessment

Main risk: deleting or hiding real work under the label of “cleanup.”
Mitigation: only remove generated cache artifacts and document every proposed
commit group before staging.
