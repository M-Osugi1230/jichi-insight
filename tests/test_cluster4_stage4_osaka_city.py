from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "reviewed" / "osaka-city" / "assembly"
ASSEMBLY_ID = "jp-local-271004-assembly-2023"
SESSION_ID = f"{ASSEMBLY_ID}-session-2026-05"

FACTION_NAMES = [
    "大阪維新の会大阪市会議員団",
    "公明党大阪市会議員団",
    "自由民主党・市民クラブ大阪市会議員団",
    "自由民主党・国民民主党・市民とつながる・くらしが第一大阪市会議員団",
    "日本共産党大阪市会議員団",
    "無所属大阪市会議員団",
    "大阪にし大阪市会議員団",
    "福島クラブ大阪市会議員団",
    "大阪平野大阪市会議員団",
    "総活躍社会実現の会大阪市会議員団",
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


def test_osaka_city_catalog_is_valid() -> None:
    catalog = load_json(ROOT / "data" / "catalog" / "osaka_city_assembly_sources.json")
    assert_valid("schemas/source_catalog.schema.json", catalog)
    assert len(catalog["records"]) == 27
    assert {r["municipality_key"] for r in catalog["records"]} == {"osaka-city"}


def test_osaka_city_assembly_and_session_match_contracts() -> None:
    assemblies = load_json(BASE / "assembly_records.json")
    sessions = load_json(BASE / "sessions.json")
    packets = load_json(BASE / "assembly_evidence_packets.json")

    assert len(assemblies) == 1
    assembly = assemblies[0]
    assert_valid("schemas/assembly.schema.json", assembly)
    assert assembly["id"] == ASSEMBLY_ID
    assert assembly["municipality_id"] == "jp-local-271004"
    assert assembly["seat_count"] == 81
    assert assembly["term_start"] == "2023-04-30"
    assert assembly["term_end"] == "2027-04-29"
    assert [f["name"] for f in assembly["factions"]] == FACTION_NAMES
    assert sum(f["member_count"] for f in assembly["factions"]) == 81

    assert len(sessions) == 1
    assert_valid("schemas/session.schema.json", sessions[0])
    assert sessions[0]["id"] == SESSION_ID
    assert sessions[0]["name"] == "令和8年5・6月市会"
    assert sessions[0]["start_date"] == "2026-05-15"
    assert sessions[0]["end_date"] == "2026-06-11"

    assert [p["subject_id"] for p in packets] == [ASSEMBLY_ID]
    for packet in packets:
        assert_valid("schemas/evidence_packet.schema.json", packet)


def test_osaka_city_proposals_and_votes_match_contracts() -> None:
    proposals = load_json(BASE / "proposals.json")
    votes = load_json(BASE / "votes.json")
    faction_votes = load_json(BASE / "faction_votes.json")
    packets = load_json(BASE / "proposal_vote_evidence_packets.json")

    # Only the 26 votable items are registered; the 12 procedural items on
    # the official list carry no faction positions and are documented in the
    # assembly evidence packet instead.
    assert len(proposals) == 26
    assert len(votes) == 26
    assert len(faction_votes) == 260
    assert len(packets) == 52
    assert {p["subject_id"] for p in packets} == {p["id"] for p in proposals} | {
        v["id"] for v in votes
    }

    for proposal in proposals:
        assert_valid("schemas/proposal.schema.json", proposal)
        assert proposal["assembly_id"] == ASSEMBLY_ID
        assert proposal["session_id"] == SESSION_ID
        # The official list does not print submission dates.
        assert proposal["submitted_at"] is None
    for vote in votes:
        assert_valid("schemas/vote.schema.json", vote)
        # Member-level positions are not published; nothing is fabricated.
        assert vote["member_vote_availability"] == "not_published"
        assert vote["member_votes"] == []
        assert vote["totals"] is None
        assert vote["method"] == "unknown"

    by_number = {p["proposal_number"]: p for p in proposals}
    assert by_number["議案第105号"]["kind"] == "budget"
    assert by_number["議案第105号"]["outcome"] == "approved"
    assert by_number["議員提出議案第6号"]["kind"] == "resolution"
    assert by_number["議員提出議案第6号"]["submitted_by"] == "member"
    rejected = [p for p in proposals if p["outcome"] == "rejected"]
    assert len(rejected) == 1
    assert rejected[0]["title"] == "副議長辞職許可について"
    assert rejected[0]["decided_at"] == "2026-06-11"

    # Every votable item has exactly one row per faction, transcribed from
    # the printed positions (counts are not published, so they stay null).
    for vote in votes:
        rows = [fv for fv in faction_votes if fv["vote_id"] == vote["id"]]
        assert len(rows) == 10
        assert [r["faction_name"] for r in rows] == FACTION_NAMES
        for row in rows:
            assert_valid("schemas/faction_vote.schema.json", row)
            assert row["for_count"] is None
            assert row["against_count"] is None
            assert (
                sum(
                    f["member_count"]
                    for f in load_json(BASE / "assembly_records.json")[0]["factions"]
                )
                == 81
            )

    def positions(number: str) -> dict[str, str]:
        proposal = by_number[number]
        vote = next(v for v in votes if v["proposal_id"] == proposal["id"])
        return {
            fv["faction_name"]: fv["position"]
            for fv in faction_votes
            if fv["vote_id"] == vote["id"]
        }

    p104 = positions("議案第104号")
    assert {n for n, p in p104.items() if p == "against"} == {"日本共産党大阪市会議員団"}
    p105 = positions("議案第105号")
    assert {n for n, p in p105.items() if p == "for"} == {
        "大阪維新の会大阪市会議員団",
        "無所属大阪市会議員団",
        "福島クラブ大阪市会議員団",
        "大阪平野大阪市会議員団",
    }
    vice = next(p for p in proposals if p["title"] == "副議長辞職許可について")
    vice_vote = next(v for v in votes if v["proposal_id"] == vice["id"])
    vice_positions = {
        fv["faction_name"]: fv["position"]
        for fv in faction_votes
        if fv["vote_id"] == vice_vote["id"]
    }
    # Verified against the raw official HTML: the against rows are 維新,
    # 無所属 and 大阪平野 (an earlier inventory note said 大阪にし, which the
    # primary source does not support).
    assert {n for n, p in vice_positions.items() if p == "against"} == {
        "大阪維新の会大阪市会議員団",
        "無所属大阪市会議員団",
        "大阪平野大阪市会議員団",
    }


def test_osaka_city_expenses_reconcile() -> None:
    expenses = load_json(BASE / "political_activity_expenses.json")
    packets = load_json(BASE / "expense_evidence_packets.json")

    assert len(expenses) == 37
    assert len(packets) == 37
    assert {p["subject_id"] for p in packets} == {e["id"] for e in expenses}
    counts = {}
    for expense in expenses:
        assert_valid("schemas/political_activity_expense.schema.json", expense)
        assert expense["assembly_id"] == ASSEMBLY_ID
        assert expense["recipient_type"] == "faction"
        assert expense["report_status"] == "published"
        assert expense["receipt_access"] == "online"
        # The breakdown lists every category printed on the summary table
        # (printed zeros are kept) and sums to the printed total spent.
        assert len(expense["breakdown"]) == 10
        assert sum(b["amount_yen"] for b in expense["breakdown"]) == expense["spent_yen"]
        counts[expense["fiscal_year"]] = counts.get(expense["fiscal_year"], 0) + 1
    # FY2023 is split into two published periods (April / May-March).
    assert counts == {2021: 5, 2022: 5, 2023: 10, 2024: 7, 2025: 10}
    for packet in packets:
        assert_valid("schemas/evidence_packet.schema.json", packet)
        assert packet["claims"][0]["source_ids"] == next(
            e["sources"] for e in expenses if e["id"] == packet["subject_id"]
        )

    fy2025 = [e for e in expenses if e["fiscal_year"] == 2025]
    assert sum(e["granted_yen"] for e in fy2025) == 551_760_000
    assert sum(e["spent_yen"] for e in fy2025) == 531_723_352
    hirano = next(e for e in fy2025 if e["recipient_name"] == "大阪平野大阪市会議員団")
    assert hirano["granted_yen"] == 1_140_000
    assert hirano["spent_yen"] == 1_146_612
    # The summary table prints the residual as 0 even where spending exceeds
    # the grant; the printed value is registered as-is.
    assert hirano["returned_yen"] == 0


def test_osaka_city_inspection_trips() -> None:
    trips = load_json(BASE / "inspection_trips.json")
    packets = load_json(BASE / "inspection_evidence_packets.json")

    assert len(trips) == 9
    # One packet per trip plus one assembly-level packet recording that
    # domestic committee inspection reports are not published.
    assert len(packets) == 10
    assert {t["id"] for t in trips} <= {p["subject_id"] for p in packets}
    for trip in trips:
        assert_valid("schemas/inspection_trip.schema.json", trip)
        assert trip["assembly_id"] == ASSEMBLY_ID
        assert trip["trip_type"] == "overseas"
        assert trip["report_status"] == "published"
        assert trip["cost_status"] == "available"
        assert trip["participant_count"] == len(trip["participants"])
        assert trip["total_cost_yen"] > 0
        # Totals include staff travel and shared costs, so no per-person
        # figure is derived.
        assert trip["cost_per_person_yen"] is None
    r7 = next(t for t in trips if t["id"].endswith("2025-uk-netherlands"))
    assert r7["start_date"] == "2025-10-01"
    assert r7["end_date"] == "2025-10-09"
    assert r7["participant_count"] == 12
    assert r7["total_cost_yen"] == 18_601_816
    manchester = next(t for t in trips if t["id"].endswith("2025-manchester"))
    assert manchester["participant_count"] == 1
    assert manchester["participants"][0]["name"] == "杉村幸太郎"
    for packet in packets:
        assert_valid("schemas/evidence_packet.schema.json", packet)


def test_osaka_city_disclosure_profile() -> None:
    profiles = load_json(BASE / "disclosure_profiles.json")
    assert len(profiles) == 1
    profile = profiles[0]
    assert_valid("schemas/disclosure_profile.schema.json", profile)
    items = {i["item"]: i for i in profile["items"]}
    assert items["faction_votes"]["availability"] == "published"
    assert items["member_votes"]["availability"] == "not_published"
    assert items["petition_results"]["availability"] == "not_published"
    assert items["political_activity_expense_receipts"]["availability"] == "published"


def test_osaka_city_sources_resolve() -> None:
    known = catalog_source_ids()
    for name in (
        "assembly_records.json",
        "sessions.json",
        "proposals.json",
        "votes.json",
        "faction_votes.json",
        "political_activity_expenses.json",
        "inspection_trips.json",
        "disclosure_profiles.json",
        "assembly_evidence_packets.json",
        "proposal_vote_evidence_packets.json",
        "expense_evidence_packets.json",
        "inspection_evidence_packets.json",
    ):
        missing = referenced_sources(load_json(BASE / name)) - known
        assert missing == set(), f"{name}: unknown sources {sorted(missing)}"
