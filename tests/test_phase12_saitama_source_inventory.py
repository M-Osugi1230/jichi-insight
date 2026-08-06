from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = ROOT / "data/indexed/saitama-city/source_inventory.json"
INVENTORY_SCHEMA_PATH = ROOT / "schemas/phase12_saitama_source_inventory.schema.json"
QUEUE_PATH = ROOT / "data/catalog/phase12_designated_city_execution_queue.json"
QUEUE_SCHEMA_PATH = ROOT / "schemas/phase12_designated_city_execution_queue.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_saitama_partial_inventory_validates():
    validator = Draft202012Validator(
        load(INVENTORY_SCHEMA_PATH), format_checker=FormatChecker()
    )
    inventory = load(INVENTORY_PATH)
    assert list(validator.iter_errors(inventory)) == []
    assert inventory["official_code"] == "111007"
    assert inventory["status"] == "source_inventory_partial"
    assert inventory["review_status"] == "indexed_not_reviewed"


def test_only_verified_official_source_is_recorded():
    inventory = load(INVENTORY_PATH)
    assert len(inventory["verified_sources"]) == 1
    source = inventory["verified_sources"][0]
    assert source["layer"] == "comprehensive_plan"
    assert source["official_url"].startswith(
        "https://gakushu.city.saitama.jp/"
    )
    assert source["status"] == "official_overview_verified"


def test_all_unresolved_layers_remain_explicit():
    inventory = load(INVENTORY_PATH)
    assert {item["layer"] for item in inventory["unresolved_layers"]} == {
        "canonical_comprehensive_plan",
        "implementation_plan",
        "annual_progress",
        "budget",
        "settlement",
    }
    assert "does not invent unresolved city URLs" in inventory["quality_boundary"]
    assert "only after all five layers" in inventory["next_action"]


def test_queue_keeps_saitama_as_next_until_complete():
    queue_validator = Draft202012Validator(
        load(QUEUE_SCHEMA_PATH), format_checker=FormatChecker()
    )
    queue = load(QUEUE_PATH)
    assert list(queue_validator.iter_errors(queue)) == []
    city = next(
        item for item in queue["execution_queue"]
        if item["official_code"] == "111007"
    )
    assert city["status"] == "source_inventory_partial"
    assert city["inventory_path"] == (
        "data/indexed/saitama-city/source_inventory.json"
    )
    assert queue["summary"]["source_inventory_complete_count"] == 2
    assert queue["summary"]["source_inventory_partial_count"] == 1
    assert queue["summary"]["pending_city_count"] == 15
    assert queue["summary"]["next_official_code"] == "111007"
