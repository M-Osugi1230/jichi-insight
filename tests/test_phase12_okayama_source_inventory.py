"""Regression coverage for the Okayama Phase 12 source inventory."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = ROOT / "data/indexed/okayama-city/source_inventory.json"
SCHEMA_PATH = ROOT / "schemas/phase12_okayama_source_inventory.schema.json"
QUEUE_PATH = ROOT / "data/catalog/phase12_designated_city_execution_queue.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_okayama_inventory_matches_schema():
    validator = Draft202012Validator(load(SCHEMA_PATH), format_checker=FormatChecker())
    assert list(validator.iter_errors(load(INVENTORY_PATH))) == []


def test_okayama_current_plan_has_pdca_without_invented_result():
    inventory = load(INVENTORY_PATH)
    assert inventory["official_code"] == "331007"
    assert inventory["status"] == "source_inventory_partial"
    assert inventory["plan_period"] == {
        "start_fiscal_year": 2026,
        "end_fiscal_year": 2035,
        "current_plan_name": "岡山市第七次総合計画",
    }
    layers = {source["layer"] for source in inventory["sources"]}
    assert layers == {
        "comprehensive_plan",
        "implementation_plan",
        "progress_governance",
        "budget",
        "settlement",
    }
    assert inventory["unresolved_layers"][0]["layer"] == "annual_progress"
    governance = next(
        source
        for source in inventory["sources"]
        if source["layer"] == "progress_governance"
    )
    assert (
        "does not infer a completed current-plan annual result"
        in governance["review_boundary"]
    )


def test_okayama_queue_entry_is_partial_and_counts_are_consistent():
    queue = load(QUEUE_PATH)
    city = next(
        item for item in queue["execution_queue"] if item["official_code"] == "331007"
    )
    assert city == {
        "sequence": 16,
        "official_code": "331007",
        "name_ja": "岡山市",
        "prefecture_name_ja": "岡山県",
        "status": "source_inventory_partial",
        "inventory_path": "data/indexed/okayama-city/source_inventory.json",
    }
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
