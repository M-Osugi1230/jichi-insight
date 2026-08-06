from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = ROOT / "data/indexed/niigata-city/source_inventory.json"
SCHEMA_PATH = ROOT / "schemas/phase12_niigata_source_inventory.schema.json"
QUEUE_PATH = ROOT / "data/catalog/phase12_designated_city_execution_queue.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_niigata_inventory_matches_schema():
    validator = Draft202012Validator(
        load(SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(load(INVENTORY_PATH))) == []


def test_niigata_inventory_preserves_plan_revision_and_evidence_boundaries():
    inventory = load(INVENTORY_PATH)
    assert inventory["official_code"] == "151009"
    assert inventory["review_status"] == "indexed_not_reviewed"
    assert inventory["plan_period"] == {
        "start_fiscal_year": 2023,
        "end_fiscal_year": 2030,
        "current_plan_name": "新潟市総合計画2030",
    }
    assert {source["layer"] for source in inventory["sources"]} == {
        "comprehensive_plan",
        "implementation_plan",
        "annual_progress",
        "budget",
        "settlement",
    }
    implementation = next(
        source
        for source in inventory["sources"]
        if source["layer"] == "implementation_plan"
    )
    assert "March 2026 revision" in implementation["review_boundary"]
    progress = next(
        source for source in inventory["sources"] if source["layer"] == "annual_progress"
    )
    assert "separate evidence types" in progress["review_boundary"]


def test_niigata_queue_entry_is_complete_but_not_reviewed():
    queue = load(QUEUE_PATH)
    city = next(
        item for item in queue["execution_queue"] if item["official_code"] == "151009"
    )
    assert city == {
        "sequence": 8,
        "official_code": "151009",
        "name_ja": "新潟市",
        "prefecture_name_ja": "新潟県",
        "status": "source_inventory_complete",
        "inventory_path": "data/indexed/niigata-city/source_inventory.json",
    }
    assert queue["summary"]["source_inventory_complete_count"] == 7
    assert queue["summary"]["pending_city_count"] == 10
