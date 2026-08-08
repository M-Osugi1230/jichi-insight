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


def test_saitama_complete_inventory_validates():
    validator = Draft202012Validator(
        load(INVENTORY_SCHEMA_PATH), format_checker=FormatChecker()
    )
    inventory = load(INVENTORY_PATH)
    assert list(validator.iter_errors(inventory)) == []
    assert inventory["official_code"] == "111007"
    assert inventory["status"] == "source_inventory_complete"
    assert inventory["review_status"] == "indexed_not_reviewed"


def test_saitama_has_all_five_official_layers():
    inventory = load(INVENTORY_PATH)
    assert {source["layer"] for source in inventory["sources"]} == {
        "comprehensive_plan",
        "implementation_plan",
        "annual_progress",
        "budget",
        "settlement",
    }
    assert all(
        source["official_url"].startswith("https://www.city.saitama.lg.jp/")
        for source in inventory["sources"]
    )


def test_saitama_preserves_version_and_fiscal_boundaries():
    inventory = load(INVENTORY_PATH)
    implementation = next(
        source
        for source in inventory["sources"]
        if source["layer"] == "implementation_plan"
    )
    progress = next(
        source
        for source in inventory["sources"]
        if source["layer"] == "annual_progress"
    )
    budget = next(
        source for source in inventory["sources"] if source["layer"] == "budget"
    )
    settlement = next(
        source
        for source in inventory["sources"]
        if source["layer"] == "settlement"
    )
    assert implementation["effective_period"] == "2026年度～2030年度"
    assert progress["reporting_fiscal_year"] == 2024
    assert "must not be relabeled" in progress["review_boundary"]
    assert budget["fiscal_year"] == 2026
    assert "enacted" in budget["review_boundary"]
    assert settlement["fiscal_year"] == 2024


def test_queue_advances_after_saitama_completion():
    queue_validator = Draft202012Validator(
        load(QUEUE_SCHEMA_PATH), format_checker=FormatChecker()
    )
    queue = load(QUEUE_PATH)
    assert list(queue_validator.iter_errors(queue)) == []
    cities = queue["execution_queue"]
    city = next(item for item in cities if item["official_code"] == "111007")
    assert city["status"] == "source_inventory_complete"
    assert city["inventory_path"] == (
        "data/indexed/saitama-city/source_inventory.json"
    )
    assert queue["summary"]["source_inventory_complete_count"] == sum(
        item["status"] == "source_inventory_complete" for item in cities
    )
    assert queue["summary"]["source_inventory_partial_count"] == sum(
        item["status"] == "source_inventory_partial" for item in cities
    )
    assert queue["summary"]["pending_city_count"] == 0
    assert queue["summary"]["next_official_code"] == "221007"
