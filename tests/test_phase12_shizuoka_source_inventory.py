from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = ROOT / "data/indexed/shizuoka-city/source_inventory.json"
SCHEMA_PATH = ROOT / "schemas/phase12_shizuoka_source_inventory.schema.json"
QUEUE_PATH = ROOT / "data/catalog/phase12_designated_city_execution_queue.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def assert_summary_matches_queue(queue: dict) -> None:
    statuses = [item["status"] for item in queue["execution_queue"]]
    assert queue["summary"]["source_inventory_complete_count"] == statuses.count(
        "source_inventory_complete"
    )
    assert queue["summary"]["source_inventory_partial_count"] == statuses.count(
        "source_inventory_partial"
    )
    assert queue["summary"]["pending_city_count"] == statuses.count(
        "pending_source_inventory"
    )


def test_shizuoka_current_plan_inventory_matches_complete_schema():
    validator = Draft202012Validator(
        load(SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(load(INVENTORY_PATH))) == []


def test_shizuoka_uses_fifth_plan_and_keeps_fourth_plan_legacy():
    inventory = load(INVENTORY_PATH)
    assert inventory["official_code"] == "221007"
    assert inventory["status"] == "source_inventory_complete"
    assert inventory["review_status"] == "indexed_not_reviewed"
    assert inventory["plan_period"] == {
        "start_fiscal_year": 2026,
        "end_fiscal_year": 2035,
        "current_plan_name": "第5次静岡市総合計画",
    }
    layers = {source["layer"] for source in inventory["sources"]}
    assert layers == {
        "comprehensive_plan",
        "implementation_plan_reference",
        "legacy_progress",
        "budget",
        "settlement",
    }
    legacy = next(
        source for source in inventory["sources"] if source["layer"] == "legacy_progress"
    )
    assert legacy["reporting_fiscal_year"] == 2024
    assert "must not be attributed" in legacy["review_boundary"]


def test_shizuoka_complete_inventory_keeps_unavailable_evidence_explicit():
    inventory = load(INVENTORY_PATH)
    unresolved = {item["layer"]: item for item in inventory["unresolved_layers"]}
    assert set(unresolved) == {"canonical_implementation_plan", "annual_progress"}
    assert unresolved["canonical_implementation_plan"]["status"] == (
        "canonical_current_document_not_yet_resolved"
    )
    assert unresolved["annual_progress"]["status"] == (
        "current_plan_result_not_yet_available"
    )
    assert "Phase 13" in unresolved["canonical_implementation_plan"]["boundary"]
    assert "not yet available" in unresolved["annual_progress"]["boundary"]
    assert "Source-inventory coverage is complete" in inventory["quality_boundary"]


def test_shizuoka_queue_entry_is_complete_without_inventing_missing_records():
    queue = load(QUEUE_PATH)
    city = next(
        item for item in queue["execution_queue"] if item["official_code"] == "221007"
    )
    assert city == {
        "sequence": 9,
        "official_code": "221007",
        "name_ja": "静岡市",
        "prefecture_name_ja": "静岡県",
        "status": "source_inventory_complete",
        "inventory_path": "data/indexed/shizuoka-city/source_inventory.json",
    }
    assert_summary_matches_queue(queue)
