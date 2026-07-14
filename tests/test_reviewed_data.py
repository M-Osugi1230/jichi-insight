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


def all_fiscal_records() -> list[dict[str, Any]]:
    return [
        *load_json("data/reviewed/fukuoka-prefecture/fiscal_records.json"),
        *load_json("data/reviewed/fukuoka-prefecture/settlement_records.json"),
    ]


def all_evidence_packets() -> list[dict[str, Any]]:
    return [
        *load_json("data/reviewed/fukuoka-prefecture/evidence_packets.json"),
        *load_json(
            "data/reviewed/fukuoka-prefecture/settlement_evidence_packets.json"
        ),
    ]


def test_fukuoka_reviewed_data_matches_contracts() -> None:
    municipality = load_json("data/reviewed/fukuoka-prefecture/municipality.json")

    assert_valid("schemas/municipality.schema.json", municipality)
    for record in all_fiscal_records():
        assert_valid("schemas/fiscal_record.schema.json", record)
    for packet in all_evidence_packets():
        assert_valid("schemas/evidence_packet.schema.json", packet)


def test_fukuoka_budget_values_and_stages_are_explicit() -> None:
    records = load_json("data/reviewed/fukuoka-prefecture/fiscal_records.json")
    by_metric = {record["metric"]: record for record in records}

    assert by_metric["total_revenue"]["amount_yen"] == 2_300_000_000_000
    assert by_metric["local_tax"]["amount_yen"] == 830_800_000_000
    assert all(record["stage"] == "initial_budget" for record in records)
    assert all(record["account_type"] == "general" for record in records)
    assert all(record["review_status"] == "reviewed" for record in records)


def test_fukuoka_settlement_series_is_complete_and_separate() -> None:
    records = load_json("data/reviewed/fukuoka-prefecture/settlement_records.json")
    trend_records = [record for record in records if record["metric"] != "local_tax"]

    assert {record["fiscal_year"] for record in trend_records} == {
        2020,
        2021,
        2022,
        2023,
        2024,
    }
    for fiscal_year in range(2020, 2025):
        metrics = {
            record["metric"]
            for record in trend_records
            if record["fiscal_year"] == fiscal_year
        }
        assert metrics == {"total_revenue", "total_expenditure"}
    assert all(record["stage"] == "settlement" for record in records)
    assert all(record["account_type"] == "ordinary" for record in records)


def test_fukuoka_2024_settlement_values_match_official_tables() -> None:
    records = load_json("data/reviewed/fukuoka-prefecture/settlement_records.json")
    values = {
        record["metric"]: record["amount_yen"]
        for record in records
        if record["fiscal_year"] == 2024
    }

    assert values == {
        "total_revenue": 2_093_700_000_000,
        "total_expenditure": 2_032_626_000_000,
        "local_tax": 784_235_000_000,
    }


def test_every_reviewed_fukuoka_value_has_an_evidence_packet() -> None:
    records = all_fiscal_records()
    packets = all_evidence_packets()
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in records
    }
