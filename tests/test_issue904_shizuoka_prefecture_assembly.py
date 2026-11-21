import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "reviewed" / "shizuoka-prefecture" / "assembly"
CATALOG = ROOT / "data" / "catalog" / "shizuoka_prefecture_assembly_sources.json"
ASSEMBLY_ID = "jp-local-220001-assembly-2023"
SESSION_ID = f"{ASSEMBLY_ID}-session-2026-09"


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def catalog():
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def source_ids():
    return {record["id"] for record in catalog()["records"]}


def test_catalog_is_shizuoka_prefecture_only():
    records = catalog()["records"]
    assert len(records) == 13
    assert {record["municipality_key"] for record in records} == {
        "shizuoka-prefecture"
    }
    assert len({record["id"] for record in records}) == 13
    categories = {record["category"] for record in records}
    assert {
        "assembly",
        "inspection_trips",
        "political_activity_expenses",
        "proposals",
    } <= categories


def test_assembly_record():
    records = load("assembly_records.json")
    assert len(records) == 1
    record = records[0]
    assert record["id"] == ASSEMBLY_ID
    assert record["municipality_id"] == "jp-local-220001"
    assert record["name"] == "静岡県議会"
    assert record["seat_count"] == 68
    assert record["term_start"] == "2023-04-30"
    # The stage-0 inventory's "2029-04-29" was an error; the term of the
    # members elected in the 2023 unified local elections ends 2027-04-29.
    assert record["term_end"] == "2027-04-29"
    assert [f["member_count"] for f in record["factions"]] == [
        39, 17, 5, 6,
    ]
    # Roster of 2026-07-14: 67 sitting members, one vacancy
    # (Hamamatsu City Chuo ward).
    assert sum(f["member_count"] for f in record["factions"]) == 67
    assert record["member_count_current"] == 67
    assert len(record["committees"]) == 11


def test_session_is_september_2026_regular_session():
    sessions = load("sessions.json")
    assert len(sessions) == 1
    session = sessions[0]
    assert session["id"] == SESSION_ID
    assert session["name"] == "令和8年9月定例会"
    assert session["session_type"] == "regular"
    assert session["start_date"] == "2026-09-18"
    assert session["end_date"] == "2026-10-15"


def test_proposals_cover_all_kinds_and_outcomes():
    proposals = load("proposals.json")
    assert len(proposals) == 43
    assert {p["session_id"] for p in proposals} == {SESSION_ID}
    by_submitter = {}
    for proposal in proposals:
        by_submitter[proposal["submitted_by"]] = (
            by_submitter.get(proposal["submitted_by"], 0) + 1
        )
    assert by_submitter == {
        "executive": 36,
        "member": 6,
        "resident_petition": 1,
    }
    kinds = {}
    for proposal in proposals:
        kinds[proposal["kind"]] = kinds.get(proposal["kind"], 0) + 1
    assert kinds == {
        "budget": 3,
        "ordinance": 3,
        "other": 13,
        "personnel": 1,
        "settlement": 17,
        "petition": 1,
        "resolution": 5,
    }
    pending = [p for p in proposals if p["outcome"] == "pending"]
    assert len(pending) == 17
    assert {p["kind"] for p in pending} == {"settlement"}
    assert all(p["decided_at"] is None for p in pending)
    rejected = [p for p in proposals if p["outcome"] == "rejected"]
    assert len(rejected) == 1
    assert rejected[0]["proposal_number"] == "請願第1号"


def test_votes_are_faction_and_independent_member_records():
    votes = load("votes.json")
    proposals = {p["id"]: p for p in load("proposals.json")}
    assert len(votes) == 25
    decided = {
        p["id"] for p in proposals.values() if p["outcome"] == "approved"
    }
    assert {v["proposal_id"] for v in votes} == decided
    independents = {
        "大石哲司", "木内満", "遠藤行洋", "塚本大", "桜井勝郎", "山本隆久",
    }
    for vote in votes:
        assert vote["member_vote_availability"] == "published"
        assert vote["vote_date"] == "2026-10-15"
        # The published table gives no numeric totals, only marks.
        assert vote["totals"] is None
        assert {m["member_name"] for m in vote["member_votes"]} == independents
        assert all(m["position"] == "for" for m in vote["member_votes"])


def test_faction_votes_cover_three_factions_for_every_vote():
    faction_votes = load("faction_votes.json")
    votes = load("votes.json")
    assert len(faction_votes) == 25 * 3
    assert {fv["vote_id"] for fv in faction_votes} == {v["id"] for v in votes}
    assert {fv["faction_name"] for fv in faction_votes} == {
        "自民改革会議", "ふじのくに県民クラブ", "公明党静岡県議団",
    }
    assert all(fv["position"] == "for" for fv in faction_votes)


def test_petition_has_no_vote_record():
    # Petition No. 1 was deemed rejected (みなし不採択) when the member
    # bill redrawing the Izu City district passed; no ballot was taken,
    # so the published table leaves the vote columns blank.
    proposals = {p["id"]: p for p in load("proposals.json")}
    petition = next(
        p for p in proposals.values() if p["kind"] == "petition"
    )
    votes = load("votes.json")
    assert petition["id"] not in {v["proposal_id"] for v in votes}


def test_expenses_cover_eight_recipient_units():
    expenses = load("political_activity_expenses.json")
    assert len(expenses) == 8
    assert {e["fiscal_year"] for e in expenses} == {2025}
    assert sum(e["granted_yen"] for e in expenses) == 367_200_000
    assert sum(e["spent_yen"] for e in expenses) == 319_311_921
    assert sum(e["returned_yen"] for e in expenses) == 47_888_079
    assert {e["recipient_type"] for e in expenses} == {"faction"}
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
    assert len(trips) == 7
    assert {t["cost_status"] for t in trips} == {"not_published"}
    assert {t["trip_type"] for t in trips} == {"domestic"}
    assert all(t["total_cost_yen"] is None for t in trips)
    assert all(t["report_status"] == "published" for t in trips)
    assert all(
        t["participant_count"] == len(t["participants"]) for t in trips
    )
    assert all(t["start_date"].startswith("2026-07") for t in trips)
    committees = {t["title"].split("委員会")[0] for t in trips}
    assert len(committees) == 7


def test_disclosure_profile_notes():
    profiles = load("disclosure_profiles.json")
    assert len(profiles) == 1
    items = {item["item"]: item for item in profiles[0]["items"]}
    assert len(items) == 12
    assert items["faction_votes"]["availability"] == "published"
    assert items["faction_votes"]["granularity"] == "faction"
    assert "事後記録" in items["faction_votes"]["note"]
    assert items["member_votes"]["availability"] == "published"
    assert items["member_votes"]["granularity"] == "member"
    assert "事後記録" in items["member_votes"]["note"]
    assert "みなし不採択" in items["petition_results"]["note"]


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
    settlement_packets = [
        p for p in pv
        if p["subject_type"] == "proposal"
        and p["subject_id"].endswith(tuple(
            f"settlement-{i:02d}" for i in range(1, 18)
        ))
    ]
    assert len(settlement_packets) == 17
    assert all(p["open_questions"] for p in settlement_packets)
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
        "faction_votes.json",
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
