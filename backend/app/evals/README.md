## Eval Assets

This directory stores the first checked-in evaluation artifacts for FitCoach AI.

- `workout_plan_eval_dataset_v1.json` defines 30 representative workout-plan
  cases with expected behavior and risk tags.
- `workout_plan_eval_rubric_v1.json` defines the scoring dimensions and
  hard-fail rules a future eval runner should apply.

The files are intentionally machine-readable so later issues can build a local
or provider-backed eval runner without reformatting the source data first.

Run the live eval runner with:

```bash
cd backend
uv run python -m app.evals.runner --output reports/eval-report.md --report-format markdown
```
