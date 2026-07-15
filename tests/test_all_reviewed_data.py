from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def validate(schema_path: str, instance: Any) -> list[str]:
    schema = load_json(ROOT / schema_path)
    validator = Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    )
    return [error.message for error in validator.iter_errors(instance)]


def source_ids() -> set[str]:
    ids: set[str] = set()
    for path in (ROOT / "data" / "catalog").glob("*.json"):
        value = load_json(path)
        if isinstance(value, dict) and isinstance(value.get("records"), list):
            ids.update(record["id"] for record in value["records"])
    return ids


def referenced_sources(value: Any) -> set[str]:
    result: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            source_keys = {"sources", "source_ids", "manifesto_source_ids"}
            if key in source_keys and isinstance(child, list):
                result.update(
                    item for item in child if isinstance(item, str)
                )
            result.update(referenced_sources(child))
    elif isinstance(value, list):
        for child in value:
            result.update(referenced_sources(child))
    return result


def test_all_reviewed_municipalities_have_complete_evidence() -> None:
    known_sources = source_ids()
    reviewed_root = ROOT / "data" / "reviewed"
    municipalities = sorted(
        path for path in reviewed_root.iterdir() if path.is_dir()
    )
    assert [path.name for path in municipalities] == [
        "fukuoka-city",
        "fukuoka-prefecture",
        "kitakyushu-city",
    ]

    total_records = 0
    total_packets = 0
    all_record_ids: set[str] = set()

    for directory in municipalities:
        municipality = load_json(directory / "municipality.json")
        assert validate(
            "schemas/municipality.schema.json",
            municipality,
        ) == []

        record_files = sorted(directory.glob("*records.json"))
        packet_files = sorted(directory.glob("*evidence_packets.json"))
        records = [
            record
            for path in record_files
            for record in load_json(path)
        ]
        packets = [
            packet
            for path in packet_files
            for packet in load_json(path)
        ]

        assert records
        assert len(records) == len(packets)
        assert {packet["subject_id"] for packet in packets} == {
            record["id"] for record in records
        }
        assert all(
            record["municipality_id"] == municipality["id"]
            for record in records
        )
        assert all(
            record["review_status"] in {"reviewed", "verified"}
            for record in records
        )
        assert all(
            validate("schemas/fiscal_record.schema.json", record) == []
            for record in records
        )
        assert all(
            validate("schemas/evidence_packet.schema.json", packet) == []
            for packet in packets
        )

        references = referenced_sources([municipality, records, packets])
        assert references <= known_sources
        current_ids = {record["id"] for record in records}
        assert not (all_record_ids & current_ids)
        all_record_ids.update(current_ids)
        total_records += len(records)
        total_packets += len(packets)

    assert total_records == 22
    assert total_packets == 22
