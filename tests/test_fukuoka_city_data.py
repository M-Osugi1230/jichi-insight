from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: str) -> Any:
    with (ROOT / path).open(encoding="utf-8") as handle:
        return json.load(handle)


def assert_valid(schema_path: str, instance: Any) -> None:
    validator = Draft202012Validator(
        load_json(schema_path),
        format_checker=FormatChecker(),
    )
    errors = list(validator.iter_errors(instance))
    assert errors == [], "; ".join(error.message for error in errors)


def test_fukuoka_city_sources_and_reviewed_data_match_contracts() -> None:
    catalog = load_json("data/catalog/fukuoka_city_finance_sources.json")
    municipality = load_json("data/reviewed/fukuoka-city/municipality.json")
    records = load_json("data/reviewed/fukuoka-city/fiscal_records.json")
    packets = load_json("data/reviewed/fukuoka-city/evidence_packets.json")

    assert_valid("schemas/source_catalog.schema.json", catalog)
    assert_valid("schemas/municipality.schema.json", municipality)
    for record in records:
        assert_valid("schemas/fiscal_record.schema.json", record)
    for packet in packets:
        assert_valid("schemas/evidence_packet.schema.json", packet)


def test_fukuoka_city_exact_values_and_stages() -> None:
    records = load_json("data/reviewed/fukuoka-city/fiscal_records.json")
    values = {record["id"]: record["amount_yen"] for record in records}

    assert values == {
        "jp-local-401307-fiscal-2026-total-revenue": 1_131_800_000_000,
        "jp-local-401307-fiscal-2026-local-tax": 426_300_000_000,
        "jp-local-401307-fiscal-2024-total-revenue": 1_126_286_330_000,
        "jp-local-401307-fiscal-2024-total-expenditure": 1_108_780_593_000,
    }
    assert {
        (record["fiscal_year"], record["stage"], record["account_type"])
        for record in records
    } == {
        (2026, "initial_budget", "general"),
        (2024, "settlement", "general"),
    }


def test_every_fukuoka_city_value_has_evidence_and_known_sources() -> None:
    municipality = load_json("data/reviewed/fukuoka-city/municipality.json")
    records = load_json("data/reviewed/fukuoka-city/fiscal_records.json")
    packets = load_json("data/reviewed/fukuoka-city/evidence_packets.json")
    catalogs = [
        load_json("data/catalog/official_sources.json"),
        load_json("data/catalog/fukuoka_finance_sources.json"),
        load_json("data/catalog/fukuoka_city_finance_sources.json"),
    ]
    source_ids = {
        source["id"]
        for catalog in catalogs
        for source in catalog["records"]
    }

    assert municipality["id"] == "jp-local-401307"
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in records
    }
    referenced_sources = set(municipality["sources"])
    for record in records:
        referenced_sources.update(record["sources"])
    for packet in packets:
        for claim in packet["claims"]:
            referenced_sources.update(claim["source_ids"])
    assert referenced_sources <= source_ids
