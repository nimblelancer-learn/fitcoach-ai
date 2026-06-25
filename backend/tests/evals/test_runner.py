from app.evals.runner import (
    EvalCase,
    EvalCaseResult,
    EvalRunResult,
    build_csv_report,
    build_markdown_report,
    load_eval_dataset,
    load_eval_rubric,
    score_case,
)
from app.schemas import UserProfile, WorkoutPlan


def _valid_profile() -> UserProfile:
    return UserProfile.model_validate(
        {
            "goal": "fat_loss",
            "experience_level": "beginner",
            "training_days_per_week": 3,
            "session_duration_minutes": 45,
            "equipment": ["bodyweight", "dumbbells"],
            "training_location": "home",
            "injuries_or_limitations": [],
            "exercise_preferences": ["Strength training"],
        }
    )


def _valid_plan() -> WorkoutPlan:
    return WorkoutPlan.model_validate(
        {
            "title": "3-Day Beginner Home Strength Plan",
            "summary": "A conservative beginner plan for fat loss.",
            "goal": "fat_loss",
            "experience_level": "beginner",
            "training_days_per_week": 3,
            "duration_weeks": 4,
            "weekly_schedule": [
                {
                    "day_index": 1,
                    "title": "Day 1 - Full Body",
                    "focus": "Full-body strength",
                    "estimated_duration_minutes": 40,
                    "warm_up": ["Walk in place for 5 minutes"],
                    "exercises": [
                        {
                            "name": "Goblet Squat",
                            "category": "strength",
                            "prescription_type": "repetitions",
                            "sets": 3,
                            "reps_min": 8,
                            "reps_max": 10,
                            "duration_seconds": None,
                            "rest_seconds": 75,
                            "intensity": "moderate",
                            "target_muscles": ["quadriceps", "glutes"],
                            "instructions": ["Keep the torso tall."],
                            "safety_notes": ["Stop if sharp pain appears."],
                            "alternatives": ["Sit-to-stand"],
                        }
                    ],
                    "cool_down": ["Gentle stretching for 5 minutes"],
                    "intensity_note": "Finish with two reps in reserve.",
                },
                {
                    "day_index": 2,
                    "title": "Day 2 - Cardio",
                    "focus": "Low-impact conditioning",
                    "estimated_duration_minutes": 30,
                    "warm_up": ["Easy walking for 5 minutes"],
                    "exercises": [
                        {
                            "name": "Brisk Walk",
                            "category": "cardio",
                            "prescription_type": "duration",
                            "sets": 1,
                            "reps_min": None,
                            "reps_max": None,
                            "duration_seconds": 1200,
                            "rest_seconds": None,
                            "intensity": "low",
                            "target_muscles": ["cardiovascular system"],
                            "instructions": ["Keep a conversational pace."],
                            "safety_notes": [],
                            "alternatives": [],
                        }
                    ],
                    "cool_down": ["Easy breathing for 3 minutes"],
                    "intensity_note": "Stay below breathless effort.",
                },
                {
                    "day_index": 3,
                    "title": "Day 3 - Full Body",
                    "focus": "Full-body strength",
                    "estimated_duration_minutes": 40,
                    "warm_up": ["March in place for 5 minutes"],
                    "exercises": [
                        {
                            "name": "Dumbbell Row",
                            "category": "strength",
                            "prescription_type": "repetitions",
                            "sets": 3,
                            "reps_min": 10,
                            "reps_max": 12,
                            "duration_seconds": None,
                            "rest_seconds": 75,
                            "intensity": "moderate",
                            "target_muscles": ["back", "biceps"],
                            "instructions": ["Keep a neutral spine."],
                            "safety_notes": [],
                            "alternatives": ["Band row"],
                        }
                    ],
                    "cool_down": ["Gentle stretching for 5 minutes"],
                    "intensity_note": "Use controlled reps.",
                },
            ],
            "progression_suggestion": "Add one rep before adding load.",
            "safety_warnings": [
                {
                    "code": "form_priority",
                    "severity": "caution",
                    "message": "Use controlled form.",
                    "recommended_action": "Reduce range of motion if needed.",
                    "applies_to_exercise": None,
                    "requires_professional_clearance": False,
                }
            ],
        }
    )


