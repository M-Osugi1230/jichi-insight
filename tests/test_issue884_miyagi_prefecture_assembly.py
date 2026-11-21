import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "reviewed" / "miyagi-prefecture" / "assembly"
CATALOG = ROOT / "data" / "catalog" / "miyagi_prefecture_assembly_sources.json"
ASSEMBLY_ID = "jp-local-040002-assembly-2023"
SESSION_ID = f"{ASSEMBLY_ID}-session-2026-401"


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def catalog():
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def source_ids():
    return {record["id"] for record in catalog()["records"]}


def test_catalog_is_miyagi_prefecture_only():
    records = catalog()["records"]
    assert len(records) == 21
    assert {record["municipality_key"] for record in records} == {
        "miyagi-prefecture"
    }
    assert len({record["id"] for record in records}) == 21
    categories = {record["category"] for record in records}
    assert {
        "assembly",
        "election",
        "inspection_trips",
        "political_activity_expenses",
        "proposals",
    } <= categories


def test_assembly_record():
    records = load("assembly_records.json")
    assert len(records) == 1
    record = records[0]
    assert record["id"] == ASSEMBLY_ID
    assert record["municipality_id"] == "jp-local-040002"
    assert record["name"] == "宮城県議会"
    assert record["seat_count"] == 59
    assert record["term_start"] == "2023-11-13"
    assert record["term_end"] == "2027-11-12"
    assert [f["member_count"] for f in record["factions"]] == [
        30, 9, 5, 4, 3, 2, 2,
    ]
    assert sum(f["member_count"] for f in record["factions"]) == 55
    assert len(record["committees"]) == 14


def test_session_is_401st_regular_session():
    sessions = load("sessions.json")
    assert len(sessions) == 1
    session = sessions[0]
    assert session["id"] == SESSION_ID
    assert session["name"] == "令和8年9月第401回定例会"
    assert session["session_type"] == "regular"
    assert session["start_date"] == "2026-09-10"
    assert session["end_date"] == "2026-10-14"


def test_proposals_cover_all_kinds_and_outcomes():
    proposals = load("proposals.json")
    assert len(proposals) == 29
    assert {p["session_id"] for p in proposals} == {SESSION_ID}
    by_submitter = {}
    for proposal in proposals:
        by_submitter[proposal["submitted_by"]] = (
            by_submitter.get(proposal["submitted_by"], 0) + 1
        )
    assert by_submitter == {
        "executive": 20,
        "member": 7,
        "resident_petition": 2,
    }
    kinds = {}
    for proposal in proposals:
        kinds[proposal["kind"]] = kinds.get(proposal["kind"], 0) + 1
    assert kinds == {
        "budget": 2,
        "ordinance": 6,
        "other": 8,
        "personnel": 2,
        "settlement": 2,
        "resolution": 7,
        "petition": 2,
    }
    pending = [p for p in proposals if p["outcome"] == "pending"]
    assert len(pending) == 1
    assert pending[0]["proposal_number"] == "第401-2号"
    assert pending[0]["decided_at"] is None
    settlements = [p for p in proposals if p["kind"] == "settlement"]
    assert all(p["outcome"] == "approved" for p in settlements)
    personnel = [p for p in proposals if p["kind"] == "personnel"]
    assert {p["decided_at"] for p in personnel} == {"2026-09-30"}


def test_votes_are_individual_member_records():
    votes = load("votes.json")
    proposals = {p["id"]: p for p in load("proposals.json")}
    assert len(votes) == 28
    assert sum(len(v["member_votes"]) for v in votes) == 28 * 56
    decided = {p["id"] for p in proposals.values() if p["outcome"] == "approved"}
    assert {v["proposal_id"] for v in votes} == decided
    for vote in votes:
        assert vote["member_vote_availability"] == "published"
        assert len(vote["member_votes"]) == 56
        counts = {"for": 0, "against": 0, "abstain": 0, "absent": 0, "excused": 0}
        for member_vote in vote["member_votes"]:
            counts[member_vote["position"]] += 1
        assert counts["for"] == vote["totals"]["for"]
        assert counts["against"] == vote["totals"]["against"]
        assert counts["absent"] == vote["totals"]["absent"]
        assert counts["excused"] == 1
        chair = [m for m in vote["member_votes"] if m["position"] == "excused"]
        assert chair[0]["member_name"] == "佐々木幸士"


def test_settlement_votes_split_fifty_to_five():
    votes = {v["proposal_id"]: v for v in load("votes.json")}
    proposals = {p["id"]: p for p in load("proposals.json")}
    settlements = [pid for pid, p in proposals.items() if p["kind"] == "settlement"]
    assert len(settlements) == 2
    for pid in settlements:
        vote = votes[pid]
        assert vote["method"] == "standing"
        assert vote["totals"]["for"] == 50
        assert vote["totals"]["against"] == 5
        against = {
            m["member_name"] for m in vote["member_votes"]
            if m["position"] == "against"
        }
        assert against == {
            "ふなやま由美", "藤原益栄", "金田もとる", "天下みゆき", "三浦一敏",
        }


