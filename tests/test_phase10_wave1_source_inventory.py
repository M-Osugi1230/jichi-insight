import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "data/catalog/phase10_wave1_source_inventory.json"
SCHEMA_PATH = ROOT / "schemas/phase10_wave1_source_inventory.schema.json"
QUEUE_PATH = ROOT / "data/catalog/phase10_execution_queue.json"
COMPLETION_PATH = ROOT / "data/catalog/phase10_completion.json"
NATIONWIDE_PATH = ROOT / "data/catalog/nationwide_source_inventory.json"

CATEGORIES = {
    "annual_evaluation",
    "budget",
    "project_evaluation",
    "contracts",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_phase10_wave1_source_inventory_matches_schema():
    validator = Draft202012Validator(
        load(SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(load(SOURCE_PATH))) == []


def test_miyagi_and_fukuoka_cover_all_vertical_source_categories():
    inventory = load(SOURCE_PATH)
    records = inventory["records"]

    assert inventory["prefecture_codes"] == ["04", "40"]
    assert set(inventory["categories"]) == CATEGORIES
    assert len({record["id"] for record in records}) == len(records)
    assert all(record["url"].startswith("https://www.pref.") for record in records)

    for code in inventory["prefecture_codes"]:
        assert {
            record["category"]
            for record in records
            if record["prefecture_code"] == code
        } == CATEGORIES


def test_source_inventory_summary_is_derived_from_records():
    inventory = load(SOURCE_PATH)
    records = inventory["records"]
    linkage_counts = Counter(record["linkage_status"] for record in records)

    assert inventory["summary"] == {
        "prefecture_count": 2,
        "source_count": len(records),
        "category_prefecture_counts": {
            category: len(
                {
                    record["prefecture_code"]
                    for record in records
                    if record["category"] == category
                }
            )
            for category in inventory["categories"]
        },
        "linked_existing_source_count": linkage_counts["linked_existing"],
        "candidate_linkage_source_count": linkage_counts["candidate_linkage"],
        "not_linked_source_count": linkage_counts["not_linked"],
    }
    assert inventory["policy_achievement_assessment_status"] == "not_assessed"


def test_wave1_queue_promotes_only_source_inventory_depth():
    queue = load(QUEUE_PATH)
    by_code = {
        record["prefecture_code"]: record for record in queue["wave1_records"]
    }

    assert by_code["04"]["current_depth"] == {
        "target_statements": "reviewed",
        "annual_evaluation": "linked",
        "budget": "indexed",
        "project_evaluation": "indexed",
        "contracts": "indexed",
    }
    assert by_code["40"]["current_depth"] == {
        "target_statements": "reviewed",
        "annual_evaluation": "indexed",
        "budget": "reviewed",
        "project_evaluation": "indexed",
        "contracts": "indexed",
    }
    assert queue["counts"]["project_evaluation_indexed_or_better"] == 2
    assert queue["counts"]["contracts_indexed_or_better"] == 2
    assert queue["policy_achievement_assessment_status"] == "not_assessed"


def test_nationwide_inventory_reflects_miyagi_and_fukuoka_source_indexing():
    inventory = load(NATIONWIDE_PATH)
    by_code = {record["prefecture_code"]: record for record in inventory["records"]}

    assert by_code["04"]["sources"]["annual_evaluation"] == "linked"
    assert by_code["04"]["sources"]["budget"] == "indexed"
    assert by_code["04"]["sources"]["project_evaluation"] == "indexed"

    assert by_code["40"]["sources"]["annual_evaluation"] == "indexed"
    assert by_code["40"]["sources"]["budget"] == "reviewed"
    assert by_code["40"]["sources"]["project_evaluation"] == "indexed"

    for category in inventory["categories"]:
        counts = Counter(
            record["sources"][category] for record in inventory["records"]
        )
        assert inventory["summary"][category] == {
            status: counts[status] for status in inventory["status_order"]
        }


def test_phase10_completion_tracks_new_source_inventory_depth():
    completion = load(COMPLETION_PATH)
    assert completion["counts"]["project_evaluation_indexed_or_better"] == 2
    assert completion["counts"]["contracts_indexed_or_better"] == 2

    gates = {gate["id"]: gate for gate in completion["gates"]}
    assert gates["wave1_money_and_project_spine"]["status"] == "in_progress"
    assert gates["contracts_and_accountability_linkage"]["status"] == "in_progress"
    assert all(
        "data/catalog/phase10_wave1_source_inventory.json"
        in gates[gate_id]["evidence_paths"]
        for gate_id in (
            "nationwide_vertical_source_inventory",
            "wave1_annual_actuals_linkage",
            "wave1_money_and_project_spine",
            "contracts_and_accountability_linkage",
        )
    )
