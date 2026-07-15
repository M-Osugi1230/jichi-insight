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


def test_kitakyushu_reviewed_data_matches_contracts() -> None:
    assert_valid(
        "schemas/source_catalog.schema.json",
        load_json("data/catalog/kitakyushu_finance_sources.json"),
    )
    assert_valid(
        "schemas/municipality.schema.json",
        load_json("data/reviewed/kitakyushu-city/municipality.json"),
    )
    for record in load_json("data/reviewed/kitakyushu-city/fiscal_records.json"):
        assert_valid("schemas/fiscal_record.schema.json", record)
    for packet in load_json("data/reviewed/kitakyushu-city/evidence_packets.json"):
        assert_valid("schemas/evidence_packet.schema.json", packet)


def test_kitakyushu_exact_values_and_evidence() -> None:
    records = load_json("data/reviewed/kitakyushu-city/fiscal_records.json")
    packets = load_json("data/reviewed/kitakyushu-city/evidence_packets.json")
    assert {record["id"]: record["amount_yen"] for record in records} == {
        "jp-local-401005-fiscal-2026-total-revenue": 647_684_000_000,
        "jp-local-401005-fiscal-2026-local-tax": 192_500_000_000,
        "jp-local-401005-fiscal-2024-total-revenue": 619_800_427_000,
        "jp-local-401005-fiscal-2024-total-expenditure": 615_895_866_000,
        "jp-local-401005-fiscal-2024-local-tax": 180_177_794_000,
    }
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in records
    }
    assert all(record["account_type"] == "general" for record in records)


def test_kitakyushu_source_references_are_known() -> None:
    municipality = load_json("data/reviewed/kitakyushu-city/municipality.json")
    records = load_json("data/reviewed/kitakyushu-city/fiscal_records.json")
    packets = load_json("data/reviewed/kitakyushu-city/evidence_packets.json")
    catalogs = [
        load_json("data/catalog/official_sources.json"),
        load_json("data/catalog/kitakyushu_finance_sources.json"),
    ]
    source_ids = {
        source["id"]
        for catalog in catalogs
        for source in catalog["records"]
    }
    referenced = set(municipality["sources"])
    for record in records:
        referenced.update(record["sources"])
    for packet in packets:
        for claim in packet["claims"]:
            referenced.update(claim["source_ids"])
    assert referenced <= source_ids
