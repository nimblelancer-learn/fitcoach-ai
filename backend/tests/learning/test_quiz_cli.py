from __future__ import annotations

from io import StringIO
from pathlib import Path

import pytest

from app.learning.quiz.cli import run_quiz
from app.learning.quiz.loader import ExercisePackError, load_exercise_pack


def test_load_exercise_pack_reads_real_topic() -> None:
    pack = load_exercise_pack("pyproject-and-uv-lock")

    assert pack.topic.slug == "pyproject-and-uv-lock"
    assert pack.topic.source_files == ["backend/pyproject.toml", "backend/uv.lock"]
    assert [question.mode for question in pack.questions] == [
        "multiple_choice",
        "short_answer",
        "multiple_choice",
        "self_check",
        "multiple_choice",
        "short_answer",
    ]


def test_load_exercise_pack_reads_explain_back_topic() -> None:
    pack = load_exercise_pack("app-main-and-learning-portal")

    assert pack.topic.slug == "app-main-and-learning-portal"
    assert pack.topic.source_files == [
        "backend/app/main.py",
        "backend/app/api/routes_learning.py",
        "backend/app/learning/loader.py",
    ]
    assert [question.mode for question in pack.questions] == [
        "multiple_choice",
        "explain_back",
        "explain_back",
        "self_check",
    ]


def test_load_exercise_pack_reads_prediction_topic() -> None:
    pack = load_exercise_pack("runtime-and-workflow-predictions")

    assert pack.topic.slug == "runtime-and-workflow-predictions"
    assert [question.mode for question in pack.questions] == [
        "prediction",
        "prediction",
        "prediction",
        "prediction",
    ]


def test_missing_topic_fails_with_clear_message(tmp_path: Path) -> None:
    with pytest.raises(ExercisePackError) as exc_info:
        load_exercise_pack("missing-topic", tmp_path)

    assert "Unknown quiz topic 'missing-topic'" in str(exc_info.value)


def test_invalid_pack_schema_fails_with_clear_message(tmp_path: Path) -> None:
    pack_dir = tmp_path
    (pack_dir / "broken.toml").write_text(
        """
[topic]
slug = "broken"
title = "Broken"
summary = "Broken pack"

[[questions]]
id = "bad-mc"
mode = "multiple_choice"
level = "recognize"
prompt = "Broken question"
choices = ["Only one"]
answer_index = 0
explanation = "Broken explanation"
""".strip()
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ExercisePackError) as exc_info:
        load_exercise_pack("broken", pack_dir)

    assert "multiple_choice questions require at least two choices" in str(exc_info.value)


def test_duplicate_question_id_fails_with_clear_message(tmp_path: Path) -> None:
    pack_dir = tmp_path
    (pack_dir / "duplicate.toml").write_text(
        """
[topic]
slug = "duplicate"
title = "Duplicate"
summary = "Duplicate ids"

[[questions]]
id = "repeat"
mode = "short_answer"
level = "recognize"
prompt = "Question one"
expected_answer = "Answer one"

[[questions]]
id = "repeat"
mode = "self_check"
level = "explain"
prompt = "Question two"
expected_answer = "Answer two"
""".strip()
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ExercisePackError) as exc_info:
        load_exercise_pack("duplicate", pack_dir)

    assert "duplicate question id 'repeat'" in str(exc_info.value)


def test_explain_back_schema_rejects_too_many_expected_points(tmp_path: Path) -> None:
    pack_dir = tmp_path
    (pack_dir / "too-many-points.toml").write_text(
        """
[topic]
slug = "too-many-points"
title = "Too many points"
summary = "Broken explain-back pack"

[[questions]]
id = "explain"
mode = "explain_back"
level = "explain"
prompt = "Explain it"
expected_points = ["1", "2", "3", "4", "5", "6"]
""".strip()
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ExercisePackError) as exc_info:
        load_exercise_pack("too-many-points", pack_dir)

    assert "support at most five expected points" in str(exc_info.value)


