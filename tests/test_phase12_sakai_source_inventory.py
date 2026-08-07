"""Regression coverage for the Sakai Phase 12 source inventory."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = ROOT / "data/indexed/sakai-city/source_inventory.json"
SCHEMA_PATH = ROOT / "schemas/phase12_sakai_source_inventory.schema.json"
QUEUE_PATH = ROOT / "data/catalog/phase12_designated_city_execution_queue.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sakai_inventory_matches_schema():
    validator = Draft202012Validator(load(SCHEMA_PATH), format_checker=FormatChecker())
    assert list(validator.iter_errors(load(INVENTORY_PATH))) == []


def test_sakai_preserves_current_and_legacy_plan_boundaries():
    inventory = load(INVENTORY_PATH)
    assert inventory["official_code"] == "271403"
    assert inventory["status"] == "source_inventory_partial"
    assert inventory["review_status"] == "indexed_not_reviewed"
    assert inventory["plan_period"] == {
        "start_fiscal_year": 2026,
        "end_fiscal_year": 2030,
        "current_plan_name": "堺市基本計画2030",
    }
    layers = {source["layer"] for source in inventory["sources"]}
    assert layers == {
        "comprehensive_plan",
        "kpi_reference",
        "legacy_progress",
        "budget",
        "settlement",
    }
    unresolved = {item["layer"] for item in inventory["unresolved_layers"]}
    assert unresolved == {"implementation_plan", "annual_progress"}
    legacy = next(source for source in inventory["sources"] if source["layer"] == "legacy_progress")
    assert "must not be attributed" in legacy["review_boundary"]


def test_sakai_queue_entry_is_partial_and_counts_are_consistent():
    queue = load(QUEUE_PATH)
    city = next(item for item in queue["execution_queue"] if item["official_code"] == "271403")
    assert city == {
        "sequence": 14,
        "official_code": "271403",
        "name_ja": "堺市",
        "prefecture_name_ja": "大阪府",
        "status": "source_inventory_partial",
        "inventory_path": "data/indexed/sakai-city/source_inventory.json",
    }
    statuses = [item["status"] for item in queue["execution_queue"]]
    assert queue["summary"]["source_inventory_complete_count"] == statuses.count("source_inventory_complete")
    assert queue["summary"]["source_inventory_partial_count"] == statuses.count("source_inventory_partial")
    assert queue["summary"]["pending_city_count"] == statuses.count("pending_source_inventory")
