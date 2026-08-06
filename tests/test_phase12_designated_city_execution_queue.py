from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "data/catalog/phase12_designated_city_execution_queue.json"
SCHEMA_PATH = ROOT / "schemas/phase12_designated_city_execution_queue.schema.json"
SAPPORO_INVENTORY_PATH = ROOT / "data/indexed/sapporo-city/source_inventory.json"
SAPPORO_SCHEMA_PATH = ROOT / "schemas/phase12_sapporo_source_inventory.schema.json"
SENDAI_INVENTORY_PATH = ROOT / "data/indexed/sendai-city/source_inventory.json"
SENDAI_SCHEMA_PATH = ROOT / "schemas/phase12_sendai_source_inventory.schema.json"
CHIBA_INVENTORY_PATH = ROOT / "data/indexed/chiba-city/source_inventory.json"
CHIBA_SCHEMA_PATH = ROOT / "schemas/phase12_chiba_source_inventory.schema.json"
YOKOHAMA_INVENTORY_PATH = ROOT / "data/indexed/yokohama-city/source_inventory.json"
YOKOHAMA_SCHEMA_PATH = ROOT / "schemas/phase12_yokohama_source_inventory.schema.json"

EXPECTED_CODES = [
    "011002",
    "041009",
    "111007",
    "121002",
    "141003",
    "141305",
    "141500",
    "151009",
    "221007",
    "221309",
    "231002",
    "261009",
    "271004",
    "271403",
    "281000",
    "331007",
    "341002",
    "401005",
    "401307",
    "431001",
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_queue_matches_schema():
    validator = Draft202012Validator(
        load(SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(load(QUEUE_PATH))) == []


def test_all_twenty_designated_cities_are_covered_once():
    queue = load(QUEUE_PATH)
    references = queue["reference_implementations"]
    pending = queue["execution_queue"]
    codes = [item["official_code"] for item in references + pending]
    assert len(codes) == 20
    assert len(set(codes)) == 20
    assert sorted(codes) == sorted(EXPECTED_CODES)
    assert [item["sequence"] for item in pending] == list(range(1, 19))


def test_reference_implementations_resolve_to_reviewed_municipalities():
    queue = load(QUEUE_PATH)
    for reference in queue["reference_implementations"]:
        municipality_path = ROOT / reference["municipality_path"]
        reviewed_data_path = ROOT / reference["reviewed_data_path"]
        assert municipality_path.exists()
        assert reviewed_data_path.is_dir()
        municipality = load(municipality_path)
        assert municipality["official_code"] == reference["official_code"]
        assert municipality["name_ja"] == reference["name_ja"]
        assert municipality["municipality_type"] == "designated_city"
        assert municipality["data_status"] == "reviewed"


def assert_indexed_inventory(path: Path, schema_path: Path, code: str, host: str):
    inventory = load(path)
    validator = Draft202012Validator(
        load(schema_path), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(inventory)) == []
    assert inventory["review_status"] == "indexed_not_reviewed"
    assert inventory["official_code"] == code
    assert len(inventory["sources"]) == 5
    assert all(
        source["official_url"].startswith(host) for source in inventory["sources"]
    )


def test_sapporo_inventory_is_valid_but_not_promoted_to_reviewed():
    assert_indexed_inventory(
        SAPPORO_INVENTORY_PATH,
        SAPPORO_SCHEMA_PATH,
        "011002",
        "https://www.city.sapporo.jp/",
    )


def test_sendai_inventory_is_valid_but_not_promoted_to_reviewed():
    assert_indexed_inventory(
        SENDAI_INVENTORY_PATH,
        SENDAI_SCHEMA_PATH,
        "041009",
        "https://www.city.sendai.jp/",
    )


def test_chiba_inventory_is_valid_but_not_promoted_to_reviewed():
    assert_indexed_inventory(
        CHIBA_INVENTORY_PATH,
        CHIBA_SCHEMA_PATH,
        "121002",
        "https://www.city.chiba.jp/",
    )
    inventory = load(CHIBA_INVENTORY_PATH)
    assert {source["layer"] for source in inventory["sources"]} == {
        "comprehensive_plan",
        "implementation_plan",
        "annual_progress",
        "budget",
        "settlement",
    }
    assert inventory["plan_period"] == {
        "start_fiscal_year": 2023,
        "end_fiscal_year": 2032,
        "current_plan_name": "千葉市基本計画",
    }


def test_yokohama_inventory_preserves_current_and_prior_plan_boundary():
    assert_indexed_inventory(
        YOKOHAMA_INVENTORY_PATH,
        YOKOHAMA_SCHEMA_PATH,
        "141003",
        "https://www.city.yokohama.lg.jp/",
    )
    inventory = load(YOKOHAMA_INVENTORY_PATH)
    assert {source["layer"] for source in inventory["sources"]} == {
        "comprehensive_plan",
        "implementation_plan",
        "annual_progress",
        "budget",
        "settlement",
    }
    assert inventory["plan_period"] == {
        "start_fiscal_year": 2026,
        "end_fiscal_year": 2029,
        "current_plan_name": "横浜市中期計画2026～2029",
    }
    progress = next(
        source for source in inventory["sources"] if source["layer"] == "annual_progress"
    )
    assert "prior 2022–2025 plan" in progress["review_boundary"]
    assert "must not be treated as actuals" in progress["review_boundary"]


def test_summary_is_derived_from_queue_contents():
    queue = load(QUEUE_PATH)
    references = queue["reference_implementations"]
    cities = queue["execution_queue"]
    active = next(
        item
        for item in cities
        if item["status"]
        in {"source_inventory_partial", "pending_source_inventory"}
    )
    assert queue["summary"] == {
        "designated_city_count": len(references) + len(cities),
        "reference_implementation_count": len(references),
        "queued_city_count": len(cities),
        "reviewed_city_count": 2,
        "source_inventory_complete_count": sum(
            item["status"] == "source_inventory_complete" for item in cities
        ),
        "source_inventory_partial_count": sum(
            item["status"] == "source_inventory_partial" for item in cities
        ),
        "pending_city_count": sum(
            item["status"] == "pending_source_inventory" for item in cities
        ),
        "next_official_code": active["official_code"],
    }


def test_quality_gate_blocks_unsupported_comparison_and_assessment():
    rules = " ".join(load(QUEUE_PATH)["quality_gate"])
    assert "Do not infer policy achievement" in rules
    assert "Do not rank cities" in rules
    assert "automatically extracted material" in rules
    assert "denominator" in rules
    assert "supplementary budget" in rules
