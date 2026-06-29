from __future__ import annotations

import tomllib
from pathlib import Path

from pydantic import ValidationError

from app.learning.quiz.models import ExercisePack


class ExercisePackError(RuntimeError):
    """Raised when quiz exercise content is missing or invalid."""


def load_exercise_pack(topic: str, exercises_dir: Path | None = None) -> ExercisePack:
    base_dir = exercises_dir or Path(__file__).resolve().parent.parent / "exercises"
    path = base_dir / f"{topic}.toml"

    try:
        raw_data = tomllib.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ExercisePackError(
            f"Unknown quiz topic '{topic}'. Expected pack file at {path}",
        ) from exc
    except tomllib.TOMLDecodeError as exc:
        raise ExercisePackError(f"Invalid TOML in exercise pack {path}: {exc}") from exc

    try:
        pack = ExercisePack.model_validate(raw_data)
    except ValidationError as exc:
        raise ExercisePackError(f"Invalid exercise pack schema in {path}: {exc}") from exc

    if pack.topic.slug != topic:
        raise ExercisePackError(
            f"Exercise pack slug '{pack.topic.slug}' does not match requested topic '{topic}'",
        )

    if not pack.questions:
        raise ExercisePackError(f"Exercise pack {path} must contain at least one question")

    return pack
