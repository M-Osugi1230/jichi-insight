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


def test_overseas_activity_data_matches_contracts() -> None:
    catalog = load_json("data/catalog/fukuoka_assembly_sources.json")
    trips = load_json(
        "data/reviewed/fukuoka-prefecture/assembly/inspection_trips.json"
    )
    packets = load_json(
        "data/reviewed/fukuoka-prefecture/assembly/inspection_evidence_packets.json"
    )

    assert_valid("schemas/source_catalog.schema.json", catalog)
    for trip in trips:
        assert_valid("schemas/inspection_trip.schema.json", trip)
    for packet in packets:
        assert_valid("schemas/evidence_packet.schema.json", packet)


def test_2026_register_preserves_disclosure_gaps() -> None:
    trips = load_json(
        "data/reviewed/fukuoka-prefecture/assembly/inspection_trips.json"
    )
    by_destination = {trip["destinations"][0]: trip for trip in trips}

    assert len(trips) == 3
    assert sum(trip["report_status"] == "published" for trip in trips) == 1
    assert sum(trip["cost_status"] == "available" for trip in trips) == 0
    assert sum(trip["participant_count"] is not None for trip in trips) == 1

    bangkok = by_destination["タイ王国・バンコク都"]
    assert bangkok["participant_count"] == 14
    assert len(
        [
            participant
            for participant in bangkok["participants"]
            if participant["participant_type"] == "elected_member"
        ]
    ) == 10
    assert bangkok["report_status"] == "published"
    assert bangkok["cost_status"] == "not_found"
    assert len(bangkok["policy_follow_up"]) == 2

    assert by_destination["アメリカ合衆国・ハワイ州"]["report_status"] == (
        "not_published"
    )
    assert by_destination["大韓民国・慶尚南道"]["report_status"] == (
        "not_published"
    )


def test_every_activity_has_evidence_and_known_sources() -> None:
    trips = load_json(
        "data/reviewed/fukuoka-prefecture/assembly/inspection_trips.json"
    )
    packets = load_json(
        "data/reviewed/fukuoka-prefecture/assembly/inspection_evidence_packets.json"
    )
    catalog_paths = [
        "data/catalog/official_sources.json",
        "data/catalog/fukuoka_assembly_sources.json",
    ]
    source_ids = {
        source["id"]
        for path in catalog_paths
        for source in load_json(path)["records"]
    }

    assert {packet["subject_id"] for packet in packets} == {
        trip["id"] for trip in trips
    }

    referenced_sources: set[str] = set()
    for trip in trips:
        referenced_sources.update(trip["sources"])
    for packet in packets:
        for claim in packet["claims"]:
            referenced_sources.update(claim["source_ids"])

    assert referenced_sources <= source_ids
