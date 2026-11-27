import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "reviewed" / "iwate-prefecture" / "assembly"
CATALOG = ROOT / "data" / "catalog" / "iwate_prefecture_assembly_sources.json"
FINANCE_CATALOG = ROOT / "data" / "catalog" / "iwate_prefecture_finance_sources.json"
ASSEMBLY_ID = "jp-local-030007-assembly-2023"
SESSION_ID = f"{ASSEMBLY_ID}-session-2026-09"


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def catalog():
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def source_ids():
    return {record["id"] for record in catalog()["records"]}


def test_catalog_is_iwate_prefecture_only():
    records = catalog()["records"]
    assert len(records) == 14
    assert {record["municipality_key"] for record in records} == {"iwate-prefecture"}
    assert len({record["id"] for record in records}) == 14
    categories = {record["category"] for record in records}
    assert {"assembly", "political_activity_expenses", "proposals"} <= categories
    assert all(record["id"].startswith("iwate-pref-assembly-") for record in records)
    # IDs must not collide with the finance catalog's iwate-pref-* IDs
    # (which already use two iwate-pref-assembly-2026-feb-* IDs).
    finance_ids = {
        record["id"]
        for record in json.loads(FINANCE_CATALOG.read_text(encoding="utf-8"))["records"]
    }
    assert not (source_ids() & finance_ids)


def test_assembly_record():
    records = load("assembly_records.json")
    assert len(records) == 1
    record = records[0]
    assert record["id"] == ASSEMBLY_ID
    assert record["municipality_id"] == "jp-local-030007"
    assert record["name"] == "岩手県議会"
    assert record["seat_count"] == 48
    assert record["term_start"] == "2023-09-11"
    assert record["term_end"] == "2027-09-10"
    # Measured 2026-11-27 from the official faction roster: 44 sitting
    # members (4 vacancies after resignations) in 9 factions.
    assert [f["member_count"] for f in record["factions"]] == [16, 13, 5, 4, 2, 1, 1, 1, 1]
    assert sum(f["member_count"] for f in record["factions"]) == 44
    assert len(record["committees"]) == 11
    assert set(record["sources"]) <= source_ids()


def test_session_is_september_2026_regular_session():
    sessions = load("sessions.json")
    assert len(sessions) == 1
    session = sessions[0]
    assert session["id"] == SESSION_ID
    assert session["name"] == "令和8年9月定例会"
    assert session["session_type"] == "regular"
    assert session["start_date"] == "2026-09-25"
    assert session["end_date"] == "2026-10-27"
    # The December session is still sitting, so it is not registered.


def test_proposals_cover_the_whole_september_session():
    proposals = load("proposals.json")
    assert len(proposals) == 61
    by_number = {p["proposal_number"]: p for p in proposals}
    governor = [p for p in proposals if p["submitted_by"] == "executive"]
    assert len(governor) == 42  # 議案27 + 認定15
    member = [p for p in proposals if p["submitted_by"] == "member"]
    assert len(member) == 11  # 発議案
    petitions = [p for p in proposals if p["kind"] == "petition"]
    assert len(petitions) == 8  # 請願6件、第102号は項目別に3件
    assert all(p["session_id"] == SESSION_ID for p in proposals)
    assert by_number["議案第26号"]["kind"] == "personnel"
    assert by_number["議案第26号"]["decided_at"] == "2026-09-25"
    assert by_number["議案第27号"]["submitted_at"] == "2026-10-02"
    assert by_number["発議案第2号"]["kind"] == "ordinance"
    assert "定数等に関する条例" in by_number["発議案第2号"]["title"]
    # Petition No. 102 was voted item by item with split outcomes.
    assert by_number["請願第102号（項目1）"]["outcome"] == "rejected"
    assert by_number["請願第102号（項目2）"]["outcome"] == "approved"
    assert by_number["請願第102号（項目3）"]["outcome"] == "rejected"
    assert by_number["請願第97号"]["outcome"] == "rejected"
    assert by_number["請願第99号"]["outcome"] == "approved"
    for p in proposals:
        assert set(p["sources"]) <= source_ids()


def test_pending_settlement_is_registered_without_a_vote():
    proposals = load("proposals.json")
    by_number = {p["proposal_number"]: p for p in proposals}
    pending = by_number["認定第1号"]
    assert pending["kind"] == "settlement"
    assert pending["outcome"] == "pending"
    assert pending["decided_at"] is None
    votes = load("votes.json")
    assert pending["id"] not in {v["proposal_id"] for v in votes}
    decided = [p for p in proposals if p["kind"] == "settlement" and p["outcome"] == "approved"]
    assert len(decided) == 14
    assert all(p["decided_at"] == "2026-10-27" for p in decided)


