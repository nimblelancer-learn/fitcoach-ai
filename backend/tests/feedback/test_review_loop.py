import json
from pathlib import Path

from app.feedback.review_loop import (
    _load_export_rows,
    _normalize_row,
    build_review_summary,
    write_review_artifacts,
)


def test_load_export_rows_accepts_wrangler_results_shape(tmp_path: Path) -> None:
    export_path = tmp_path / "feedback-export.json"
    export_path.write_text(
        json.dumps(
            [
                {
                    "results": [
                        {
                            "request_id": "req-1",
                            "feedback_created_at": "2026-07-14T18:00:00+00:00",
                            "feedback_channel": "public_mvp",
                            "usefulness_rating": 1,
                            "difficulty_feedback": "too_hard",
                            "felt_safe": 0,
                            "would_follow_plan": 0,
                            "feedback_text": "Too hard for a beginner.",
                            "generated_at": "2026-07-14T17:58:00+00:00",
                            "model_name": "gpt-4.1-mini",
                            "latency_ms": 650,
                            "used_fallback": 0,
                            "retrieved_chunk_count": 0,
                            "retrieved_chunk_ids_json": "[]",
                            "safety_trigger_codes_json": "[]",
                            "trace_id": "req-1",
                            "trace_enabled": 1,
                        }
                    ]
                }
            ]
        ),
        encoding="utf-8",
    )

    rows = _load_export_rows(export_path)

    assert len(rows) == 1
    assert rows[0]["request_id"] == "req-1"


def test_review_summary_marks_only_repeated_negative_patterns() -> None:
    records = [
        _normalize_row(
            {
                "request_id": "req-1",
                "feedback_created_at": "2026-07-14T18:00:00+00:00",
                "feedback_channel": "public_mvp",
                "usefulness_rating": 1,
                "difficulty_feedback": "too_hard",
                "felt_safe": 0,
                "would_follow_plan": 0,
                "feedback_text": "Too hard for a beginner.",
                "generated_at": "2026-07-14T17:58:00+00:00",
                "model_name": "gpt-4.1-mini",
                "latency_ms": 650,
                "used_fallback": 0,
                "retrieved_chunk_count": 0,
                "retrieved_chunk_ids_json": "[]",
                "safety_trigger_codes_json": "[]",
                "trace_id": "req-1",
                "trace_enabled": 1,
            }
        ),
        _normalize_row(
            {
                "request_id": "req-2",
                "feedback_created_at": "2026-07-14T18:05:00+00:00",
                "feedback_channel": "public_mvp",
                "usefulness_rating": 2,
                "difficulty_feedback": "too_hard",
                "felt_safe": 1,
                "would_follow_plan": 0,
                "feedback_text": "Still too hard.",
                "generated_at": "2026-07-14T18:02:00+00:00",
                "model_name": "gpt-4.1-mini",
                "latency_ms": 610,
                "used_fallback": 0,
                "retrieved_chunk_count": 1,
                "retrieved_chunk_ids_json": '["doc-1::chunk-001"]',
                "safety_trigger_codes_json": "[]",
                "trace_id": "req-2",
                "trace_enabled": 1,
            }
        ),
        _normalize_row(
            {
                "request_id": "req-3",
                "feedback_created_at": "2026-07-14T18:10:00+00:00",
                "feedback_channel": "public_mvp",
                "usefulness_rating": 4,
                "difficulty_feedback": "about_right",
                "felt_safe": 1,
                "would_follow_plan": 1,
                "feedback_text": "",
                "generated_at": "2026-07-14T18:07:00+00:00",
                "model_name": "gpt-4.1-mini",
                "latency_ms": 590,
                "used_fallback": 0,
                "retrieved_chunk_count": 2,
                "retrieved_chunk_ids_json": '["doc-1::chunk-001", "doc-1::chunk-002"]',
                "safety_trigger_codes_json": "[]",
                "trace_id": "req-3",
                "trace_enabled": 1,
            }
        ),
    ]

    summary = build_review_summary(records, min_pattern_count=2)

    repeated_keys = [item.key for item in summary.repeated_patterns]
    one_off_keys = [item.key for item in summary.one_off_patterns]

    assert repeated_keys == [
        "difficulty_too_hard",
        "low_usefulness",
        "wont_follow_plan",
    ]
    assert "weak_retrieval" in one_off_keys
    assert summary.request_ids_without_negative_signals == ["req-3"]


def test_write_review_artifacts_outputs_expected_files(tmp_path: Path) -> None:
    records = [
        _normalize_row(
            {
                "request_id": "req-1",
                "feedback_created_at": "2026-07-14T18:00:00+00:00",
                "feedback_channel": "public_mvp",
                "usefulness_rating": 1,
                "difficulty_feedback": "too_hard",
                "felt_safe": 0,
                "would_follow_plan": 0,
                "feedback_text": "Too hard for a beginner.",
                "generated_at": "2026-07-14T17:58:00+00:00",
                "model_name": "gpt-4.1-mini",
                "latency_ms": 650,
                "used_fallback": 0,
                "retrieved_chunk_count": 0,
                "retrieved_chunk_ids_json": "[]",
                "safety_trigger_codes_json": "[]",
                "trace_id": "req-1",
                "trace_enabled": 1,
            }
        )
    ]
    summary = build_review_summary(records, min_pattern_count=2)
    output_dir = tmp_path / "review-artifacts"

    write_review_artifacts(
        records=records,
        summary=summary,
        output_dir=output_dir,
        campaign_label="test-campaign",
        min_pattern_count=2,
    )

    assert (output_dir / "feedback-summary.md").is_file()
    assert (output_dir / "feedback-summary.json").is_file()
    assert (output_dir / "eval-candidates.json").is_file()
    assert (output_dir / "changelog-seed.md").is_file()

    markdown = (output_dir / "feedback-summary.md").read_text(encoding="utf-8")
    assert "No repeated negative patterns met the threshold yet." in markdown
