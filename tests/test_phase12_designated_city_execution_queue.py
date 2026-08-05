from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "data/catalog/phase12_designated_city_execution_queue.json"
SCHEMA_PATH = ROOT / "schemas/phase12_designated_city_execution_queue.schema.json"

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


def test_summary_is_derived_from_queue_contents():
    queue = load(QUEUE_PATH)
    references = queue["reference_implementations"]
    pending = queue["execution_queue"]
    summary = queue["summary"]
    assert summary == {
        "designated_city_count": len(references) + len(pending),
        "reference_implementation_count": len(references),
        "queued_city_count": len(pending),
        "reviewed_city_count": sum(
            item["status"] == "reviewed_reference" for item in references
        ),
        "pending_city_count": sum(
            item["status"] == "pending_source_inventory" for item in pending
        ),
        "next_official_code": pending[0]["official_code"],
    }


def test_quality_gate_blocks_unsupported_comparison_and_assessment():
    queue = load(QUEUE_PATH)
    rules = " ".join(queue["quality_gate"])
    assert "Do not infer policy achievement" in rules
    assert "Do not rank cities" in rules
    assert "automatically extracted material" in rules
    assert "denominator" in rules
    assert "supplementary budget" in rules
