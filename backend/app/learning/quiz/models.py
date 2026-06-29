from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class QuizBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


QuestionLevel = Literal[
    "recognize",
    "distinguish",
    "predict",
    "apply",
    "critique",
    "explain",
]


QuestionMode = Literal[
    "multiple_choice",
    "short_answer",
    "self_check",
    "explain_back",
    "prediction",
]


class TopicMetadata(QuizBaseModel):
    slug: str
    title: str
    summary: str
    source_files: list[str] = Field(default_factory=list)


class QuestionBase(QuizBaseModel):
    id: str
    level: QuestionLevel
    prompt: str


class MultipleChoiceQuestion(QuestionBase):
    mode: Literal["multiple_choice"]
    choices: list[str]
    answer_index: int
    explanation: str

    @model_validator(mode="after")
    def validate_choices(self) -> MultipleChoiceQuestion:
        if len(self.choices) < 2:
            raise ValueError("multiple_choice questions require at least two choices")

        if not 0 <= self.answer_index < len(self.choices):
            raise ValueError("answer_index must point at one of the listed choices")

        return self


class ShortAnswerQuestion(QuestionBase):
    mode: Literal["short_answer"]
    expected_answer: str
    rubric_hints: list[str] = Field(default_factory=list)


class SelfCheckQuestion(QuestionBase):
    mode: Literal["self_check"]
    expected_answer: str
    rubric_hints: list[str] = Field(default_factory=list)


class ExplainBackQuestion(QuestionBase):
    mode: Literal["explain_back"]
    expected_points: list[str]
    rubric: list[str] = Field(default_factory=list)
    reflection_prompt: str | None = None

    @model_validator(mode="after")
    def validate_expected_points(self) -> ExplainBackQuestion:
        if not self.expected_points:
            raise ValueError("explain_back questions require at least one expected point")

        if len(self.expected_points) > 5:
            raise ValueError("explain_back questions support at most five expected points")

        return self


class PredictionQuestion(QuestionBase):
    mode: Literal["prediction"]
    scenario: str
    target_files: list[str] = Field(default_factory=list)
    expected_outcome: str
    why: str
    follow_up_check: str | None = None

    @model_validator(mode="after")
    def validate_target_files(self) -> PredictionQuestion:
        if not self.target_files:
            raise ValueError("prediction questions require at least one target file")

        return self


Question = Annotated[
    MultipleChoiceQuestion
    | ShortAnswerQuestion
    | SelfCheckQuestion
    | ExplainBackQuestion
    | PredictionQuestion,
    Field(discriminator="mode"),
]


class ExercisePack(QuizBaseModel):
    topic: TopicMetadata
    questions: list[Question]

    @model_validator(mode="after")
    def validate_question_ids(self) -> ExercisePack:
        seen: set[str] = set()

        for question in self.questions:
            if question.id in seen:
                raise ValueError(f"duplicate question id '{question.id}'")
            seen.add(question.id)

        return self
