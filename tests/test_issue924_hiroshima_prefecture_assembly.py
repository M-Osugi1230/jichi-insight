import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "reviewed" / "hiroshima-prefecture" / "assembly"
CATALOG = (
    ROOT / "data" / "catalog" / "hiroshima_prefecture_assembly_sources.json"
)
ASSEMBLY_ID = "jp-local-340006-assembly-2023"
SESSION_ID = f"{ASSEMBLY_ID}-session-2026-09"

FACTIONS = {
    "自由民主党広島県議会議員連盟",
    "広島県議会民主県政会",
    "公明党広島県議会議員団",
    "自由民主党広島県議会広志会",
    "日本共産党広島県議会議員団",
    "自由民主党広島県議会議員会",
    "無所属ひとわ",
    "ひろしま、刷新",
}


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def catalog():
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def source_ids():
    return {record["id"] for record in catalog()["records"]}


def test_catalog_is_hiroshima_prefecture_only():
    records = catalog()["records"]
    assert len(records) == 20
    assert {record["municipality_key"] for record in records} == {
        "hiroshima-prefecture"
    }
    assert len({record["id"] for record in records}) == 20
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
    assert record["municipality_id"] == "jp-local-340006"
    assert record["name"] == "広島県議会"
    assert record["seat_count"] == 64
    assert record["term_start"] == "2023-04-30"
    assert record["term_end"] == "2027-04-29"
    assert [f["member_count"] for f in record["factions"]] == [
        35, 14, 6, 3, 2, 1, 1, 1,
    ]
    # 63 sitting members (one vacancy in Aki county); the LDP league's
    # 35 includes the chair, who does not take part in votes.
    assert sum(f["member_count"] for f in record["factions"]) == 63
    assert {f["name"] for f in record["factions"]} == FACTIONS
    assert len(record["committees"]) == 17
    assert all(isinstance(c, str) for c in record["committees"])


def test_session_is_september_2026_regular_session():
    sessions = load("sessions.json")
    assert len(sessions) == 1
    session = sessions[0]
    assert session["id"] == SESSION_ID
    assert session["name"] == "令和8年9月定例会"
    assert session["session_type"] == "regular"
    assert session["start_date"] == "2026-09-18"
    assert session["end_date"] == "2026-10-06"


def test_proposals_cover_all_kinds_and_outcomes():
    proposals = load("proposals.json")
    assert len(proposals) == 20
    assert {p["session_id"] for p in proposals} == {SESSION_ID}
    by_submitter = {}
    for proposal in proposals:
        by_submitter[proposal["submitted_by"]] = (
            by_submitter.get(proposal["submitted_by"], 0) + 1
        )
    assert by_submitter == {"executive": 16, "member": 4}
    kinds = {}
    for proposal in proposals:
        kinds[proposal["kind"]] = kinds.get(proposal["kind"], 0) + 1
    assert kinds == {
        "budget": 1,
        "ordinance": 4,
        "other": 8,
        "personnel": 1,
        "settlement": 2,
        "resolution": 4,
    }
    # The two FY2025 settlement certifications were carried over for
    # continued review by the settlement special committee; the plenary
    # votes on them are expected at the December 2026 session.
    pending = [p for p in proposals if p["outcome"] == "pending"]
    assert len(pending) == 2
    assert {p["kind"] for p in pending} == {"settlement"}
    assert all(p["decided_at"] is None for p in pending)
    assert {p["title"] for p in pending} == {
        "令和7年度広島県歳入歳出決算認定の件",
        "令和7年度広島県公営企業決算認定の件",
    }
    # No petitions were submitted to or reported for this session.
    assert not [p for p in proposals if p["kind"] == "petition"]


def test_votes_match_decided_proposals():
    votes = load("votes.json")
    proposals = {p["id"]: p for p in load("proposals.json")}
    assert len(votes) == 18
    decided = {
        p["id"] for p in proposals.values() if p["outcome"] == "approved"
    }
    assert {v["proposal_id"] for v in votes} == decided
    for vote in votes:
        # Member-level votes are not published; only faction marks are.
        assert vote["member_vote_availability"] == "not_published"
        assert vote["member_votes"] == []
        assert vote["totals"] is None
    # The personnel consent (No. 75) was voted on 2026-09-30, all other
    # items on 2026-10-06.
    by_proposal = {v["proposal_id"]: v for v in votes}
    personnel = next(
        p for p in proposals.values() if p["kind"] == "personnel"
    )
    assert by_proposal[personnel["id"]]["vote_date"] == "2026-09-30"
    others = [
        v for pid, v in by_proposal.items() if pid != personnel["id"]
    ]
    assert all(v["vote_date"] == "2026-10-06" for v in others)


