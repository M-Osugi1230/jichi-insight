from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = ROOT / "data/indexed/sagamihara-city/source_inventory.json"
SCHEMA_PATH = ROOT / "schemas/phase12_sagamihara_source_inventory.schema.json"
QUEUE_PATH = ROOT / "data/catalog/phase12_designated_city_execution_queue.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def assert_summary_matches_queue(queue: dict) -> None:
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


def test_sagamihara_inventory_matches_schema():
    validator = Draft202012Validator(
        load(SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(load(INVENTORY_PATH))) == []


def test_sagamihara_inventory_preserves_plan_and_progress_boundaries():
    inventory = load(INVENTORY_PATH)
    assert inventory["official_code"] == "141500"
    assert inventory["review_status"] == "indexed_not_reviewed"
    assert inventory["plan_period"] == {
        "start_fiscal_year": 2020,
        "end_fiscal_year": 2027,
        "current_plan_name": "未来へつなぐ さがみはらプラン～相模原市総合計画～",
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
    assert "fiscal 2020 through fiscal 2024" in progress["review_boundary"]
    assert "causal claims remain unreviewed" in progress["review_boundary"]


def test_sagamihara_queue_entry_is_complete_but_not_reviewed():
    queue = load(QUEUE_PATH)
    city = next(
        item for item in queue["execution_queue"] if item["official_code"] == "141500"
    )
    assert city == {
        "sequence": 7,
        "official_code": "141500",
        "name_ja": "相模原市",
        "prefecture_name_ja": "神奈川県",
        "status": "source_inventory_complete",
        "inventory_path": "data/indexed/sagamihara-city/source_inventory.json",
    }
    assert_summary_matches_queue(queue)
