from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = ROOT / "data/indexed/nagoya-city/source_inventory.json"
SCHEMA_PATH = ROOT / "schemas/phase12_nagoya_source_inventory.schema.json"
QUEUE_PATH = ROOT / "data/catalog/phase12_designated_city_execution_queue.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_nagoya_inventory_matches_schema():
    validator = Draft202012Validator(load(SCHEMA_PATH), format_checker=FormatChecker())
    assert list(validator.iter_errors(load(INVENTORY_PATH))) == []


def test_nagoya_inventory_preserves_embedded_implementation_boundary():
    inventory = load(INVENTORY_PATH)
    assert inventory["official_code"] == "231002"
    assert inventory["review_status"] == "indexed_not_reviewed"
    assert inventory["plan_period"] == {
        "start_fiscal_year": 2024,
        "end_fiscal_year": 2028,
        "current_plan_name": "名古屋市総合計画2028",
    }
    by_layer = {source["layer"]: source for source in inventory["sources"]}
    assert set(by_layer) == {
        "comprehensive_plan",
        "implementation_plan",
        "annual_progress",
        "budget",
        "settlement",
    }
    assert "42 measures and 506 listed projects" in by_layer["implementation_plan"]["review_boundary"]
    assert "135 plan indicators" in by_layer["annual_progress"]["review_boundary"]
    assert "council amendment" in by_layer["budget"]["review_boundary"]


def test_nagoya_queue_entry_is_complete_but_not_reviewed():
    queue = load(QUEUE_PATH)
    city = next(item for item in queue["execution_queue"] if item["official_code"] == "231002")
    assert city == {
        "sequence": 11,
        "official_code": "231002",
        "name_ja": "名古屋市",
        "prefecture_name_ja": "愛知県",
        "status": "source_inventory_complete",
        "inventory_path": "data/indexed/nagoya-city/source_inventory.json",
    }
    complete_count = sum(
        item["status"] == "source_inventory_complete" for item in queue["execution_queue"]
    )
    partial_count = sum(
        item["status"] == "source_inventory_partial" for item in queue["execution_queue"]
    )
    pending_count = sum(
        item["status"] == "pending_source_inventory" for item in queue["execution_queue"]
    )
    assert queue["summary"]["source_inventory_complete_count"] == complete_count
    assert queue["summary"]["source_inventory_partial_count"] == partial_count
    assert queue["summary"]["pending_city_count"] == pending_count
