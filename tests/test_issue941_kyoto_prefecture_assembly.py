"""Issue #941: Kyoto Prefectural Assembly stage-4 registration checks."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "reviewed" / "kyoto-prefecture" / "assembly"
CATALOG = (
    ROOT / "data" / "catalog" / "kyoto_prefecture_assembly_sources.json"
)
ASSEMBLY_ID = "jp-local-260002-assembly-2023"
SESSION_ID = "jp-local-260002-assembly-2023-session-2026-09"
FACTIONS = {
    "自由民主党京都府議会議員団",
    "国民民主党・日本維新の会京都府議会議員団",
    "日本共産党京都府議会議員団",
    "府民クラブ京都府議会議員団",
    "公明党京都府議会議員団",
    "京都が好きだ",
}


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def source_ids():
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    return {record["id"] for record in catalog["records"]}


def test_catalog_is_kyoto_prefecture_only():
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    records = catalog["records"]
    assert len(records) == 95
    assert {r["municipality_key"] for r in records} == {
        "kyoto-prefecture"
    }
    assert len(source_ids()) == 95
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
    assert record["municipality_id"] == "jp-local-260002"
    assert record["name"] == "京都府議会"
    assert record["term_start"] == "2023-04-30"
    assert record["term_end"] == "2027-04-29"
    # Statutory strength 60; the official roster lists 59 members
    # (one vacancy) across the six factions.
    assert record["seat_count"] == 60
    sizes = [f["member_count"] for f in record["factions"]]
    assert sizes == [28, 11, 9, 5, 5, 1]
    assert sum(sizes) == 59
    assert {f["name"] for f in record["factions"]} == FACTIONS
    assert len(record["committees"]) == 14


def test_session_is_september_2026_regular_session():
    sessions = load("sessions.json")
    assert len(sessions) == 1
    session = sessions[0]
    assert session["id"] == SESSION_ID
    assert session["name"] == "令和8年9月定例会"
    assert session["session_type"] == "regular"
    assert session["start_date"] == "2026-09-16"
    assert session["end_date"] == "2026-11-09"


def test_proposals_cover_all_kinds_and_outcomes():
    proposals = load("proposals.json")
    assert len(proposals) == 39
    assert {p["session_id"] for p in proposals} == {SESSION_ID}
    by_submitter = {}
    for proposal in proposals:
        by_submitter[proposal["submitted_by"]] = (
            by_submitter.get(proposal["submitted_by"], 0) + 1
        )
    assert by_submitter == {
        "executive": 19,
        "member": 14,
        "committee": 1,
        "resident_petition": 2,
        "other": 3,
    }
    kinds = {}
    for proposal in proposals:
        kinds[proposal["kind"]] = kinds.get(proposal["kind"], 0) + 1
    assert kinds == {
        "budget": 1,
        "ordinance": 5,
        "other": 12,
        "personnel": 1,
        "settlement": 6,
        "resolution": 11,
        "petition": 3,
    }
    outcomes = {}
    for proposal in proposals:
        outcomes[proposal["outcome"]] = (
            outcomes.get(proposal["outcome"], 0) + 1
        )
    assert outcomes == {"approved": 30, "rejected": 9}
    # The six FY2025 settlement certifications were decided at this
    # session (certified on 2026-11-09); nothing is left pending.
    settlements = [p for p in proposals if p["kind"] == "settlement"]
    assert len(settlements) == 6
    assert all(p["outcome"] == "approved" for p in settlements)
    assert all(p["decided_at"] == "2026-11-09" for p in settlements)
    assert not [p for p in proposals if p["outcome"] == "pending"]
    # The two numbered petitions were rejected (not adopted); the
    # committee's petition-review item itself was approved.
    petitions = [p for p in proposals if p["kind"] == "petition"]
    numbered = [
        p for p in petitions if p["submitted_by"] == "resident_petition"
    ]
    assert len(numbered) == 2
    assert all(p["outcome"] == "rejected" for p in numbered)
    assert {p["proposal_number"] for p in numbered} == {
        "請願第784号",
        "請願第785号",
    }


def test_votes_match_marked_proposals():
    votes = load("votes.json")
    proposals = {p["id"]: p for p in load("proposals.json")}
    assert len(votes) == 32
    # Exactly the proposals carrying a faction-mark table have votes:
    # all decided items except the five procedural ones and the two
    # individually reported petitions. The committee's petition-review
    # item does carry a mark table and therefore has a vote.
    no_vote_numbers = {
        "請願第784号",
        "請願第785号",
        "その他（決算特別委員会設置の件）",
        "その他（決算特別委員会委員選任の件）",
        "その他（議員派遣の件）",
        "その他（閉会中継続審査・調査の件）",
    }
    no_vote = {
        p["id"]
        for p in proposals.values()
        if p["proposal_number"] in no_vote_numbers
    }
    assert len(no_vote) == 7
    assert {v["proposal_id"] for v in votes} == (
        set(proposals) - no_vote
    )
    review_item = next(
        p for p in proposals.values()
        if p["proposal_number"] == "その他（請願審査の件）"
    )
    assert review_item["id"] in {v["proposal_id"] for v in votes}
    for vote in votes:
        # The published table shows only "in favour" marks; its nature
        # (post-vote record vs pre-vote stance) is not asserted, so the
        # method stays unknown and no totals are published.
        assert vote["method"] == "unknown"
        assert vote["member_vote_availability"] == "not_published"
        assert vote["member_votes"] == []
        assert vote["totals"] is None
    dates = {}
    for vote in votes:
        dates[vote["vote_date"]] = dates.get(vote["vote_date"], 0) + 1
    assert dates == {
        "2026-09-30": 2,
        "2026-10-14": 24,
        "2026-11-09": 6,
    }


def test_faction_votes_never_infer_blank_cells():
    faction_votes = load("faction_votes.json")
    votes = load("votes.json")
    assert len(faction_votes) == 32 * 6
    assert {fv["vote_id"] for fv in faction_votes} == {
        v["id"] for v in votes
    }
    assert {fv["faction_name"] for fv in faction_votes} == FACTIONS
    # Blank cells are registered as unknown, never as opposition:
    # 152 explicit in-favour marks and 40 blanks, no inferred against.
    positions = [fv["position"] for fv in faction_votes]
    assert positions.count("for") == 152
    assert positions.count("unknown") == 40
    assert "against" not in positions
    # Head-counts per faction are not published either.
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

    # Settlement No. 13: only the JCP cell is blank.
    m13 = marks("第13号")
    assert m13["日本共産党京都府議会議員団"] == "unknown"
    assert sum(1 for v in m13.values() if v == "for") == 5
    # The member bill on assembly size: only the Ishin/Kokumin faction
    # is marked in favour; it was rejected.
    g1 = marks("議第1号")
    assert g1["国民民主党・日本維新の会京都府議会議員団"] == "for"
    assert sum(1 for v in g1.values() if v == "unknown") == 5


def test_expenses_cover_factions_and_members():
    expenses = load("political_activity_expenses.json")
    assert len(expenses) == 67
    assert {e["fiscal_year"] for e in expenses} == {2025}
    factions = [e for e in expenses if e["recipient_type"] == "faction"]
    members = [e for e in expenses if e["recipient_type"] == "member"]
    assert len(factions) == 6
    assert len(members) == 61
    assert {e["recipient_name"] for e in factions} == FACTIONS
    # Report totals across all 67 published units.
    assert sum(e["granted_yen"] for e in expenses) == 378_600_000
    assert sum(e["spent_yen"] for e in expenses) == 334_954_978
    assert sum(e["returned_yen"] for e in expenses) == 45_956_234
    # The overview page's member aggregate caps each member's used
    # amount at the grant (overspend is borne personally); with that
    # cap the 61 reports reproduce the overview figure exactly.
    assert sum(
        min(e["spent_yen"], e["granted_yen"]) for e in members
    ) == 206_619_786
    for expense in expenses:
        assert sum(
            b["amount_yen"] for b in expense["breakdown"]
        ) == expense["spent_yen"]
        assert expense["report_status"] == "published"
        # Reports and receipt copies are published on the web.
        assert expense["receipt_access"] == "online"
        if expense["spent_yen"] <= expense["granted_yen"]:
            assert expense["returned_yen"] == (
                expense["granted_yen"] - expense["spent_yen"]
            )
        else:
            # Overspending members report a printed remainder of zero.
            assert expense["returned_yen"] == 0
    # The faction form has nine categories (no office-cost row); the
    # member form has ten.
    assert all(len(e["breakdown"]) == 9 for e in factions)
    assert all(len(e["breakdown"]) == 10 for e in members)
    # Two recipients are FY2025 leavers absent from the current
    # roster; their reports are part of the official FY2025 list.
    names = {e["recipient_name"] for e in members}
    assert {"近藤永太郎", "四方源太郎"} <= names


def test_inspection_trips_cover_overseas_and_committee_trips():
    trips = load("inspection_trips.json")
    assert len(trips) == 12
    assert {t["cost_status"] for t in trips} == {"not_published"}
    assert {t["trip_type"] for t in trips} == {"domestic", "overseas"}
    overseas = [t for t in trips if t["trip_type"] == "overseas"]
    assert len(overseas) == 2
    assert all(t["participant_count"] == 10 for t in overseas)
    assert all(len(t["participants"]) == 10 for t in overseas)
    assert all(
        t["start_date"] == "2025-11-09" for t in overseas
    )
    domestic = [t for t in trips if t["trip_type"] == "domestic"]
    assert len(domestic) == 10
    # Committee trip reports do not name participants per trip.
    assert all(t["participants"] == [] for t in domestic)
    assert all(t["participant_count"] is None for t in domestic)
    assert all(t["total_cost_yen"] is None for t in trips)
    assert all(t["report_status"] == "published" for t in trips)
    assert sum(len(t["destinations"]) for t in trips) == 53


def test_disclosure_profile_notes():
    profiles = load("disclosure_profiles.json")
    assert len(profiles) == 1
    items = {item["item"]: item for item in profiles[0]["items"]}
    assert len(items) == 12
    assert items["faction_votes"]["availability"] == "published"
    assert items["faction_votes"]["granularity"] == "faction"
    # The nature of the faction table is deliberately not asserted:
    # the September 2026 minutes are not yet published.
    assert "断定せず" in items["faction_votes"]["note"]
    assert items["member_votes"]["availability"] == "not_published"
    assert (
        items["political_activity_expense_receipts"]["availability"]
        == "published"
    )
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
        "断定せず" in (claim["review_note"] or "")
        for packet in vote_packets
        for claim in packet["claims"]
    )
    assert all(packet["open_questions"] for packet in vote_packets)
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
