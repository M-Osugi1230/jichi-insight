from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = ROOT / "data/indexed/osaka-city/source_inventory.json"
SCHEMA_PATH = ROOT / "schemas/phase12_osaka_source_inventory.schema.json"
QUEUE_PATH = ROOT / "data/catalog/phase12_designated_city_execution_queue.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_osaka_inventory_matches_schema():
    validator = Draft202012Validator(load(SCHEMA_PATH), format_checker=FormatChecker())
    assert list(validator.iter_errors(load(INVENTORY_PATH))) == []


def test_osaka_inventory_preserves_decentralized_operating_model():
    inventory = load(INVENTORY_PATH)
    assert inventory["official_code"] == "271004"
    assert inventory["review_status"] == "indexed_not_reviewed"
    assert inventory["plan_structure"] == {
        "current_plan_name": "大阪市基本構想",
        "period_status": "no_fixed_end_verified",
        "implementation_model": "annual_city_policy_plus_ward_and_bureau_operating_policies",
    }
    by_layer = {source["layer"]: source for source in inventory["sources"]}
    assert set(by_layer) == {
        "comprehensive_plan",
        "implementation_plan",
        "annual_progress",
        "budget",
        "settlement",
    }
    assert (
        "not a multi-year implementation plan"
        in by_layer["implementation_plan"]["review_boundary"]
    )
    assert (
        "decentralized self-evaluations"
        in by_layer["annual_progress"]["review_boundary"]
    )
    assert "attached resolution" in by_layer["budget"]["review_boundary"]


def test_osaka_queue_entry_is_complete_but_not_reviewed():
    queue = load(QUEUE_PATH)
    city = next(
        item for item in queue["execution_queue"] if item["official_code"] == "271004"
    )
    assert city == {
        "sequence": 13,
        "official_code": "271004",
        "name_ja": "大阪市",
        "prefecture_name_ja": "大阪府",
        "status": "source_inventory_complete",
        "inventory_path": "data/indexed/osaka-city/source_inventory.json",
    }
    complete_count = sum(
        item["status"] == "source_inventory_complete"
        for item in queue["execution_queue"]
    )
    partial_count = sum(
        item["status"] == "source_inventory_partial"
        for item in queue["execution_queue"]
    )
    pending_count = sum(
        item["status"] == "pending_source_inventory"
        for item in queue["execution_queue"]
    )
    assert queue["summary"]["source_inventory_complete_count"] == complete_count
    assert queue["summary"]["source_inventory_partial_count"] == partial_count
    assert queue["summary"]["pending_city_count"] == pending_count
