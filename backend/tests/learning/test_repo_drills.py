from __future__ import annotations

from io import StringIO
from pathlib import Path

import pytest

from app.learning.drills.runner import (
    DrillSetError,
    load_drill_set,
    run_drills,
)


def test_load_drill_set_reads_real_topic() -> None:
    drill_set = load_drill_set("repo-drills")

    assert drill_set.drill_set.slug == "repo-drills"
    assert [drill.category for drill in drill_set.drills] == [
        "call_flow_tracing",
        "impact_prediction",
        "test_selection",
        "constrained_repo_task",
    ]


def test_load_drill_set_requires_pytest_path(tmp_path: Path) -> None:
    exercises_dir = tmp_path
    (exercises_dir / "broken.toml").write_text(
        """
[drill_set]
slug = "broken"
title = "Broken"
summary = "Broken drill"

[[drills]]
id = "bad"
category = "constrained_repo_task"
title = "Bad"
prompt = "Bad"

[drills.validator]
type = "pytest_target"
pytest_args = ["-q"]
""".strip()
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(DrillSetError) as exc_info:
        load_drill_set("broken", exercises_dir)

    assert "requires at least one tests/ path" in str(exc_info.value)


def test_run_drills_validates_answer_files_and_test_selection(tmp_path: Path) -> None:
    drill_set = load_drill_set("repo-drills")
    workspace = tmp_path / "workspace"
    drill_workspace = workspace / drill_set.drill_set.slug
    drill_workspace.mkdir(parents=True)
    (drill_workspace / "startup-call-flow-trace.txt").write_text(
        "startup enable_dev_learning_portal load_learning_portal app.state.learning_portal\n",
        encoding="utf-8",
    )
    (drill_workspace / "loader-impact-prediction.txt").write_text(
        "LearningContentError related_modules featured_modules\n",
        encoding="utf-8",
    )

    answers = iter(["", "", "tests/test_learning_portal.py", ""])
    output = StringIO()

    summary = run_drills(
        drill_set,
        workspace_root=workspace,
        input_fn=lambda prompt: next(answers),
        output=output,
        command_runner=lambda command: (0, "ok", ""),
    )
    rendered = output.getvalue()

    assert "Answer file:" in rendered
    assert "Selected tests" in rendered
    assert (
        "Validation target: python -m pytest tests/services/test_workout_plan_generator.py -q"
    ) in rendered
    assert "Drill summary" in rendered
    assert summary.passed == 4
    assert summary.failed == 0


def test_run_drills_reports_missing_answer_file_and_bad_test_selection(tmp_path: Path) -> None:
    drill_set = load_drill_set("repo-drills")
    workspace = tmp_path / "workspace"
    drill_workspace = workspace / drill_set.drill_set.slug
    drill_workspace.mkdir(parents=True)
    (drill_workspace / "loader-impact-prediction.txt").write_text(
        "LearningContentError related_modules featured_modules\n",
        encoding="utf-8",
    )

    answers = iter(["", "", "", "tests/test_eval_assets.py", ""])
    output = StringIO()

    summary = run_drills(
        drill_set,
        workspace_root=workspace,
        input_fn=lambda prompt: next(answers),
        output=output,
        command_runner=lambda command: (1, "FAILED", "boom"),
    )
    rendered = output.getvalue()

    assert "Missing answer file:" in rendered
    assert "Missing tests: tests/test_learning_portal.py" in rendered
    assert "Unexpected tests: tests/test_eval_assets.py" in rendered
    assert "Focused pytest validation failed." in rendered
    assert summary.failed == 3
