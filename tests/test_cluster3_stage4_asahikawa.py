"""Cluster 3 stage 4: Asahikawa City assembly registration contract tests."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "reviewed" / "asahikawa-city" / "assembly"
CATALOG_PATH = ROOT / "data" / "catalog" / "asahikawa_city_assembly_sources.json"


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

ASSEMBLY_ID = "jp-local-012041-assembly-2023"
SESSION_ID = f"{ASSEMBLY_ID}-session-2026-3"

DIVIDED_NUMBERS = {
    "認定第1号",
    "認定第9号",
    "認定第10号",
    "議案第1号",
    "意見書案第1号",
    "意見書案第2号",
    "意見書案第3号",
    "陳情第46号",
}
EXPECTED_TOTALS = {
    "認定第1号": {"for": 28, "against": 4, "abstained": 0, "absent": 1},
    "認定第9号": {"for": 28, "against": 4, "abstained": 0, "absent": 1},
    "認定第10号": {"for": 28, "against": 4, "abstained": 0, "absent": 1},
    "議案第1号": {"for": 29, "against": 4, "abstained": 0, "absent": 0},
    "意見書案第1号": {"for": 15, "against": 17, "abstained": 0, "absent": 1},
    "意見書案第2号": {"for": 20, "against": 12, "abstained": 0, "absent": 1},
    "意見書案第3号": {"for": 15, "against": 17, "abstained": 0, "absent": 1},
    "陳情第46号": {"for": 7, "against": 26, "abstained": 0, "absent": 0},
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


def test_asahikawa_assembly_catalog_records_valid() -> None:
    payload = load_json(CATALOG_PATH)
    assert_valid("schemas/source_catalog.schema.json", payload)
    records = payload["records"]
    assert payload["version"] == "0.1.0"
    assert payload["scope"] == "pilot"
    assert len(records) == 35
    assert len({r["id"] for r in records}) == 35
    for record in records:
        assert record["municipality_key"] == "asahikawa-city"
        assert record["review_status"] == "reviewed"
        assert record["availability"] == "published"


def test_asahikawa_assembly_and_session_match_contracts() -> None:
    assemblies = load_json(BASE / "assembly_records.json")
    sessions = load_json(BASE / "sessions.json")
    packets = load_json(BASE / "assembly_evidence_packets.json")

    assert len(assemblies) == 1
    assembly = assemblies[0]
    assert_valid("schemas/assembly.schema.json", assembly)
    assert assembly["id"] == ASSEMBLY_ID
    assert assembly["municipality_id"] == "jp-local-012041"
    assert assembly["name"] == "旭川市議会"
    assert assembly["seat_count"] == 34
    # Term start is documented on the council site; the end date is printed
    # in the Hokkaido Election Administration Commission's term-expiry list.
    assert assembly["term_start"] == "2023-05-02"
    assert assembly["term_end"] == "2027-05-01"
    assert sum(f["member_count"] for f in assembly["factions"]) == 34

    assert len(sessions) == 1
    assert_valid("schemas/session.schema.json", sessions[0])
    assert sessions[0]["id"] == SESSION_ID
    assert sessions[0]["start_date"] == "2026-09-09"
    assert sessions[0]["end_date"] == "2026-10-08"

    assert [p["subject_id"] for p in packets] == [ASSEMBLY_ID]
    for packet in packets:
        assert_valid("schemas/evidence_packet.schema.json", packet)


def test_asahikawa_proposals_match_contract() -> None:
    proposals = load_json(BASE / "proposals.json")
    packets = load_json(BASE / "proposal_vote_evidence_packets.json")
    known_sources = catalog_record_ids()

    assert len(proposals) == 55
    kinds = Counter(p["kind"] for p in proposals)
    assert kinds == {
        "settlement": 11,
        "budget": 4,
        "ordinance": 2,
        "personnel": 4,
        "resolution": 11,
        "petition": 12,
        "other": 11,
    }
    # The 14 petitions left under continued review are not registered.
    petitions = [p for p in proposals if p["kind"] == "petition"]
    assert {p["proposal_number"] for p in petitions} == {
        f"陳情第{n}号" for n in (20, 25, 26, 27, 28, 37, 38, 40, 46, 48, 50, 51)
    }
    for proposal in proposals:
        assert_valid("schemas/proposal.schema.json", proposal)
        assert proposal["assembly_id"] == ASSEMBLY_ID
        assert proposal["session_id"] == SESSION_ID
        # The proposal list prints no submission dates.
        assert proposal["submitted_at"] is None
        assert proposal["related_fiscal_record_ids"] == []
        for source_id in proposal["sources"]:
            assert source_id in known_sources
    by_number = {p["proposal_number"]: p for p in proposals}
    # The FY2025 settlements were certified as printed (never a rejection).
    assert by_number["認定第1号"]["outcome"] == "approved"
    assert by_number["意見書案第1号"]["outcome"] == "rejected"
    # The petition vote is a vote on adoption: 7 for, yet not adopted.
    assert by_number["陳情第46号"]["outcome"] == "rejected"
    assert by_number["陳情第46号"]["submitted_by"] == "resident_petition"
    # Report-only items have no vote outcome to assess.
    reports_no_vote = [
        p
        for p in proposals
        if p["proposal_number"] in {"報告第1号", "報告第2号", "報告第5号", "報告第6号", "報告第7号"}
    ]
    assert all(p["outcome"] == "not_assessable" for p in reports_no_vote)
    assert len([p for p in packets if p["subject_type"] == "proposal"]) == 55


def test_asahikawa_votes_match_contract() -> None:
    proposals = load_json(BASE / "proposals.json")
    votes = load_json(BASE / "votes.json")
    faction_votes = load_json(BASE / "faction_votes.json")
    packets = load_json(BASE / "proposal_vote_evidence_packets.json")
    by_number = {p["proposal_number"]: p for p in proposals}
    vote_by_proposal = {v["proposal_id"]: v for v in votes}

    assert len(votes) == 50
    assert len([p for p in packets if p["subject_type"] == "vote"]) == 50
    # No vote record exists for the five report-only items.
    assert len(vote_by_proposal) == 50
    for proposal in proposals:
        if proposal["outcome"] == "not_assessable":
            assert proposal["id"] not in vote_by_proposal
    for vote in votes:
        assert_valid("schemas/vote.schema.json", vote)

    divided = {
        number: vote_by_proposal[by_number[number]["id"]] for number in DIVIDED_NUMBERS
    }
    for number, vote in divided.items():
        assert vote["member_vote_availability"] == "published"
        assert len(vote["member_votes"]) == 34
        # The council's publication does not state the voting method.
        assert vote["method"] == "unknown"
        assert vote["totals"] == EXPECTED_TOTALS[number]
        positions = Counter(mv["position"] for mv in vote["member_votes"])
        assert positions["for"] == EXPECTED_TOTALS[number]["for"]
        assert positions["against"] == EXPECTED_TOTALS[number]["against"]
        assert positions["absent"] == EXPECTED_TOTALS[number]["absent"]
        # The chair does not take part in the vote (printed note).
        assert positions["excused"] == 1

    # Unanimous items publish only the fact of unanimity: no member rows
    # are fabricated and no totals are invented.
    for proposal in proposals:
        if proposal["id"] not in vote_by_proposal:
            continue
        vote = vote_by_proposal[proposal["id"]]
        if proposal["proposal_number"] in DIVIDED_NUMBERS:
            continue
        assert vote["method"] == "unanimous"
        assert vote["member_vote_availability"] == "not_published"
        assert vote["member_votes"] == []
        assert vote["totals"] is None

    # Faction rows are an aggregation of the published member tables.
    assert len(faction_votes) == 48
    member_by_vote: dict[str, list[dict]] = {v["id"]: v["member_votes"] for v in votes}
    for faction_vote in faction_votes:
        assert_valid("schemas/faction_vote.schema.json", faction_vote)
        members = member_by_vote[faction_vote["vote_id"]]
        assert faction_vote["member_count"] <= len(members)
    for vote in divided.values():
        rows = [fv for fv in faction_votes if fv["vote_id"] == vote["id"]]
        assert len(rows) == 6
        assert sum(fv["member_count"] for fv in rows) == 34
        assert sum(fv["for_count"] for fv in rows) == vote["totals"]["for"]
        assert sum(fv["against_count"] for fv in rows) == vote["totals"]["against"]


def test_asahikawa_expenses_reconcile() -> None:
    expenses = load_json(BASE / "political_activity_expenses.json")
    packets = load_json(BASE / "expense_evidence_packets.json")

    assert len(expenses) == 8
    assert len(packets) == 8
    assert {p["subject_id"] for p in packets} == {e["id"] for e in expenses}
    faction_count = 0
    member_count = 0
    for expense in expenses:
        assert_valid("schemas/political_activity_expense.schema.json", expense)
        assert expense["assembly_id"] == ASSEMBLY_ID
        assert expense["fiscal_year"] == 2025
        assert expense["report_status"] == "published"
        # Receipt copies are published online (unlike Nagoya's in-person rule).
        assert expense["receipt_access"] == "online"
        assert len(expense["breakdown"]) == 9
        assert sum(b["amount_yen"] for b in expense["breakdown"]) == expense["spent_yen"]
        assert expense["granted_yen"] - expense["spent_yen"] == expense["returned_yen"]
        if expense["recipient_type"] == "faction":
            faction_count += 1
        else:
            member_count += 1
    assert faction_count == 5
    assert member_count == 3
    for packet in packets:
        assert_valid("schemas/evidence_packet.schema.json", packet)
        assert packet["claims"][0]["source_ids"] == next(
            e["sources"] for e in expenses if e["id"] == packet["subject_id"]
        )

    jimin = next(e for e in expenses if e["recipient_name"] == "自民党・市民会議")
    assert jimin["granted_yen"] == 11_920_000
    assert jimin["spent_yen"] == 6_969_920
    assert jimin["returned_yen"] == 4_950_080
    # The resubmitted statement is the registered original for Minshu.
    minshu = next(e for e in expenses if e["recipient_name"] == "民主・市民連合")
    assert minshu["spent_yen"] == 2_699_695
    assert "再提出" in next(
        p for p in packets if p["subject_id"] == minshu["id"]
    )["claims"][0]["statement"]


def test_asahikawa_inspection_trips_match_contract() -> None:
    trips = load_json(BASE / "inspection_trips.json")
    packets = load_json(BASE / "inspection_evidence_packets.json")

    assert len(trips) == 4
    assert len(packets) == 4
    assert {p["subject_id"] for p in packets} == {t["id"] for t in trips}
    for trip in trips:
        assert_valid("schemas/inspection_trip.schema.json", trip)
        assert trip["assembly_id"] == ASSEMBLY_ID
        assert trip["trip_type"] == "domestic"
        assert trip["report_status"] == "published"
        # Costs are not published in the overview; nothing is invented.
        assert trip["cost_status"] == "not_published"
        assert trip["total_cost_yen"] is None
        assert trip["cost_per_person_yen"] is None
        # All published inspection members are recorded, not just a reporter.
        assert trip["participant_count"] == 8
        assert len(trip["participants"]) == 8
    committees = {t["title"].split("視察")[0] for t in trips}
    assert committees == {
        "総務常任委員会",
        "民生常任委員会",
        "経済建設常任委員会",
        "子育て文教常任委員会",
    }
    for packet in packets:
        assert_valid("schemas/evidence_packet.schema.json", packet)


def test_asahikawa_disclosure_profile() -> None:
    profiles = load_json(BASE / "disclosure_profiles.json")
    assert len(profiles) == 1
    profile = profiles[0]
    assert_valid("schemas/disclosure_profile.schema.json", profile)
    assert profile["assembly_id"] == ASSEMBLY_ID
    items = {item["item"]: item for item in profile["items"]}
    assert len(items) == 12
    # Member votes are published only for divided items.
    assert items["member_votes"]["availability"] == "published"
    # No independent faction-vote publication exists.
    assert items["faction_votes"]["availability"] == "not_published"
    # Receipt copies are published on the web.
    assert items["political_activity_expense_receipts"]["availability"] == "published"
    assert items["political_activity_expense_receipts"]["granularity"] == "document"