def test_votes_match_printed_totals_and_member_symbols():
    votes = load("votes.json")
    assert len(votes) == 60
    for vote in votes:
        assert vote["member_vote_availability"] == "published"
        # The September session's minutes are not yet published, so the
        # nature of the vote table could not be cross-checked and the
        # method stays unknown (tracked in Issue #706).
        assert vote["method"] == "unknown"
        assert len(vote["member_votes"]) == 44
        positions = [m["position"] for m in vote["member_votes"]]
        totals = vote["totals"]
        assert positions.count("for") == totals["for"]
        assert positions.count("against") == totals["against"]
        assert positions.count("abstained") == totals["abstained"]
        assert positions.count("absent") == totals["absent"]
        # The speaker (excused) does not vote; the four totals plus the
        # speaker account for all 44 sitting members.
        assert positions.count("excused") == 1
        assert sum(totals.values()) + 1 == 44
        chair = next(m for m in vote["member_votes"] if m["position"] == "excused")
        assert chair["member_name"] == "城内愛彦"
        assert set(vote["sources"]) <= source_ids()
    by_number = {
        p["proposal_number"]: p for p in load("proposals.json")
    }
    by_proposal = {v["proposal_id"]: v for v in votes}
    consent = by_proposal[by_number["議案第26号"]["id"]]
    assert consent["totals"] == {"absent": 4, "abstained": 0, "against": 0, "for": 39}
    assert consent["vote_date"] == "2026-09-25"
    petition97 = by_proposal[by_number["請願第97号"]["id"]]
    assert petition97["totals"] == {"absent": 2, "abstained": 0, "against": 23, "for": 18}
    seat_bill = by_proposal[by_number["発議案第2号"]["id"]]
    assert seat_bill["totals"] == {"absent": 3, "abstained": 0, "against": 15, "for": 25}
    # はぎの幸弘 was printed "－" (not present in the chamber) and is
    # registered as absent alongside the two "欠" members.
    absent_names = {
        m["member_name"] for m in seat_bill["member_votes"] if m["position"] == "absent"
    }
    assert absent_names == {"大久保隆規", "上原康樹", "はぎの幸弘"}


def test_faction_votes_empty_because_not_published():
    assert load("faction_votes.json") == []


def test_political_activity_expenses_cover_all_48_units():
    expenses = load("political_activity_expenses.json")
    assert len(expenses) == 48
    assert all(e["recipient_type"] == "member" for e in expenses)
    for expense in expenses:
        assert expense["fiscal_year"] == 2025
        assert expense["report_status"] == "published"
        # Receipts are viewable only in person under the reading system.
        assert expense["receipt_access"] == "in_person_only"
        assert len(expense["breakdown"]) == 10
        # The breakdown printed on each report form sums to the printed
        # total expenditure.
        assert sum(b["amount_yen"] for b in expense["breakdown"]) == expense["spent_yen"]
        # Most units satisfy granted - spent == returned; units whose
        # printed expenditure exceeds the grant print a remainder of 0.
        if expense["spent_yen"] <= expense["granted_yen"]:
            assert expense["granted_yen"] - expense["spent_yen"] == expense["returned_yen"]
        else:
            assert expense["returned_yen"] == 0
        assert set(expense["sources"]) <= source_ids()
    # 310,000 yen per month: full-year members receive 3,720,000 yen; the
    # three members who resigned mid-year receive 7, 8 and 10 months.
    grants = sorted(e["granted_yen"] for e in expenses)
    assert grants == [2170000, 2480000, 3100000] + [3720000] * 45
    by_name = {e["recipient_name"]: e for e in expenses}
    assert by_name["中平均"]["granted_yen"] == 2480000
    assert by_name["五日市王"]["granted_yen"] == 2170000
    assert by_name["郷右近浩"]["granted_yen"] == 3100000


def test_inspection_trips_empty_with_disclosed_scope():
    assert load("inspection_trips.json") == []
    profile = load("disclosure_profiles.json")[0]
    items = {i["item"]: i for i in profile["items"]}
    # Trip lists (committee, period, destinations) are published in the
    # assembly library, but costs and reports are not.
    assert items["inspection_trip_reports"]["availability"] == "published"


def test_disclosure_profile_covers_twelve_items():
    profiles = load("disclosure_profiles.json")
    assert len(profiles) == 1
    profile = profiles[0]
    assert profile["assembly_id"] == ASSEMBLY_ID
    assert len(profile["items"]) == 12
    items = {i["item"]: i for i in profile["items"]}
    assert items["member_votes"]["availability"] == "published"
    assert items["faction_votes"]["availability"] == "not_published"
    assert items["political_activity_expense_receipts"]["availability"] == "restricted"
    # The profile must state the unverified nature of the vote table.
    assert "unknown" in items["member_votes"]["note"]
    assert set(profile["sources"]) <= source_ids()


def test_evidence_packets_cover_all_subjects():
    assembly_packets = load("assembly_evidence_packets.json")
    assert len(assembly_packets) == 2
    by_subject = {p["subject_id"]: p for p in assembly_packets}
    packet = by_subject[ASSEMBLY_ID]
    assert {c["field"] for c in packet["claims"]} == {
        "term_and_seats", "factions", "committees",
        "member_vote_table_nature", "seat_revision",
    }
    # The minutes cross-check and the pending settlement stay open.
    assert len(packet["open_questions"]) == 2
    assert by_subject[SESSION_ID]["claims"][0]["field"] == "session_dates"
    pv_packets = load("proposal_vote_evidence_packets.json")
    assert len(pv_packets) == 121  # 61 proposals + 60 votes
    assert {p["subject_id"] for p in pv_packets} == (
        {p["id"] for p in load("proposals.json")}
        | {v["id"] for v in load("votes.json")}
    )
    exp_packets = load("expense_evidence_packets.json")
    assert len(exp_packets) == 48
    assert {p["subject_id"] for p in exp_packets} == {
        e["id"] for e in load("political_activity_expenses.json")
    }
    assert load("inspection_evidence_packets.json") == []
    all_packets = assembly_packets + pv_packets + exp_packets
    for p in all_packets:
        for claim in p["claims"]:
            assert set(claim["source_ids"]) <= source_ids()


def test_all_record_sources_resolve_to_catalog():
    for name in (
        "assembly_records.json",
        "sessions.json",
        "proposals.json",
        "votes.json",
        "political_activity_expenses.json",
        "disclosure_profiles.json",
    ):
        for record in load(name):
            assert set(record["sources"]) <= source_ids(), (name, record["id"])
