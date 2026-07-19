# Public Feedback Loop Runbook

This runbook is the repo-local part of Phase 6. It does not claim that real-user
submissions already exist. Its purpose is to make the operational loop explicit
enough that another engineer can run it without guessing.

## Scope

Use this only for the shipped Cloudflare MVP:

- deployed Worker runtime
- public Vietnamese UI
- D1-backed feedback storage
- Langfuse traces when configured

Do not widen product scope during this loop. The goal is to collect evidence,
find repeated weaknesses, turn those weaknesses into eval coverage, and record
the fix.

## Closed loop

1. Deploy the current MVP and verify `POST /api/workout-plans` plus `POST /api/feedback`.
2. Collect real feedback from Vietnamese testers.
3. Export feedback plus runtime metadata from D1.
4. Summarize repeated negative patterns.
5. Convert confirmed repeated weaknesses into eval cases and regression tests.
6. Fix the underlying issue.
7. Re-run validation.
8. Publish the technical changelog entry and interview evidence.

The phase is not complete at step 3. Raw submissions alone are not the evidence.

## Tester instructions

Keep the ask short and concrete:

- Generate one workout plan using your real profile.
- If the plan feels wrong, say exactly what felt wrong.
- Use the built-in feedback form right after reading the plan.
- For the two free-text profile fields, keep English short and simple.

Do not ask testers to imagine scenarios they did not experience.

## Export the feedback rows

Run the checked-in query against the deployed D1 database:

```bash
npx wrangler d1 execute FITCOACH_DB \
  --remote \
  --json \
  --file cloudflare/d1/queries/export_feedback_review.sql \
  > artifacts/feedback-loop/feedback-export-YYYYMMDD.json
```

Notes:

- `--remote` is required for the deployed database, not the local preview DB.
- The export should stay raw. Do not hand-edit rows before review.
- Keep the timestamp in the filename so the evidence trail stays clear.

## Build the review artifacts

From the backend directory:

```bash
cd backend
uv run python -m app.feedback.review_loop \
  --input ../artifacts/feedback-loop/feedback-export-YYYYMMDD.json \
  --output-dir ../artifacts/feedback-loop/review-YYYYMMDD \
  --campaign-label july-public-feedback \
  --min-pattern-count 2
```

The CLI writes:

- `feedback-summary.md`
- `feedback-summary.json`
- `eval-candidates.json`
- `changelog-seed.md`

Interpretation rule:

- only repeated negative patterns belong in eval-candidate review
- one-off anecdotes stay documented but should not drive dataset churn

## Review standard for repeated failures

Treat a pattern as repeated only when both are true:

- it appears at least twice in the same review batch
- the underlying weakness is materially the same

Examples:

- repeated "too hard" feedback from beginner users with short sessions can justify a beginner-overload eval case
- one "too hard" complaint and one "too easy" complaint are not the same pattern
- one unsafe comment caused by a medical-risk fallback and one unsafe comment caused by poor exercise selection should not be merged

## Convert repeated failures into evals

For each repeated pattern:

1. Read the raw comments and linked request IDs.
2. Confirm the weakness is product-level, not user misunderstanding.
3. Add the smallest representative eval case to `backend/app/evals/workout_plan_eval_dataset_v1.json`.
4. Update `backend/tests/evals/test_runner.py` or a narrower regression test if needed.
5. Record the fix in the changelog seed and evidence docs.

Do not add eval cases that are speculative or copied from hypothetical examples.

## Changelog standard

Each evidence entry should answer:

- What repeated failure happened?
- How many real submissions showed it?
- What code, prompt, or retrieval change fixed it?
- Which eval or regression now protects it?
- What validation commands passed after the fix?

Keep the tone technical. Avoid launch or marketing language.

## Minimum completion bar

Repo-local Phase 6 support is ready when:

- the D1 export query is checked in
- the review CLI can summarize raw exported rows
- the operator workflow is documented end to end
- the changelog/evidence templates exist

Full Phase 6 is ready only after real submissions exist and at least one repeated
problem has been converted into eval coverage.
