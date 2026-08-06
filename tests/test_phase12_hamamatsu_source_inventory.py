from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = ROOT / "data/indexed/hamamatsu-city/source_inventory.json"
SCHEMA_PATH = ROOT / "schemas/phase12_hamamatsu_source_inventory.schema.json"
QUEUE_PATH = ROOT / "data/catalog/phase12_designated_city_execution_queue.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_hamamatsu_inventory_matches_schema():
    validator = Draft202012Validator(
        load(SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(load(INVENTORY_PATH))) == []


def test_hamamatsu_inventory_has_all_five_layers_but_is_not_reviewed():
    inventory = load(INVENTORY_PATH)
    assert inventory["official_code"] == "221309"
    assert inventory["review_status"] == "indexed_not_reviewed"
    assert inventory["plan_period"] == {
        "start_fiscal_year": 2025,
        "end_fiscal_year": 2034,
        "current_plan_name": "浜松市総合計画 第2期基本計画",
    }
    assert {source["layer"] for source in inventory["sources"]} == {
        "comprehensive_plan",
        "implementation_plan",
        "annual_progress",
        "budget",
        "settlement",
    }


def test_hamamatsu_queue_entry_is_complete_but_not_reviewed():
    queue = load(QUEUE_PATH)
    city = next(
        item for item in queue["execution_queue"] if item["official_code"] == "221309"
    )
    assert city == {
        "sequence": 10,
        "official_code": "221309",
        "name_ja": "浜松市",
        "prefecture_name_ja": "静岡県",
        "status": "source_inventory_complete",
        "inventory_path": "data/indexed/hamamatsu-city/source_inventory.json",
    }
    assert queue["summary"]["source_inventory_complete_count"] == 8
    assert queue["summary"]["source_inventory_partial_count"] == 2
    assert queue["summary"]["pending_city_count"] == 8
