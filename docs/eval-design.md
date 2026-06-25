# Eval Design v1

## Purpose

FitCoach AI now includes a first local eval stack for workout-plan generation.
This document explains how the dataset, rubric, and runner fit together today.

## Current artifacts

- Dataset: `backend/app/evals/workout_plan_eval_dataset_v1.json`
- Rubric: `backend/app/evals/workout_plan_eval_rubric_v1.json`
- Runner: `backend/app/evals/runner.py`
- Local asset tests: `backend/tests/test_eval_assets.py`
- Runner tests: `backend/tests/evals/test_runner.py`

## Dataset design

The dataset currently contains 30 cases. Each case includes:

- `id`
- `title`
- `expected_outcome_type`
- `risk_tags`
- `input`
- `expected_behavior`

The `input` object mirrors the current `UserProfile` contract so the eval stack
can exercise the same structured request surface as the main API.

## Risk-tag vocabulary

The rubric currently allows these tags:

- `baseline`
- `schedule_constraint`
- `equipment_constraint`
- `location_constraint`
- `mild_limitation`
- `preference_constraint`
- `beginner_overload`
- `recovery_emphasis`
- `medical_referral`
- `safety_fallback_expected`
- `retrieval_grounding`

These tags help later filtering, slicing, and reporting without changing the
dataset schema.

## Rubric design

The rubric stores:

- scoring dimensions and weights
- the allowed risk-tag vocabulary
- expected outcome types
- hard-fail rules

The current scoring dimensions are:

- schema validity
- goal alignment
- constraint adherence
- safety boundary
- beginner appropriateness
- clarity and progression

The runner reports the issue-facing summary categories as:

- schema validity
- safety behavior
- personalization
- clarity

`personalization` is currently a deterministic combination of goal alignment,
constraint adherence, and beginner-appropriateness checks.

## Runner design

The runner is intentionally local-first.

Core behaviors:

1. Load the dataset and rubric JSON files.
2. Generate a `WorkoutPlan` for each case.
3. Score the result with deterministic heuristics.
4. Render a Markdown or CSV report.

The runner exposes an injectable execution path so unit tests can pass fake
plans directly without making OpenAI requests. When run from the CLI, it uses
the real `OpenAIWorkoutPlanClient`.

Example command:

```bash
cd backend
uv run python -m app.evals.runner --output reports/eval-report.md --report-format markdown
```

## Pass and fail examples

### Pass examples

- A baseline beginner fat-loss case returns a valid `WorkoutPlan` with matching
  goal, training frequency, conservative exercise choices, and clear
  progression notes.
- A medical-risk case such as chest pain returns the structured safety fallback
  instead of a normal training plan.
- A beginner-overload case avoids `high` intensity or advanced exercises like
  barbell snatches.

### Fail examples

- The response is not schema-valid and cannot be parsed as `WorkoutPlan`.
- A medical-risk case receives normal coaching instead of fallback behavior.
- A home bodyweight-only case contains machine or barbell exercise
  recommendations.
- A beginner case exceeds the requested session duration or uses clearly unsafe
  overload patterns.

## Known limitations

- The current runner uses deterministic heuristics, not an LLM judge or human
  review loop.
- Personalization scoring is approximate; it mostly checks top-level field
  alignment, duration limits, and obvious equipment mismatches.
- Safety scoring relies on the current runtime fallback contract and a small set
  of overload patterns, so nuanced unsafe plans may still score too generously.
- Retrieval quality is not directly graded yet; the `retrieval_grounding` tag is
  metadata for future eval expansion rather than a full retrieval evaluator.
- The CLI runner currently assumes live OpenAI credentials if you execute the
  generation path outside tests.
