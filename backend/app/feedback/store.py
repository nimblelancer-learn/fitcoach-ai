import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from app.core.errors import AppError
from app.schemas import FeedbackRuntimeMetadata, PlanFeedback, UserProfile, WorkoutPlan


@dataclass(frozen=True)
class StoredFeedback:
    feedback_id: int
    created_at: str
    request_id: str
    profile: UserProfile
    workout_plan: WorkoutPlan
    feedback: PlanFeedback
    runtime_metadata: FeedbackRuntimeMetadata


def _sqlite_path_from_database_url(database_url: str) -> Path:
    sqlite_prefix = "sqlite:///"
    if not database_url.startswith(sqlite_prefix):
        raise AppError(
            status_code=500,
            code="UNSUPPORTED_DATABASE_URL",
            message="The configured app database must use sqlite for feedback storage.",
        )

    raw_path = database_url.removeprefix(sqlite_prefix)
    if not raw_path:
        raise AppError(
            status_code=500,
            code="INVALID_DATABASE_URL",
            message="The configured app database URL is missing a sqlite path.",
        )

    if raw_path != ":memory:":
        return Path("/" + raw_path.lstrip("/")).resolve()

    return Path(raw_path)


class LocalFeedbackStore:
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url
        self._sqlite_path = _sqlite_path_from_database_url(database_url)

    def initialize(self) -> None:
        if self._sqlite_path != Path(":memory:"):
            self._sqlite_path.parent.mkdir(parents=True, exist_ok=True)

        with self._connect() as connection:
            connection.execute(
                """
                create table if not exists plan_feedback (
                    id integer primary key autoincrement,
                    created_at text not null,
                    request_id text not null,
                    profile_json text not null,
                    workout_plan_json text not null,
                    feedback_json text not null,
                    runtime_metadata_json text not null default '{}'
                )
                """
            )
            existing_columns = {
                str(row["name"])
                for row in connection.execute("pragma table_info(plan_feedback)").fetchall()
            }
            if "runtime_metadata_json" not in existing_columns:
                connection.execute(
                    """
                    alter table plan_feedback
                    add column runtime_metadata_json text not null default '{}'
                    """
                )
            connection.commit()

    def save_feedback(
        self,
        *,
        request_id: str,
        profile: UserProfile,
        workout_plan: WorkoutPlan,
        feedback: PlanFeedback,
        runtime_metadata: FeedbackRuntimeMetadata,
    ) -> StoredFeedback:
        created_at = datetime.now(UTC).isoformat()
        profile_json = profile.model_dump_json()
        workout_plan_json = workout_plan.model_dump_json()
        feedback_json = feedback.model_dump_json()
        runtime_metadata_json = runtime_metadata.model_dump_json()

        with self._connect() as connection:
            cursor = connection.execute(
                """
                insert into plan_feedback (
                    created_at,
                    request_id,
                    profile_json,
                    workout_plan_json,
                    feedback_json,
                    runtime_metadata_json
                ) values (?, ?, ?, ?, ?, ?)
                """,
                (
                    created_at,
                    request_id,
                    profile_json,
                    workout_plan_json,
                    feedback_json,
                    runtime_metadata_json,
                ),
            )
            connection.commit()

        return StoredFeedback(
            feedback_id=int(cursor.lastrowid),
            created_at=created_at,
            request_id=request_id,
            profile=profile,
            workout_plan=workout_plan,
            feedback=feedback,
            runtime_metadata=runtime_metadata,
        )

    def list_recent_feedback(self, *, limit: int = 20) -> list[StoredFeedback]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select id, created_at, request_id, profile_json, workout_plan_json, feedback_json,
                    runtime_metadata_json
                from plan_feedback
                order by id desc
                limit ?
                """,
                (limit,),
            ).fetchall()

        return [
            StoredFeedback(
                feedback_id=int(row["id"]),
                created_at=str(row["created_at"]),
                request_id=str(row["request_id"]),
                profile=UserProfile.model_validate(json.loads(row["profile_json"])),
                workout_plan=WorkoutPlan.model_validate(json.loads(row["workout_plan_json"])),
                feedback=PlanFeedback.model_validate(json.loads(row["feedback_json"])),
                runtime_metadata=FeedbackRuntimeMetadata.model_validate(
                    json.loads(row["runtime_metadata_json"] or "{}")
                ),
            )
            for row in rows
        ]

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._sqlite_path)
        connection.row_factory = sqlite3.Row
        return connection


# The local FastAPI surface remains a legacy engineering path.
# Keep this alias stable so the existing local app and tests do not need a broader rewrite.
FeedbackStore = LocalFeedbackStore
