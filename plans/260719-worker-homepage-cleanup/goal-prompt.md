/goal Execute Phase 1-4: Clean working tree and simplify public homepage.

You are implementing the current cleanup and UI-stabilization pass for the FitCoach AI public Cloudflare MVP.

Before implementation:
1. Read:
   - `README.md`
   - `backend/README.md`
   - `docs/cloudflare-migration-guide.md`
   - `plans/260714-cloudflare-feedback-launch/plan.md`
   - `plans/260719-worker-homepage-cleanup/plan.md`
   - `plans/260719-worker-homepage-cleanup/phase-01-audit-and-cleanup-working-tree.md`
   - `plans/260719-worker-homepage-cleanup/phase-02-refactor-public-homepage-ui.md`
   - `plans/260719-worker-homepage-cleanup/phase-03-strengthen-validation-and-tests.md`
   - `plans/260719-worker-homepage-cleanup/phase-04-prepare-commit-strategy-and-autonomous-goal-prompt.md`
   - `public/index.html`
   - `cloudflare/worker.mjs`
   - `cloudflare/public_ui_copy.test.mjs`
   - `cloudflare/worker.test.mjs`
   - `.gitignore`
2. Inspect the current working tree before editing anything. Do not assume dirty files are disposable.

Primary implementation skill:
- Use skill `$ck:cook` for all implementation and execution tasks.
- Do NOT bypass `$ck:cook` for core implementation work.

UI/UX requirement:
- Any task related to UI, UX, layout, forms, interactions, accessibility, responsive behavior, loading states, empty states, typography, visual hierarchy, or dashboard presentation MUST use skill `$ck:ui-ux-pro-max`.

Role and product intent:
- Improve the deployed public Worker homepage so it feels like a simple end-user app, not a project showcase.
- Keep the current MVP focused on one workout-plan generation flow plus feedback capture.
- Prepare the branch for clean commits without dragging local cache artifacts or ambiguous staging decisions along.

Architecture constraints:
- The production public surface is the Cloudflare Worker path, not the legacy FastAPI reference UI.
- Keep the implementation centered on `public/index.html`, `cloudflare/worker.mjs`, and Worker-facing tests.
- Do not change the request/response contract for `POST /api/workout-plans` or `POST /api/feedback` unless required to fix a validation bug already present in the Worker.
- Do not change D1 schema, persistence strategy, or tracing architecture.
- Treat translation as UI-copy switching only. Do not translate enum values, payload keys, stored values, or API schema fields.

Implementation scope:
Build ONLY:
- working-tree cleanup needed to make this branch commitable
- `.gitignore` cleanup for local deploy/cache artifacts
- a simplified public homepage that removes project, learning, and interview/process messaging
- a desktop-friendly centered hero/form layout
- a visible Vietnamese/English language toggle
- stronger Worker-focused tests and validation coverage for the changed UI and request boundaries
- a clear recommended commit grouping for the resulting changes

Explicit non-goals:
- no auth
- no admin/review dashboard expansion
- no analytics productization
- no redesign of the workout plan schema
- no migration away from Cloudflare Worker + D1
- no hidden i18n framework or unnecessary build tooling
- no speculative component system
- no changes to legacy FastAPI reference UI unless required by a shared contract that the Worker also depends on

Execution requirements:
- First classify the working tree into:
  - local-only artifacts
  - public Worker runtime/UI changes
  - backend reference changes
  - docs/plan changes
- Remove or ignore only generated/local artifacts such as `.wrangler/`.
- Preserve intentional source changes already present in the branch.
- Simplify the homepage aggressively: short intro, user form, result area, feedback area. Remove roadmap, learning, portfolio, and “how the project was built” language from the public UI.
- Fix the desktop layout issue where the title is pushed or compressed to one side.
- Keep mobile behavior working.

UI/UX guidance:
- Favor a balanced desktop composition with a centered content column or clearly weighted two-column layout.
- Keep typography intentional and readable. Do not let the headline collapse into an overly narrow measure.
- Use one obvious language toggle with explicit current-state indication.
- Keep the form and result panels visually simpler than the current version.
- Avoid generic admin/dashboard aesthetics and avoid “AI product marketing” fluff.

Validation requirements:
Validation loop:
After every meaningful implementation step:
- run lint if available
- run typecheck if available
- run tests if available
- run build when appropriate
- fix failures before continuing

Performance requirements:
- Keep the public page static and lightweight.
- Do not introduce heavy client-side dependencies for translation or layout.
- Keep the Worker request path deterministic and cheap.

Code quality rules:
- Prefer explicit copy maps and simple client-side state for language switching.
- Keep translation logic easy to read from one file.
- Avoid premature abstraction.
- Keep tests focused on behavior and contract, not incidental markup noise.

Decision policy:
- Low-risk implementation details may be decided autonomously.
- If a decision changes architecture, persistence strategy, AI behavior, product direction, or MVP scope, stop and request confirmation.

Testing requirements:
- Run `node --test cloudflare/public_ui_copy.test.mjs cloudflare/worker.test.mjs` or the smallest equivalent focused command after UI/Worker changes.
- Add or update assertions for:
  - simplified public copy
  - absence of project/learning/interview messaging on the public page
  - Vietnamese/English language toggle presence
  - tightened Worker validation behavior if changed
- If any backend reference tests are touched, run only the relevant targeted backend tests rather than the entire suite unless needed.

Completion criteria:
- `.wrangler/` and other local artifacts are not part of the commitable branch state
- `.gitignore` is clean and non-duplicated
- the public homepage is simplified, desktop-friendly, and bilingual via a deterministic toggle
- the public UI no longer exposes the user’s learning/project-process narrative
- Worker-focused tests pass for the updated UI and validation behavior
- the final response includes exact commit grouping recommendations and any remaining manual follow-up
