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


def test_stage5_register_reflects_current_publication() -> None:
    # Stage 5 (2026-11-18) re-checked the official list: reports and cost
    # breakdowns are now published for every delegation of the term, so
    # the July gaps recorded for the three 2026 trips no longer hold.
    # The dated July claims stay in the evidence packets as history.
    trips = load_json(
        "data/reviewed/fukuoka-prefecture/assembly/inspection_trips.json"
    )
    by_id = {trip["id"]: trip for trip in trips}

    assert len(trips) == 24
    assert all(trip["report_status"] == "published" for trip in trips)
    assert sum(trip["cost_status"] == "available" for trip in trips) == 22

    bangkok = by_id["jp-local-400009-assembly-2023-inspection-2026-bangkok"]
    assert bangkok["participant_count"] == 14
    assert len(
        [
            participant
            for participant in bangkok["participants"]
            if participant["participant_type"] == "elected_member"
        ]
    ) == 10
    assert bangkok["report_status"] == "published"
    assert bangkok["total_cost_yen"] == 4_839_000
    assert len(bangkok["policy_follow_up"]) == 2

    hawaii = by_id["jp-local-400009-assembly-2023-inspection-2026-hawaii"]
    assert hawaii["report_status"] == "published"
    assert hawaii["total_cost_yen"] == 10_600_000
    assert hawaii["participant_count"] == 13

    gyeongsangnam = by_id[
        "jp-local-400009-assembly-2023-inspection-2026-gyeongsangnam-do"
    ]
    assert gyeongsangnam["report_status"] == "published"
    assert gyeongsangnam["total_cost_yen"] == 2_490_000
    assert gyeongsangnam["participant_count"] == 13

    # The Qatar delegation's costs were borne by the executive branch
    # (the list publishes no cost breakdown), and the January 2024 Hanoi
    # delegation only appears in a combined cost document, so neither
    # carries a per-trip total.
    qatar = by_id["jp-local-400009-assembly-2023-inspection-2025-qatar"]
    assert qatar["cost_status"] == "not_found"
    assert qatar["total_cost_yen"] is None
    hanoi_jan = by_id["jp-local-400009-assembly-2023-inspection-2024-hanoi-jan"]
    assert hanoi_jan["cost_status"] == "not_found"
    assert hanoi_jan["total_cost_yen"] is None


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
