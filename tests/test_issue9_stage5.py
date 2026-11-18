from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

PREFECTURE = "jp-local-400009-assembly-2023"
CITY = "jp-local-401307-assembly-2023"

# Printed totals (thousands of yen) in the assembly's published cost
# breakdowns, keyed by trip id suffix. The two trips absent here have
# no per-trip total (see the test below).
PREFECTURE_TOTALS_SEN = {
    "2026-gyeongsangnam-do": 2490,
    "2026-hawaii": 10600,
    "2026-bangkok": 4839,
    "2025-paris": 14077,
    "2025-china": 3892,
    "2025-gyeongsangnam-do": 3901,
    "2025-hanoi": 5304,
    "2025-hawaii": 14130,
    "2024-bangkok-nov": 7808,
    "2024-egypt-cairo": 10994,
    "2024-new-south-wales": 12727,
    "2024-london-paris": 17511,
    "2024-hawaii-may": 11537,
    "2024-south-africa-dubai": 26271,
    "2024-gyeongsangnam-do": 3846,
    "2024-europe": 30038,
    "2024-bangkok-jan": 2830,
    "2024-hawaii-jan": 23207,
    "2023-delhi": 6360,
    "2023-malaysia": 15331,
    "2023-boston-new-york": 17300,
    "2023-new-south-wales": 13592,
}

CITY_TRIPS = {
    "2026-singapore": 3,
    "2026-taiwan": 3,
    "2026-uk": 2,
    "2025-australia-new-zealand": 8,
    "2025-portugal-spain": 6,
    "2024-usa-oakland": 6,
    "2023-korea-uae": 9,
    "2025-china-seimu": 1,
    "2024-china-seimu": 1,
}


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


def load_trips(slug: str) -> tuple[list[dict], list[dict]]:
    base = ROOT / "data" / "reviewed" / slug / "assembly"
    trips = load_json(base / "inspection_trips.json")
    packets = load_json(base / "inspection_evidence_packets.json")
    return trips, packets


def participant_headcount(trip: dict) -> int:
    # Named entries count once; placeholder entries carry their group
    # size in the name (氏名非掲載（N人）), or count once when no size
    # is printed （氏名非掲載）.
    total = 0
    for participant in trip["participants"]:
        match = re.search(r"（(\d+)人）", participant["name"])
        total += int(match.group(1)) if match else 1
    return total


def test_stage5_prefecture_trips_match_contracts() -> None:
    trips, packets = load_trips("fukuoka-prefecture")
    assert len(trips) == 24
    assert len(packets) == 24
    assert {packet["subject_id"] for packet in packets} == {
        trip["id"] for trip in trips
    }

    for trip in trips:
        assert_valid("schemas/inspection_trip.schema.json", trip)
        assert trip["assembly_id"] == PREFECTURE
        assert trip["trip_type"] == "overseas"
        assert trip["report_status"] == "published"
        assert trip["review_status"] == "reviewed"
        assert trip["confidence"] == "high"
        # All 24 delegations fall inside the current term
        # (2023-04-30 to 2027-04-29).
        assert "2023-08-04" <= trip["start_date"] <= "2026-03-30"
        if trip["participant_count"] is not None:
            assert participant_headcount(trip) == trip["participant_count"]

    for packet in packets:
        assert_valid("schemas/evidence_packet.schema.json", packet)
        assert packet["subject_type"] == "inspection_trip"

    references = referenced_sources([trips, packets])
    assert references <= catalog_source_ids()


def test_stage5_prefecture_costs_match_published_breakdowns() -> None:
    trips, _ = load_trips("fukuoka-prefecture")
    by_suffix = {
        trip["id"].split("-inspection-", 1)[1]: trip for trip in trips
    }
    assert set(by_suffix) == set(PREFECTURE_TOTALS_SEN) | {
        "2025-qatar",
        "2024-hanoi-jan",
    }
    for suffix, sen in PREFECTURE_TOTALS_SEN.items():
        trip = by_suffix[suffix]
        assert trip["cost_status"] == "available"
        # The breakdowns print totals in thousands of yen (rounded);
        # the register stores that printed value at yen precision.
        assert trip["total_cost_yen"] == sen * 1000
        assert trip["cost_per_person_yen"] is None

    # Qatar: the list states the executive branch bore the costs and no
    # breakdown is published. Hanoi (Jan 2024): the only cost document
    # is a combined one for two delegations (printed total 6,377
    # thousand yen), so no per-trip amount may be registered.
    for suffix in ("2025-qatar", "2024-hanoi-jan"):
        trip = by_suffix[suffix]
        assert trip["cost_status"] == "not_found"
        assert trip["total_cost_yen"] is None


