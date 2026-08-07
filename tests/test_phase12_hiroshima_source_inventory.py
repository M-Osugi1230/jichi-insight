"""Regression coverage for the Hiroshima Phase 12 source inventory."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = ROOT / "data/indexed/hiroshima-city/source_inventory.json"
SCHEMA_PATH = ROOT / "schemas/phase12_hiroshima_source_inventory.schema.json"
QUEUE_PATH = ROOT / "data/catalog/phase12_designated_city_execution_queue.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_hiroshima_inventory_matches_schema():
    validator = Draft202012Validator(load(SCHEMA_PATH), format_checker=FormatChecker())
    assert list(validator.iter_errors(load(INVENTORY_PATH))) == []


def test_hiroshima_keeps_current_cycle_progress_unresolved():
    inventory = load(INVENTORY_PATH)
    assert inventory["official_code"] == "341002"
    assert inventory["status"] == "source_inventory_partial"
    assert inventory["unresolved_layers"][0]["layer"] == "annual_progress"
    implementation = next(source for source in inventory["sources"] if source["layer"] == "implementation_plan")
    assert implementation["effective_period"] == "2025年度～2030年度"
    governance = next(source for source in inventory["sources"] if source["layer"] == "progress_governance")
    assert "not inferred" in governance["review_boundary"]


def test_hiroshima_queue_entry_is_partial_and_counts_are_consistent():
    queue = load(QUEUE_PATH)
    city = next(item for item in queue["execution_queue"] if item["official_code"] == "341002")
    assert city["status"] == "source_inventory_partial"
    assert city["inventory_path"] == "data/indexed/hiroshima-city/source_inventory.json"
    statuses = [item["status"] for item in queue["execution_queue"]]
    assert queue["summary"]["source_inventory_complete_count"] == statuses.count("source_inventory_complete")
    assert queue["summary"]["source_inventory_partial_count"] == statuses.count("source_inventory_partial")
    assert queue["summary"]["pending_city_count"] == statuses.count("pending_source_inventory")
