from __future__ import annotations

import argparse
import subprocess
import sys
import tomllib
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated, Literal, TextIO

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

InputFn = Callable[[str], str]
CommandRunner = Callable[[list[str]], tuple[int, str, str]]

BACKEND_DIR = Path(__file__).resolve().parents[3]
DEFAULT_WORKSPACE_ROOT = Path("/tmp/fitcoach-learning-drills")


class DrillBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


DrillCategory = Literal[
    "call_flow_tracing",
    "impact_prediction",
    "test_selection",
    "constrained_repo_task",
]


class DrillSetMetadata(DrillBaseModel):
    slug: str
    title: str
    summary: str
    source_files: list[str] = Field(default_factory=list)


class AnswerFileValidator(DrillBaseModel):
    type: Literal["answer_file"]
    relative_path: str
    required_substrings: list[str]

    @model_validator(mode="after")
    def validate_required_substrings(self) -> AnswerFileValidator:
        if not self.required_substrings:
            raise ValueError("answer_file validator requires at least one required substring")
        return self


class TestSelectionValidator(DrillBaseModel):
    type: Literal["test_selection"]
    expected_tests: list[str]

    @model_validator(mode="after")
    def validate_expected_tests(self) -> TestSelectionValidator:
        if not self.expected_tests:
            raise ValueError("test_selection validator requires at least one expected test")
        return self


class PytestTargetValidator(DrillBaseModel):
    type: Literal["pytest_target"]
    pytest_args: list[str]

    @model_validator(mode="after")
    def validate_pytest_args(self) -> PytestTargetValidator:
        if not self.pytest_args:
            raise ValueError("pytest_target validator requires at least one pytest argument")

        if not any(arg.startswith("tests/") for arg in self.pytest_args):
            raise ValueError("pytest_target validator requires at least one tests/ path")

        return self


DrillValidator = Annotated[
    AnswerFileValidator | TestSelectionValidator | PytestTargetValidator,
    Field(discriminator="type"),
]


class RepoDrill(DrillBaseModel):
    id: str
    category: DrillCategory
    title: str
    prompt: str
    target_files: list[str] = Field(default_factory=list)
    instructions: list[str] = Field(default_factory=list)
    validator: DrillValidator


class RepoDrillSet(DrillBaseModel):
    drill_set: DrillSetMetadata
    drills: list[RepoDrill]

    @model_validator(mode="after")
    def validate_drill_ids(self) -> RepoDrillSet:
        seen: set[str] = set()
        for drill in self.drills:
            if drill.id in seen:
                raise ValueError(f"duplicate drill id '{drill.id}'")
            seen.add(drill.id)

        if not self.drills:
            raise ValueError("repo drill sets must contain at least one drill")

        return self


class DrillSetError(RuntimeError):
    """Raised when repo drill content is missing or invalid."""


@dataclass(slots=True)
class DrillOutcome:
    drill_id: str
    success: bool
    details: list[str] = field(default_factory=list)


