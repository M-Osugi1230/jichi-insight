"""Issue #1049: Yamagata Prefectural Assembly stage-4 registration checks."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "reviewed" / "yamagata-prefecture" / "assembly"
CATALOG = (
    ROOT / "data" / "catalog" / "yamagata_prefecture_assembly_sources.json"
)
ASSEMBLY_ID = "jp-local-060003-assembly-2023"
SESSION_ID = "jp-local-060003-assembly-2023-session-2026-09"
FACTIONS = {"自由民主党", "県政クラブ", "日本共産党山形県議団", "公明党"}


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def source_ids():
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    return {record["id"] for record in catalog["records"]}


def test_catalog_is_yamagata_prefecture_only():
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    records = catalog["records"]
    assert len(records) == 59
    assert {r["municipality_key"] for r in records} == {
        "yamagata-prefecture"
    }
    assert len(source_ids()) == 59
    categories = {r["category"] for r in records}
    assert {
        "assembly",
        "political_activity_expenses",
        "proposals",
    } <= categories


def test_assembly_record_matches_official_roster():
    records = load("assembly_records.json")
    assert len(records) == 1
    record = records[0]
    assert record["id"] == ASSEMBLY_ID
    assert record["municipality_id"] == "jp-local-060003"
    assert record["name"] == "山形県議会"
    assert record["term_start"] == "2023-04-30"
    assert record["term_end"] == "2027-04-29"
    # Statutory strength 43 with no vacancy at the September 2026
    # session. The Liberal Democratic Party count of 26 includes the
    # speaker; the result table counts 25 voting participants for it.
    assert record["seat_count"] == 43
    sizes = [f["member_count"] for f in record["factions"]]
    assert sizes == [26, 14, 2, 1]
    assert sum(sizes) == 43
    assert {f["name"] for f in record["factions"]} == FACTIONS
    assert len(record["committees"]) == 12


def test_session_is_september_2026_regular_session():
    sessions = load("sessions.json")
    assert len(sessions) == 1
    session = sessions[0]
    assert session["id"] == SESSION_ID
    assert session["name"] == "令和8年9月定例会"
    assert session["session_type"] == "regular"
    assert session["start_date"] == "2026-09-16"
    assert session["end_date"] == "2026-10-08"


def test_proposals_cover_all_kinds_and_outcomes():
    proposals = load("proposals.json")
    assert len(proposals) == 65
    assert {p["session_id"] for p in proposals} == {SESSION_ID}
    by_submitter = {}
    for proposal in proposals:
        by_submitter[proposal["submitted_by"]] = (
            by_submitter.get(proposal["submitted_by"], 0) + 1
        )
    assert by_submitter == {
        "executive": 51,
        "member": 10,
        "resident_petition": 4,
    }
    kinds = {}
    for proposal in proposals:
        kinds[proposal["kind"]] = kinds.get(proposal["kind"], 0) + 1
    assert kinds == {
        "budget": 5,
        "ordinance": 4,
        "other": 31,
        "settlement": 17,
        "personnel": 2,
        "resolution": 2,
        "petition": 4,
    }
    outcomes = {}
    for proposal in proposals:
        outcomes[proposal["outcome"]] = (
            outcomes.get(proposal["outcome"], 0) + 1
        )
    assert outcomes == {"approved": 40, "pending": 24, "withdrawn": 1}
    # The 17 FY2025 settlement items carry no bill number in the
    # result table; following the Shizuoka/Hiroshima/Okayama/Chiba
    # precedents they are registered with proposal_number 決算認定.
    # They were only introduced, explained and referred to the
    # settlement special committee on 2026-10-08: still under review,
    # never recorded as certified.
    settlements = [p for p in proposals if p["kind"] == "settlement"]
    assert len(settlements) == 17
    assert {p["proposal_number"] for p in settlements} == {"決算認定"}
    assert all(p["outcome"] == "pending" for p in settlements)
    assert all(p["decided_at"] is None for p in settlements)
    # The five additional bills 123-127 were also carried over.
    added = [
        p
        for p in proposals
        if p["proposal_number"] in {f"議第{n}号" for n in range(123, 128)}
    ]
    assert len(added) == 5
    assert all(p["outcome"] == "pending" for p in added)
    # Member dispatches use their own cumulative numbering.
    dispatches = [
        p
        for p in proposals
        if (p["proposal_number"] or "").startswith("議員派遣第")
    ]
    assert len(dispatches) == 8
    assert all(p["outcome"] == "approved" for p in dispatches)
    # Petitions: one adopted, two under continued review, one
    # withdrawn.
    petitions = [p for p in proposals if p["kind"] == "petition"]
    assert len(petitions) == 4
    by_number = {p["proposal_number"]: p for p in petitions}
    assert by_number["請願第41号"]["outcome"] == "approved"
    assert by_number["請願第31号"]["outcome"] == "pending"
    assert by_number["請願第36号"]["outcome"] == "pending"
    assert by_number["請願第40号"]["outcome"] == "withdrawn"


def test_votes_match_all_proposals():
    votes = load("votes.json")
    proposals = {p["id"]: p for p in load("proposals.json")}
    # Every one of the 65 items has a row in the official result
    # table, including the items carried over for continued review,
    # so every proposal carries a vote record.
    assert len(votes) == 65
    assert {v["proposal_id"] for v in votes} == set(proposals)
    for vote in votes:
        # The mark table was cross-checked against the June 2026
        # plenary minutes and judged to be a post-vote record, but
        # the September 2026 minutes are not yet published, so the
        # voting method of each item stays unknown and no totals are
        # given.
        assert vote["method"] == "unknown"
        assert vote["member_vote_availability"] == "not_published"
        assert vote["member_votes"] == []
        assert vote["totals"] is None
        proposal = proposals[vote["proposal_id"]]
        if proposal["proposal_number"] in {"議第121号", "議第122号"}:
            # The two personnel consent items were decided on
            # 2026-10-02; everything else on 2026-10-08.
            assert vote["vote_date"] == "2026-10-02"
        else:
            assert vote["vote_date"] == "2026-10-08"
        if proposal["proposal_number"] == "請願第40号":
            # The all-faction mark approves the withdrawal handling
            # itself, while the proposal outcome stays withdrawn.
            assert proposal["outcome"] == "withdrawn"
            assert vote["outcome"] == "approved"
        else:
            assert vote["outcome"] == proposal["outcome"]


def test_faction_votes_follow_the_published_marks():
    faction_votes = load("faction_votes.json")
    votes = load("votes.json")
    assert len(faction_votes) == 65 * 4
    assert {fv["vote_id"] for fv in faction_votes} == {
        v["id"] for v in votes
    }
    assert {fv["faction_name"] for fv in faction_votes} == FACTIONS
    # Every row of the September 2026 result tables shows the
    # in-favour mark for all four factions (no against or abstention
    # marks anywhere in this session).
    positions = [fv["position"] for fv in faction_votes]
    assert positions.count("for") == 260
    assert "against" not in positions
    assert "abstained" not in positions
    assert "absent" not in positions
    # Head-counts per faction are not printed in the table.
    assert all(fv["for_count"] is None for fv in faction_votes)
    assert all(fv["against_count"] is None for fv in faction_votes)
    assert all(fv["member_count"] is None for fv in faction_votes)


def test_expenses_cover_factions_and_members():
    expenses = load("political_activity_expenses.json")
    assert len(expenses) == 47
    assert {e["fiscal_year"] for e in expenses} == {2025}
    factions = [e for e in expenses if e["recipient_type"] == "faction"]
    members = [e for e in expenses if e["recipient_type"] == "member"]
    assert len(factions) == 4
    assert len(members) == 43
    assert {e["recipient_name"] for e in factions} == {
        "自由民主党県議会",
        "県政クラブ",
        "日本共産党山形県議団",
        "公明党",
    }
    # Report totals across all 47 published units, matching the
    # assembly secretariat's official FY2025 summary list.
    assert sum(e["granted_yen"] for e in expenses) == 159_340_000
    assert sum(e["spent_yen"] for e in expenses) == 121_935_713
    assert sum(e["returned_yen"] for e in expenses) == 37_404_287
    for expense in expenses:
        assert expense["report_status"] == "published"
        # Reports and receipt copies are published on the web.
        assert expense["receipt_access"] == "online"
        assert expense["returned_yen"] == (
            expense["granted_yen"] - expense["spent_yen"]
        )
        breakdown_sum = sum(
            b["amount_yen"] for b in expense["breakdown"]
        )
        assert breakdown_sum == expense["spent_yen"]
        # Both the faction and member forms print the same ten
        # categories.
        assert len(expense["breakdown"]) == 10
    # Endo Hiroaki resigned on 2026-01-20, so his FY2025 grant is
    # ten monthly instalments of 280,000 yen.
    by_name = {e["recipient_name"]: e for e in members}
    assert by_name["遠藤寛明"]["granted_yen"] == 2_800_000
    # Shibata Masato received a full-year FY2025 grant although he
    # no longer appears on the September 2026 roster.
    assert by_name["柴田正人"]["granted_yen"] == 3_360_000


def test_inspection_trips_not_registered():
    # No official publication format for committee inspection-trip
    # reports could be identified (stage-0 open question OQ-4), so
    # no trips are registered; the gap is recorded in the disclosure
    # profile instead.
    assert load("inspection_trips.json") == []
    assert load("inspection_evidence_packets.json") == []


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
    assert "撤回" in items["petition_results"]["note"]
    assert (
        items["inspection_trip_reports"]["availability"] == "not_found"
    )


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
