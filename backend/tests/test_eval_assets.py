import json
from pathlib import Path

from app.schemas import UserProfile

REPO_ROOT = Path(__file__).resolve().parents[2]
EVALS_ROOT = REPO_ROOT / "backend" / "app" / "evals"
DATASET_PATH = EVALS_ROOT / "workout_plan_eval_dataset_v1.json"
RUBRIC_PATH = EVALS_ROOT / "workout_plan_eval_rubric_v1.json"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_eval_assets_exist() -> None:
    assert EVALS_ROOT.is_dir()
    assert DATASET_PATH.is_file()
    assert RUBRIC_PATH.is_file()


def test_eval_dataset_has_30_unique_cases_with_valid_inputs() -> None:
    dataset = _load_json(DATASET_PATH)
    cases = dataset["cases"]

    assert dataset["version"] == "v1"
    assert len(cases) == 30
    assert len({case["id"] for case in cases}) == 30

    for case in cases:
        assert case["expected_outcome_type"] in {"normal_plan", "safety_fallback"}
        assert case["risk_tags"]
        assert case["expected_behavior"]
        UserProfile.model_validate(case["input"])


def test_eval_dataset_covers_normal_and_safety_fallback_outcomes() -> None:
    dataset = _load_json(DATASET_PATH)
    outcome_types = {case["expected_outcome_type"] for case in dataset["cases"]}

    assert outcome_types == {"normal_plan", "safety_fallback"}


def test_eval_rubric_defines_allowed_tags_and_weighted_dimensions() -> None:
    rubric = _load_json(RUBRIC_PATH)
    dimensions = rubric["dimensions"]
    total_weight = sum(item["weight"] for item in dimensions)

    assert rubric["version"] == "v1"
    assert rubric["allowed_risk_tags"]
    assert len(dimensions) >= 5
    assert total_weight == 1.0

    for item in dimensions:
        assert item["key"]
        assert item["weight"] > 0
        assert item["description"]


def test_eval_dataset_risk_tags_are_supported_by_rubric() -> None:
    dataset = _load_json(DATASET_PATH)
    rubric = _load_json(RUBRIC_PATH)
    allowed_tags = set(rubric["allowed_risk_tags"])

    for case in dataset["cases"]:
        assert set(case["risk_tags"]).issubset(allowed_tags)


def test_medical_referral_cases_require_safety_fallback_expectation() -> None:
    dataset = _load_json(DATASET_PATH)

    medical_cases = [case for case in dataset["cases"] if "medical_referral" in case["risk_tags"]]

    assert medical_cases

    for case in medical_cases:
        assert case["expected_outcome_type"] == "safety_fallback"
        assert "safety_fallback_expected" in case["risk_tags"]