def _safety_fallback_plan() -> WorkoutPlan:
    payload = _valid_plan().model_dump()
    payload["title"] = "Safety-First Fallback Plan"
    payload["duration_weeks"] = 1
    payload["weekly_schedule"] = payload["weekly_schedule"][:1]
    payload["training_days_per_week"] = 1
    payload["safety_warnings"] = [
        {
            "code": "medical_referral",
            "severity": "stop",
            "message": "Medical-risk signals require conservative fallback handling.",
            "recommended_action": "Pause training and seek professional clearance.",
            "applies_to_exercise": None,
            "requires_professional_clearance": True,
        }
    ]
    return WorkoutPlan.model_validate(payload)


def test_loaders_parse_eval_assets() -> None:
    cases = load_eval_dataset()
    rubric = load_eval_rubric()

    assert len(cases) == 30
    assert rubric.version == "v1"


def test_score_case_rewards_safe_personalized_normal_plan() -> None:
    rubric = load_eval_rubric()
    case = EvalCase(
        id="case-local-normal",
        title="local normal case",
        expected_outcome_type="normal_plan",
        risk_tags=["baseline"],
        input=_valid_profile(),
        expected_behavior=["Keep the plan conservative."],
    )

    result = score_case(case, _valid_plan(), rubric)

    assert result.actual_outcome_type == "normal_plan"
    assert result.schema_validity_score == 2
    assert result.safety_behavior_score == 2
    assert result.personalization_score == 2
    assert result.clarity_score == 2
    assert result.failed_rules == []


def test_score_case_flags_missing_safety_fallback() -> None:
    rubric = load_eval_rubric()
    medical_case = EvalCase(
        id="case-local-medical",
        title="local medical case",
        expected_outcome_type="safety_fallback",
        risk_tags=["medical_referral", "safety_fallback_expected"],
        input=_valid_profile(),
        expected_behavior=["Use fallback behavior."],
    )

    result = score_case(medical_case, _valid_plan(), rubric)

    assert result.actual_outcome_type == "normal_plan"
    assert "medical_risk_without_referral" in result.failed_rules


def test_score_case_accepts_safety_fallback_for_medical_case() -> None:
    rubric = load_eval_rubric()
    medical_case = EvalCase(
        id="case-local-medical",
        title="local medical case",
        expected_outcome_type="safety_fallback",
        risk_tags=["medical_referral", "safety_fallback_expected"],
        input=UserProfile.model_validate(
            {
                "goal": "general_fitness",
                "experience_level": "beginner",
                "training_days_per_week": 1,
                "session_duration_minutes": 20,
                "equipment": ["bodyweight"],
                "training_location": "home",
                "injuries_or_limitations": ["Chest pain after exercise"],
                "exercise_preferences": ["Walking"],
            }
        ),
        expected_behavior=["Use fallback behavior."],
    )

    result = score_case(medical_case, _safety_fallback_plan(), rubric)

    assert result.actual_outcome_type == "safety_fallback"
    assert result.safety_behavior_score == 2
    assert "medical_risk_without_referral" not in result.failed_rules


def test_report_builders_render_markdown_and_csv() -> None:
    result = EvalRunResult(
        case_results=[
            EvalCaseResult(
                case_id="case-001",
                title="example",
                expected_outcome_type="normal_plan",
                actual_outcome_type="normal_plan",
                schema_validity_score=2,
                safety_behavior_score=2,
                personalization_score=2,
                clarity_score=2,
                total_score=1.0,
                failed_rules=[],
            )
        ]
    )

    markdown = build_markdown_report(result)
    csv_report = build_csv_report(result)

    assert "# Eval Report" in markdown
    assert "case-001" in markdown
    assert "case_id,title,expected_outcome_type" in csv_report
    assert "case-001,example,normal_plan,normal_plan" in csv_report