@dataclass(slots=True)
class DrillSessionSummary:
    topic: str
    total_drills: int
    passed: int = 0
    failed: int = 0
    outcomes: list[DrillOutcome] = field(default_factory=list)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="learning-drills",
        description="Run one curated repo drill set from disk.",
    )
    parser.add_argument(
        "--topic",
        required=True,
        help="Topic slug to load from app/learning/exercises.",
    )
    parser.add_argument(
        "--workspace",
        default=str(DEFAULT_WORKSPACE_ROOT),
        help="Directory for learner-created drill artifacts.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        drill_set = load_drill_set(args.topic)
    except DrillSetError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    run_drills(drill_set, workspace_root=Path(args.workspace))
    return 0


def load_drill_set(topic: str, exercises_dir: Path | None = None) -> RepoDrillSet:
    base_dir = exercises_dir or Path(__file__).resolve().parent.parent / "exercises"
    path = base_dir / f"{topic}.toml"

    try:
        raw_data = tomllib.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise DrillSetError(
            f"Unknown drill topic '{topic}'. Expected drill file at {path}",
        ) from exc
    except tomllib.TOMLDecodeError as exc:
        raise DrillSetError(f"Invalid TOML in drill set {path}: {exc}") from exc

    try:
        drill_set = RepoDrillSet.model_validate(raw_data)
    except ValidationError as exc:
        raise DrillSetError(f"Invalid drill set schema in {path}: {exc}") from exc

    if drill_set.drill_set.slug != topic:
        raise DrillSetError(
            f"Drill set slug '{drill_set.drill_set.slug}' does not match requested topic '{topic}'",
        )

    return drill_set


def run_drills(
    drill_set: RepoDrillSet,
    *,
    workspace_root: Path,
    input_fn: InputFn = input,
    output: TextIO = sys.stdout,
    command_runner: CommandRunner | None = None,
) -> DrillSessionSummary:
    summary = DrillSessionSummary(
        topic=drill_set.drill_set.slug,
        total_drills=len(drill_set.drills),
    )
    workspace_dir = workspace_root / drill_set.drill_set.slug
    workspace_dir.mkdir(parents=True, exist_ok=True)
    command_runner = command_runner or _run_command

    _write_line(output, f"Drill set: {drill_set.drill_set.title}")
    _write_line(output, drill_set.drill_set.summary)

    if drill_set.drill_set.source_files:
        _write_line(output, "Source files:")
        for path in drill_set.drill_set.source_files:
            _write_line(output, f"  - {path}")

    _write_line(output, f"Workspace: {workspace_dir}")

    for index, drill in enumerate(drill_set.drills, start=1):
        _write_line(output, "")
        _write_line(output, f"[{index}/{len(drill_set.drills)}] {drill.category} | {drill.title}")
        _write_line(output, drill.prompt)

        if drill.target_files:
            _write_line(output, "Target files:")
            for path in drill.target_files:
                _write_line(output, f"  - {path}")

        if drill.instructions:
            _write_line(output, "Instructions:")
            for item in drill.instructions:
                _write_line(output, f"  - {item}")

        outcome = _run_validator(
            drill=drill,
            workspace_dir=workspace_dir,
            input_fn=input_fn,
            output=output,
            command_runner=command_runner,
        )
        summary.outcomes.append(outcome)

        if outcome.success:
            summary.passed += 1
            _write_line(output, "Validation: passed")
        else:
            summary.failed += 1
            _write_line(output, "Validation: failed")
            for detail in outcome.details:
                _write_line(output, f"  - {detail}")

    _print_summary(summary, output)
    return summary


def _run_validator(
    *,
    drill: RepoDrill,
    workspace_dir: Path,
    input_fn: InputFn,
    output: TextIO,
    command_runner: CommandRunner,
) -> DrillOutcome:
    validator = drill.validator

    if isinstance(validator, AnswerFileValidator):
        artifact_path = workspace_dir / validator.relative_path
        _write_line(output, f"Answer file: {artifact_path}")
        _prompt_input(
            "Press Enter after preparing the answer file: ",
            input_fn=input_fn,
            output=output,
        )
        return _validate_answer_file(drill.id, artifact_path, validator)

    if isinstance(validator, TestSelectionValidator):
        selected_tests = _prompt_for_selected_tests(input_fn=input_fn, output=output)
        return _validate_test_selection(drill.id, selected_tests, validator)

    if isinstance(validator, PytestTargetValidator):
        command_text = "python -m pytest " + " ".join(validator.pytest_args)
        _write_line(output, f"Validation target: {command_text}")
        _prompt_input(
            "Press Enter to run the focused pytest target: ",
            input_fn=input_fn,
            output=output,
        )
        return _validate_pytest_target(drill.id, validator, command_runner)

    raise RuntimeError(f"Unsupported validator type: {type(validator).__name__}")


def _validate_answer_file(
    drill_id: str,
    artifact_path: Path,
    validator: AnswerFileValidator,
) -> DrillOutcome:
    if not artifact_path.exists():
        return DrillOutcome(
            drill_id=drill_id,
            success=False,
            details=[f"Missing answer file: {artifact_path}"],
        )

    answer_text = artifact_path.read_text(encoding="utf-8")
    missing_substrings = [
        snippet for snippet in validator.required_substrings if snippet not in answer_text
    ]
    if missing_substrings:
        return DrillOutcome(
            drill_id=drill_id,
            success=False,
            details=[f"Missing expected text: {snippet}" for snippet in missing_substrings],
        )

    return DrillOutcome(drill_id=drill_id, success=True)


def _prompt_for_selected_tests(
    *,
    input_fn: InputFn,
    output: TextIO,
) -> list[str]:
    while True:
        raw_answer = _prompt_input(
            "Selected tests (comma-separated paths): ",
            input_fn=input_fn,
            output=output,
        ).strip()
        selected_tests = [item.strip() for item in raw_answer.split(",") if item.strip()]
        if selected_tests:
            return selected_tests

        _write_line(output, "Enter one or more test paths separated by commas.")


def _validate_test_selection(
    drill_id: str,
    selected_tests: list[str],
    validator: TestSelectionValidator,
) -> DrillOutcome:
    selected = set(selected_tests)
    expected = set(validator.expected_tests)

    missing = sorted(expected - selected)
    unexpected = sorted(selected - expected)
    if missing or unexpected:
        details: list[str] = []
        if missing:
            details.append(f"Missing tests: {', '.join(missing)}")
        if unexpected:
            details.append(f"Unexpected tests: {', '.join(unexpected)}")
        return DrillOutcome(drill_id=drill_id, success=False, details=details)

    return DrillOutcome(drill_id=drill_id, success=True)


def _validate_pytest_target(
    drill_id: str,
    validator: PytestTargetValidator,
    command_runner: CommandRunner,
) -> DrillOutcome:
    exit_code, stdout, stderr = command_runner(
        [sys.executable, "-m", "pytest", *validator.pytest_args]
    )
    if exit_code == 0:
        return DrillOutcome(drill_id=drill_id, success=True)

    details = ["Focused pytest validation failed."]
    if stdout.strip():
        details.append(stdout.strip().splitlines()[-1])
    if stderr.strip():
        details.append(stderr.strip().splitlines()[-1])
    return DrillOutcome(drill_id=drill_id, success=False, details=details)


def _run_command(command: list[str]) -> tuple[int, str, str]:
    completed = subprocess.run(
        command,
        cwd=BACKEND_DIR,
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.returncode, completed.stdout, completed.stderr


def _print_summary(summary: DrillSessionSummary, output: TextIO) -> None:
    _write_line(output, "")
    _write_line(output, "Drill summary")
    _write_line(output, f"  Topic: {summary.topic}")
    _write_line(output, f"  Total drills: {summary.total_drills}")
    _write_line(output, f"  Passed: {summary.passed}")
    _write_line(output, f"  Failed: {summary.failed}")


def _prompt_input(prompt: str, *, input_fn: InputFn, output: TextIO) -> str:
    output.write(prompt)
    return input_fn("")


def _write_line(output: TextIO, text: str) -> None:
    output.write(text + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
