"""Issue #1047: Fukushima Prefectural Assembly stage-4 registration checks."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "reviewed" / "fukushima-prefecture" / "assembly"
CATALOG = (
    ROOT / "data" / "catalog" / "fukushima_prefecture_assembly_sources.json"
)
ASSEMBLY_ID = "jp-local-070009-assembly-2023"
SESSION_ID = "jp-local-070009-assembly-2023-session-2026-09"
JIMIN = "自由民主党福島県議会議員会"
KENMIN = "福島県議会県民連合議員会"
KYOSAN = "日本共産党福島県議会議員団"
KOMEI = "公明党福島県議会議員団"
ISHIN = "日本維新・無所属の会"
FACTIONS = {JIMIN, KENMIN, KYOSAN, KOMEI, ISHIN}


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def source_ids():
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    return {record["id"] for record in catalog["records"]}


def test_catalog_is_fukushima_prefecture_only():
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    records = catalog["records"]
    assert len(records) == 17
    assert {r["municipality_key"] for r in records} == {
        "fukushima-prefecture"
    }
    assert len(source_ids()) == 17
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
    assert record["municipality_id"] == "jp-local-070009"
    assert record["name"] == "福島県議会"
    # The term end (2027-11-19) is printed on the official district
    # roster; the start is the day after the previous term expired.
    assert record["term_start"] == "2023-11-20"
    assert record["term_end"] == "2027-11-19"
    # Statutory strength 58 and current membership 58: the October
    # 2026 by-elections filled the three vacancies. Bill 171 (seat
    # reduction to 57) applies only from the next general election,
    # so the current seat count stays 58.
    assert record["seat_count"] == 58
    sizes = [f["member_count"] for f in record["factions"]]
    assert sizes == [31, 17, 4, 4, 2]
    assert sum(sizes) == 58
    assert {f["name"] for f in record["factions"]} == FACTIONS
    assert len(record["committees"]) == 11


def test_session_is_september_2026_regular_session():
    sessions = load("sessions.json")
    assert len(sessions) == 1
    session = sessions[0]
    assert session["id"] == SESSION_ID
    assert session["name"] == "令和8年9月定例会"
    assert session["session_type"] == "regular"
    assert session["start_date"] == "2026-09-15"
    assert session["end_date"] == "2026-10-05"


def test_proposals_cover_all_kinds_and_outcomes():
    proposals = load("proposals.json")
    assert len(proposals) == 38
    assert {p["session_id"] for p in proposals} == {SESSION_ID}
    by_submitter = {}
    for proposal in proposals:
        by_submitter[proposal["submitted_by"]] = (
            by_submitter.get(proposal["submitted_by"], 0) + 1
        )
    assert by_submitter == {
        "executive": 23,
        "member": 11,
        "resident_petition": 4,
    }
    kinds = {}
    for proposal in proposals:
        kinds[proposal["kind"]] = kinds.get(proposal["kind"], 0) + 1
    assert kinds == {
        "budget": 2,
        "ordinance": 6,
        "other": 12,
        "settlement": 4,
        "resolution": 10,
        "petition": 4,
    }
    outcomes = {}
    for proposal in proposals:
        outcomes[proposal["outcome"]] = (
            outcomes.get(proposal["outcome"], 0) + 1
        )
    assert outcomes == {"approved": 25, "rejected": 2, "pending": 11}
    # The four FY2025 settlement bills (governor bills 20-23) were
    # carried over for continued review: pending, undecided, and
    # without a vote record. They are not recorded as certified.
    settlements = [p for p in proposals if p["kind"] == "settlement"]
    assert len(settlements) == 4
    assert all(p["outcome"] == "pending" for p in settlements)
    assert all(p["decided_at"] is None for p in settlements)
    # Four member bills also remain under continued review.
    member_pending = [
        p
        for p in proposals
        if p["submitted_by"] == "member" and p["outcome"] == "pending"
    ]
    assert {
        p["proposal_number"] for p in member_pending
    } == {"第162号", "第165号", "第168号", "第170号"}
    # Petitions: no. 108 was not adopted; nos. 109-111 continue.
    petitions = [p for p in proposals if p["kind"] == "petition"]
    assert len(petitions) == 4
    by_number = {p["proposal_number"]: p for p in petitions}
    assert by_number["請願第108号"]["outcome"] == "rejected"
    assert by_number["請願第108号"]["decided_at"] == "2026-10-05"
    for number in ("請願第109号", "請願第110号", "請願第111号"):
        assert by_number[number]["outcome"] == "pending"
        assert by_number[number]["decided_at"] is None
    # Bill 171 (seat-count ordinance) was approved; reports 1-9 are
    # not decision items and are not registered.
    bill171 = next(
        p for p in proposals if p["proposal_number"] == "第171号"
    )
    assert bill171["kind"] == "ordinance"
    assert bill171["outcome"] == "approved"
    assert all(
        not p["proposal_number"].startswith("報告") for p in proposals
    )


def test_votes_match_decided_proposals():
    votes = load("votes.json")
    proposals = {p["id"]: p for p in load("proposals.json")}
    assert len(votes) == 27
    # Exactly the decided proposals carry a published faction-mark
    # table (the table includes petition no. 108) and have votes.
    expected = {
        p["id"] for p in proposals.values() if p["outcome"] != "pending"
    }
    assert len(expected) == 27
    assert {v["proposal_id"] for v in votes} == expected
    for vote in votes:
        # The mark table was cross-checked against the June 2026
        # plenary minutes and judged to be a post-vote record, but
        # the September 2026 minutes are not yet published, so the
        # voting method stays unknown and no totals are given.
        assert vote["method"] == "unknown"
        assert vote["member_vote_availability"] == "not_published"
        assert vote["member_votes"] == []
        assert vote["totals"] is None
        assert vote["vote_date"] == "2026-10-05"
        assert vote["outcome"] == proposals[vote["proposal_id"]]["outcome"]


def test_faction_votes_follow_the_published_marks():
    faction_votes = load("faction_votes.json")
    votes = load("votes.json")
    assert len(faction_votes) == 27 * 5
    assert {fv["vote_id"] for fv in faction_votes} == {
        v["id"] for v in votes
    }
    assert {fv["faction_name"] for fv in faction_votes} == FACTIONS
    # 121 in-favour marks, 13 against marks and one absence mark
    # (※ = left the chamber), exactly as printed in the table.
    positions = [fv["position"] for fv in faction_votes]
    assert positions.count("for") == 121
    assert positions.count("against") == 13
    assert positions.count("absent") == 1
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

    # Governor bills 1 and 3: only the Communist column is against.
    for number in ("第1号", "第3号"):
        m = marks(number)
        assert m[KYOSAN] == "against"
        assert sum(1 for v in m.values() if v == "for") == 4
    # Member bill 161 and petition 108: only the Communist column
    # is in favour; both were rejected / not adopted.
    for number in ("第161号", "請願第108号"):
        m = marks(number)
        assert m[KYOSAN] == "for"
        assert sum(1 for v in m.values() if v == "against") == 4
    # Bill 163: the Communist column is ※ (absent from the chamber).
    m163 = marks("第163号")
    assert m163[KYOSAN] == "absent"
    assert sum(1 for v in m163.values() if v == "for") == 4
    # Bill 171: LDP and Ishin/Mushozoku in favour, three against.
    m171 = marks("第171号")
    assert m171[JIMIN] == "for"
    assert m171[ISHIN] == "for"
    assert sum(1 for v in m171.values() if v == "against") == 3


def test_expenses_cover_the_six_fy2025_factions():
    expenses = load("political_activity_expenses.json")
    assert len(expenses) == 6
    assert {e["fiscal_year"] for e in expenses} == {2025}
    assert all(e["recipient_type"] == "faction" for e in expenses)
    # FY2025 had six recipient factions (the current roster has
    # five; ONE for ALLふくしま received funds in FY2025).
    assert {e["recipient_name"] for e in expenses} == {
        JIMIN,
        KENMIN,
        KYOSAN,
        KOMEI,
        ISHIN,
        "ONE for ALLふくしま",
    }
    # Totals reconcile with the official summary (appendix table 1).
    assert sum(e["granted_yen"] for e in expenses) == 204_000_000
    assert sum(e["spent_yen"] for e in expenses) == 200_738_476
    assert sum(e["returned_yen"] for e in expenses) == 3_261_524
    for expense in expenses:
        assert expense["report_status"] == "published"
        # Receipt copies are not published on the web; inspection
        # at the assembly secretariat only.
        assert expense["receipt_access"] == "in_person_only"
        assert expense["returned_yen"] == (
            expense["granted_yen"] - expense["spent_yen"]
        )
        # The ten printed categories sum to the printed total.
        assert len(expense["breakdown"]) == 10
        assert (
            sum(b["amount_yen"] for b in expense["breakdown"])
            == expense["spent_yen"]
        )


def test_inspection_trips_are_the_two_overseas_delegations():
    trips = load("inspection_trips.json")
    assert len(trips) == 2
    assert {t["cost_status"] for t in trips} == {"not_published"}
    assert {t["trip_type"] for t in trips} == {"overseas"}
    assert all(t["total_cost_yen"] is None for t in trips)
    assert all(t["report_status"] == "published" for t in trips)
    by_id = {t["id"]: t for t in trips}
    team_a = by_id[ASSEMBLY_ID + "-inspection-fy2025-overseas-a"]
    team_b = by_id[ASSEMBLY_ID + "-inspection-fy2025-overseas-b"]
    assert (team_a["start_date"], team_a["end_date"]) == (
        "2025-11-18",
        "2025-11-27",
    )
    assert (team_b["start_date"], team_b["end_date"]) == (
        "2025-11-14",
        "2025-11-23",
    )
    assert team_a["participant_count"] == 8
    assert team_b["participant_count"] == 9
    assert all(
        len(t["participants"]) == t["participant_count"] for t in trips
    )
    assert len(team_a["destinations"]) == 13
    assert len(team_b["destinations"]) == 10


def test_disclosure_profile_notes():
    profiles = load("disclosure_profiles.json")
    assert len(profiles) == 1
    items = {item["item"]: item for item in profiles[0]["items"]}
    assert len(items) == 12
    assert items["faction_votes"]["availability"] == "published"
    assert items["faction_votes"]["granularity"] == "faction"
    assert items["member_votes"]["availability"] == "not_published"
    assert (
        items["political_activity_expense_receipts"]["availability"]
        == "restricted"
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
    expenses = {e["id"] for e in load("political_activity_expenses.json")}
    ex = load("expense_evidence_packets.json")
    assert {p["subject_id"] for p in ex} == expenses
    trips = {t["id"] for t in load("inspection_trips.json")}
    ins = load("inspection_evidence_packets.json")
    assert {p["subject_id"] for p in ins} == trips
    assembly_packets = load("assembly_evidence_packets.json")
    assert {
        p["subject_id"] for p in assembly_packets
    } == {ASSEMBLY_ID, SESSION_ID}
    assembly_packet = next(
        p for p in assembly_packets if p["subject_id"] == ASSEMBLY_ID
    )
    # Follow-ups: September minutes cross-check, the four pending
    # settlement bills, and the seven continued member bills whose
    # numbers/titles are not individually published.
    assert len(assembly_packet["open_questions"]) == 3


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
