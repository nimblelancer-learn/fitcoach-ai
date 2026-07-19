from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class FeedbackReviewRecord:
    request_id: str
    feedback_created_at: str
    feedback_channel: str
    usefulness_rating: int
    difficulty_feedback: str
    felt_safe: bool
    would_follow_plan: bool
    feedback_text: str
    generated_at: str | None
    model_name: str | None
    latency_ms: int | None
    used_fallback: bool
    retrieved_chunk_count: int
    retrieved_chunk_ids: list[str]
    safety_trigger_codes: list[str]
    trace_id: str | None
    trace_enabled: bool


@dataclass(frozen=True)
class PatternSummary:
    key: str
    label: str
    count: int
    request_ids: list[str]
    evidence_excerpt: str | None
    recommended_eval_action: str
    recommended_test_surface: str


@dataclass(frozen=True)
class ReviewSummary:
    total_submissions: int
    negative_signal_counts: dict[str, int]
    repeated_patterns: list[PatternSummary]
    one_off_patterns: list[PatternSummary]
    request_ids_without_negative_signals: list[str]


PATTERN_LABELS = {
    "low_usefulness": "Low usefulness rating (<=2/5)",
    "difficulty_too_hard": "Plan felt too hard",
    "difficulty_too_easy": "Plan felt too easy",
    "unsafe_plan": "User reported the plan did not feel safe",
    "wont_follow_plan": "User would not follow the plan",
    "fallback_response": "Fallback path was used",
    "weak_retrieval": "No retrieval chunks were attached",
    "safety_triggered": "Safety trigger codes were recorded",
}

EVAL_ACTIONS = {
    "low_usefulness": (
        "Review free-text comments and abstract the recurring "
        "personalization gap into a new eval case."
    ),
    "difficulty_too_hard": (
        "Add a beginner-overload or duration/volume eval case that reproduces "
        "the repeated over-prescription pattern."
    ),
    "difficulty_too_easy": (
        "Add a progression or goal-alignment eval case that checks for under-prescription."
    ),
    "unsafe_plan": (
        "Add or strengthen a safety-boundary eval case and a regression test "
        "around the repeated unsafe recommendation."
    ),
    "wont_follow_plan": (
        "Translate the repeated adherence objection into a "
        "constraint-adherence eval case before widening product scope."
    ),
    "fallback_response": (
        "Check whether the fallback was appropriate; add eval coverage only if "
        "the fallback was repeatedly triggered for otherwise normal profiles."
    ),
    "weak_retrieval": (
        "Add retrieval-grounding eval coverage for the repeated missing-context pattern."
    ),
    "safety_triggered": (
        "Confirm the trigger was correct and add a regression case if the same "
        "trigger path keeps producing poor outcomes."
    ),
}

TEST_SURFACES = {
    "low_usefulness": "backend/app/evals/workout_plan_eval_dataset_v1.json",
    "difficulty_too_hard": (
        "backend/app/evals/workout_plan_eval_dataset_v1.json + backend/tests/evals/test_runner.py"
    ),
    "difficulty_too_easy": (
        "backend/app/evals/workout_plan_eval_dataset_v1.json + backend/tests/evals/test_runner.py"
    ),
    "unsafe_plan": (
        "backend/app/evals/workout_plan_eval_dataset_v1.json + "
        "backend/tests/services/test_workout_plan_generator.py"
    ),
    "wont_follow_plan": (
        "backend/app/evals/workout_plan_eval_dataset_v1.json + backend/tests/evals/test_runner.py"
    ),
    "fallback_response": (
        "backend/app/evals/workout_plan_eval_dataset_v1.json + cloudflare/worker.test.mjs"
    ),
    "weak_retrieval": (
        "backend/app/evals/workout_plan_eval_dataset_v1.json + "
        "backend/tests/rag/test_retrieval_quality.py"
    ),
    "safety_triggered": (
        "backend/app/evals/workout_plan_eval_dataset_v1.json + "
        "backend/tests/services/test_workout_plan_generator.py"
    ),
}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Summarize exported public MVP feedback rows and surface repeated negative patterns "
            "that should become eval or regression updates."
        )
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the exported D1 feedback JSON file.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory where summary Markdown/JSON artifacts will be written.",
    )
    parser.add_argument(
        "--min-pattern-count",
        type=int,
        default=2,
        help="Minimum count required to treat a negative pattern as repeated.",
    )
    parser.add_argument(
        "--campaign-label",
        default="public-feedback-loop",
        help="Short label written into the generated report headings.",
    )
    return parser.parse_args()


def _load_export_rows(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))

    if isinstance(payload, list):
        if payload and isinstance(payload[0], dict) and "results" in payload[0]:
            return [row for item in payload for row in item.get("results", [])]
        return payload

    if isinstance(payload, dict):
        if "results" in payload and isinstance(payload["results"], list):
            return payload["results"]
        if "result" in payload and isinstance(payload["result"], list):
            return payload["result"]

    raise ValueError(
        "Unsupported feedback export format. Expected a list of rows, a Wrangler D1 "
        "JSON payload with `results`, or a dict with `result`."
    )


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes"}
    return bool(value)


