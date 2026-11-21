"""Contract tests for the Kawaguchi City assembly registration (Issue #827).

The September 2026 regular session publishes only result wording: the
official results table has no vote-breakdown columns and the minutes
record standing votes only as "起立者全員 / 起立者多数", so every vote
follows the Fukuoka model (member_vote_availability: not_published).
FY2025 political activity expense reports are image-only PDFs for all
48 units (5 factions + 43 members); every unit was transcribed visually
and cross-checked against its printed category totals, and the 15 units
whose printed balance disagrees with granted minus spent are registered
with the published figures, the discrepancy recorded in their packets.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "reviewed" / "kawaguchi-city" / "assembly"
ASSEMBLY_ID = "jp-local-112038-assembly-2023"
SESSION_ID = "jp-local-112038-assembly-2023-session-2026-sep"

FACTION_COUNTS = {
    "自民党川口市議会議員団": 19,
    "公明党川口市議会議員団": 10,
    "日本共産党川口市議会議員団": 4,
    "川口青嵐会": 4,
    "川口新風会": 2,
    "川口維新": 1,
    "無所属": 1,
}
# Units whose printed balance (always 0) disagrees with granted - spent.
BALANCE_MISMATCHES = {
    "自民党川口市議会議員団",
    "日本共産党川口市議会議員団",
    "川口青嵐会",
    "荻野梓",
    "奥富精一",
    "藤田みつぐ",
    "榊原秀忠",
    "若谷正巳",
    "最上祐次",
    "坂本だいすけ",
    "吉田英司",
    "宇田川好秀",
    "松本幸恵",
    "金子幸弘",
    "菅野静華",
}


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_valid(schema_rel: str, instance: object) -> None:
    schema = load_json(ROOT / schema_rel)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
    assert errors == [], f"{schema_rel}: {[e.message for e in errors]}"


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


def test_kawaguchi_catalog_is_valid() -> None:
    catalog = load_json(ROOT / "data" / "catalog" / "kawaguchi_city_assembly_sources.json")
    assert_valid("schemas/source_catalog.schema.json", catalog)
    assert catalog["version"] == "0.1.0"
    assert catalog["scope"] == "pilot"
    # 18 general sources plus one report source per expense unit (48).
    assert len(catalog["records"]) == 66
    assert len({r["id"] for r in catalog["records"]}) == 66
    assert {r["municipality_key"] for r in catalog["records"]} == {"kawaguchi-city"}


def test_kawaguchi_assembly_and_session_match_contracts() -> None:
    records = load_json(BASE / "assembly_records.json")
    sessions = load_json(BASE / "sessions.json")
    packets = load_json(BASE / "assembly_evidence_packets.json")

    assert len(records) == 1
    assembly = records[0]
    assert_valid("schemas/assembly.schema.json", assembly)
    assert assembly["id"] == ASSEMBLY_ID
    assert assembly["municipality_id"] == "jp-local-112038"
    assert assembly["term_start"] == "2023-05-02"
    assert assembly["term_end"] == "2027-05-01"
    assert assembly["seat_count"] == 42
    # 41 sitting members (one vacancy) after the mid-session resignation.
    assert {f["name"]: f["member_count"] for f in assembly["factions"]} == FACTION_COUNTS
    assert sum(f["member_count"] for f in assembly["factions"]) == 41
    assert len(assembly["committees"]) == 10

    assert len(sessions) == 1
    assert_valid("schemas/session.schema.json", sessions[0])
    assert sessions[0]["id"] == SESSION_ID
    assert sessions[0]["start_date"] == "2026-09-01"
    assert sessions[0]["end_date"] == "2026-09-29"

    assert {p["subject_type"] for p in packets} == {
        "assembly",
        "session",
        "disclosure_profile",
    }
    for packet in packets:
        assert_valid("schemas/evidence_packet.schema.json", packet)
    assembly_packet = next(p for p in packets if p["subject_type"] == "assembly")
    # The seven inventory open questions stay open on the assembly packet.
    assert len(assembly_packet["open_questions"]) == 7


def test_kawaguchi_proposals_match_contract() -> None:
    proposals = load_json(BASE / "proposals.json")
    packets = load_json(BASE / "proposal_vote_evidence_packets.json")
    known_sources = catalog_record_ids()

    assert len(proposals) == 29
    kinds = Counter(p["kind"] for p in proposals)
    assert kinds == {
        "budget": 4,
        "ordinance": 7,
        "other": 13,
        "settlement": 4,
        "resolution": 1,
    }
    outcomes = Counter(p["outcome"] for p in proposals)
    assert outcomes == {"approved": 25, "pending": 4}
    for proposal in proposals:
        assert_valid("schemas/proposal.schema.json", proposal)
        assert proposal["assembly_id"] == ASSEMBLY_ID
        assert proposal["session_id"] == SESSION_ID
        assert proposal["related_fiscal_record_ids"] == []
        for source_id in proposal["sources"]:
            assert source_id in known_sources
    by_number = {p["proposal_number"]: p for p in proposals}
    # Bills 123-149 were submitted on the opening day; bill 152 is the
    # supplementary bill the stage-0 inventory missed (submitted 9/16).
    for n in range(123, 150):
        assert by_number[f"議案第{n}号"]["submitted_at"] == "2026-09-01"
    assert by_number["議案第152号"]["submitted_at"] == "2026-09-16"
    assert by_number["議案第152号"]["submitted_by"] == "executive"
    # Bills 150 and 151 do not appear in this session's results table.
    assert "議案第150号" not in by_number
    assert "議案第151号" not in by_number
    # The four FY2025 settlement bills are pending (continuing review by
    # the settlement special committee) and carry no decision date.
    for n in range(146, 150):
        bill = by_number[f"議案第{n}号"]
        assert bill["kind"] == "settlement"
        assert bill["outcome"] == "pending"
        assert bill["decided_at"] is None
    for proposal in proposals:
        if proposal["outcome"] == "approved":
            assert proposal["decided_at"] == "2026-09-29"
    # The single member-submitted item is the TKB opinion paper.
    opinion = by_number["議員提案第4号"]
    assert opinion["submitted_by"] == "member"
    assert opinion["submitted_at"] == "2026-09-29"
    assert opinion["kind"] == "resolution"
    assert len([p for p in packets if p["subject_type"] == "proposal"]) == 29
    # Each pending settlement packet points at the Issue #706 update cycle.
    for packet in packets:
        if packet["subject_type"] != "proposal":
            continue
        proposal = next(p for p in proposals if p["id"] == packet["subject_id"])
        if proposal["outcome"] == "pending":
            assert any("#706" in q for q in packet["open_questions"])


def test_kawaguchi_votes_match_contract() -> None:
    proposals = load_json(BASE / "proposals.json")
    votes = load_json(BASE / "votes.json")
    faction_votes = load_json(BASE / "faction_votes.json")
    packets = load_json(BASE / "proposal_vote_evidence_packets.json")

    # No faction or member breakdown is published anywhere, so there are
    # no faction vote rows at all (Fukuoka model).
    assert faction_votes == []
    assert len(votes) == 29
    assert len([p for p in packets if p["subject_type"] == "vote"]) == 29
    assert {v["proposal_id"] for v in votes} == {p["id"] for p in proposals}
    outcome_by_proposal = {p["id"]: p["outcome"] for p in proposals}
    for vote in votes:
        assert_valid("schemas/vote.schema.json", vote)
        assert vote["member_vote_availability"] == "not_published"
        assert vote["member_votes"] == []
        assert vote["totals"] is None
        assert vote["method"] == "standing"
        assert vote["vote_date"] == "2026-09-29"
        assert vote["outcome"] == outcome_by_proposal[vote["proposal_id"]]


def test_kawaguchi_expenses_match_contract() -> None:
    expenses = load_json(BASE / "political_activity_expenses.json")
    packets = load_json(BASE / "expense_evidence_packets.json")
    known_sources = catalog_record_ids()

    assert len(expenses) == 48
    assert len(packets) == 48
    assert {p["subject_id"] for p in packets} == {e["id"] for e in expenses}
    types = Counter(e["recipient_type"] for e in expenses)
    assert types == {"faction": 5, "member": 43}
    for expense in expenses:
        assert_valid("schemas/political_activity_expense.schema.json", expense)
        assert expense["assembly_id"] == ASSEMBLY_ID
        assert expense["fiscal_year"] == 2025
        assert expense["report_status"] == "published"
        assert expense["receipt_access"] == "online"
        assert len(expense["breakdown"]) == 11
        # Category amounts always add up to the printed total.
        assert sum(b["amount_yen"] for b in expense["breakdown"]) == expense["spent_yen"]
        for source_id in expense["sources"]:
            assert source_id in known_sources
    by_name = {e["recipient_name"]: e for e in expenses}
    # The LDP faction unit: spending exceeds the grant and the printed
    # balance is 0, so the published figures stand as registered.
    jimin = by_name["自民党川口市議会議員団"]
    assert (jimin["granted_yen"], jimin["spent_yen"], jimin["returned_yen"]) == (
        2170000,
        2215329,
        0,
    )
    # A fully consistent member unit (inventory spot check).
    sakaguchi = by_name["坂口安那"]
    assert (sakaguchi["granted_yen"], sakaguchi["spent_yen"], sakaguchi["returned_yen"]) == (
        170000,
        98350,
        71650,
    )
    mismatch_names = {
        e["recipient_name"]
        for e in expenses
        if e["granted_yen"] - e["spent_yen"] != e["returned_yen"]
    }
    assert mismatch_names == BALANCE_MISMATCHES
    # Every mismatch unit's packet records the discrepancy explicitly.
    packet_by_subject = {p["subject_id"]: p for p in packets}
    for expense in expenses:
        packet = packet_by_subject[expense["id"]]
        assert_valid("schemas/evidence_packet.schema.json", packet)
        statement = packet["claims"][0]["statement"]
        if expense["recipient_name"] in BALANCE_MISMATCHES:
            assert "一致しない" in statement
        else:
            assert "検算も一致した" in statement


def test_kawaguchi_inspection_trips_are_an_explicit_gap() -> None:
    trips = load_json(BASE / "inspection_trips.json")
    packets = load_json(BASE / "inspection_evidence_packets.json")

    # No assembly inspection-trip reports are published on the web, so
    # the trip list is intentionally empty and a gap packet records it.
    assert trips == []
    assert len(packets) == 1
    packet = packets[0]
    assert_valid("schemas/evidence_packet.schema.json", packet)
    assert packet["subject_type"] == "assembly"
    assert packet["subject_id"] == ASSEMBLY_ID


def test_kawaguchi_disclosure_profile() -> None:
    profiles = load_json(BASE / "disclosure_profiles.json")
    assert len(profiles) == 1
    profile = profiles[0]
    assert_valid("schemas/disclosure_profile.schema.json", profile)
    assert profile["assembly_id"] == ASSEMBLY_ID
    items = {item["item"]: item for item in profile["items"]}
    assert len(items) == 12
    # Vote breakdowns are published nowhere (Fukuoka model).
    assert items["faction_votes"]["availability"] == "not_published"
    assert items["member_votes"]["availability"] == "not_published"
    # Expense reports and receipts are published per unit online.
    assert items["political_activity_expense_reports"]["availability"] == "published"
    assert items["political_activity_expense_receipts"]["availability"] == "published"
    # Inspection trip reports have no web publication.
    assert items["inspection_trip_reports"]["availability"] == "not_published"
    # Petitions are voted in plenary and printed in the results table;
    # this session had none voted.
    assert items["petition_results"]["availability"] == "published"
