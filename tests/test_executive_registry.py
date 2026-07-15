from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: str) -> Any:
    with (ROOT / path).open(encoding="utf-8") as handle:
        return json.load(handle)


def validation_errors(schema_path: str, instance: Any) -> list[str]:
    validator = Draft202012Validator(
        load_json(schema_path),
        format_checker=FormatChecker(),
    )
    return [error.message for error in validator.iter_errors(instance)]


def test_registry_records_match_contract() -> None:
    records = load_json("data/reviewed/executives/executive_terms.json")
    assert len(records) == 3
    assert len({record["municipality_id"] for record in records}) == 3
    for record in records:
        assert validation_errors("schemas/executive_term.schema.json", record) == []
        assert record["status"] == "current"
        assert record["review_status"] == "reviewed"
        assert record["manifesto_source_ids"] == []


def test_registry_evidence_is_complete() -> None:
    records = load_json("data/reviewed/executives/executive_terms.json")
    packets = load_json("data/reviewed/executives/evidence_packets.json")
    catalog = load_json("data/catalog/official_sources.json")
    source_ids = {source["id"] for source in catalog["records"]}

    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in records
    }
    for packet in packets:
        assert validation_errors("schemas/evidence_packet.schema.json", packet) == []
        assert packet["open_questions"]
        for claim in packet["claims"]:
            assert set(claim["source_ids"]) <= source_ids
    for record in records:
        assert set(record["sources"]) <= source_ids