def _as_int(value: Any, *, default: int = 0) -> int:
    if value is None or value == "":
        return default
    return int(value)


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _parse_json_list(value: Any) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str):
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
    raise ValueError(f"Expected JSON list value, got: {value!r}")


def _normalize_row(row: dict[str, Any]) -> FeedbackReviewRecord:
    return FeedbackReviewRecord(
        request_id=_as_text(row["request_id"]),
        feedback_created_at=_as_text(
            row.get("feedback_created_at") or row.get("created_at") or row.get("submitted_at")
        ),
        feedback_channel=_as_text(row.get("feedback_channel") or "public_mvp"),
        usefulness_rating=_as_int(row.get("usefulness_rating"), default=0),
        difficulty_feedback=_as_text(row.get("difficulty_feedback")),
        felt_safe=_as_bool(row.get("felt_safe")),
        would_follow_plan=_as_bool(row.get("would_follow_plan")),
        feedback_text=_as_text(row.get("feedback_text")).strip(),
        generated_at=row.get("generated_at"),
        model_name=row.get("model_name"),
        latency_ms=_as_int(row["latency_ms"]) if row.get("latency_ms") not in {None, ""} else None,
        used_fallback=_as_bool(row.get("used_fallback")),
        retrieved_chunk_count=_as_int(row.get("retrieved_chunk_count"), default=0),
        retrieved_chunk_ids=_parse_json_list(
            row.get("retrieved_chunk_ids") or row.get("retrieved_chunk_ids_json") or []
        ),
        safety_trigger_codes=_parse_json_list(
            row.get("safety_trigger_codes") or row.get("safety_trigger_codes_json") or []
        ),
        trace_id=_as_text(row.get("trace_id")) or None,
        trace_enabled=_as_bool(row.get("trace_enabled")),
    )


def _record_pattern_keys(record: FeedbackReviewRecord) -> list[str]:
    pattern_keys: list[str] = []
    if record.usefulness_rating <= 2:
        pattern_keys.append("low_usefulness")
    if record.difficulty_feedback == "too_hard":
        pattern_keys.append("difficulty_too_hard")
    if record.difficulty_feedback == "too_easy":
        pattern_keys.append("difficulty_too_easy")
    if not record.felt_safe:
        pattern_keys.append("unsafe_plan")
    if not record.would_follow_plan:
        pattern_keys.append("wont_follow_plan")
    if record.used_fallback:
        pattern_keys.append("fallback_response")
    if record.retrieved_chunk_count == 0:
        pattern_keys.append("weak_retrieval")
    if record.safety_trigger_codes:
        pattern_keys.append("safety_triggered")
    return pattern_keys


def build_review_summary(
    records: list[FeedbackReviewRecord],
    *,
    min_pattern_count: int,
) -> ReviewSummary:
    counter: Counter[str] = Counter()
    request_ids_by_pattern: dict[str, list[str]] = defaultdict(list)
    excerpt_by_pattern: dict[str, str] = {}
    requests_without_negative_signals: list[str] = []

    for record in records:
        pattern_keys = _record_pattern_keys(record)
        if not pattern_keys:
            requests_without_negative_signals.append(record.request_id)
            continue

        for key in pattern_keys:
            counter[key] += 1
            request_ids_by_pattern[key].append(record.request_id)
            if key not in excerpt_by_pattern and record.feedback_text:
                excerpt_by_pattern[key] = record.feedback_text

    def to_pattern_summary(key: str) -> PatternSummary:
        return PatternSummary(
            key=key,
            label=PATTERN_LABELS[key],
            count=counter[key],
            request_ids=request_ids_by_pattern[key],
            evidence_excerpt=excerpt_by_pattern.get(key),
            recommended_eval_action=EVAL_ACTIONS[key],
            recommended_test_surface=TEST_SURFACES[key],
        )

    repeated = [
        to_pattern_summary(key) for key, count in counter.items() if count >= min_pattern_count
    ]
    one_off = [
        to_pattern_summary(key) for key, count in counter.items() if count < min_pattern_count
    ]

    repeated.sort(key=lambda item: (-item.count, item.key))
    one_off.sort(key=lambda item: (-item.count, item.key))

    return ReviewSummary(
        total_submissions=len(records),
        negative_signal_counts=dict(sorted(counter.items())),
        repeated_patterns=repeated,
        one_off_patterns=one_off,
        request_ids_without_negative_signals=requests_without_negative_signals,
    )


