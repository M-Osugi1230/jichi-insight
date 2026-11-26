import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "reviewed" / "akita-prefecture" / "assembly"
CATALOG = ROOT / "data" / "catalog" / "akita_prefecture_assembly_sources.json"
ASSEMBLY_ID = "jp-local-050008-assembly-2023"
SESSION_OCT = f"{ASSEMBLY_ID}-session-2026-10"
SESSION_SEP = f"{ASSEMBLY_ID}-session-2026-09"


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def catalog():
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def source_ids():
    return {record["id"] for record in catalog()["records"]}


def test_catalog_is_akita_prefecture_only():
    records = catalog()["records"]
    assert len(records) == 8
    assert {record["municipality_key"] for record in records} == {"akita-prefecture"}
    assert len({record["id"] for record in records}) == 8
    categories = {record["category"] for record in records}
    assert {"assembly", "political_activity_expenses", "proposals"} <= categories
    # IDs must not collide with the finance catalog's akita-prefecture-* IDs.
    assert all(record["id"].startswith("akita-pref-assembly-") for record in records)


def test_assembly_record():
    records = load("assembly_records.json")
    assert len(records) == 1
    record = records[0]
    assert record["id"] == ASSEMBLY_ID
    assert record["municipality_id"] == "jp-local-050008"
    assert record["name"] == "秋田県議会"
    assert record["seat_count"] == 41
    assert record["term_start"] == "2023-04-30"
    assert record["term_end"] == "2027-04-29"
    # November 2026 composition, read from the vote-table faction headers.
    assert [f["member_count"] for f in record["factions"]] == [27, 5, 4, 1, 1, 1, 1, 1]
    assert sum(f["member_count"] for f in record["factions"]) == 41
    assert len(record["committees"]) == 9
    assert set(record["sources"]) <= source_ids()


def test_sessions_are_completed_parts_of_second_regular_session():
    sessions = load("sessions.json")
    assert len(sessions) == 2
    by_id = {s["id"]: s for s in sessions}
    october = by_id[SESSION_OCT]
    assert october["name"] == "令和8年第2回定例会（10月議会）"
    assert october["session_type"] == "regular"
    assert october["start_date"] == "2026-10-14"
    assert october["end_date"] == "2026-11-02"
    september = by_id[SESSION_SEP]
    assert september["name"] == "令和8年第2回定例会（9月議会）"
    assert september["start_date"] == "2026-09-08"
    assert september["end_date"] == "2026-10-07"
    # The December part is still in session (the 2nd regular session itself
    # continues), so it is intentionally not registered.
    assert all("12月" not in s["name"] for s in sessions)


def test_proposals_are_the_three_settlement_certifications():
    proposals = load("proposals.json")
    assert len(proposals) == 3
    assert all(p["kind"] == "settlement" for p in proposals)
    assert all(p["outcome"] == "approved" for p in proposals)
    assert all(p["submitted_by"] == "executive" for p in proposals)
    by_number = {p["proposal_number"]: p for p in proposals}
    assert by_number["認定第3号"]["session_id"] == SESSION_OCT
    assert by_number["認定第3号"]["title"] == "令和7年度秋田県歳入歳出決算の認定について"
    assert by_number["認定第3号"]["decided_at"] == "2026-11-02"
    # 認定第1号・第2号 are printed with identical titles in the primary
    # source; they are registered as printed, without guessing which
    # public-enterprise account each covers.
    assert by_number["認定第1号"]["title"] == by_number["認定第2号"]["title"]
    assert by_number["認定第1号"]["session_id"] == SESSION_SEP
    assert by_number["認定第2号"]["session_id"] == SESSION_SEP


def test_votes_match_printed_totals_and_member_symbols():
    votes = load("votes.json")
    assert len(votes) == 3
    for vote in votes:
        assert vote["member_vote_availability"] == "published"
        assert len(vote["member_votes"]) == 41
        positions = [m["position"] for m in vote["member_votes"]]
        totals = vote["totals"]
        assert positions.count("for") == totals["for"]
        assert positions.count("against") == totals["against"]
        assert positions.count("abstained") == totals["abstained"]
        assert positions.count("absent") == totals["absent"]
        # The speaker (excused) does not vote; the four totals plus the
        # speaker account for all 41 members.
        assert positions.count("excused") == 1
        assert sum(totals.values()) + 1 == 41
        chair = next(m for m in vote["member_votes"] if m["position"] == "excused")
        assert chair["member_name"] == "工藤嘉範"
    by_proposal = {v["proposal_id"]: v for v in votes}
    oct_vote = by_proposal[f"{ASSEMBLY_ID}-proposal-2026-10-001"]
    assert oct_vote["method"] == "standing"
    assert oct_vote["vote_date"] == "2026-11-02"
    assert oct_vote["totals"] == {"absent": 1, "abstained": 0, "against": 1, "for": 38}
    sep1 = by_proposal[f"{ASSEMBLY_ID}-proposal-2026-09-001"]
    assert sep1["method"] == "standing"
    assert sep1["totals"] == {"absent": 2, "abstained": 0, "against": 1, "for": 37}
    sep2 = by_proposal[f"{ASSEMBLY_ID}-proposal-2026-09-002"]
    assert sep2["method"] == "voice"
    assert sep2["totals"] == {"absent": 2, "abstained": 0, "against": 0, "for": 38}
    # The sole dissenting member in both standing votes.
    for vote in (oct_vote, sep1):
        dissent = [m["member_name"] for m in vote["member_votes"] if m["position"] == "against"]
        assert dissent == ["加賀屋千鶴子"]


