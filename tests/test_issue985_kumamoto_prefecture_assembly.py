import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "reviewed" / "kumamoto-prefecture" / "assembly"
CATALOG = ROOT / "data" / "catalog" / "kumamoto_prefecture_assembly_sources.json"
ASSEMBLY_ID = "jp-local-430005-assembly-2023"
SESSION_ID = f"{ASSEMBLY_ID}-session-2026-08"


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def catalog():
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def source_ids():
    return {record["id"] for record in catalog()["records"]}


def test_catalog_is_kumamoto_prefecture_only():
    records = catalog()["records"]
    assert len(records) == 12
    assert {record["municipality_key"] for record in records} == {
        "kumamoto-prefecture"
    }
    assert len({record["id"] for record in records}) == 12
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
    assert record["municipality_id"] == "jp-local-430005"
    assert record["name"] == "熊本県議会"
    assert record["seat_count"] == 49
    assert record["term_start"] == "2023-04-30"
    assert record["term_end"] == "2027-04-29"
    assert [f["member_count"] for f in record["factions"]] == [
        35, 3, 3, 1, 1, 1, 3,
    ]
    assert sum(f["member_count"] for f in record["factions"]) == 47
    assert len(record["committees"]) == 11


def test_session_is_august_2026_regular_session():
    sessions = load("sessions.json")
    assert len(sessions) == 1
    session = sessions[0]
    assert session["id"] == SESSION_ID
    assert session["name"] == "令和8年8月定例会"
    assert session["session_type"] == "regular"
    # The opening day could not be fixed from primary sources; the closing
    # day is the main voting day, 2026-09-08.
    assert session["start_date"] is None
    assert session["end_date"] == "2026-09-08"


def test_proposals_cover_all_kinds_and_outcomes():
    proposals = load("proposals.json")
    assert len(proposals) == 103
    assert {p["session_id"] for p in proposals} == {SESSION_ID}
    by_submitter = {}
    for proposal in proposals:
        by_submitter[proposal["submitted_by"]] = (
            by_submitter.get(proposal["submitted_by"], 0) + 1
        )
    assert by_submitter == {"executive": 101, "member": 2}
    kinds = {}
    for proposal in proposals:
        kinds[proposal["kind"]] = kinds.get(proposal["kind"], 0) + 1
    assert kinds == {
        "budget": 7,
        "ordinance": 9,
        "other": 63,
        "personnel": 1,
        "resolution": 2,
        "settlement": 21,
    }
    pending = [p for p in proposals if p["outcome"] == "pending"]
    assert len(pending) == 21
    assert {p["proposal_number"] for p in pending} == {
        f"第{n}号" for n in range(38, 59)
    }
    assert all(p["kind"] == "settlement" for p in pending)
    assert all(p["decided_at"] is None for p in pending)
    reports = [p for p in proposals if p["outcome"] == "not_assessable"]
    assert len(reports) == 37
    assert {p["proposal_number"] for p in reports} == {
        f"報告第{n}号" for n in range(1, 38)
    }
    early = [p for p in proposals if p["proposal_number"] == "第59号"]
    assert early[0]["decided_at"] == "2026-08-31"
    decided = [
        p for p in proposals
        if p["outcome"] == "approved" and p["proposal_number"] != "第59号"
    ]
    assert {p["decided_at"] for p in decided} == {"2026-09-08"}


def test_votes_are_individual_member_records():
    votes = load("votes.json")
    proposals = {p["id"]: p for p in load("proposals.json")}
    assert len(votes) == 66
    assert sum(len(v["member_votes"]) for v in votes) == 66 * 47
    voted = {
        p["id"] for p in proposals.values()
        if p["outcome"] in ("approved", "pending")
    }
    assert {v["proposal_id"] for v in votes} == voted
    for vote in votes:
        assert vote["member_vote_availability"] == "published"
        assert vote["method"] == "unknown"
        assert len(vote["member_votes"]) == 47
        chair = [
            m for m in vote["member_votes"] if m["position"] == "excused"
        ]
        assert chair[0]["member_name"] == "内野幸喜"
        proposal = proposals[vote["proposal_id"]]
        if proposal["outcome"] == "pending":
            assert vote["totals"] is None
            positions = [m["position"] for m in vote["member_votes"]]
            assert positions.count("for") == 46
            assert positions.count("excused") == 1
        else:
            counts = {"for": 0, "against": 0, "abstained": 0, "absent": 0}
            for member_vote in vote["member_votes"]:
                if member_vote["position"] in counts:
                    counts[member_vote["position"]] += 1
            assert counts == vote["totals"]


