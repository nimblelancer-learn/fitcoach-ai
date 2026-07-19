---
phase: 2
title: "Refactor public homepage UI"
status: completed
priority: P2
effort: "4-6h"
dependencies: [1]
---

# Phase 2: Refactor public homepage UI

## Overview

Turn the Cloudflare homepage into a clean desktop-friendly product page that
focuses on user input, not project narrative, while keeping the existing public
form flow intact.

## Requirements

- Functional: remove public UI copy related to project-building, learning,
  interviews, observability roadmap, and internal process.
- Functional: keep only a short app introduction, the user input form, result
  rendering, and feedback flow that directly serves end users.
- Functional: add a visible language switch for Vietnamese and English.
- Functional: ensure form labels, helper text, alerts, buttons, and empty
  states all switch deterministically between the two languages.
- Non-functional: desktop layout must feel centered and balanced, without the
  current title compression and left-heavy hero layout.
- Non-functional: mobile behavior must remain intact.

## Architecture

The implementation should stay inside the existing static-asset Worker surface:

- `public/index.html` remains the main public document
- copy should move into a structured in-page dictionary or similarly explicit
  client-side translation map
- the language switch should update UI copy only; request payload values and API
  contracts must stay unchanged
- preserve the current `fetch` submission flow to Worker endpoints

## Related Code Files

- Modify: `public/index.html`
- Review: `cloudflare/worker.mjs`
- Review: `cloudflare/worker.test.mjs`
- Modify: `cloudflare/public_ui_copy.test.mjs`

## Implementation Steps

1. Audit the current homepage sections and mark every block that is product UI
   versus project/process exposition.
2. Simplify the page structure to a centered hero plus form/result surface.
3. Fix desktop spacing, widths, and alignment so the headline no longer feels
   squeezed to one side.
4. Introduce a small bilingual copy system for Vietnamese and English.
5. Add a language-toggle control with accessible state indication.
6. Keep generated-plan and feedback panels aligned with the same language system
   where copy is local UI text.

## Success Criteria

- [ ] The public page no longer mentions learning portal, project evidence,
  internal roadmap language, or interview framing.
- [ ] Headline and hero layout are visually centered and usable on desktop.
- [ ] Vietnamese and English toggles update the visible UI copy without
  changing API payload semantics.
- [ ] The page remains functional on mobile and desktop.

## Risk Assessment

Main risk: mixing translated UI strings with payload or schema fields, causing
submission regressions.
Mitigation: constrain translation to presentation text only and leave request
values, enums, and API JSON untouched.