def test_faction_votes_cover_eight_factions_for_every_vote():
    faction_votes = load("faction_votes.json")
    votes = load("votes.json")
    assert len(faction_votes) == 18 * 8
    assert {fv["vote_id"] for fv in faction_votes} == {
        v["id"] for v in votes
    }
    assert {fv["faction_name"] for fv in faction_votes} == FACTIONS
    # The JCP voted against the supplementary budget (No. 62), the
    # ordinance package (No. 63) and the personnel consent (No. 75);
    # every other mark in the published table is in favour.
    against = [
        fv for fv in faction_votes if fv["position"] == "against"
    ]
    assert len(against) == 3
    assert {fv["faction_name"] for fv in against} == {
        "日本共産党広島県議会議員団"
    }
    proposals = {p["id"]: p for p in load("proposals.json")}
    vote_proposal = {v["id"]: v["proposal_id"] for v in votes}
    assert {
        proposals[vote_proposal[fv["vote_id"]]]["proposal_number"]
        for fv in against
    } == {"県第62号", "県第63号", "県第75号"}
    assert all(
        fv["position"] == "for"
        for fv in faction_votes
        if fv not in against
    )


def test_expenses_cover_nine_faction_units():
    expenses = load("political_activity_expenses.json")
    assert len(expenses) == 9
    assert {e["fiscal_year"] for e in expenses} == {2025}
    assert sum(e["granted_yen"] for e in expenses) == 265_650_000
    assert sum(e["spent_yen"] for e in expenses) == 242_002_669
    assert sum(e["returned_yen"] for e in expenses) == 24_315_501
    assert {e["recipient_type"] for e in expenses} == {"faction"}
    # The dissolved Giyukai faction is part of the official FY2025 list.
    assert "義友会" in {e["recipient_name"] for e in expenses}
    for expense in expenses:
        assert sum(b["amount_yen"] for b in expense["breakdown"]) == (
            expense["spent_yen"]
        )
        assert len(expense["breakdown"]) == 8
        assert expense["report_status"] == "published"
        # Reports and receipts are open to in-person inspection only.
        assert expense["receipt_access"] == "in_person_only"
    # Three factions spent beyond their income (grant plus interest);
    # the published remainder is floored at zero for them, so the total
    # remainder is not simply total income minus total spending.
    floored = {
        e["recipient_name"]
        for e in expenses
        if e["returned_yen"] == 0 and e["spent_yen"] > e["granted_yen"]
    }
    assert floored == {
        "自由民主党広島県議会広志会",
        "日本共産党広島県議会議員団",
        "ひろしま、刷新",
    }


def test_inspection_trips_are_fy2026_committee_trips():
    trips = load("inspection_trips.json")
    assert len(trips) == 13
    assert {t["cost_status"] for t in trips} == {"not_published"}
    assert {t["trip_type"] for t in trips} == {"domestic", "overseas"}
    overseas = [t for t in trips if t["trip_type"] == "overseas"]
    assert len(overseas) == 1
    assert "モンゴル" in overseas[0]["purpose"]
    assert all(t["total_cost_yen"] is None for t in trips)
    assert all(t["report_status"] == "published" for t in trips)
    # Participant names are not published for these trips.
    assert all(t["participants"] == [] for t in trips)
    assert all(t["participant_count"] is None for t in trips)
    assert all(t["start_date"].startswith("2026-") for t in trips)
    assert sum(len(t["destinations"]) for t in trips) == 60


def test_disclosure_profile_notes():
    profiles = load("disclosure_profiles.json")
    assert len(profiles) == 1
    items = {item["item"]: item for item in profiles[0]["items"]}
    assert len(items) == 12
    assert items["faction_votes"]["availability"] == "published"
    assert items["faction_votes"]["granularity"] == "faction"
    # The nature of the faction table is deliberately not asserted:
    # the minutes cross-check is still outstanding.
    assert "断定せず" in items["faction_votes"]["note"]
    assert items["member_votes"]["availability"] == "not_published"
    assert "復元" in items["member_votes"]["note"]
    assert (
        items["political_activity_expense_receipts"]["availability"]
        == "restricted"
    )
    assert "0件" in items["petition_results"]["note"]


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
    settlement_packets = [
        p for p in pv
        if p["subject_type"] == "proposal"
        and p["subject_id"].endswith(("settlement-01", "settlement-02"))
    ]
    assert len(settlement_packets) == 2
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
