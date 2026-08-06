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


def test_shizuoka_partial_inventory_matches_schema():
    validator = Draft202012Validator(
        load(SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(load(INVENTORY_PATH))) == []


def test_shizuoka_preserves_unresolved_citywide_progress_boundary():
    inventory = load(INVENTORY_PATH)
    assert inventory["official_code"] == "221007"
    assert inventory["status"] == "source_inventory_partial"
    assert inventory["review_status"] == "indexed_not_reviewed"
    assert inventory["plan_period"] == {
        "start_fiscal_year": 2023,
        "end_fiscal_year": 2030,
        "current_plan_name": "第4次静岡市総合計画",
    }
    assert {source["layer"] for source in inventory["sources"]} == {
        "comprehensive_plan",
        "implementation_plan",
        "budget",
        "settlement",
    }
    assert inventory["unresolved_layers"] == [
        {
            "layer": "annual_progress",
            "status": "official_citywide_progress_landing_not_yet_resolved",
            "boundary": inventory["unresolved_layers"][0]["boundary"],
        }
    ]
    assert "Sector-plan progress must not be substituted" in inventory[
        "unresolved_layers"
    ][0]["boundary"]


def test_shizuoka_queue_entry_stays_partial_until_progress_is_resolved():
    queue = load(QUEUE_PATH)
    city = next(
        item for item in queue["execution_queue"] if item["official_code"] == "221007"
    )
    assert city == {
        "sequence": 9,
        "official_code": "221007",
        "name_ja": "静岡市",
        "prefecture_name_ja": "静岡県",
        "status": "source_inventory_partial",
        "inventory_path": "data/indexed/shizuoka-city/source_inventory.json",
    }
    assert queue["summary"]["source_inventory_complete_count"] == 7
    assert queue["summary"]["source_inventory_partial_count"] == 2
    assert queue["summary"]["pending_city_count"] == 9
