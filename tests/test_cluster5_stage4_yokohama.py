"""Cluster 5 stage 4: Yokohama City assembly registration contract tests."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "reviewed" / "yokohama-city" / "assembly"
CATALOG_PATH = ROOT / "data" / "catalog" / "yokohama_city_assembly_sources.json"


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


ASSEMBLY_ID = "jp-local-141003-assembly-2023"
SESSION_ID = f"{ASSEMBLY_ID}-session-2026-3"

# Totals are the registered positions toward each proposal itself. For the
# two petitions whose committee report recommended non-adoption, the printed
# symbols (votes on the report) are inverted: petition 7 was 78-7 on the
# report, petition 9 was 77-8.
EXPECTED_TOTALS = {
    "市第20号議案": {"for": 79, "against": 6, "abstained": 0, "absent": 0},
    "市第21号議案": {"for": 84, "against": 1, "abstained": 0, "absent": 0},
    "市第36号議案": {"for": 79, "against": 6, "abstained": 0, "absent": 0},
    "市第41号議案": {"for": 84, "against": 1, "abstained": 0, "absent": 0},
    "市第42号議案": {"for": 83, "against": 2, "abstained": 0, "absent": 0},
    "市第43号議案": {"for": 85, "against": 0, "abstained": 0, "absent": 0},
    "請願第7号": {"for": 7, "against": 78, "abstained": 0, "absent": 0},
    "請願第9号": {"for": 8, "against": 77, "abstained": 0, "absent": 0},
    "議第10号議案": {"for": 15, "against": 70, "abstained": 0, "absent": 0},
}


def catalog_record_ids() -> set[str]:
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


def test_yokohama_assembly_catalog_records_valid() -> None:
    payload = load_json(CATALOG_PATH)
    assert_valid("schemas/source_catalog.schema.json", payload)
    records = payload["records"]
    assert payload["version"] == "0.1.0"
    assert payload["scope"] == "pilot"
    assert len(records) == 157
    assert len({r["id"] for r in records}) == 157
    for record in records:
        assert record["municipality_key"] == "yokohama-city"
        assert record["review_status"] == "reviewed"
        assert record["availability"] == "published"


def test_yokohama_assembly_and_session_match_contracts() -> None:
    assemblies = load_json(BASE / "assembly_records.json")
    sessions = load_json(BASE / "sessions.json")
    packets = load_json(BASE / "assembly_evidence_packets.json")

    assert len(assemblies) == 1
    assembly = assemblies[0]
    assert_valid("schemas/assembly.schema.json", assembly)
    assert assembly["id"] == ASSEMBLY_ID
    assert assembly["municipality_id"] == "jp-local-141003"
    assert assembly["name"] == "横浜市会"
    assert assembly["seat_count"] == 86
    assert assembly["term_start"] == "2023-04-30"
    assert assembly["term_end"] == "2027-04-29"
    assert sum(f["member_count"] for f in assembly["factions"]) == 86

    assert len(sessions) == 1
    assert_valid("schemas/session.schema.json", sessions[0])
    assert sessions[0]["id"] == SESSION_ID
    assert sessions[0]["start_date"] == "2026-09-07"
    assert sessions[0]["end_date"] == "2026-09-25"

    assert [p["subject_id"] for p in packets] == [ASSEMBLY_ID]
    for packet in packets:
        assert_valid("schemas/evidence_packet.schema.json", packet)


def test_yokohama_proposals_match_contract() -> None:
    proposals = load_json(BASE / "proposals.json")
    packets = load_json(BASE / "proposal_vote_evidence_packets.json")
    known_sources = catalog_record_ids()

    assert len(proposals) == 72
    kinds = Counter(p["kind"] for p in proposals)
    assert kinds == {
        "settlement": 24,
        "budget": 2,
        "ordinance": 3,
        "resolution": 5,
        "petition": 5,
        "personnel": 1,
        "other": 32,
    }
    outcomes = Counter(p["outcome"] for p in proposals)
    assert outcomes == {
        "approved": 33,
        "rejected": 3,
        "pending": 27,
        "not_assessable": 9,
    }
    for proposal in proposals:
        assert_valid("schemas/proposal.schema.json", proposal)
        assert proposal["assembly_id"] == ASSEMBLY_ID
        assert proposal["session_id"] == SESSION_ID
        assert proposal["related_fiscal_record_ids"] == []
        for source_id in proposal["sources"]:
            assert source_id in known_sources
    by_number = {}
    for p in proposals:
        by_number.setdefault(p["proposal_number"], []).append(p)
    # The acting mayor submitted the executive items (mayoral vacancy).
    assert by_number["市第42号議案"][0]["outcome"] == "approved"
    assert by_number["議第10号議案"][0]["outcome"] == "rejected"
    petitions = [p for p in proposals if p["kind"] == "petition"]
    assert len(petitions) == 5
    for petition in petitions:
        assert petition["submitted_by"] == "resident_petition"
        assert petition["submitted_at"] == "2026-09-09"
    # The FY2025 settlement package (24 certifications + 3 profit
    # dispositions) is still under review: no result is printed.
    pending = [p for p in proposals if p["outcome"] == "pending"]
    assert len(pending) == 27
    assert all(p["decided_at"] is None for p in pending)
    assert len([p for p in packets if p["subject_type"] == "proposal"]) == 72
    for packet in packets:
        assert_valid("schemas/evidence_packet.schema.json", packet)
    pending_packets = [
        p for p in packets
        if p["subject_type"] == "proposal"
        and any(pp["outcome"] == "pending" and pp["id"] == p["subject_id"] for pp in proposals)
    ]
    assert len(pending_packets) == 27
    assert all(p["open_questions"] for p in pending_packets)


def test_yokohama_votes_match_contract() -> None:
    proposals = load_json(BASE / "proposals.json")
    votes = load_json(BASE / "votes.json")
    faction_votes = load_json(BASE / "faction_votes.json")
    packets = load_json(BASE / "proposal_vote_evidence_packets.json")
    by_number = {}
    for p in proposals:
        by_number.setdefault(p["proposal_number"], []).append(p)
    vote_by_proposal = {v["proposal_id"]: v for v in votes}

    assert len(votes) == 63
    assert len([p for p in packets if p["subject_type"] == "vote"]) == 63
    # Report-only items and the by-election have no vote record.
    for proposal in proposals:
        if proposal["outcome"] == "not_assessable":
            assert proposal["id"] not in vote_by_proposal
    for vote in votes:
        assert_valid("schemas/vote.schema.json", vote)

    published = [v for v in votes if v["member_vote_availability"] == "published"]
    assert len(published) == 36
    for vote in published:
        # The chair (Watanabe Tadanori) does not vote; 85 members remain.
        assert len(vote["member_votes"]) == 85
        assert all(mv["member_name"] != "渡邊忠則" for mv in vote["member_votes"])
        assert vote["method"] == "unknown"
        positions = Counter(mv["position"] for mv in vote["member_votes"])
        assert positions["for"] == vote["totals"]["for"]
        assert positions["against"] == vote["totals"]["against"]
        assert positions["absent"] == vote["totals"]["absent"]
    for number, expected in EXPECTED_TOTALS.items():
        vote = vote_by_proposal[by_number[number][0]["id"]]
        assert vote["totals"] == expected, number
    retirement = next(
        v for v in votes
        if by_number["ー"][0]["id"] == v["proposal_id"] and v["vote_date"] == "2026-09-07"
    )
    assert retirement["totals"] == {"for": 84, "against": 0, "abstained": 0, "absent": 1}

    pending_votes = [v for v in votes if v["outcome"] == "pending"]
    assert len(pending_votes) == 27
    for vote in pending_votes:
        assert vote["member_votes"] == []
        assert vote["totals"] is None
        assert vote["member_vote_availability"] == "not_published"

    # Faction rows are an aggregation of the member tables into the 17
    # groups printed as column marks in the tables themselves.
    assert len(faction_votes) == 36 * 17
    for faction_vote in faction_votes:
        assert_valid("schemas/faction_vote.schema.json", faction_vote)
    for vote in published:
        rows = [fv for fv in faction_votes if fv["vote_id"] == vote["id"]]
        assert len(rows) == 17
        assert sum(fv["member_count"] for fv in rows) == 85
        assert sum(fv["for_count"] for fv in rows) == vote["totals"]["for"]
        assert sum(fv["against_count"] for fv in rows) == vote["totals"]["against"]


def test_yokohama_expenses_reconcile() -> None:
    expenses = load_json(BASE / "political_activity_expenses.json")
    packets = load_json(BASE / "expense_evidence_packets.json")

    assert len(expenses) == 62
    assert len(packets) == 62
    assert {p["subject_id"] for p in packets} == {e["id"] for e in expenses}
    assert Counter(e["fiscal_year"] for e in expenses) == {2023: 18, 2024: 22, 2025: 22}
    assert Counter(e["recipient_type"] for e in expenses) == {"faction": 16, "member": 46}
    for expense in expenses:
        assert_valid("schemas/political_activity_expense.schema.json", expense)
        assert expense["assembly_id"] == ASSEMBLY_ID
        assert expense["report_status"] == "published"
        # Receipts are viewable only at the assembly library.
        assert expense["receipt_access"] == "in_person_only"
        assert len(expense["breakdown"]) == 11
        assert sum(b["amount_yen"] for b in expense["breakdown"]) == expense["spent_yen"]
        assert expense["granted_yen"] - expense["spent_yen"] == expense["returned_yen"]
    for packet in packets:
        assert_valid("schemas/evidence_packet.schema.json", packet)

    komei = next(
        e for e in expenses
        if e["fiscal_year"] == 2024 and e["recipient_name"] == "公明党横浜市会議員団"
    )
    assert komei["granted_yen"] == 99_000_000
    assert komei["spent_yen"] == 97_342_509
    assert komei["returned_yen"] == 1_657_491
    jimin = next(
        e for e in expenses
        if e["fiscal_year"] == 2023 and e["recipient_name"] == "自由民主党横浜市会議員団"
    )
    assert jimin["granted_yen"] == 211_750_000
    assert jimin["spent_yen"] == 211_750_000
    assert jimin["returned_yen"] == 0


def test_yokohama_inspection_trips_match_contract() -> None:
    trips = load_json(BASE / "inspection_trips.json")
    packets = load_json(BASE / "inspection_evidence_packets.json")

    assert len(trips) == 73
    assert len(packets) == 73
    assert {p["subject_id"] for p in packets} == {t["id"] for t in trips}
    published = [t for t in trips if t["report_status"] == "published"]
    assert len(published) == 53
    assert sum(t["participant_count"] for t in published) == 536
    overseas = [t for t in trips if t["trip_type"] == "overseas"]
    assert len(overseas) == 1
    assert "仁川港湾公社（大韓民国 仁川広域市）" in overseas[0]["destinations"]
    for trip in trips:
        assert_valid("schemas/inspection_trip.schema.json", trip)
        assert trip["assembly_id"] == ASSEMBLY_ID
        assert trip["cost_status"] == "not_published"
        assert trip["total_cost_yen"] is None
        assert trip["cost_per_person_yen"] is None
        assert len(trip["destinations"]) >= 1
        if trip["report_status"] == "published":
            assert trip["participant_count"] == len(trip["participants"])
            assert trip["participant_count"] >= 8
        else:
            assert trip["participants"] == []
            assert trip["participant_count"] is None
    for packet in packets:
        assert_valid("schemas/evidence_packet.schema.json", packet)


def test_yokohama_disclosure_profile() -> None:
    profiles = load_json(BASE / "disclosure_profiles.json")
    assert len(profiles) == 1
    profile = profiles[0]
    assert_valid("schemas/disclosure_profile.schema.json", profile)
    assert profile["assembly_id"] == ASSEMBLY_ID
    items = {item["item"]: item for item in profile["items"]}
    assert len(items) == 12
    assert items["member_votes"]["availability"] == "published"
    # No official faction-level table for this session: aggregation only.
    assert items["faction_votes"]["availability"] == "not_published"
    assert items["political_activity_expense_receipts"]["availability"] == "restricted"