def test_prediction_schema_requires_target_files(tmp_path: Path) -> None:
    pack_dir = tmp_path
    (pack_dir / "prediction-without-targets.toml").write_text(
        """
[topic]
slug = "prediction-without-targets"
title = "Missing target files"
summary = "Broken prediction pack"

[[questions]]
id = "predict"
mode = "prediction"
level = "predict"
prompt = "Predict it"
scenario = "Change a file"
expected_outcome = "Something happens"
why = "Because of the code"
""".strip()
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ExercisePackError) as exc_info:
        load_exercise_pack("prediction-without-targets", pack_dir)

    assert "prediction questions require at least one target file" in str(exc_info.value)


def test_run_quiz_handles_each_supported_question_mode() -> None:
    pack = load_exercise_pack("pyproject-and-uv-lock")
    answers = iter(
        [
            "1",
            "Resolved graph for reproducible installs",
            "B",
            "",
            "2",
            "Update uv.lock and rerun tests",
        ]
    )
    output = StringIO()

    summary = run_quiz(pack, input_fn=lambda prompt: next(answers), output=output)
    rendered = output.getvalue()

    assert "Topic: Reading backend/pyproject.toml and uv.lock" in rendered
    assert "A) backend/pyproject.toml" in rendered
    assert "Correct." in rendered
    assert "Captured." in rendered
    assert "Expected answer: It pins the resolved package graph" in rendered
    assert "Reveal: It shows the Python-version ranges uv resolved for" in rendered
    assert "Not quite. Expected: C) >=3.12" in rendered
    assert "Session summary" in rendered
    assert summary.multiple_choice_total == 3
    assert summary.multiple_choice_correct == 2
    assert summary.short_answer_total == 2
    assert summary.self_check_total == 1


def test_run_quiz_handles_explain_back_flow_and_summary() -> None:
    pack = load_exercise_pack("app-main-and-learning-portal")
    answers = iter(
        [
            "2",
            "startup loads the portal behind a flag",
            "1,3",
            "it reads app state after checking the flag",
            "",
            "",
        ]
    )
    output = StringIO()

    summary = run_quiz(pack, input_fn=lambda prompt: next(answers), output=output)
    rendered = output.getvalue()

    assert "Expected points:" in rendered
    assert "Self-review rubric:" in rendered
    assert "Reflection: Which file would you open next" in rendered
    assert "Missed expected points:" in rendered
    assert "routes-learning-explain: When enabled, the route reads the already-loaded" in rendered
    assert summary.explain_back_total == 2
    assert summary.explain_back_reviews[0].missed_points == [
        (
            "The loaded content is stored on `app.state.learning_portal` for the dev-only "
            "route handlers to read later."
        )
    ]
    assert len(summary.explain_back_reviews[1].missed_points) == 3


def test_run_quiz_handles_prediction_flow() -> None:
    pack = load_exercise_pack("runtime-and-workflow-predictions")
    answers = iter(
        [
            "lockfile drift",
            "uv sync updates the lock",
            "learn routes are disabled",
            "loader fails on stale slugs",
        ]
    )
    output = StringIO()

    summary = run_quiz(pack, input_fn=lambda prompt: next(answers), output=output)
    rendered = output.getvalue()

    assert "Scenario:" in rendered
    assert "Target files:" in rendered
    assert "Expected outcome:" in rendered
    assert "Why:" in rendered
    assert "Manual follow-up:" in rendered
    assert "Prediction: 4 attempted" in rendered
    assert summary.prediction_total == 4


def test_run_quiz_reprompts_for_invalid_multiple_choice_input() -> None:
    pack = load_exercise_pack("pyproject-and-uv-lock")
    answers = iter(["z", "A", "lockfile", "C", "", "3", "sync and test"])
    output = StringIO()

    run_quiz(pack, input_fn=lambda prompt: next(answers), output=output)
    rendered = output.getvalue()

    assert "Enter one listed letter or number." in rendered
    assert rendered.count("Correct.") >= 2


def test_run_quiz_reprompts_for_invalid_explain_back_self_review_input() -> None:
    pack = load_exercise_pack("app-main-and-learning-portal")
    answers = iter(
        [
            "2",
            "startup explanation",
            "4",
            "1,2",
            "route explanation",
            "all",
            "",
        ]
    )
    output = StringIO()

    run_quiz(pack, input_fn=lambda prompt: next(answers), output=output)
    rendered = output.getvalue()

    assert "Enter point numbers like '1,3', 'all', or press Enter for none." in rendered
    assert "Missed expected points:" in rendered