def _render_markdown(
    *,
    campaign_label: str,
    summary: ReviewSummary,
    min_pattern_count: int,
) -> str:
    lines = [
        f"# Feedback Review Summary: {campaign_label}",
        "",
        "## Scope",
        "",
        f"- Total submissions reviewed: {summary.total_submissions}",
        f"- Repeated-pattern threshold: {min_pattern_count}",
        (
            "- Submissions without negative signals: "
            f"{len(summary.request_ids_without_negative_signals)}"
        ),
        "",
        "## Repeated negative patterns",
        "",
    ]

    if summary.repeated_patterns:
        for pattern in summary.repeated_patterns:
            lines.extend(
                [
                    f"### {pattern.label}",
                    "",
                    f"- Count: {pattern.count}",
                    f"- Request IDs: {', '.join(pattern.request_ids)}",
                    f"- Recommended eval action: {pattern.recommended_eval_action}",
                    f"- Recommended test surface: `{pattern.recommended_test_surface}`",
                ]
            )
            if pattern.evidence_excerpt:
                lines.append(f"- Example comment: {pattern.evidence_excerpt}")
            lines.append("")
    else:
        lines.extend(
            [
                "No repeated negative patterns met the threshold yet.",
                "",
                "Do not add eval cases or changelog claims until real repeated evidence exists.",
                "",
            ]
        )

    lines.extend(["## One-off negative patterns", ""])
    if summary.one_off_patterns:
        for pattern in summary.one_off_patterns:
            lines.append(f"- {pattern.label}: {pattern.count} submission(s)")
        lines.append("")
    else:
        lines.extend(["None.", ""])

    lines.extend(
        [
            "## Next operator actions",
            "",
            (
                "1. Confirm that each repeated pattern reflects the same "
                "underlying product weakness, not different anecdotes."
            ),
            (
                "2. Convert only confirmed repeated patterns into eval dataset "
                "additions and regression tests."
            ),
            (
                "3. Update the project changelog or interview evidence with "
                "the specific failure, fix, and validation result."
            ),
            "",
        ]
    )

    return "\n".join(lines)


def _build_eval_candidates(summary: ReviewSummary) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for pattern in summary.repeated_patterns:
        candidates.append(
            {
                "pattern_key": pattern.key,
                "pattern_label": pattern.label,
                "evidence_request_ids": pattern.request_ids,
                "evidence_count": pattern.count,
                "recommended_eval_action": pattern.recommended_eval_action,
                "recommended_test_surface": pattern.recommended_test_surface,
                "status": "pending-human-abstraction",
                "guardrail": (
                    "Do not add this to the dataset until the repeated product "
                    "weakness is confirmed from real submissions."
                ),
            }
        )
    return candidates


def _build_changelog_seed(
    *,
    campaign_label: str,
    summary: ReviewSummary,
) -> str:
    lines = [
        f"# Change Log Seed: {campaign_label}",
        "",
        "> Fill this only after a real repeated failure has been fixed and revalidated.",
        "",
        "## Repeated problem",
        "",
        "- Pattern:",
        "- Evidence count:",
        "- Request IDs:",
        "- Why this was a repeated weakness instead of one-off noise:",
        "",
        "## Repo changes",
        "",
        "- Code or prompt change:",
        "- Eval artifact changed:",
        "- Regression test changed:",
        "",
        "## Validation",
        "",
        "- Local commands run:",
        "- Result after fix:",
        "- Remaining limitation:",
        "",
        "## Notes from this review run",
        "",
    ]

    if summary.repeated_patterns:
        for pattern in summary.repeated_patterns:
            lines.append(f"- Candidate repeated pattern: {pattern.label} ({pattern.count})")
    else:
        lines.append("- No repeated pattern met the threshold yet.")

    lines.append("")
    return "\n".join(lines)


def write_review_artifacts(
    *,
    records: list[FeedbackReviewRecord],
    summary: ReviewSummary,
    output_dir: Path,
    campaign_label: str,
    min_pattern_count: int,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    markdown_path = output_dir / "feedback-summary.md"
    json_path = output_dir / "feedback-summary.json"
    eval_candidates_path = output_dir / "eval-candidates.json"
    changelog_seed_path = output_dir / "changelog-seed.md"

    markdown_path.write_text(
        _render_markdown(
            campaign_label=campaign_label,
            summary=summary,
            min_pattern_count=min_pattern_count,
        ),
        encoding="utf-8",
    )
    json_path.write_text(
        json.dumps(
            {
                "campaign_label": campaign_label,
                "min_pattern_count": min_pattern_count,
                "records": [asdict(record) for record in records],
                "summary": asdict(summary),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    eval_candidates_path.write_text(
        json.dumps(_build_eval_candidates(summary), indent=2) + "\n",
        encoding="utf-8",
    )
    changelog_seed_path.write_text(
        _build_changelog_seed(campaign_label=campaign_label, summary=summary),
        encoding="utf-8",
    )


def main() -> None:
    args = _parse_args()
    input_path = Path(args.input).resolve()
    output_dir = Path(args.output_dir).resolve()

    rows = _load_export_rows(input_path)
    records = [_normalize_row(row) for row in rows]
    summary = build_review_summary(records, min_pattern_count=args.min_pattern_count)
    write_review_artifacts(
        records=records,
        summary=summary,
        output_dir=output_dir,
        campaign_label=args.campaign_label,
        min_pattern_count=args.min_pattern_count,
    )


if __name__ == "__main__":
    main()
