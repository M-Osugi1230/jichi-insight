"""Issue #1050 stage 4: Yamagata City assembly registration checks.

Pins the counts and cross-checks for the Yamagata City Council data
taken from the September 2026 regular session (令和8年9月定例会,
2026-09-03 to 2026-09-25), the FY2025 political activity expense
reports (33 member reports), and the FY2025 committee inspection
trips reported in the council newsletter (市議会報「みちしるべ」
第234号・第235号).
"""

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "reviewed" / "yamagata-city" / "assembly"
CATALOG = ROOT / "data" / "catalog" / "yamagata_city_assembly_sources.json"
ASM = "jp-local-062014-assembly-2023"
SESSION = f"{ASM}-session-2026-09"
CATEGORIES = ["研究研修費", "調査旅費", "広報広聴費", "要請・陳情活動費",
              "資料作成費", "資料購入費", "人件費", "事務所費", "通信・交通費"]
FACTION_COUNTS = {
    "新翔会": 11,
    "未来やまがた": 5,
    "令政会": 5,
    "緑政会": 4,
    "山形市議会公明党": 3,
    "会派に属さない議員": 5,
}


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def load_schema(name):
    return json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))


def validate(schema_name, records):
    schema = load_schema(schema_name)
    for record in records:
        jsonschema.validate(record, schema)


def test_catalog_is_valid_and_unique():
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    jsonschema.validate(catalog, load_schema("source_catalog.schema.json"))
    records = catalog["records"]
    ids = [entry["id"] for entry in records]
    assert len(ids) == len(set(ids))
    assert all(
        entry["municipality_key"] == "yamagata-city" for entry in records
    )
    # 12 general sources plus one record per expense report.
    assert len(records) == 45


def test_assembly_record():
    records = load("assembly_records.json")
    validate("assembly.schema.json", records)
    assert len(records) == 1
    record = records[0]
    assert record["id"] == ASM
    assert record["municipality_id"] == "jp-local-062014"
    assert record["name"] == "山形市議会"
    assert record["seat_count"] == 33
    # Term end 2027-04-30 is printed in the prefectural election
    # commission's term list (as of 2026-04-22); the four-year term
    # starts 2023-05-01.
    assert record["term_start"] == "2023-05-01"
    assert record["term_end"] == "2027-04-30"
    by_name = {f["name"]: f["member_count"] for f in record["factions"]}
    assert by_name == FACTION_COUNTS
    # The faction page (updated 2026-06-04) lists all 33 members.
    assert sum(by_name.values()) == 33
    assert len(record["committees"]) == 10


def test_sessions():
    sessions = load("sessions.json")
    validate("session.schema.json", sessions)
    assert len(sessions) == 1
    session = sessions[0]
    assert session["id"] == SESSION
    assert session["name"] == "令和8年9月定例会"
    assert session["session_type"] == "regular"
    assert session["start_date"] == "2026-09-03"
    assert session["end_date"] == "2026-09-25"


def test_proposals():
    proposals = load("proposals.json")
    validate("proposal.schema.json", proposals)
    assert len(proposals) == 23
    kinds = {}
    for p in proposals:
        kinds[p["kind"]] = kinds.get(p["kind"], 0) + 1
    assert kinds == {
        "budget": 3,
        "ordinance": 4,
        "other": 8,
        "petition": 3,
        "settlement": 5,
    }
    assert sum(1 for p in proposals if p["submitted_by"] == "executive") == 20
    assert (
        sum(1 for p in proposals if p["submitted_by"] == "resident_petition")
        == 3
    )
    assert all(p["session_id"] == SESSION for p in proposals)
    assert sum(1 for p in proposals if p["outcome"] == "approved") == 20
    assert sum(1 for p in proposals if p["outcome"] == "pending") == 3
    # All five FY2025 settlements (議第59号 to 議第63号) were
    # certified on 2026-09-25; none was rejected.
    settlements = [p for p in proposals if p["kind"] == "settlement"]
    assert len(settlements) == 5
    assert all(p["outcome"] == "approved" for p in settlements)
    assert all(p["decided_at"] == "2026-09-25" for p in settlements)
    by_number = {p["proposal_number"]: p for p in proposals}
    # Bill 64 (supplementary budget) was decided on the opening day;
    # the other 19 mayoral bills on the closing day.
    assert by_number["議第64号"]["decided_at"] == "2026-09-03"
    for n in range(59, 79):
        if n == 64:
            continue
        assert by_number[f"議第{n}号"]["decided_at"] == "2026-09-25"
    assert by_number["議第59号"]["title"] == (
        "令和7年度山形市一般会計及び特別会計歳入歳出決算認定について"
    )
    # The three petitions were all kept under continued review, so
    # no adoption decision date exists.
    petitions = [p for p in proposals if p["kind"] == "petition"]
    assert {p["proposal_number"] for p in petitions} == {
        "陳情第1号", "陳情第4号", "陳情第5号",
    }
    assert all(p["outcome"] == "pending" for p in petitions)
    assert all(p["decided_at"] is None for p in petitions)
    # Individual submission dates are not published per item.
    assert all(p["submitted_at"] is None for p in proposals)


def test_votes_are_empty_because_session_was_unanimous():
    votes = load("votes.json")
    validate("vote.schema.json", votes)
    faction_votes = load("faction_votes.json")
    validate("faction_vote.schema.json", faction_votes)
    # Every mayoral bill in the September 2026 session passed
    # unanimously (全員異議なく). The 議案等の賛否一覧表 only lists
    # bills where votes were divided, seats left, etc., so no
    # per-member vote record exists for this session and none is
    # fabricated here.
    assert votes == []
    assert faction_votes == []


