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


def test_fukuoka_reviewed_data_matches_contracts() -> None:
    municipality = load_json("data/reviewed/fukuoka-prefecture/municipality.json")
    records = load_json("data/reviewed/fukuoka-prefecture/fiscal_records.json")
    packets = load_json("data/reviewed/fukuoka-prefecture/evidence_packets.json")

    assert_valid("schemas/municipality.schema.json", municipality)
    for record in records:
        assert_valid("schemas/fiscal_record.schema.json", record)
    for packet in packets:
        assert_valid("schemas/evidence_packet.schema.json", packet)


def test_fukuoka_budget_values_and_stages_are_explicit() -> None:
    records = load_json("data/reviewed/fukuoka-prefecture/fiscal_records.json")
    by_metric = {record["metric"]: record for record in records}

    assert by_metric["total_revenue"]["amount_yen"] == 2_300_000_000_000
    assert by_metric["local_tax"]["amount_yen"] == 830_800_000_000
    assert all(record["stage"] == "initial_budget" for record in records)
    assert all(record["account_type"] == "general" for record in records)
    assert all(record["review_status"] == "reviewed" for record in records)


def test_every_reviewed_fukuoka_value_has_an_evidence_packet() -> None:
    records = load_json("data/reviewed/fukuoka-prefecture/fiscal_records.json")
    packets = load_json("data/reviewed/fukuoka-prefecture/evidence_packets.json")
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in records
    }
