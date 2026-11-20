"""Cluster 4 stage 4: Sakai City assembly registration contract tests."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "reviewed" / "sakai-city" / "assembly"
CATALOG_PATH = ROOT / "data" / "catalog" / "sakai_city_assembly_sources.json"


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


ASSEMBLY_ID = "jp-local-271403-assembly-2023"
SESSION_ID = f"{ASSEMBLY_ID}-session-2026-4"

# Proposals whose faction votes are published (R8 4th regular session).
VOTED_WITH_FACTIONS = {f"議案第{n}号" for n in range(91, 100)} | {"議員提出議案第15号"}


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


def test_sakai_assembly_catalog_records_valid() -> None:
    payload = load_json(CATALOG_PATH)
    assert_valid("schemas/source_catalog.schema.json", payload)
    records = payload["records"]
    assert payload["version"] == "0.1.0"
    assert payload["scope"] == "pilot"
    # 18 assembly-level sources + 37 expense units x (page + PDF).
    assert len(records) == 92
    assert len({r["id"] for r in records}) == 92
    for record in records:
        assert record["municipality_key"] == "sakai-city"
        assert record["review_status"] == "reviewed"
        assert record["availability"] == "published"


def test_sakai_assembly_and_session_match_contracts() -> None:
    assemblies = load_json(BASE / "assembly_records.json")
    sessions = load_json(BASE / "sessions.json")
    packets = load_json(BASE / "assembly_evidence_packets.json")

    assert len(assemblies) == 1
    assembly = assemblies[0]
    assert_valid("schemas/assembly.schema.json", assembly)
    assert assembly["id"] == ASSEMBLY_ID
    assert assembly["municipality_id"] == "jp-local-271403"
    assert assembly["name"] == "堺市議会"
    assert assembly["seat_count"] == 48
    # Term end is printed by both election commissions; the start is the
    # day after the previous term's expiry (Public Offices Election Act
    # Article 259 proviso), documented in the evidence packet.
    assert assembly["term_start"] == "2023-05-01"
    assert assembly["term_end"] == "2027-04-30"
    # One seat is vacant: the factions sum to the 47 sitting members.
    assert sum(f["member_count"] for f in assembly["factions"]) == 47
    assert len(assembly["committees"]) == 10

    assert len(sessions) == 1
    assert_valid("schemas/session.schema.json", sessions[0])
    assert sessions[0]["id"] == SESSION_ID
    assert sessions[0]["start_date"] == "2026-08-17"
    assert sessions[0]["end_date"] == "2026-09-25"

    assert {p["subject_type"] for p in packets} == {
        "assembly",
        "session",
        "disclosure_profile",
    }
    for packet in packets:
        assert_valid("schemas/evidence_packet.schema.json", packet)


def test_sakai_proposals_match_contract() -> None:
    proposals = load_json(BASE / "proposals.json")
    packets = load_json(BASE / "proposal_vote_evidence_packets.json")
    known_sources = catalog_record_ids()

    assert len(proposals) == 61
    kinds = Counter(p["kind"] for p in proposals)
    assert kinds == {
        "settlement": 9,
        "ordinance": 4,
        "budget": 5,
        "personnel": 2,
        "resolution": 4,
        "petition": 19,
        "other": 18,
    }
    for proposal in proposals:
        assert_valid("schemas/proposal.schema.json", proposal)
        assert proposal["assembly_id"] == ASSEMBLY_ID
        assert proposal["session_id"] == SESSION_ID
        assert proposal["submitted_at"] is None
        assert proposal["related_fiscal_record_ids"] == []
        for source_id in proposal["sources"]:
            assert source_id in known_sources
    by_number = {p["proposal_number"]: p for p in proposals}
    # The nine FY2025 settlements were certified on 2026-09-25.
    for n in range(91, 100):
        assert by_number[f"議案第{n}号"]["outcome"] == "approved"
        assert by_number[f"議案第{n}号"]["decided_at"] == "2026-09-25"
    # Only the first supplementary budget was decided on opening day.
    assert by_number["議案第109号"]["decided_at"] == "2026-08-17"
    # The member-submitted opinion statement No. 19 was rejected.
    assert by_number["議員提出議案第19号"]["outcome"] == "rejected"
    # Report-only items (all but the 専決処分 approval) carry no decision
    # date in the official list and are not assessable.
    reports = [p for p in proposals if p["proposal_number"].startswith("報告第")]
    assert len(reports) == 10
    assert by_number["報告第15号"]["outcome"] == "approved"
    assert by_number["報告第15号"]["decided_at"] == "2026-09-25"
    for report in reports:
        if report["proposal_number"] == "報告第15号":
            continue
        assert report["outcome"] == "not_assessable"
        assert report["decided_at"] is None
    # Petitions are committee-reviewed answer documents, not plenary
    # adoption votes: no outcome vocabulary applies.
    petitions = [p for p in proposals if p["kind"] == "petition"]
    assert {p["proposal_number"] for p in petitions} == {
        f"陳情第{n}号" for n in range(42, 61)
    }
    for petition in petitions:
        assert petition["submitted_by"] == "resident_petition"
        assert petition["outcome"] == "not_assessable"
        assert petition["decided_at"] is None
    assert len([p for p in packets if p["subject_type"] == "proposal"]) == 61


def test_sakai_votes_match_contract() -> None:
    proposals = load_json(BASE / "proposals.json")
    votes = load_json(BASE / "votes.json")
    faction_votes = load_json(BASE / "faction_votes.json")
    packets = load_json(BASE / "proposal_vote_evidence_packets.json")
    by_number = {p["proposal_number"]: p for p in proposals}
    vote_by_proposal = {v["proposal_id"]: v for v in votes}

    # 33 decided items (42 session items minus the 9 report-only ones).
    assert len(votes) == 33
    assert len([p for p in packets if p["subject_type"] == "vote"]) == 33
    for proposal in proposals:
        if proposal["outcome"] == "not_assessable":
            assert proposal["id"] not in vote_by_proposal
    for vote in votes:
        assert_valid("schemas/vote.schema.json", vote)
        # Member-level votes are not published, and the voting method is
        # not stated: nothing is reconstructed or invented.
        assert vote["member_vote_availability"] == "not_published"
        assert vote["member_votes"] == []
        assert vote["method"] == "unknown"
        assert vote["totals"] is None

    # Faction votes exist only for the 10 published items, with 7 rows
    # each: the chair (長谷川俊英) takes no part in the vote under Local
    # Autonomy Act Article 116(2), so no row is created for the chair.
    assert len(faction_votes) == 70
    positions = Counter(fv["position"] for fv in faction_votes)
    assert positions == {"for": 60, "against": 10}
    fv_by_vote: dict[str, list[dict]] = {}
    for fv in faction_votes:
        assert_valid("schemas/faction_vote.schema.json", fv)
        fv_by_vote.setdefault(fv["vote_id"], []).append(fv)
    assert len(fv_by_vote) == 10
    for number in VOTED_WITH_FACTIONS:
        vote = vote_by_proposal[by_number[number]["id"]]
        rows = fv_by_vote[vote["id"]]
        assert len(rows) == 7
        # 47 sitting members minus the chair, who has no row.
        assert sum(r["member_count"] for r in rows) == 46
    # Settlement block A (bill 91): the Communists and 井関貴史 against.
    vote91 = vote_by_proposal[by_number["議案第91号"]["id"]]
    against91 = {
        r["faction_name"] for r in fv_by_vote[vote91["id"]] if r["position"] == "against"
    }
    assert against91 == {"日本共産党堺市議会議員団", "会派に属さない議員（井関貴史）"}
    # Settlement block B (bills 92-99, merged-cell display): 井関貴史
    # switches to "for"; only the Communists are against.
    for n in range(92, 100):
        vote = vote_by_proposal[by_number[f"議案第{n}号"]["id"]]
        against = {
            r["faction_name"] for r in fv_by_vote[vote["id"]] if r["position"] == "against"
        }
        assert against == {"日本共産党堺市議会議員団"}
    # Member bill 15 (harassment prevention ordinance): all factions for.
    vote15 = vote_by_proposal[by_number["議員提出議案第15号"]["id"]]
    assert all(r["position"] == "for" for r in fv_by_vote[vote15["id"]])


def test_sakai_expenses_reconcile() -> None:
    expenses = load_json(BASE / "political_activity_expenses.json")
    packets = load_json(BASE / "expense_evidence_packets.json")

    assert len(expenses) == 37
    assert len(packets) == 37
    assert {p["subject_id"] for p in packets} == {e["id"] for e in expenses}
    faction_count = 0
    member_count = 0
    for expense in expenses:
        assert_valid("schemas/political_activity_expense.schema.json", expense)
        assert expense["assembly_id"] == ASSEMBLY_ID
        assert expense["fiscal_year"] == 2025
        assert expense["report_status"] == "published"
        # Receipt PDFs are published on the web as well.
        assert expense["receipt_access"] == "online"
        assert len(expense["breakdown"]) == 9
        assert sum(b["amount_yen"] for b in expense["breakdown"]) == expense["spent_yen"]
        assert 0 <= expense["returned_yen"] <= expense["granted_yen"]
        if expense["recipient_type"] == "faction":
            faction_count += 1
        else:
            member_count += 1
    assert faction_count == 8
    assert member_count == 29
    for packet in packets:
        assert_valid("schemas/evidence_packet.schema.json", packet)
        assert packet["claims"][0]["source_ids"] == next(
            e["sources"] for e in expenses if e["id"] == packet["subject_id"]
        )

    by_name = {e["recipient_name"]: e for e in expenses}
    ishin = by_name["大阪維新の会堺市議会議員団"]
    assert ishin["granted_yen"] == 5_762_000
    assert ishin["spent_yen"] == 2_599_633
    assert ishin["returned_yen"] == 3_162_367
    komei = by_name["公明党堺市議団"]
    assert komei["granted_yen"] == 39_600_000
    assert komei["spent_yen"] == 39_586_674
    # Kibata spent beyond the grant from his own funds (printed as
    # その他・自己資金): the grant itself was fully charged.
    kibata = by_name["木畑匡"]
    assert kibata["granted_yen"] == 3_240_000
    assert kibata["spent_yen"] == 3_856_668
    assert kibata["returned_yen"] == 0


def test_sakai_inspection_trips_match_contract() -> None:
    trips = load_json(BASE / "inspection_trips.json")
    packets = load_json(BASE / "inspection_evidence_packets.json")

    assert len(trips) == 8
    assert len(packets) == 8
    assert {p["subject_id"] for p in packets} == {t["id"] for t in trips}
    for trip in trips:
        assert_valid("schemas/inspection_trip.schema.json", trip)
        assert trip["assembly_id"] == ASSEMBLY_ID
        assert trip["trip_type"] == "domestic"
        # Only committee, dates, cities and themes are published:
        # participants, reports and costs are not published.
        assert trip["participants"] == []
        assert trip["participant_count"] is None
        assert trip["report_status"] == "not_published"
        assert trip["cost_status"] == "not_published"
        assert trip["total_cost_yen"] is None
        assert trip["cost_per_person_yen"] is None
    for packet in packets:
        assert_valid("schemas/evidence_packet.schema.json", packet)


def test_sakai_disclosure_profile() -> None:
    profiles = load_json(BASE / "disclosure_profiles.json")
    assert len(profiles) == 1
    profile = profiles[0]
    assert_valid("schemas/disclosure_profile.schema.json", profile)
    assert profile["assembly_id"] == ASSEMBLY_ID
    items = {item["item"]: item for item in profile["items"]}
    assert len(items) == 11
    # Faction votes are published only for selected major bills.
    assert items["faction_votes"]["availability"] == "published"
    assert items["faction_votes"]["granularity"] == "faction"
    # Member votes are not published at all.
    assert items["member_votes"]["availability"] == "not_published"
    # Inspection trip reports are not published (list entries only).
    assert items["inspection_trip_reports"]["availability"] == "not_published"
    # Receipt PDFs are published on the web.
    assert items["political_activity_expense_receipts"]["availability"] == "published"
    assert items["political_activity_expense_receipts"]["granularity"] == "document"
