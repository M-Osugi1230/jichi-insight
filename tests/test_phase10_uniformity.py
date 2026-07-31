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
ANCHOR_CODES = {"01", "13", "23", "27", "34", "37", "47"}
TOHOKU_CODES = {"02", "03", "05", "06", "07"}
KANTO_CODES = {"08", "09", "10", "11", "12", "14"}
FIVE_LAYER_CODES = ANCHOR_CODES | TOHOKU_CODES | KANTO_CODES
STATUSES = ("not_indexed", "indexed", "reviewed", "linked")
STATUS_RANK = {status: index for index, status in enumerate(STATUSES)}


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


def test_uniformity_uses_all_eleven_dimensions_once():
    uniformity = load(UNIFORMITY_PATH)
    dimensions = [dimension["id"] for dimension in uniformity["dimensions"]]
    assert dimensions == [
        "target_statements",
        "evidence_packets",
        "annual_actuals",
        "budget",
        "settlement",
        "priority_projects",
        "contracts",
        "assembly",
        "audit",
        "executive_manifesto",
        "publication",
    ]
    assert set(uniformity["default_depth"]) == set(dimensions)
    assert uniformity["completion_rule"] == {
        "description": uniformity["completion_rule"]["description"],
        "required_prefecture_count": 47,
        "allow_partial_complete": False,
    }


def test_compact_manifest_expands_to_all_prefectures():
    uniformity, records = expanded_records()
    assert [record["prefecture_code"] for record in records] == ALL_CODES
    unique_codes = {record["prefecture_code"] for record in records}
    assert len(records) == len(unique_codes) == 47
    assert set(uniformity["overrides"]) <= set(ALL_CODES)
    assert all(record["gap_count"] >= 0 for record in records)


def test_baseline_is_conservative_and_matches_verified_work():
    _, records = expanded_records()
    by_code = {record["prefecture_code"]: record for record in records}

    assert by_code["04"]["current_depth"] == {
        "target_statements": "reviewed",
        "evidence_packets": "reviewed",
        "annual_actuals": "linked",
        "budget": "reviewed",
        "settlement": "indexed",
        "priority_projects": "reviewed",
        "contracts": "indexed",
        "assembly": "indexed",
        "audit": "reviewed",
        "executive_manifesto": "not_indexed",
        "publication": "reviewed",
    }
    assert by_code["40"]["current_depth"] == {
        "target_statements": "reviewed",
        "evidence_packets": "reviewed",
        "annual_actuals": "reviewed",
        "budget": "reviewed",
        "settlement": "reviewed",
        "priority_projects": "reviewed",
        "contracts": "indexed",
        "assembly": "indexed",
        "audit": "reviewed",
        "executive_manifesto": "indexed",
        "publication": "reviewed",
    }
    for code in FIVE_LAYER_CODES:
        assert by_code[code]["status"] == "linkage_in_progress"
        for dimension in (
            "annual_actuals",
            "budget",
            "settlement",
            "priority_projects",
            "audit",
        ):
            assert by_code[code]["current_depth"][dimension] == "reviewed"
        assert by_code[code]["current_depth"]["contracts"] == "not_indexed"
        assert by_code[code]["current_depth"]["assembly"] == "not_indexed"
        assert by_code[code]["current_depth"]["executive_manifesto"] == (
            "not_indexed"
        )

    assert all(
        record["current_depth"]["target_statements"] == "reviewed"
        and record["current_depth"]["evidence_packets"] == "reviewed"
        and record["current_depth"]["publication"] == "reviewed"
        for record in records
    )
    assert all(record["gap_count"] > 0 for record in records)


def test_uniform_summary_matches_expected_baseline():
    uniformity, records = expanded_records()
    summary = {}
    for dimension in uniformity["dimensions"]:
        dimension_id = dimension["id"]
        counts = Counter(
            record["current_depth"][dimension_id] for record in records
        )
        summary[dimension_id] = {status: counts[status] for status in STATUSES}

    assert summary["annual_actuals"] == {
        "not_indexed": 27,
        "indexed": 0,
        "reviewed": 19,
        "linked": 1,
    }
    assert summary["budget"] == {
        "not_indexed": 27,
        "indexed": 0,
        "reviewed": 20,
        "linked": 0,
    }
    assert summary["settlement"] == {
        "not_indexed": 27,
        "indexed": 1,
        "reviewed": 19,
        "linked": 0,
    }
    assert summary["priority_projects"] == {
        "not_indexed": 27,
        "indexed": 0,
        "reviewed": 20,
        "linked": 0,
    }
    assert summary["assembly"] == {
        "not_indexed": 45,
        "indexed": 2,
        "reviewed": 0,
        "linked": 0,
    }
    assert summary["audit"] == {
        "not_indexed": 27,
        "indexed": 0,
        "reviewed": 20,
        "linked": 0,
    }


def test_uniformity_is_consistent_with_existing_phase10_control_files():
    uniformity = load(UNIFORMITY_PATH)
    queue = load(QUEUE_PATH)
    completion = load(COMPLETION_PATH)

    assert queue["prefecture_order"] == ALL_CODES
    assert queue["counts"]["target_statements_reviewed"] == 47
    assert uniformity["policy_achievement_assessment_status"] == "not_assessed"
    assert uniformity["ranking_eligibility"] == "excluded_until_comparability_verified"
    assert completion["status"] == "in_progress"
    assert "data/catalog/phase10_uniformity.json" in {
        path
        for gate in completion["gates"]
        for path in gate["evidence_paths"]
    }
