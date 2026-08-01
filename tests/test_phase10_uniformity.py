import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
UNIFORMITY_PATH = ROOT / "data/catalog/phase10_uniformity.json"
SCHEMA_PATH = ROOT / "schemas/phase10_uniformity.schema.json"
QUEUE_PATH = ROOT / "data/catalog/phase10_execution_queue.json"
COMPLETION_PATH = ROOT / "data/catalog/phase10_completion.json"

ALL_CODES = [f"{value:02d}" for value in range(1, 48)]
STATUSES = ("not_indexed", "indexed", "reviewed", "linked")
STATUS_RANK = {status: index for index, status in enumerate(STATUSES)}
EXPECTED_DEPTH = {
    "target_statements": "reviewed",
    "evidence_packets": "reviewed",
    "annual_actuals": "linked",
    "budget": "linked",
    "settlement": "linked",
    "priority_projects": "linked",
    "contracts": "reviewed",
    "assembly": "reviewed",
    "audit": "linked",
    "executive_manifesto": "reviewed",
    "publication": "reviewed",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def expanded_records():
    uniformity = load(UNIFORMITY_PATH)
    records = []
    for code in ALL_CODES:
        override = uniformity["overrides"].get(code, {})
        depth = {
            **uniformity["default_depth"],
            **override.get("current_depth", {}),
        }
        gap_count = sum(
            STATUS_RANK[depth[dimension["id"]]]
            < STATUS_RANK[dimension["completion_status"]]
            for dimension in uniformity["dimensions"]
        )
        records.append(
            {
                "prefecture_code": code,
                "status": override.get(
                    "status", uniformity["default_work"]["status"]
                ),
                "current_depth": depth,
                "gap_count": gap_count,
                "next_gate": override.get(
                    "next_gate", uniformity["default_work"]["next_gate"]
                ),
            }
        )
    return uniformity, records


def test_phase10_uniformity_matches_schema():
    validator = Draft202012Validator(
        load(SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(load(UNIFORMITY_PATH))) == []


def test_uniformity_uses_all_eleven_dimensions_at_declared_depths():
    uniformity = load(UNIFORMITY_PATH)
    dimensions = [dimension["id"] for dimension in uniformity["dimensions"]]

    assert dimensions == list(EXPECTED_DEPTH)
    assert {
        dimension["id"]: dimension["completion_status"]
        for dimension in uniformity["dimensions"]
    } == EXPECTED_DEPTH
    assert uniformity["default_depth"] == EXPECTED_DEPTH
    assert uniformity["completion_rule"]["required_prefecture_count"] == 47
    assert uniformity["completion_rule"]["allow_partial_complete"] is False
    assert "個票単位" in uniformity["completion_rule"]["description"]


def test_all_prefectures_expand_to_complete_zero_gap_records():
    uniformity, records = expanded_records()

    assert uniformity["status"] == "complete"
    assert uniformity["overrides"] == {}
    assert [record["prefecture_code"] for record in records] == ALL_CODES
    assert len({record["prefecture_code"] for record in records}) == 47
    assert all(record["status"] == "complete" for record in records)
    assert all(record["current_depth"] == EXPECTED_DEPTH for record in records)
    assert all(record["gap_count"] == 0 for record in records)
    assert all(
        record["next_gate"] == "publication_verification" for record in records
    )


def test_uniform_summary_has_forty_seven_at_each_required_depth():
    uniformity, records = expanded_records()

    for dimension in uniformity["dimensions"]:
        dimension_id = dimension["id"]
        counts = Counter(
            record["current_depth"][dimension_id] for record in records
        )
        expected_status = EXPECTED_DEPTH[dimension_id]
        assert counts == {expected_status: 47}


def test_accountability_is_reviewed_not_falsely_linked():
    _, records = expanded_records()

    for record in records:
        assert record["current_depth"]["contracts"] == "reviewed"
        assert record["current_depth"]["assembly"] == "reviewed"
        assert record["current_depth"]["executive_manifesto"] == "reviewed"
        for dimension in (
            "annual_actuals",
            "budget",
            "settlement",
            "priority_projects",
            "audit",
        ):
            assert record["current_depth"][dimension] == "linked"


def test_uniformity_is_consistent_with_completed_control_files():
    uniformity = load(UNIFORMITY_PATH)
    queue = load(QUEUE_PATH)
    completion = load(COMPLETION_PATH)

    assert queue["status"] == "complete"
    assert queue["prefecture_order"] == ALL_CODES
    assert queue["counts"]["annual_evaluation_linked"] == 47
    assert queue["counts"]["contracts_indexed_or_better"] == 47
    assert completion["status"] == "complete"
    assert completion["nationwide_uniform_counts"]["uniform_depth_complete"] == 47
    assert all(gate["status"] == "passed" for gate in completion["gates"])
    assert uniformity["policy_achievement_assessment_status"] == "not_assessed"
    assert uniformity["ranking_eligibility"] == (
        "excluded_until_comparability_verified"
    )
