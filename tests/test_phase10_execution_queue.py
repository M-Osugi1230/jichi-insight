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
INDEXED_OR_BETTER = {"indexed", "reviewed", "linked"}


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


def test_phase10_wave1_baseline_is_conservative_and_verified():
    queue = load(QUEUE_PATH)
    by_code = {
        record["prefecture_code"]: record for record in queue["wave1_records"]
    }

    assert set(by_code) == WAVE1_CODES
    assert queue["active_prefecture_code"] == "04"
    assert by_code["04"]["status"] == "linked_baseline"
    assert by_code["04"]["current_depth"]["annual_evaluation"] == "linked"
    assert by_code["04"]["next_gate"] == "budget_linkage"

    assert by_code["40"]["status"] == "review_ready"
    assert by_code["40"]["current_depth"]["annual_evaluation"] == "indexed"
    assert by_code["40"]["current_depth"]["budget"] == "reviewed"
    assert by_code["40"]["next_gate"] == "annual_actuals_linkage"

    assert all(
        record["current_depth"]["target_statements"] == "reviewed"
        for record in queue["wave1_records"]
    )
    assert queue["policy_achievement_assessment_status"] == "not_assessed"
    assert queue["ranking_eligibility"] == "excluded_until_comparability_verified"


def test_phase10_counts_are_derived_from_wave1_depth():
    queue = load(QUEUE_PATH)
    records = queue["wave1_records"]
    counts = queue["counts"]

    assert counts["total_prefectures"] == 47
    assert counts["wave1_prefectures"] == len(records)
    assert counts["target_statements_reviewed"] == 47
    assert counts["annual_evaluation_linked"] == sum(
        record["current_depth"]["annual_evaluation"] == "linked"
        for record in records
    )
    assert counts["annual_evaluation_indexed"] == sum(
        record["current_depth"]["annual_evaluation"] == "indexed"
        for record in records
    )
    assert counts["budget_reviewed"] == sum(
        record["current_depth"]["budget"] == "reviewed"
        for record in records
    )
    assert counts["project_evaluation_indexed_or_better"] == sum(
        record["current_depth"]["project_evaluation"] in INDEXED_OR_BETTER
        for record in records
    )
    assert counts["contracts_indexed_or_better"] == sum(
        record["current_depth"]["contracts"] in INDEXED_OR_BETTER
        for record in records
    )


def test_phase10_completion_counts_match_execution_queue():
    queue = load(QUEUE_PATH)
    completion = load(COMPLETION_PATH)

    for key in (
        "total_prefectures",
        "wave1_prefectures",
        "target_statements_reviewed",
        "annual_evaluation_linked",
        "annual_evaluation_indexed",
        "budget_reviewed",
        "project_evaluation_indexed_or_better",
        "contracts_indexed_or_better",
    ):
        assert completion["counts"][key] == queue["counts"][key]

    gates = {gate["id"]: gate for gate in completion["gates"]}
    assert gates["phase9_handoff_verified"]["status"] == "passed"
    assert gates["nationwide_vertical_source_inventory"]["status"] == "in_progress"
    assert completion["status"] == "in_progress"
