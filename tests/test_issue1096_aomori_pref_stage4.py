"""Issue #1096: Aomori Prefectural Assembly stage-4 registration checks."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "reviewed" / "aomori-prefecture" / "assembly"
CATALOG = (
    ROOT / "data" / "catalog" / "aomori_prefecture_assembly_sources.json"
)
ASSEMBLY_ID = "jp-local-020001-assembly-2023"
SESSION_ID = "jp-local-020001-assembly-2023-session-2026-09"
JIMIN = "自由民主党"
ALL = "オール青森"
RIKKEN_M = "立憲民主・無所属の会"
KYOSAN = "日本共産党"
KOMEI = "公明党"
RIKKEN_K = "立憲民主・憲法をいかす県民の会"
SANSEI = "参政党"
MUSHOZOKU = "無所属"
FACTIONS = {JIMIN, ALL, RIKKEN_M, KYOSAN, KOMEI, RIKKEN_K, SANSEI, MUSHOZOKU}


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def source_ids():
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    return {record["id"] for record in catalog["records"]}


def test_catalog_is_aomori_prefecture_only():
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    records = catalog["records"]
    assert len(records) == 21
    assert {r["municipality_key"] for r in records} == {
        "aomori-prefecture"
    }
    assert len(source_ids()) == 21
    categories = {r["category"] for r in records}
    assert {
        "assembly",
        "inspection_trips",
        "political_activity_expenses",
        "proposals",
    } <= categories
    # The assembly catalog uses its own ID prefix so it cannot collide
    # with the fiscal catalog's aomori-pref-* IDs.
    assert all(
        r["id"].startswith("aomori-pref-assembly-") for r in records
    )


def test_assembly_record_matches_official_roster():
    records = load("assembly_records.json")
    assert len(records) == 1
    record = records[0]
    assert record["id"] == ASSEMBLY_ID
    assert record["municipality_id"] == "jp-local-020001"
    assert record["name"] == "青森県議会"
    # The term end (2027-04-29) is printed on the official district
    # roster; the start is the day after the previous term expired.
    assert record["term_start"] == "2023-04-30"
    assert record["term_end"] == "2027-04-29"
    # Statutory strength 48, current membership 46: the gojuon roster
    # prints "【定数48人】（欠員2人）".
    assert record["seat_count"] == 48
    sizes = [f["member_count"] for f in record["factions"]]
    assert sizes == [27, 5, 4, 3, 2, 2, 1, 2]
    assert sum(sizes) == 46
    assert {f["name"] for f in record["factions"]} == FACTIONS
    assert len(record["committees"]) == 10


def test_session_is_327th_regular_session():
    sessions = load("sessions.json")
    assert len(sessions) == 1
    session = sessions[0]
    assert session["id"] == SESSION_ID
    assert session["name"] == "令和8年9月第327回定例会"
    assert session["session_type"] == "regular"
    assert session["start_date"] == "2026-09-10"
    assert session["end_date"] == "2026-10-01"


def test_proposals_cover_all_kinds_and_outcomes():
    proposals = load("proposals.json")
    assert len(proposals) == 45
    assert {p["session_id"] for p in proposals} == {SESSION_ID}
    by_submitter = {}
    for proposal in proposals:
        by_submitter[proposal["submitted_by"]] = (
            by_submitter.get(proposal["submitted_by"], 0) + 1
        )
    assert by_submitter == {
        "executive": 29,
        "member": 14,
        "resident_petition": 2,
    }
    kinds = {}
    for proposal in proposals:
        kinds[proposal["kind"]] = kinds.get(proposal["kind"], 0) + 1
    assert kinds == {
        "budget": 4,
        "ordinance": 4,
        "other": 22,
        "personnel": 1,
        "settlement": 4,
        "resolution": 8,
        "petition": 2,
    }
    outcomes = {}
    for proposal in proposals:
        outcomes[proposal["outcome"]] = (
            outcomes.get(proposal["outcome"], 0) + 1
        )
    assert outcomes == {"approved": 30, "rejected": 8, "pending": 7}
    # The four FY2025 settlement bills (26-29) and the three surplus /
    # reserve bills (22-24) were referred to the settlement special
    # committee and left undecided in the plenary: pending, no decided
    # date, no vote record. They are not recorded as certified.
    pending = [p for p in proposals if p["outcome"] == "pending"]
    assert {
        p["proposal_number"] for p in pending
    } == {"第22号", "第23号", "第24号", "第26号", "第27号", "第28号", "第29号"}
    assert all(p["decided_at"] is None for p in pending)
    settlements = [p for p in proposals if p["kind"] == "settlement"]
    assert len(settlements) == 4
    assert all(p["outcome"] == "pending" for p in settlements)
    # Member bills 1-6 were rejected en bloc on 2026-09-28; 7-8 passed.
    member_bills = {
        p["proposal_number"]: p
        for p in proposals
        if p["proposal_number"].startswith("発議")
    }
    assert len(member_bills) == 8
    for i in range(1, 7):
        bill = member_bills[f"発議第{i}号"]
        assert bill["outcome"] == "rejected"
        assert bill["decided_at"] == "2026-09-28"
    for i in (7, 8):
        assert member_bills[f"発議第{i}号"]["outcome"] == "approved"
    # The petition and the petition-like 陳情 were both not adopted;
    # the vote was on the committee chair's report (不採択).
    petitions = [p for p in proposals if p["kind"] == "petition"]
    assert len(petitions) == 2
    assert all(p["outcome"] == "rejected" for p in petitions)
    assert all(p["decided_at"] == "2026-10-01" for p in petitions)
    # The 29 governor-submitted reports （報告） are not decision items
    # and are not registered.
    assert all(
        not p["proposal_number"].startswith("報告") for p in proposals
    )


def test_votes_match_decided_proposals():
    votes = load("votes.json")
    proposals = {p["id"]: p for p in load("proposals.json")}
    assert len(votes) == 38
    expected = {
        p["id"] for p in proposals.values() if p["outcome"] != "pending"
    }
    assert len(expected) == 38
    assert {v["proposal_id"] for v in votes} == expected
    for vote in votes:
        # The mark table was cross-checked against the session minutes
        # (速報版): standing votes were actually held, so the method is
        # standing, except the six member dispatches decided without
        # objection (unanimous).
        if proposals[vote["proposal_id"]]["proposal_number"].startswith(
            "議員派遣"
        ):
            assert vote["method"] == "unanimous"
        else:
            assert vote["method"] == "standing"
        assert vote["member_vote_availability"] == "published"
        assert len(vote["member_votes"]) == 46
        assert vote["outcome"] == proposals[vote["proposal_id"]]["outcome"]
        totals = vote["totals"]
        # Printed totals: 45 voting members (46 minus the chair).
        assert totals["for"] + totals["against"] == 45
        assert totals["absent"] == 0 and totals["abstained"] == 0
        marks = [m["position"] for m in vote["member_votes"]]
        assert marks.count("for") == totals["for"]
        assert marks.count("against") == totals["against"]
        assert marks.count("excused") == 1
        chair = next(
            m for m in vote["member_votes"] if m["position"] == "excused"
        )
        assert chair["member_name"] == "工藤慎康"


def test_member_vote_splits_match_the_printed_table():
    votes = load("votes.json")
    proposals = {p["id"]: p for p in load("proposals.json")}
    by_number = {
        proposals[v["proposal_id"]]["proposal_number"]: v for v in votes
    }

    def against_names(number):
        return {
            m["member_name"]
            for m in by_number[number]["member_votes"]
            if m["position"] == "against"
        }

    # Bill 2: only Gotō (Sanseitō) against. Bill 3: only Shikanai
    # against (verified against the table's header glyphs).
    assert against_names("第2号") == {"後藤清安"}
    assert against_names("第3号") == {"鹿内博"}
    # Bills 5 and 6: the three Communist members against.
    for number in ("第5号", "第6号"):
        assert against_names(number) == {"安藤晴美", "吉俣洋", "田端深雪"}
    # Member bills 1-6: 12 for / 33 against, identical marks.
    for i in range(1, 7):
        vote = by_number[f"発議第{i}号"]
        assert vote["totals"]["for"] == 12
        assert vote["totals"]["against"] == 33
        assert vote["vote_date"] == "2026-09-28"
    # Petition: 41/4 (Communists + Shikanai against the chair's report).
    petition = by_number["請願受理番号第2号"]
    assert petition["totals"] == {
        "absent": 0, "abstained": 0, "against": 4, "for": 41,
    }
    assert against_names("請願受理番号第2号") == {
        "安藤晴美", "吉俣洋", "田端深雪", "鹿内博",
    }
    # 陳情: 43/2.
    assert against_names("陳情受理番号第1号") == {"鹿内博", "後藤清安"}


def test_faction_votes_are_aggregated_member_marks():
    faction_votes = load("faction_votes.json")
    votes = load("votes.json")
    assert len(faction_votes) == 38 * 8
    assert {fv["vote_id"] for fv in faction_votes} == {v["id"] for v in votes}
    assert {fv["faction_name"] for fv in faction_votes} == FACTIONS
    by_vote = {v["id"]: v for v in votes}
    for vote in votes:
        rows = [fv for fv in faction_votes if fv["vote_id"] == vote["id"]]
        assert len(rows) == 8
        assert sum(r["member_count"] for r in rows) == 46
        assert sum(r["for_count"] for r in rows) == vote["totals"]["for"]
        assert (
            sum(r["against_count"] for r in rows)
            == vote["totals"]["against"]
        )
        # The chair belongs to the LDP: its member_count includes him
        # (27) but he is in neither the for nor the against count.
        jimin = next(r for r in rows if r["faction_name"] == JIMIN)
        assert jimin["member_count"] == 27
        assert jimin["for_count"] + jimin["against_count"] <= 26

    def faction_row(number, faction):
        proposals = {p["id"]: p for p in load("proposals.json")}
        vote = next(
            v for v in votes
            if proposals[v["proposal_id"]]["proposal_number"] == number
        )
        return next(
            fv for fv in faction_votes
            if fv["vote_id"] == vote["id"]
            and fv["faction_name"] == faction
        )

    # Bill 3 split the two-member Rikken-Kenpo group 1-1.
    row = faction_row("第3号", RIKKEN_K)
    assert row["position"] == "split"
    assert (row["for_count"], row["against_count"]) == (1, 1)
    # Member bill 1: LDP against (26 voting), independents split.
    row = faction_row("発議第1号", JIMIN)
    assert row["position"] == "against"
    assert row["against_count"] == 26
    row = faction_row("発議第1号", MUSHOZOKU)
    assert row["position"] == "split"
    assert (row["for_count"], row["against_count"]) == (1, 1)
    # Bill 5: Communists against, everyone else for.
    row = faction_row("第5号", KYOSAN)
    assert row["position"] == "against"
    assert row["against_count"] == 3
    assert by_vote[row["vote_id"]]["totals"]["against"] == 3


def test_expenses_reconcile_with_official_totals():
    expenses = load("political_activity_expenses.json")
    assert len(expenses) == 51
    assert {e["fiscal_year"] for e in expenses} == {2025}
    members = [e for e in expenses if e["recipient_type"] == "member"]
    commons = [e for e in expenses if e["recipient_type"] == "faction"]
    assert len(members) == 48
    assert len(commons) == 3
    assert {e["recipient_name"] for e in commons} == {
        "自由民主党共通経費",
        "立憲民主・無所属の会共通経費",
        "日本共産党共通経費",
    }
    # Official aggregates (assembly's political-activity page) cover
    # the 48 member reports only; they reconcile exactly.
    assert sum(e["granted_yen"] for e in members) == 177_010_000
    assert (
        sum(min(e["spent_yen"], e["granted_yen"]) for e in members)
        == 138_523_992
    )
    assert (
        sum(
            e["returned_yen"] for e in members if e["returned_yen"] > 0
        )
        == 38_486_008
    )
    for expense in expenses:
        assert expense["report_status"] == "published"
        # Receipt copies are not published on the web; inspection by
        # viewing request at the assembly.
        assert expense["receipt_access"] == "in_person_only"
        assert expense["returned_yen"] == (
            expense["granted_yen"] - expense["spent_yen"]
        )
        assert len(expense["breakdown"]) == 10
        assert (
            sum(b["amount_yen"] for b in expense["breakdown"])
            == expense["spent_yen"]
        )
    # Fourteen members spent beyond their grant; the printed balance
    # is negative (△) and is registered as printed.
    overspent = [e for e in members if e["returned_yen"] < 0]
    assert len(overspent) == 14
    # Retired members received pro-rated grants (310,000 yen/month):
    # Abe and Tanigawa 11 months, Kudō Takahiro 9 months.
    by_name = {e["recipient_name"]: e for e in members}
    assert by_name["阿部広悦"]["granted_yen"] == 3_410_000
    assert by_name["谷川政人"]["granted_yen"] == 3_410_000
    assert by_name["工藤貴弘"]["granted_yen"] == 2_790_000
    assert by_name["田中順造"]["granted_yen"] == 3_720_000


def test_inspection_trips_are_the_four_fy2026_dispatches():
    trips = load("inspection_trips.json")
    assert len(trips) == 4
    assert {t["cost_status"] for t in trips} == {"not_published"}
    assert all(t["total_cost_yen"] is None for t in trips)
    assert all(t["report_status"] == "published" for t in trips)
    by_id = {t["id"]: t for t in trips}
    tottori = by_id[ASSEMBLY_ID + "-inspection-fy2026-domestic-tottori"]
    assert (tottori["start_date"], tottori["end_date"]) == (
        "2026-04-15",
        "2026-04-17",
    )
    assert tottori["participant_count"] == 5
    nagasaki = by_id[ASSEMBLY_ID + "-inspection-fy2026-domestic-nagasaki"]
    assert nagasaki["participant_count"] == 10
    shimane = by_id[ASSEMBLY_ID + "-inspection-fy2026-domestic-shimane"]
    assert (shimane["start_date"], shimane["end_date"]) == (
        "2026-10-21",
        "2026-10-22",
    )
    assert shimane["participant_count"] == 4
    overseas = by_id[ASSEMBLY_ID + "-inspection-fy2026-overseas-nz-au"]
    assert overseas["trip_type"] == "overseas"
    assert overseas["participant_count"] == 9
    assert all(
        len(t["participants"]) == t["participant_count"] for t in trips
    )


def test_disclosure_profile_notes():
    profiles = load("disclosure_profiles.json")
    assert len(profiles) == 1
    items = {item["item"]: item for item in profiles[0]["items"]}
    assert len(items) == 12
    assert items["member_votes"]["availability"] == "published"
    assert items["member_votes"]["granularity"] == "member"
    assert items["faction_votes"]["availability"] == "published"
    assert (
        items["political_activity_expense_receipts"]["availability"]
        == "restricted"
    )
    assert "欠員2人" in items["member_roster"]["note"]
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
    # Follow-ups: the seven pending bills referred to the settlement
    # special committee, and the absence of a separately published
    # faction-position table.
    assert len(assembly_packet["open_questions"]) == 2


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