def test_abstention_and_recusal_marks():
    votes = {v["proposal_id"]: v for v in load("votes.json")}
    proposals = {p["id"]: p for p in load("proposals.json")}
    abstained = [
        pid for pid, v in votes.items()
        if v["totals"] is not None and v["totals"]["abstained"] == 1
    ]
    # Matsumura Shuichi abstained (△) on executive proposals No. 1-37
    # and No. 60-63, and voted for No. 59, No. 64 and both member bills.
    assert len(abstained) == 41
    numbers = {proposals[pid]["proposal_number"] for pid in abstained}
    assert numbers == {
        f"第{n}号" for n in list(range(1, 38)) + [60, 61, 62, 63]
    }
    for pid in abstained:
        marks = {
            m["member_name"]: m["position"]
            for m in votes[pid]["member_votes"]
        }
        assert marks["松村秀逸"] == "abstained"
        assert proposals[pid]["submitted_by"] == "executive"
    recused = [
        v for v in votes.values()
        if sum(
            1 for m in v["member_votes"] if m["position"] == "excused"
        ) == 2
    ]
    assert len(recused) == 1
    assert proposals[recused[0]["proposal_id"]]["proposal_number"] == "第25号"
    marks = {
        m["member_name"]: m["position"]
        for m in recused[0]["member_votes"]
    }
    assert marks["吉田孝平"] == "excused"


def test_faction_votes_are_not_aggregated():
    # Kumamoto publishes individual member votes only; no faction record.
    assert load("faction_votes.json") == []


def test_expenses_cover_48_members_and_one_faction():
    expenses = load("political_activity_expenses.json")
    assert len(expenses) == 49
    assert {e["fiscal_year"] for e in expenses} == {2025}
    recipient_types = [e["recipient_type"] for e in expenses]
    assert recipient_types.count("member") == 48
    assert recipient_types.count("faction") == 1
    assert sum(e["granted_yen"] for e in expenses) == 170_100_000
    assert sum(e["spent_yen"] for e in expenses) == 171_339_810
    for expense in expenses:
        assert sum(b["amount_yen"] for b in expense["breakdown"]) == (
            expense["spent_yen"]
        )
        assert len(expense["breakdown"]) == 10
        if expense["spent_yen"] <= expense["granted_yen"]:
            assert (
                expense["granted_yen"] - expense["spent_yen"]
                == expense["returned_yen"]
            )
        else:
            assert expense["returned_yen"] == 0
        assert expense["report_status"] == "published"
        # Receipt copies are not published online; library viewing only.
        assert expense["receipt_access"] == "in_person_only"
    faction = [e for e in expenses if e["recipient_type"] == "faction"]
    assert faction[0]["recipient_name"] == "自由民主党熊本県議会議員団"
    assert faction[0]["granted_yen"] == 8_400_000
    kamata = [e for e in expenses if e["recipient_name"] == "鎌田聡"]
    assert kamata[0]["granted_yen"] == 900_000
    assert kamata[0]["returned_yen"] == 255_327


def test_inspection_trips_are_fy2026_committee_trips():
    trips = load("inspection_trips.json")
    assert len(trips) == 6
    assert {t["cost_status"] for t in trips} == {"not_published"}
    assert {t["trip_type"] for t in trips} == {"domestic"}
    assert all(t["total_cost_yen"] is None for t in trips)
    assert all(t["report_status"] == "published" for t in trips)
    assert all(
        t["participant_count"] == len(t["participants"]) for t in trips
    )
    assert all(t["start_date"].startswith("2026-") for t in trips)
    assert {t["title"] for t in trips} == {
        "令和8年度総務常任委員会管内視察",
        "令和8年度厚生常任委員会管内視察",
        "令和8年度経済環境常任委員会管内視察",
        "令和8年度農林水産常任委員会管内視察",
        "令和8年度建設常任委員会管内視察",
        "令和8年度教育警察常任委員会管内視察",
    }
    kosei = [t for t in trips if "厚生" in t["title"]][0]
    assert kosei["start_date"] == "2026-11-05"
    assert kosei["end_date"] == "2026-11-06"
    assert kosei["participant_count"] == 7


def test_disclosure_profile_notes():
    profiles = load("disclosure_profiles.json")
    assert len(profiles) == 1
    items = {item["item"]: item for item in profiles[0]["items"]}
    assert len(items) == 12
    assert items["member_votes"]["availability"] == "published"
    assert items["member_votes"]["granularity"] == "member"
    assert "事後記録" in items["member_votes"]["note"]
    assert items["faction_votes"]["availability"] == "not_published"
    receipts = items["political_activity_expense_receipts"]
    assert receipts["availability"] == "not_published"
    assert "図書室" in receipts["note"]
    assert "未公表" in items["meeting_minutes"]["note"]


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
    pending_packets = [
        p for p in pv
        if p["subject_type"] == "proposal" and p["open_questions"]
    ]
    assert len(pending_packets) == 21
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
