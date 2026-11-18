from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

ASSEMBLY_DIRS = {
    "fukuoka-prefecture": ("jp-local-400009-assembly-2023", 87, 86),
    "fukuoka-city": ("jp-local-401307-assembly-2023", 62, 60),
    "kitakyushu-city": ("jp-local-401005-assembly-2025", 57, 57),
}

NEW_SCHEMAS = [
    "faction_vote",
    "member",
    "political_activity_expense",
    "session",
    "committee",
    "disclosure_profile",
]


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def assert_valid(schema_path: str, instance: Any) -> None:
    validator = Draft202012Validator(
        load_json(ROOT / schema_path),
        format_checker=FormatChecker(),
    )
    errors = list(validator.iter_errors(instance))
    assert errors == [], "; ".join(error.message for error in errors)


def catalog_source_ids() -> set[str]:
    ids: set[str] = set()
    for path in (ROOT / "data" / "catalog").glob("*.json"):
        value = load_json(path)
        if isinstance(value, dict) and isinstance(value.get("records"), list):
            ids.update(
                record["id"]
                for record in value["records"]
                if isinstance(record, dict) and isinstance(record.get("id"), str)
            )
    return ids


def referenced_sources(value: Any) -> set[str]:
    result: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"sources", "source_ids"} and isinstance(child, list):
                result.update(item for item in child if isinstance(item, str))
            result.update(referenced_sources(child))
    elif isinstance(value, list):
        for child in value:
            result.update(referenced_sources(child))
    return result


def test_new_schemas_are_registered_with_valid_fixtures() -> None:
    registry = load_json(ROOT / "schemas" / "registry.json")
    entries = {entry["name"]: entry for entry in registry["entries"]}
    for name in NEW_SCHEMAS:
        assert name in entries
        assert_valid(entries[name]["schema"], load_json(ROOT / entries[name]["fixture"]))


def test_member_schema_has_no_activity_metrics() -> None:
    schema = load_json(ROOT / "schemas" / "member.schema.json")
    assert schema["additionalProperties"] is False
    forbidden = {
        "question_count",
        "speech_count",
        "speaking_count",
        "attendance_rate",
        "attendance_count",
        "bill_count",
        "proposal_count",
        "score",
        "ranking",
    }
    assert forbidden.isdisjoint(schema["properties"].keys())


def test_faction_vote_schema_supports_split_positions() -> None:
    schema = load_json(ROOT / "schemas" / "faction_vote.schema.json")
    positions = schema["properties"]["position"]["enum"]
    # Kitakyushu publishes factions whose members split for and against.
    assert "split" in positions
    assert {"for", "against"} <= set(positions)


def test_assembly_records_match_contracts_and_facts() -> None:
    known_sources = catalog_source_ids()
    for slug, (assembly_id, seat_count, faction_total) in ASSEMBLY_DIRS.items():
        base = ROOT / "data" / "reviewed" / slug / "assembly"
        records = load_json(base / "assembly_records.json")
        profiles = load_json(base / "disclosure_profiles.json")
        packets = load_json(base / "assembly_evidence_packets.json")

        assert len(records) == 1
        record = records[0]
        assert_valid("schemas/assembly.schema.json", record)
        assert record["id"] == assembly_id
        assert record["seat_count"] == seat_count
        assert sum(f["member_count"] for f in record["factions"]) == faction_total
        assert faction_total <= seat_count
        assert record["review_status"] in {"reviewed", "verified"}

        assert len(profiles) == 1
        profile = profiles[0]
        assert_valid("schemas/disclosure_profile.schema.json", profile)
        assert profile["assembly_id"] == assembly_id

        for packet in packets:
            assert_valid("schemas/evidence_packet.schema.json", packet)
        assert {packet["subject_id"] for packet in packets} == {
            record["id"],
            profile["id"],
        }

        references = referenced_sources([records, profiles, packets])
        assert references <= known_sources


def test_member_votes_are_not_published_in_any_pilot_assembly() -> None:
    # Design decision for Issue #9: the absence of per-member votes is itself
    # registered as primary information; votes are never reconstructed.
    expected_faction_votes = {
        "fukuoka-prefecture": "not_published",
        "fukuoka-city": "published",
        "kitakyushu-city": "published",
    }
    for slug, faction_availability in expected_faction_votes.items():
        profile = load_json(
            ROOT / "data" / "reviewed" / slug / "assembly" / "disclosure_profiles.json"
        )[0]
        items = {item["item"]: item for item in profile["items"]}
        assert items["member_votes"]["availability"] == "not_published"
        assert items["member_votes"]["granularity"] == "none"
        assert items["faction_votes"]["availability"] == faction_availability
        assert (
            items["political_activity_expense_receipts"]["availability"]
            == "restricted"
        )