def test_stage5_city_trips_match_contracts() -> None:
    trips, packets = load_trips("fukuoka-city")
    assert len(trips) == 9
    assert len(packets) == 9
    assert {packet["subject_id"] for packet in packets} == {
        trip["id"] for trip in trips
    }

    by_suffix = {
        trip["id"].split("-inspection-", 1)[1]: trip for trip in trips
    }
    assert set(by_suffix) == set(CITY_TRIPS)
    for suffix, members in CITY_TRIPS.items():
        trip = by_suffix[suffix]
        assert_valid("schemas/inspection_trip.schema.json", trip)
        assert trip["assembly_id"] == CITY
        assert trip["trip_type"] == "overseas"
        assert trip["report_status"] == "published"
        assert trip["participant_count"] == members
        assert len(trip["participants"]) == members
        # Costs are published neither on the list page nor in the
        # report PDFs, so no amount is registered for any city trip.
        assert trip["cost_status"] == "not_found"
        assert trip["total_cost_yen"] is None
        assert trip["review_status"] == "reviewed"

    # The two trips the page lists under its political-activity-expense
    # section carry that funding status for their sole participant.
    for suffix in ("2025-china-seimu", "2024-china-seimu"):
        trip = by_suffix[suffix]
        assert trip["participants"][0]["funding_status"] == (
            "political_activity_expense"
        )

    for packet in packets:
        assert_valid("schemas/evidence_packet.schema.json", packet)
        assert packet["subject_type"] == "inspection_trip"

    references = referenced_sources([trips, packets])
    assert references <= catalog_source_ids()


def test_stage5_kitakyushu_gap_is_explicit() -> None:
    # Kitakyushu publishes inspection reports only up to FY2018, which
    # predates the current assembly term; no trip records are created
    # (they would be misattributed to the 2025-term assembly), and the
    # published reports are catalogued instead.
    base = ROOT / "data" / "reviewed" / "kitakyushu-city" / "assembly"
    assert not (base / "inspection_trips.json").exists()

    catalog = load_json(ROOT / "data" / "catalog" / "kitakyushu_assembly_sources.json")
    report_ids = {
        record["id"]
        for record in catalog["records"]
        if record["id"].startswith("kitakyushu-assembly-inspection-report-")
    }
    assert report_ids == {
        "kitakyushu-assembly-inspection-report-2018-europe",
        "kitakyushu-assembly-inspection-report-2018-offshore-wind",
        "kitakyushu-assembly-inspection-report-2015",
        "kitakyushu-assembly-inspection-report-2013",
    }

    profiles = load_json(base / "disclosure_profiles.json")
    items = {item["item"]: item for profile in profiles for item in profile["items"]}
    reports = items["inspection_trip_reports"]
    assert reports["availability"] == "published"
    assert "平成30年度" in reports["note"]


def test_stage5_disclosure_profiles_match_registration() -> None:
    # All three assemblies publish inspection reports; the registered
    # data and the profiles agree on that. Granularity stays at the
    # document level everywhere (no per-trip cost ledger is published
    # by the two cities).
    for slug in ("fukuoka-prefecture", "fukuoka-city", "kitakyushu-city"):
        base = ROOT / "data" / "reviewed" / slug / "assembly"
        profiles = load_json(base / "disclosure_profiles.json")
        items = {
            item["item"]: item for profile in profiles for item in profile["items"]
        }
        reports = items["inspection_trip_reports"]
        assert reports["availability"] == "published"
        assert reports["granularity"] == "document"


def test_stage5_catalog_versions() -> None:
    versions = {
        "fukuoka_assembly_sources.json": "0.5.0",
        "fukuoka_city_assembly_sources.json": "0.4.0",
        "kitakyushu_assembly_sources.json": "0.4.0",
    }
    for filename, version in versions.items():
        catalog = load_json(ROOT / "data" / "catalog" / filename)
        assert_valid("schemas/source_catalog.schema.json", catalog)
        assert catalog["version"] == version
        assert catalog["updated_at"] == "2026-11-18"
