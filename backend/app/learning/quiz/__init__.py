"""Local quiz CLI for curated FitCoach learning exercises."""

from app.learning.quiz.loader import ExercisePackError, load_exercise_pack
from app.learning.quiz.models import ExercisePack


def main(argv: list[str] | None = None) -> int:
    from app.learning.quiz.cli import main as cli_main

    return cli_main(argv)


def run_quiz(*args: object, **kwargs: object) -> object:
    from app.learning.quiz.cli import run_quiz as cli_run_quiz

    return cli_run_quiz(*args, **kwargs)


__all__ = [
    "ExercisePack",
    "ExercisePackError",
    "load_exercise_pack",
    "main",
    "run_quiz",
]
