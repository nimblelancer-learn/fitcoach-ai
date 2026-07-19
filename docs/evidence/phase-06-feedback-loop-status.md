# Phase 6 Feedback Loop Status

## Current status

Phase 6 is prepared at the repository level but not fully closed operationally.

What is true in this repo snapshot:

- the Cloudflare MVP deployment path is documented
- feedback rows and runtime metadata already persist in D1
- a local review surface exists for recent feedback
- a checked-in D1 export query now exists for public MVP feedback review
- a deterministic CLI now converts exported feedback rows into:
  - repeated-pattern summaries
  - eval candidate lists
  - changelog seeds

What is not yet true in this repo snapshot:

- there are no checked-in real-user public submissions
- no honest repeated failure has been confirmed from production usage
- no new eval case has been added from real public feedback yet

## Why no eval dataset change was made here

The current environment does not contain verified repeated production failures.
Adding dataset cases anyway would weaken the evidence path and turn Phase 6 into
fiction. The correct repo-side move is to prepare the loop, not invent the
inputs.

## Repo artifacts added for Phase 6

- `cloudflare/d1/queries/export_feedback_review.sql`
- `backend/app/feedback/review_loop.py`
- `backend/tests/feedback/test_review_loop.py`
- `docs/public-feedback-loop-runbook.md`

These artifacts are the minimum honest scaffolding needed to finish the phase
once real public submissions exist.

## External dependencies still required

- a deployed Cloudflare Worker with D1 bound to the real public MVP
- at least 10 real-user submissions from Vietnamese testers
- at least one repeated negative pattern that survives review as a real product weakness

## Next operational step

Run the public campaign, export the D1 rows with the checked-in SQL query, and
generate the first review bundle. Only after that should the repo gain new eval
cases and a feedback-driven changelog entry.