def test_faction_votes_empty_because_not_published():
    assert load("faction_votes.json") == []


def test_political_activity_expenses_cover_all_48_units():
    expenses = load("political_activity_expenses.json")
    assert len(expenses) == 48
    factions = [e for e in expenses if e["recipient_type"] == "faction"]
    members = [e for e in expenses if e["recipient_type"] == "member"]
    assert len(factions) == 7
    assert len(members) == 41
    assert {e["recipient_name"] for e in factions} == {
        "自由民主党", "みらい", "立憲民主党", "社会民主党", "日本共産党", "公明党", "きらり",
    }
    for expense in expenses:
        assert expense["fiscal_year"] == 2025
        assert expense["report_status"] == "published"
        # Receipts are published online together with the reports.
        assert expense["receipt_access"] == "online"
        # Arithmetic printed on each report form must hold exactly.
        assert sum(b["amount_yen"] for b in expense["breakdown"]) == expense["spent_yen"]
        assert expense["granted_yen"] - expense["spent_yen"] == expense["returned_yen"]
        assert set(expense["sources"]) <= source_ids()
    # Full-year members receive 280,000 yen/month; the two members elected
    # in the 2025 by-election receive 11 months.
    member_grants = sorted(e["granted_yen"] for e in members)
    assert member_grants == [3080000, 3080000] + [3360000] * 39
    assert sum(e["granted_yen"] for e in members) == 137200000
    assert sum(e["granted_yen"] for e in factions) == 14700000
    # Member forms have 10 categories (incl. 事務所費); faction forms have 9.
    assert all(len(e["breakdown"]) == 10 for e in members)
    assert all(len(e["breakdown"]) == 9 for e in factions)
    assert all(
        b["category"] != "事務所費" for e in factions for b in e["breakdown"]
    )


def test_inspection_trips_empty_with_disclosed_gap():
    assert load("inspection_trips.json") == []
    profile = load("disclosure_profiles.json")[0]
    items = {i["item"]: i for i in profile["items"]}
    assert items["inspection_trip_reports"]["availability"] == "not_published"


def test_disclosure_profile_covers_twelve_items():
    profiles = load("disclosure_profiles.json")
    assert len(profiles) == 1
    profile = profiles[0]
    assert profile["assembly_id"] == ASSEMBLY_ID
    assert len(profile["items"]) == 12
    items = {i["item"]: i for i in profile["items"]}
    assert items["member_votes"]["availability"] == "published"
    assert items["faction_votes"]["availability"] == "not_published"
    assert items["political_activity_expense_receipts"]["availability"] == "published"
    # The profile must state the nature caveat for voice (簡易) votes.
    assert "簡易表決" in items["member_votes"]["note"]
    assert set(profile["sources"]) <= source_ids()


def test_evidence_packets_cover_all_subjects():
    assembly_packets = load("assembly_evidence_packets.json")
    assert len(assembly_packets) == 1
    packet = assembly_packets[0]
    assert packet["subject_id"] == ASSEMBLY_ID
    assert {c["field"] for c in packet["claims"]} == {
        "term_and_seats", "factions", "committees", "session_scope",
    }
    # The unfinished cross-check against the minutes system and the
    # unregistered remainder of the September part stay as open questions.
    assert len(packet["open_questions"]) == 4
    pv_packets = load("proposal_vote_evidence_packets.json")
    assert len(pv_packets) == 3
    assert {p["subject_id"] for p in pv_packets} == {
        p["id"] for p in load("proposals.json")
    }
    exp_packets = load("expense_evidence_packets.json")
    assert len(exp_packets) == 48
    assert {p["subject_id"] for p in exp_packets} == {
        e["id"] for e in load("political_activity_expenses.json")
    }
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
