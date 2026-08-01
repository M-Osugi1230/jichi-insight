import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "data/catalog/phase10_execution_queue.json"
QUEUE_SCHEMA_PATH = ROOT / "schemas/phase10_execution_queue.schema.json"
COMPLETION_PATH = ROOT / "data/catalog/phase10_completion.json"
COMPLETION_SCHEMA_PATH = ROOT / "schemas/phase10_completion.schema.json"

ALL_CODES = [f"{value:02d}" for value in range(1, 48)]
WAVE1_CODES = {"01", "04", "13", "23", "27", "34", "37", "40", "47"}
EXPECTED_WAVE1_DEPTH = {
    "target_statements": "reviewed",
    "annual_evaluation": "linked",
    "budget": "linked",
    "project_evaluation": "linked",
    "contracts": "reviewed",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_path: Path, value) -> list[str]:
    validator = Draft202012Validator(
        load(schema_path),
        format_checker=FormatChecker(),
    )
    return [error.message for error in validator.iter_errors(value)]


def test_phase10_queue_and_completion_match_schemas():
    assert validate(QUEUE_SCHEMA_PATH, load(QUEUE_PATH)) == []
    assert validate(COMPLETION_SCHEMA_PATH, load(COMPLETION_PATH)) == []


def test_phase10_waves_cover_all_prefectures_once():
    queue = load(QUEUE_PATH)
    wave_codes = [
        code
        for wave in queue["waves"]
        for code in wave["prefecture_codes"]
    ]

    assert queue["prefecture_order"] == ALL_CODES
    assert len(wave_codes) == 47
    assert set(wave_codes) == set(ALL_CODES)
    assert len(wave_codes) == len(set(wave_codes))
    assert set(queue["waves"][0]["prefecture_codes"]) == WAVE1_CODES


def test_phase10_wave1_records_are_complete_at_declared_depth():
    queue = load(QUEUE_PATH)
    by_code = {
        record["prefecture_code"]: record for record in queue["wave1_records"]
    }

    assert queue["status"] == "complete"
    assert queue["active_prefecture_code"] == "47"
    assert set(by_code) == WAVE1_CODES
    assert queue["default_depth"] == EXPECTED_WAVE1_DEPTH
    assert all(record["status"] == "complete" for record in by_code.values())
    assert all(
        record["current_depth"] == EXPECTED_WAVE1_DEPTH
        for record in by_code.values()
    )
    assert all(
        record["next_gate"] == "publication_verification"
        for record in by_code.values()
    )
    assert queue["policy_achievement_assessment_status"] == "not_assessed"
    assert queue["ranking_eligibility"] == "excluded_until_comparability_verified"


def test_phase10_global_counts_are_complete():
    queue = load(QUEUE_PATH)

    assert queue["counts"] == {
        "total_prefectures": 47,
        "wave1_prefectures": 9,
        "target_statements_reviewed": 47,
        "annual_evaluation_linked": 47,
        "annual_evaluation_indexed": 47,
        "budget_reviewed": 47,
        "project_evaluation_indexed_or_better": 47,
        "contracts_indexed_or_better": 47,
    }


def test_phase10_completion_counts_and_gates_match_execution_queue():
    queue = load(QUEUE_PATH)
    completion = load(COMPLETION_PATH)

    for key, value in queue["counts"].items():
        assert completion["counts"][key] == value

    assert completion["status"] == "complete"
    assert completion["counts"]["published_phase10_pages"] >= 9
    assert completion["nationwide_uniform_counts"] == {
        "reviewed_anchor_prefectures": 9,
        "prefectures_with_five_layers_indexed_or_better": 47,
        "prefectures_with_five_layers_reviewed": 47,
        "annual_actuals_reviewed_or_better": 47,
        "budget_reviewed_or_better": 47,
        "settlement_reviewed_or_better": 47,
        "priority_projects_reviewed_or_better": 47,
        "audit_reviewed_or_better": 47,
        "uniform_depth_complete": 47,
    }
    assert all(gate["status"] == "passed" for gate in completion["gates"])
    assert "document scope" in completion["scope_note"]
    assert "No policy-achievement assessment" in completion["scope_note"]