def test_expenses():
    expenses = load("political_activity_expenses.json")
    validate("political_activity_expense.schema.json", expenses)
    assert len(expenses) == 33
    assert all(r["fiscal_year"] == 2025 for r in expenses)
    assert all(r["receipt_access"] == "online" for r in expenses)
    assert all(r["report_status"] == "published" for r in expenses)
    assert all(r["recipient_type"] == "member" for r in expenses)
    # The grant is 100,000 yen per month to each member, so every
    # full-year report shows 1,200,000 yen granted.
    assert all(r["granted_yen"] == 1200000 for r in expenses)
    for record in expenses:
        assert [i["category"] for i in record["breakdown"]] == CATEGORIES
        assert (
            sum(i["amount_yen"] for i in record["breakdown"])
            == record["spent_yen"]
        ), record["recipient_name"]
        if record["spent_yen"] <= record["granted_yen"]:
            assert (
                record["granted_yen"] - record["spent_yen"]
                == record["returned_yen"]
            ), record["recipient_name"]
        else:
            # Overspent reports print a zero remainder; nothing is
            # returned, so returned_yen is 0.
            assert record["returned_yen"] == 0, record["recipient_name"]
    overspent = {
        r["recipient_name"] for r in expenses
        if r["spent_yen"] > r["granted_yen"]
    }
    assert overspent == {
        "小田賢嗣", "高野英昭", "石山廣昭", "田中英子", "仁藤俊", "長谷川幸司",
    }
    by_name = {r["recipient_name"]: r for r in expenses}
    # The report for 石川亜希子 prints that name in the report
    # itself; the index page writes 佐藤（石川）亜希子.
    assert "石川亜希子" in by_name
    assert by_name["石川亜希子"]["spent_yen"] == 344890
    # 長谷川幸司: the printed total in the report (1,231,712 yen)
    # differs from the sum of the printed category amounts
    # (1,236,712 yen) by 5,000 yen in the source itself; the
    # category sum is registered as spent_yen and the discrepancy
    # is recorded in the evidence packet.
    assert by_name["長谷川幸司"]["spent_yen"] == 1236712


def test_inspection_trips():
    trips = load("inspection_trips.json")
    validate("inspection_trip.schema.json", trips)
    assert len(trips) == 10
    by_title = {}
    for trip in trips:
        assert trip["trip_type"] == "domestic"
        assert trip["report_status"] == "published"
        # The newsletter reports print dates, destinations and
        # survey items, but no participants or costs.
        assert trip["cost_status"] == "not_published"
        assert trip["total_cost_yen"] is None
        assert trip["cost_per_person_yen"] is None
        assert trip["participant_count"] is None
        assert trip["participants"] == []
        by_title[trip["title"]] = trip
    assert by_title["総務委員会（1班）行政視察"]["start_date"] == "2025-07-22"
    assert by_title["総務委員会（1班）行政視察"]["end_date"] == "2025-07-24"
    assert by_title["総務委員会（1班）行政視察"]["destinations"] == [
        "福岡市", "下関市", "佐賀市",
    ]
    assert by_title["産業文教委員会（1班）行政視察"]["start_date"] == "2025-10-08"
    assert by_title["環境建設委員会（2班）行政視察"]["end_date"] == "2025-08-01"
    assert by_title["広報広聴委員会（2班）行政視察"]["start_date"] == "2025-11-10"
    packets = load("inspection_evidence_packets.json")
    assert len(packets) == 1
    assert packets[0]["subject_id"] == ASM
    assert len(packets[0]["claims"]) == 10


def test_disclosure_profile():
    profiles = load("disclosure_profiles.json")
    validate("disclosure_profile.schema.json", profiles)
    assert len(profiles) == 1
    assert profiles[0]["as_of"] == "2026-11-27"
    items = {i["item"]: i for i in profiles[0]["items"]}
    assert len(items) == 12
    # The per-member vote table exists as a format, but this session
    # had no divided bill, so nothing was published for it.
    assert items["member_votes"]["availability"] == "not_published"
    assert items["member_votes"]["granularity"] == "member"
    assert items["faction_votes"]["availability"] == "not_published"
    assert (
        items["political_activity_expense_reports"]["granularity"]
        == "member"
    )
    assert items["inspection_trip_reports"]["availability"] == "published"
    # The September 2026 minutes are not yet published (they appear
    # around the next regular session, 2-3 months after closing).
    assert items["meeting_minutes"]["availability"] == "not_found"
    assert items["petition_results"]["availability"] == "published"


def test_evidence_packets():
    packets = []
    for name in (
        "assembly_evidence_packets.json",
        "proposal_vote_evidence_packets.json",
        "expense_evidence_packets.json",
        "inspection_evidence_packets.json",
    ):
        packets.extend(load(name))
    validate("evidence_packet.schema.json", packets)
    assert len(packets) == 58
    vote_packets = load("proposal_vote_evidence_packets.json")
    assert len(vote_packets) == 23
    assert all(p["subject_type"] == "proposal" for p in vote_packets)
    assert all(p["open_questions"] == [] for p in vote_packets)
    # The assembly packet keeps the open questions the primary
    # sources could not settle (the term start date in print, and
    # the cross-check of the vote table against the minutes).
    assembly_packets = load("assembly_evidence_packets.json")
    assert len(assembly_packets) == 1
    assert len(assembly_packets[0]["open_questions"]) == 2
    expense_packets = load("expense_evidence_packets.json")
    assert len(expense_packets) == 33
    assert all(p["open_questions"] == [] for p in expense_packets)
    # Every proposal and expense has exactly one packet.
    proposals = {p["id"] for p in load("proposals.json")}
    assert {p["subject_id"] for p in vote_packets} == proposals
    expenses = {r["id"] for r in load("political_activity_expenses.json")}
    assert {p["subject_id"] for p in expense_packets} == expenses
