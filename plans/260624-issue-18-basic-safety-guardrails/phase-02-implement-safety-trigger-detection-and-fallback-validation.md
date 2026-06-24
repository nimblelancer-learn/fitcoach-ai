---
phase: 2
title: Implement safety trigger detection and fallback validation
status: completed
priority: P2
effort: 90m
dependencies:
  - 1
---

# Phase 2: Implement safety trigger detection and fallback validation

## Overview

Add basic runtime checks for risky medical wording and unsafe beginner plans,
then route triggered cases to conservative structured fallbacks.

## Implementation Steps

1. Detect high-risk medical or rehabilitation keywords from the prompt payload.
2. Add a safety fallback template for triggered cases.
3. Validate beginner intensity and unsafe exercise names in generated plans.
4. Log safety trigger events with stable trigger codes.

## Success Criteria

- [ ] Prompt-risk detection covers medical and rehabilitation triggers.
- [ ] Triggered requests return a conservative structured fallback.
- [ ] Beginner and unsafe-exercise validators can redirect bad plans to safety fallback.
