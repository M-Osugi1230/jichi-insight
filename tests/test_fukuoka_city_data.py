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


def all_records() -> list[dict[str, Any]]:
    return [
        *load_json("data/reviewed/fukuoka-city/fiscal_records.json"),
        *load_json("data/reviewed/fukuoka-city/settlement_records.json"),
    ]


def all_packets() -> list[dict[str, Any]]:
    return [
        *load_json("data/reviewed/fukuoka-city/evidence_packets.json"),
        *load_json("data/reviewed/fukuoka-city/settlement_evidence_packets.json"),
    ]


def test_fukuoka_city_sources_and_reviewed_data_match_contracts() -> None:
    catalog = load_json("data/catalog/fukuoka_city_finance_sources.json")
    municipality = load_json("data/reviewed/fukuoka-city/municipality.json")
    records = all_records()
    packets = all_packets()

    assert_valid("schemas/source_catalog.schema.json", catalog)
    assert_valid("schemas/municipality.schema.json", municipality)
    for record in records:
        assert_valid("schemas/fiscal_record.schema.json", record)
    for packet in packets:
        assert_valid("schemas/evidence_packet.schema.json", packet)


def test_fukuoka_city_exact_values_and_stages() -> None:
    records = load_json("data/reviewed/fukuoka-city/fiscal_records.json")
    general_values = {
        record["id"]: record["amount_yen"] for record in records
    }

    # The FY2026 figures are the enacted initial budget: thousand-yen
    # precision from the official gazette (Fukuoka City Gazette No. 7233
    # supplement, Notification No. 101), refined in place from the
    # draft-stage values that were published only in hundred-million-yen
    # units (1,131,800,000,000 and 426,300,000,000). The FY2026 total
    # expenditure record is new: the draft stage had no such record.
    assert general_values == {
        "jp-local-401307-fiscal-2026-total-revenue": 1_131_811_000_000,
        "jp-local-401307-fiscal-2026-local-tax": 426_320_009_000,
        "jp-local-401307-fiscal-2026-total-expenditure": 1_131_811_000_000,
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

    settlement_records = load_json(
        "data/reviewed/fukuoka-city/settlement_records.json"
    )
    assert {
        (record["fiscal_year"], record["stage"], record["account_type"])
        for record in settlement_records
    } == {
        (2022, "settlement", "ordinary"),
        (2023, "settlement", "ordinary"),
        (2024, "settlement", "ordinary"),
    }


def test_every_fukuoka_city_value_has_evidence_and_known_sources() -> None:
    municipality = load_json("data/reviewed/fukuoka-city/municipality.json")
    records = all_records()
    packets = all_packets()
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
