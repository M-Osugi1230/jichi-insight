from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = ROOT / "data/indexed/kawasaki-city/source_inventory.json"
SCHEMA_PATH = ROOT / "schemas/phase12_kawasaki_source_inventory.schema.json"
QUEUE_PATH = ROOT / "data/catalog/phase12_designated_city_execution_queue.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_kawasaki_inventory_matches_schema():
    validator = Draft202012Validator(
        load(SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(load(INVENTORY_PATH))) == []


def test_kawasaki_inventory_preserves_current_and_prior_plan_boundary():
    inventory = load(INVENTORY_PATH)
    assert inventory["official_code"] == "141305"
    assert inventory["review_status"] == "indexed_not_reviewed"
    assert inventory["plan_period"] == {
        "start_fiscal_year": 2026,
        "end_fiscal_year": 2029,
        "current_plan_name": "川崎市総合計画 第4期実施計画",
    }
    assert {source["layer"] for source in inventory["sources"]} == {
        "comprehensive_plan",
        "implementation_plan",
        "annual_progress",
        "budget",
        "settlement",
    }
    progress = next(
        source for source in inventory["sources"] if source["layer"] == "annual_progress"
    )
    assert "prior 2022–2025 implementation plan" in progress["review_boundary"]
    assert "must not be used as an actual" in progress["review_boundary"]


def test_kawasaki_queue_entry_is_complete_but_not_reviewed():
    queue = load(QUEUE_PATH)
    city = next(
        item for item in queue["execution_queue"] if item["official_code"] == "141305"
    )
    assert city == {
        "sequence": 6,
        "official_code": "141305",
        "name_ja": "川崎市",
        "prefecture_name_ja": "神奈川県",
        "status": "source_inventory_complete",
        "inventory_path": "data/indexed/kawasaki-city/source_inventory.json",
    }
    assert queue["summary"]["source_inventory_complete_count"] == 5
    assert queue["summary"]["pending_city_count"] == 12
