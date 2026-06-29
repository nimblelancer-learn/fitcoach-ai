from __future__ import annotations

import argparse
import string
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TextIO

from app.learning.quiz.loader import ExercisePackError, load_exercise_pack
from app.learning.quiz.models import (
    ExercisePack,
    ExplainBackQuestion,
    MultipleChoiceQuestion,
    PredictionQuestion,
    SelfCheckQuestion,
    ShortAnswerQuestion,
)

InputFn = Callable[[str], str]


@dataclass(slots=True)
class ExplainBackReview:
    question_id: str
    missed_points: list[str]


@dataclass(slots=True)
class SessionSummary:
    topic: str
    total_questions: int
    multiple_choice_total: int = 0
    multiple_choice_correct: int = 0
    short_answer_total: int = 0
    self_check_total: int = 0
    explain_back_total: int = 0
    prediction_total: int = 0
    explain_back_reviews: list[ExplainBackReview] = field(default_factory=list)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="learning-quiz",
        description="Run one curated learning exercise pack from disk.",
    )
    parser.add_argument(
        "--topic",
        required=True,
        help="Topic slug to load from app/learning/exercises.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        pack = load_exercise_pack(args.topic)
    except ExercisePackError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    run_quiz(pack)
    return 0


def run_quiz(
    pack: ExercisePack,
    *,
    input_fn: InputFn = input,
    output: TextIO = sys.stdout,
) -> SessionSummary:
    summary = SessionSummary(
        topic=pack.topic.slug,
        total_questions=len(pack.questions),
    )

    _write_line(output, f"Topic: {pack.topic.title}")
    _write_line(output, pack.topic.summary)

    if pack.topic.source_files:
        _write_line(output, "Source files:")
        for path in pack.topic.source_files:
            _write_line(output, f"  - {path}")

    for index, question in enumerate(pack.questions, start=1):
        _write_line(output, "")
        _write_line(output, f"[{index}/{len(pack.questions)}] {question.level} | {question.mode}")
        _write_line(output, question.prompt)

        if isinstance(question, MultipleChoiceQuestion):
            summary.multiple_choice_total += 1
            if _ask_multiple_choice(question, input_fn=input_fn, output=output):
                summary.multiple_choice_correct += 1
            continue

        if isinstance(question, ShortAnswerQuestion):
            summary.short_answer_total += 1
            _ask_short_answer(question, input_fn=input_fn, output=output)
            continue

        if isinstance(question, SelfCheckQuestion):
            summary.self_check_total += 1
            _run_self_check(question, input_fn=input_fn, output=output)
            continue

        if isinstance(question, ExplainBackQuestion):
            summary.explain_back_total += 1
            review = _run_explain_back(question, input_fn=input_fn, output=output)
            summary.explain_back_reviews.append(review)
            continue

        if isinstance(question, PredictionQuestion):
            summary.prediction_total += 1
            _run_prediction(question, input_fn=input_fn, output=output)
            continue

        raise RuntimeError(f"Unsupported question type: {type(question).__name__}")

    _print_summary(summary, output)
    return summary


def _ask_multiple_choice(
    question: MultipleChoiceQuestion,
    *,
    input_fn: InputFn,
    output: TextIO,
) -> bool:
    labels = _choice_labels(len(question.choices))

    for label, choice in zip(labels, question.choices, strict=True):
        _write_line(output, f"  {label}) {choice}")

    expected = labels[question.answer_index]

    while True:
        raw_answer = input_fn("Your choice: ").strip()
        answer = raw_answer.upper()

        if answer in labels:
            break

        if raw_answer.isdigit():
            numeric_index = int(raw_answer) - 1
            if 0 <= numeric_index < len(labels):
                answer = labels[numeric_index]
                break

        _write_line(output, "Enter one listed letter or number.")

    is_correct = answer == expected
    if is_correct:
        _write_line(output, "Correct.")
    else:
        expected_choice = question.choices[question.answer_index]
        _write_line(output, f"Not quite. Expected: {expected}) {expected_choice}")

    _write_line(output, f"Why: {question.explanation}")
    return is_correct


def _ask_short_answer(
    question: ShortAnswerQuestion,
    *,
    input_fn: InputFn,
    output: TextIO,
) -> None:
    learner_answer = input_fn("Your answer: ").strip()
    if learner_answer:
        _write_line(output, "Captured.")
    else:
        _write_line(output, "No answer captured.")

    _write_line(output, f"Expected answer: {question.expected_answer}")
    _write_hints(question.rubric_hints, output)


def _run_self_check(
    question: SelfCheckQuestion,
    *,
    input_fn: InputFn,
    output: TextIO,
) -> None:
    input_fn("Press Enter to reveal: ")
    _write_line(output, f"Reveal: {question.expected_answer}")
    _write_hints(question.rubric_hints, output)


def _run_explain_back(
    question: ExplainBackQuestion,
    *,
    input_fn: InputFn,
    output: TextIO,
) -> ExplainBackReview:
    learner_answer = input_fn("Your explanation: ").strip()
    if learner_answer:
        _write_line(output, "Captured.")
    else:
        _write_line(output, "No answer captured.")

    _write_line(output, "Expected points:")
    for index, point in enumerate(question.expected_points, start=1):
        _write_line(output, f"  {index}. {point}")

    if question.rubric:
        _write_line(output, "Self-review rubric:")
        for item in question.rubric:
            _write_line(output, f"  - {item}")

    if question.reflection_prompt:
        _write_line(output, f"Reflection: {question.reflection_prompt}")

    covered_points = _prompt_for_covered_points(
        len(question.expected_points),
        input_fn=input_fn,
        output=output,
    )
    missed_points = [
        point
        for index, point in enumerate(question.expected_points, start=1)
        if index not in covered_points
    ]

    return ExplainBackReview(question_id=question.id, missed_points=missed_points)


def _run_prediction(
    question: PredictionQuestion,
    *,
    input_fn: InputFn,
    output: TextIO,
) -> None:
    _write_line(output, "Scenario:")
    _write_line(output, f"  {question.scenario}")
    _write_line(output, "Target files:")
    for path in question.target_files:
        _write_line(output, f"  - {path}")

    learner_answer = input_fn("Your prediction: ").strip()
    if learner_answer:
        _write_line(output, "Captured.")
    else:
        _write_line(output, "No prediction captured.")

    _write_line(output, f"Expected outcome: {question.expected_outcome}")
    _write_line(output, f"Why: {question.why}")
    if question.follow_up_check:
        _write_line(output, f"Manual follow-up: {question.follow_up_check}")


def _prompt_for_covered_points(
    point_count: int,
    *,
    input_fn: InputFn,
    output: TextIO,
) -> set[int]:
    prompt = "Covered points (comma-separated numbers, 'all', or Enter for none): "

    while True:
        raw_answer = input_fn(prompt).strip().lower()
        if raw_answer == "":
            return set()

        if raw_answer == "all":
            return set(range(1, point_count + 1))

        selected: set[int] = set()
        is_valid = True
        for part in raw_answer.split(","):
            token = part.strip()
            if not token.isdigit():
                is_valid = False
                break

            point_index = int(token)
            if not 1 <= point_index <= point_count:
                is_valid = False
                break

            selected.add(point_index)

        if is_valid:
            return selected

        _write_line(
            output,
            "Enter point numbers like '1,3', 'all', or press Enter for none.",
        )


def _write_hints(hints: list[str], output: TextIO) -> None:
    if not hints:
        return

    _write_line(output, "Rubric hints:")
    for hint in hints:
        _write_line(output, f"  - {hint}")


def _print_summary(summary: SessionSummary, output: TextIO) -> None:
    _write_line(output, "")
    _write_line(output, "Session summary")
    _write_line(output, f"  Topic: {summary.topic}")
    _write_line(output, f"  Total questions: {summary.total_questions}")
    _write_line(
        output,
        "  Multiple choice: "
        f"{summary.multiple_choice_correct}/{summary.multiple_choice_total} correct",
    )
    _write_line(output, f"  Short answer: {summary.short_answer_total} attempted")
    _write_line(output, f"  Self-check: {summary.self_check_total} revealed")
    _write_line(output, f"  Explain-back: {summary.explain_back_total} attempted")
    _write_line(output, f"  Prediction: {summary.prediction_total} attempted")

    missed_points = [
        f"{review.question_id}: {point}"
        for review in summary.explain_back_reviews
        for point in review.missed_points
    ]
    if missed_points:
        _write_line(output, "  Missed expected points:")
        for point in missed_points:
            _write_line(output, f"    - {point}")
    elif summary.explain_back_total:
        _write_line(output, "  Missed expected points: none self-reported")


def _choice_labels(count: int) -> list[str]:
    if count > len(string.ascii_uppercase):
        raise ValueError("multiple_choice questions support at most 26 choices")
    return list(string.ascii_uppercase[:count])


def _write_line(output: TextIO, text: str) -> None:
    output.write(text + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
