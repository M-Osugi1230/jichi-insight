"""Issue #983: Niigata Prefectural Assembly stage-4 registration checks."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "reviewed" / "niigata-prefecture" / "assembly"
CATALOG = (
    ROOT / "data" / "catalog" / "niigata_prefecture_assembly_sources.json"
)
ASSEMBLY_ID = "jp-local-150002-assembly-2023"
SESSION_ID = "jp-local-150002-assembly-2023-session-2026-09"
FACTIONS = {
    "自由民主党",
    "未来にいがた",
    "リベラル新潟",
    "真政にいがた",
    "公明党",
    "無所属",
}
VOTE_COLUMNS = FACTIONS - {"無所属"} | {"馬場秀幸（無所属）"}


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def source_ids():
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    return {record["id"] for record in catalog["records"]}


def test_catalog_is_niigata_prefecture_only():
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    records = catalog["records"]
    assert len(records) == 71
    assert {r["municipality_key"] for r in records} == {
        "niigata-prefecture"
    }
    assert len(source_ids()) == 71
    categories = {r["category"] for r in records}
    assert {
        "assembly",
        "inspection_trips",
        "political_activity_expenses",
        "proposals",
    } <= categories


def test_assembly_record_matches_official_roster():
    records = load("assembly_records.json")
    assert len(records) == 1
    record = records[0]
    assert record["id"] == ASSEMBLY_ID
    assert record["municipality_id"] == "jp-local-150002"
    assert record["name"] == "新潟県議会"
    assert record["term_start"] == "2023-04-30"
    assert record["term_end"] == "2027-04-29"
    # Statutory strength 53; the official roster lists 52 members
    # (one vacancy) across the six factions.
    assert record["seat_count"] == 53
    sizes = [f["member_count"] for f in record["factions"]]
    assert sizes == [32, 8, 6, 3, 2, 1]
    assert sum(sizes) == 52
    assert {f["name"] for f in record["factions"]} == FACTIONS
    assert len(record["committees"]) == 10


def test_session_is_september_2026_regular_session():
    sessions = load("sessions.json")
    assert len(sessions) == 1
    session = sessions[0]
    assert session["id"] == SESSION_ID
    assert session["name"] == "令和8年9月定例会"
    assert session["session_type"] == "regular"
    assert session["start_date"] == "2026-09-29"
    assert session["end_date"] == "2026-10-20"


def test_proposals_cover_all_kinds_and_outcomes():
    proposals = load("proposals.json")
    assert len(proposals) == 41
    assert {p["session_id"] for p in proposals} == {SESSION_ID}
    by_submitter = {}
    for proposal in proposals:
        by_submitter[proposal["submitted_by"]] = (
            by_submitter.get(proposal["submitted_by"], 0) + 1
        )
    assert by_submitter == {
        "executive": 27,
        "member": 7,
        "resident_petition": 7,
    }
    kinds = {}
    for proposal in proposals:
        kinds[proposal["kind"]] = kinds.get(proposal["kind"], 0) + 1
    assert kinds == {
        "budget": 3,
        "ordinance": 4,
        "other": 12,
        "personnel": 2,
        "settlement": 6,
        "resolution": 7,
        "petition": 7,
    }
    outcomes = {}
    for proposal in proposals:
        outcomes[proposal["outcome"]] = (
            outcomes.get(proposal["outcome"], 0) + 1
        )
    assert outcomes == {"approved": 25, "rejected": 5, "pending": 11}
    # The eight FY2025 settlement-related items (bills 103-110) were
    # carried over for continued review during the recess: pending,
    # undecided, and without a vote record.
    settlement_related = [
        p
        for p in proposals
        if p["proposal_number"]
        in {f"第{n}号" for n in range(103, 111)}
    ]
    assert len(settlement_related) == 8
    assert all(p["outcome"] == "pending" for p in settlement_related)
    assert all(p["decided_at"] is None for p in settlement_related)
    settlements = [p for p in proposals if p["kind"] == "settlement"]
    assert len(settlements) == 6
    assert all(p["outcome"] == "pending" for p in settlements)
    # Petitions: two adopted, two not adopted at this session; the
    # carried-over petition and the two carried-over petitions in
    # writing remain pending (continued review).
    petitions = [p for p in proposals if p["kind"] == "petition"]
    assert len(petitions) == 7
    by_number = {p["proposal_number"]: p for p in petitions}
    assert by_number["請願第6号"]["outcome"] == "rejected"
    assert by_number["請願第7号"]["outcome"] == "rejected"
    assert by_number["請願第8号"]["outcome"] == "approved"
    assert by_number["請願第9号"]["outcome"] == "approved"
    assert by_number["請願第13号"]["outcome"] == "pending"
    assert by_number["陳情第8号"]["outcome"] == "pending"
    assert by_number["陳情第9号"]["outcome"] == "pending"


def test_votes_match_marked_proposals():
    votes = load("votes.json")
    proposals = {p["id"]: p for p in load("proposals.json")}
    assert len(votes) == 26
    # Exactly the decided governor bills and member bills carry a
    # published faction-mark table and therefore have votes. Pending
    # items have no vote, and petitions carry no faction table.
    expected = {
        p["id"]
        for p in proposals.values()
        if p["outcome"] != "pending"
        and p["submitted_by"] in {"executive", "member"}
    }
    assert len(expected) == 26
    assert {v["proposal_id"] for v in votes} == expected
    for vote in votes:
        # The mark table was cross-checked against the June 2026
        # plenary minutes and judged to be a post-vote record, but the
        # September 2026 minutes are not yet published, so the voting
        # method of each item stays unknown and no totals are given.
        assert vote["method"] == "unknown"
        assert vote["member_vote_availability"] == "not_published"
        assert vote["member_votes"] == []
        assert vote["totals"] is None
        assert vote["vote_date"] == "2026-10-20"
        assert vote["outcome"] == proposals[vote["proposal_id"]]["outcome"]


def test_faction_votes_follow_the_published_marks():
    faction_votes = load("faction_votes.json")
    votes = load("votes.json")
    assert len(faction_votes) == 26 * 6
    assert {fv["vote_id"] for fv in faction_votes} == {
        v["id"] for v in votes
    }
    assert {fv["faction_name"] for fv in faction_votes} == VOTE_COLUMNS
    # 153 in-favour marks and exactly three against marks: the LDP
    # column on member bills 22-24 (all other columns in favour).
    positions = [fv["position"] for fv in faction_votes]
    assert positions.count("for") == 153
    assert positions.count("against") == 3
    assert "abstained" not in positions
    assert "absent" not in positions
    # Head-counts per faction are not published in the table.
    assert all(fv["for_count"] is None for fv in faction_votes)
    assert all(fv["against_count"] is None for fv in faction_votes)
    assert all(fv["member_count"] is None for fv in faction_votes)
    proposals = {p["id"]: p for p in load("proposals.json")}
    vote_proposal = {v["id"]: v["proposal_id"] for v in votes}

    def marks(proposal_number):
        return {
            fv["faction_name"]: fv["position"]
            for fv in faction_votes
            if proposals[vote_proposal[fv["vote_id"]]][
                "proposal_number"
            ]
            == proposal_number
        }

    for number in ("発議案第22号", "発議案第23号", "発議案第24号"):
        m = marks(number)
        assert m["自由民主党"] == "against"
        assert sum(1 for v in m.values() if v == "for") == 5
    m86 = marks("第86号")
    assert all(v == "for" for v in m86.values())


def test_expenses_cover_factions_and_members():
    expenses = load("political_activity_expenses.json")
    assert len(expenses) == 58
    assert {e["fiscal_year"] for e in expenses} == {2025}
    factions = [e for e in expenses if e["recipient_type"] == "faction"]
    members = [e for e in expenses if e["recipient_type"] == "member"]
    assert len(factions) == 5
    assert len(members) == 53
    assert {e["recipient_name"] for e in factions} == {
        "新潟県議会自由民主党議員団",
        "未来にいがた",
        "リベラル新潟",
        "真政にいがた",
        "公明党",
    }
    # Report totals across all 58 published units, as printed.
    assert sum(e["granted_yen"] for e in expenses) == 209_088_000
    assert sum(e["spent_yen"] for e in expenses) == 185_563_592
    assert sum(e["returned_yen"] for e in expenses) == 29_223_790
    for expense in expenses:
        assert expense["report_status"] == "published"
        # Reports and receipt copies are published on the web.
        assert expense["receipt_access"] == "online"
        if expense["spent_yen"] <= expense["granted_yen"]:
            assert expense["returned_yen"] == (
                expense["granted_yen"] - expense["spent_yen"]
            )
        else:
            # Overspending units report a printed remainder of zero.
            assert expense["returned_yen"] == 0
        breakdown_sum = sum(
            b["amount_yen"] for b in expense["breakdown"]
        )
        if expense["recipient_name"] == "馬場秀幸":
            # The printed total exceeds the sum of the printed
            # categories by 300 yen in the source document itself;
            # both are registered as printed and the discrepancy is
            # documented in the evidence packet.
            assert expense["spent_yen"] - breakdown_sum == 300
        else:
            assert breakdown_sum == expense["spent_yen"]
    # Four faction forms print nine categories (no office-cost row);
    # the Liberal Niigata form and all member forms print ten.
    by_name = {e["recipient_name"]: e for e in factions}
    assert len(by_name["リベラル新潟"]["breakdown"]) == 10
    for name in (
        "新潟県議会自由民主党議員団",
        "未来にいがた",
        "真政にいがた",
        "公明党",
    ):
        assert len(by_name[name]["breakdown"]) == 9
    assert all(len(e["breakdown"]) == 10 for e in members)
    # One FY2025 recipient is absent from the current roster; the
    # report is part of the official FY2025 list.
    names = {e["recipient_name"] for e in members}
    assert "土田竜吾" in names


def test_inspection_trips_are_committee_trips():
    trips = load("inspection_trips.json")
    assert len(trips) == 7
    assert {t["cost_status"] for t in trips} == {"not_published"}
    assert {t["trip_type"] for t in trips} == {"domestic"}
    assert all(t["total_cost_yen"] is None for t in trips)
    assert all(t["report_status"] == "published" for t in trips)
    # Every trip names its participating committee members.
    assert [t["participant_count"] for t in trips] == [
        11,
        11,
        13,
        9,
        7,
        10,
        10,
    ]
    assert all(
        len(t["participants"]) == t["participant_count"] for t in trips
    )
    assert sum(len(t["destinations"]) for t in trips) == 30


def test_disclosure_profile_notes():
    profiles = load("disclosure_profiles.json")
    assert len(profiles) == 1
    items = {item["item"]: item for item in profiles[0]["items"]}
    assert len(items) == 12
    assert items["faction_votes"]["availability"] == "published"
    assert items["faction_votes"]["granularity"] == "faction"
    # The mark table was judged a post-vote record via the June 2026
    # minutes; the September minutes are not yet published.
    assert "表決記録" in items["faction_votes"]["note"]
    assert items["member_votes"]["availability"] == "not_published"
    assert (
        items["political_activity_expense_receipts"]["availability"]
        == "published"
    )
    assert "未公表" in items["meeting_minutes"]["note"]
    assert "不採択" in items["petition_results"]["note"]


def test_evidence_packets_cover_every_record():
    proposals = {p["id"] for p in load("proposals.json")}
    votes = {v["id"] for v in load("votes.json")}
    pv = load("proposal_vote_evidence_packets.json")
    assert {
        p["subject_id"] for p in pv if p["subject_type"] == "proposal"
    } == proposals
    assert {
        p["subject_id"] for p in pv if p["subject_type"] == "vote"
    } == votes
    vote_packets = [p for p in pv if p["subject_type"] == "vote"]
    assert all(
        "表決記録" in (claim["review_note"] or "")
        for packet in vote_packets
        for claim in packet["claims"]
    )
    assert all(packet["open_questions"] for packet in vote_packets)
    expenses = {e["id"] for e in load("political_activity_expenses.json")}
    ex = load("expense_evidence_packets.json")
    assert {p["subject_id"] for p in ex} == expenses
    # The one source-document discrepancy is kept as an open question.
    baba = next(
        p
        for p in ex
        if p["subject_id"].endswith("expense-fy2025-058")
    )
    assert baba["open_questions"]
    assert any(
        "300円" in (claim["statement"] or "") for claim in baba["claims"]
    )
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
