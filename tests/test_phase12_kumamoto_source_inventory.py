"""Regression coverage for the Kumamoto Phase 12 source inventory."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = ROOT / "data/indexed/kumamoto-city/source_inventory.json"
SCHEMA_PATH = ROOT / "schemas/phase12_kumamoto_source_inventory.schema.json"
QUEUE_PATH = ROOT / "data/catalog/phase12_designated_city_execution_queue.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_kumamoto_inventory_matches_schema():
    validator = Draft202012Validator(load(SCHEMA_PATH), format_checker=FormatChecker())
    assert list(validator.iter_errors(load(INVENTORY_PATH))) == []


def test_kumamoto_preserves_proposal_and_enacted_budget_lineage():
    inventory = load(INVENTORY_PATH)
    assert inventory["official_code"] == "431001"
    assert inventory["status"] == "source_inventory_complete"
    assert inventory["plan_period"] == {
        "start_fiscal_year": 2024,
        "end_fiscal_year": 2031,
        "current_plan_name": "熊本市第8次総合計画",
    }
    assert inventory["unresolved_layers"] == []
    by_layer = {source["layer"]: source for source in inventory["sources"]}
    assert set(by_layer) == {
        "comprehensive_plan",
        "implementation_plan",
        "annual_progress",
        "budget_proposal",
        "budget",
        "settlement",
    }
    assert "proposal-stage evidence" in by_layer["budget_proposal"]["review_boundary"]
    assert "approved as originally proposed" in by_layer["budget"]["review_boundary"]
    assert "March 24, 2026" in by_layer["budget"]["review_boundary"]


def test_kumamoto_queue_entry_is_complete_and_counts_are_consistent():
    queue = load(QUEUE_PATH)
    city = next(
        item for item in queue["execution_queue"] if item["official_code"] == "431001"
    )
    assert city["status"] == "source_inventory_complete"
    assert city["inventory_path"] == "data/indexed/kumamoto-city/source_inventory.json"
    statuses = [item["status"] for item in queue["execution_queue"]]
    assert queue["summary"]["source_inventory_complete_count"] == statuses.count(
        "source_inventory_complete"
    )
    assert queue["summary"]["source_inventory_partial_count"] == statuses.count(
        "source_inventory_partial"
    )
    assert queue["summary"]["pending_city_count"] == 0
    assert "pending_source_inventory" not in statuses