def test_personnel_vote_has_one_absence():
    votes = {v["proposal_id"]: v for v in load("votes.json")}
    proposals = {p["id"]: p for p in load("proposals.json")}
    personnel = [pid for pid, p in proposals.items() if p["kind"] == "personnel"]
    for pid in personnel:
        vote = votes[pid]
        assert vote["vote_date"] == "2026-09-30"
        absent = [
            m["member_name"] for m in vote["member_votes"]
            if m["position"] == "absent"
        ]
        assert absent == ["菊地恵一"]


def test_faction_votes_are_not_aggregated():
    # Miyagi publishes individual member votes only; no faction-level record.
    assert load("faction_votes.json") == []


def test_expenses_cover_eight_recipient_units():
    expenses = load("political_activity_expenses.json")
    assert len(expenses) == 8
    assert {e["fiscal_year"] for e in expenses} == {2025}
    assert sum(e["granted_yen"] for e in expenses) == 242_550_000
    assert sum(e["spent_yen"] for e in expenses) == 189_463_400
    recipient_types = [e["recipient_type"] for e in expenses]
    assert recipient_types.count("faction") == 7
    assert recipient_types.count("member") == 1
    for expense in expenses:
        assert expense["granted_yen"] - expense["spent_yen"] == (
            expense["returned_yen"]
        )
        assert sum(b["amount_yen"] for b in expense["breakdown"]) == (
            expense["spent_yen"]
        )
        assert len(expense["breakdown"]) == 10
        assert expense["report_status"] == "published"
        assert expense["receipt_access"] == "online"


def test_inspection_trips_are_fy2026_committee_trips():
    trips = load("inspection_trips.json")
    assert len(trips) == 20
    assert {t["cost_status"] for t in trips} == {"not_published"}
    assert {t["trip_type"] for t in trips} == {"domestic"}
    assert all(t["total_cost_yen"] is None for t in trips)
    assert all(t["report_status"] == "published" for t in trips)
    assert all(
        t["participant_count"] == len(t["participants"]) for t in trips
    )
    assert all(t["start_date"].startswith("2026-") for t in trips)
    committees = {t["title"].split("委員会")[0] for t in trips}
    assert len(committees) == 10


def test_disclosure_profile_notes():
    profiles = load("disclosure_profiles.json")
    assert len(profiles) == 1
    items = {item["item"]: item for item in profiles[0]["items"]}
    assert len(items) == 12
    assert items["member_votes"]["availability"] == "published"
    assert items["member_votes"]["granularity"] == "member"
    assert "事後記録" in items["member_votes"]["note"]
    assert items["faction_votes"]["availability"] == "not_published"
    assert "陳情" in items["petition_results"]["note"]
    assert "本会議" in items["petition_results"]["note"]


def test_evidence_packets_cover_every_record():
    proposals = {p["id"] for p in load("proposals.json")}
    votes = {v["id"] for v in load("votes.json")}
    pv = load("proposal_vote_evidence_packets.json")
    assert {p["subject_id"] for p in pv if p["subject_type"] == "proposal"} == (
        proposals
    )
    assert {p["subject_id"] for p in pv if p["subject_type"] == "vote"} == votes
    vote_packets = [p for p in pv if p["subject_type"] == "vote"]
    assert all(
        "事後記録" in claim["review_note"]
        for packet in vote_packets
        for claim in packet["claims"]
    )
    expenses = {e["id"] for e in load("political_activity_expenses.json")}
    ex = load("expense_evidence_packets.json")
    assert {p["subject_id"] for p in ex} == expenses
    trips = {t["id"] for t in load("inspection_trips.json")}
    ins = load("inspection_evidence_packets.json")
    assert {p["subject_id"] for p in ins} == trips
    assembly_packets = load("assembly_evidence_packets.json")
    assert {p["subject_id"] for p in assembly_packets} == {ASSEMBLY_ID}
    assert assembly_packets[0]["open_questions"]


def test_all_sources_resolve_to_catalog():
    ids = source_ids()
    for name in (
        "assembly_records.json",
        "sessions.json",
        "proposals.json",
        "votes.json",
        "political_activity_expenses.json",
        "inspection_trips.json",
        "disclosure_profiles.json",
    ):
        for record in load(name):
            assert set(record["sources"]) <= ids, (name, record["id"])
    for name in (
        "assembly_evidence_packets.json",
        "proposal_vote_evidence_packets.json",
        "expense_evidence_packets.json",
        "inspection_evidence_packets.json",
    ):
        for packet_record in load(name):
            for claim_record in packet_record["claims"]:
                assert set(claim_record["source_ids"]) <= ids
