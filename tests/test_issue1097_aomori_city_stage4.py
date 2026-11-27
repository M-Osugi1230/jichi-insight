"""Issue #1097: Aomori City assembly (cluster 20 stage 4) checks.

Pins the counts and cross-checks for the Aomori City Council data
taken from the Reiwa 8 3rd regular session (令和8年第3回定例会,
2026-08-24 to 2026-09-29), the last session of the pre-election
assembly (32 seats), and the FY2025 political activity expense
reports published on 2026-07-01.  The published vote table gives
individual votes only for the six divided items; unanimous items
publish totals (30-0) and the single absentee's name.  The minutes
cross-check for the vote table's nature could not be completed
(the official minutes system rate-limited the check), so every
vote method is pinned as unknown with the follow-up tracked in
the assembly evidence packet under Issue #706.
"""

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "reviewed" / "aomori-city" / "assembly"
CATALOG = ROOT / "data" / "catalog" / "aomori_city_assembly_sources.json"
ASM = "jp-local-022012-assembly-2022"
SESSION = f"{ASM}-session-2026-08"
CATEGORIES = ["調査研究費", "研修費", "広報費", "広聴費", "要請・陳情活動費",
              "会議費", "資料作成費", "資料購入費", "人件費", "事務所費"]
FACTION_COUNTS = {
    "自民クラブ": 8,
    "創青会": 5,
    "市民クラブ": 4,
    "公明党": 4,
    "日本共産党": 4,
    "立憲民主・社民": 3,
    "無所属": 4,
}
DIVIDED = {"議案第112号", "議案第129号", "請願第6号", "請願第10号",
           "議員提出議案第13号", "議員提出議案第18号"}
JCP = {"村川みどり", "天内慎也", "万徳なお子", "赤平勇人"}


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
        entry["municipality_key"] == "aomori-city" for entry in records
    )
    # 8 general sources plus one record per expense report (29).
    assert len(records) == 37


def test_assembly_record():
    records = load("assembly_records.json")
    validate("assembly.schema.json", records)
    assert len(records) == 1
    record = records[0]
    assert record["id"] == ASM
    assert record["municipality_id"] == "jp-local-022012"
    assert record["name"] == "青森市議会"
    # The registered assembly is the pre-election one (32 seats);
    # the seat ordinance amendment (32 to 28) applies from the
    # 2026-11-08 election, decided in this very session.
    assert record["seat_count"] == 32
    # Term end 2026-11-25 follows from the prefectural election
    # commission's list (the current term ends 2030-11-25); the
    # four-year term starts 2022-11-26.
    assert record["term_start"] == "2022-11-26"
    assert record["term_end"] == "2026-11-25"
    by_name = {f["name"]: f["member_count"] for f in record["factions"]}
    assert by_name == FACTION_COUNTS
    assert sum(by_name.values()) == 32
    assert len(record["committees"]) == 7


def test_sessions():
    sessions = load("sessions.json")
    validate("session.schema.json", sessions)
    assert len(sessions) == 1
    session = sessions[0]
    assert session["id"] == SESSION
    assert session["name"] == "令和8年第3回定例会"
    assert session["session_type"] == "regular"
    assert session["start_date"] == "2026-08-24"
    assert session["end_date"] == "2026-09-29"


def test_proposals():
    proposals = load("proposals.json")
    validate("proposal.schema.json", proposals)
    assert len(proposals) == 35
    kinds = {}
    for p in proposals:
        kinds[p["kind"]] = kinds.get(p["kind"], 0) + 1
    assert kinds == {
        "budget": 11,
        "ordinance": 5,
        "other": 4,
        "personnel": 2,
        "petition": 2,
        "resolution": 5,
        "settlement": 6,
    }
    assert sum(1 for p in proposals if p["submitted_by"] == "executive") == 27
    assert sum(1 for p in proposals if p["submitted_by"] == "member") == 6
    assert (
        sum(1 for p in proposals if p["submitted_by"] == "resident_petition")
        == 2
    )
    assert all(p["session_id"] == SESSION for p in proposals)
    assert all(p["decided_at"] == "2026-09-29" for p in proposals)
    assert sum(1 for p in proposals if p["outcome"] == "approved") == 33
    assert sum(1 for p in proposals if p["outcome"] == "rejected") == 2
    # All six FY2025 settlements were certified; none was rejected.
    settlements = [p for p in proposals if p["kind"] == "settlement"]
    assert len(settlements) == 6
    assert all(p["outcome"] == "approved" for p in settlements)
    by_number = {p["proposal_number"]: p for p in proposals}
    # Submission dates as grouped on the official session page.
    assert by_number["議案第111号"]["submitted_at"] == "2026-08-24"
    assert by_number["議案第135号"]["submitted_at"] == "2026-08-27"
    assert by_number["議案第136号"]["submitted_at"] == "2026-09-29"
    assert by_number["議員提出議案第13号"]["submitted_at"] == "2026-09-29"
    # The two petitions were under continued review from the 2nd
    # regular session; no submission date is restated in the 3rd
    # session sources, so it stays null.
    assert by_number["請願第6号"]["submitted_at"] is None
    assert by_number["請願第10号"]["submitted_at"] is None
    # Both petitions were rejected; petition 10 tied 15-15 and was
    # rejected by the chair's casting vote.
    assert by_number["請願第6号"]["outcome"] == "rejected"
    assert by_number["請願第10号"]["outcome"] == "rejected"
    # The seat-count ordinance amendment was itself decided here.
    assert by_number["議員提出議案第13号"]["outcome"] == "approved"


def test_votes():
    votes = load("votes.json")
    validate("vote.schema.json", votes)
    proposals = {p["id"]: p for p in load("proposals.json")}
    assert len(votes) == 35
    assert {v["proposal_id"] for v in votes} == set(proposals)
    for vote in votes:
        prop = proposals[vote["proposal_id"]]
        assert vote["vote_date"] == "2026-09-29"
        assert prop["decided_at"] == vote["vote_date"]
        assert prop["outcome"] == vote["outcome"]
        assert vote["member_vote_availability"] == "published"
        # The minutes cross-check could not be completed, so the
        # nature of the vote table is not asserted: method unknown.
        assert vote["method"] == "unknown"
        number = prop["proposal_number"]
        if number in DIVIDED:
            assert len(vote["member_votes"]) == 31
            counts = {"for": 0, "against": 0, "abstained": 0, "absent": 0}
            for m in vote["member_votes"]:
                counts[m["position"]] += 1
            assert vote["totals"] == counts
        else:
            # Unanimous items publish only the totals and the
            # absentee's name; no member breakdown is reconstructed.
            assert vote["totals"] == {
                "for": 30, "against": 0, "abstained": 0, "absent": 1,
            }
            assert vote["member_votes"] == [
                {"member_name": "長谷川章悦", "position": "absent"}
            ]
        # The chair (奈良岡隆) never appears in the member votes.
        assert all(
            m["member_name"] != "奈良岡隆" for m in vote["member_votes"]
        )


def test_divided_votes():
    proposals = {p["proposal_number"]: p for p in load("proposals.json")}
    votes = {v["proposal_id"]: v for v in load("votes.json")}

    def vote_of(number):
        return votes[proposals[number]["id"]]

    def names(number, position):
        return {
            m["member_name"] for m in vote_of(number)["member_votes"]
            if m["position"] == position
        }

    # 議案第112号 and 議案第129号 (FY2025 settlement): only the
    # four JCP members opposed.
    for number in ("議案第112号", "議案第129号"):
        assert vote_of(number)["totals"] == {
            "for": 26, "against": 4, "abstained": 0, "absent": 1,
        }
        assert names(number, "against") == JCP
        assert names(number, "absent") == {"長谷川章悦"}
    # 請願第6号 was rejected 13-17; 藤田誠 split from his faction.
    assert vote_of("請願第6号")["totals"] == {
        "for": 13, "against": 17, "abstained": 0, "absent": 1,
    }
    assert "藤田誠" in names("請願第6号", "against")
    assert "蛯名和子" in names("請願第6号", "for")
    # 請願第10号 tied 15-15 (chair's casting vote rejected it);
    # 関貴光 was the only 自民クラブ member in favour.
    assert vote_of("請願第10号")["totals"] == {
        "for": 15, "against": 15, "abstained": 0, "absent": 1,
    }
    assert "関貴光" in names("請願第10号", "for")
    # 議員提出議案第13号 (seat-count amendment) passed 18-12.
    assert vote_of("議員提出議案第13号")["totals"] == {
        "for": 18, "against": 12, "abstained": 0, "absent": 1,
    }
    assert names("議員提出議案第13号", "against") >= {"奈良祥孝", "竹山美虎"}
    # 議員提出議案第18号 passed 18-12 against 自民クラブ and 創青会.
    assert vote_of("議員提出議案第18号")["totals"] == {
        "for": 18, "against": 12, "abstained": 0, "absent": 1,
    }
    assert names("議員提出議案第18号", "against") == {
        "小豆畑緑", "花田明仁", "大矢保", "中田靖人", "澁谷洋子",
        "柿崎孝治", "関貴光", "里村誠悦", "小倉尚裕", "木戸喜美男",
        "舘山善也", "木村淳司",
    }


def test_faction_votes():
    faction_votes = load("faction_votes.json")
    validate("faction_vote.schema.json", faction_votes)
    votes = {v["id"]: v for v in load("votes.json")}
    proposals = {p["id"]: p for p in load("proposals.json")}
    assert len(faction_votes) == 35 * 7
    by_vote = {}
    for fv in faction_votes:
        by_vote.setdefault(fv["vote_id"], []).append(fv)
    assert set(by_vote) == set(votes)
    for vote in votes.values():
        groups = by_vote[vote["id"]]
        assert {g["faction_name"] for g in groups} == set(FACTION_COUNTS)
        for g in groups:
            assert g["member_count"] == FACTION_COUNTS[g["faction_name"]]
        number = proposals[vote["proposal_id"]]["proposal_number"]
        if number in DIVIDED:
            assert (
                sum(g["for_count"] for g in groups)
                == vote["totals"]["for"]
            )
            assert (
                sum(g["against_count"] for g in groups)
                == vote["totals"]["against"]
            )
            for g in groups:
                if g["for_count"] and g["against_count"]:
                    assert g["position"] == "split"
        else:
            # Unanimous: every faction is recorded as for; the
            # 自民クラブ count excludes the absentee and the
            # 無所属 count excludes the chair.
            assert all(g["position"] == "for" for g in groups)
            by_name = {g["faction_name"]: g for g in groups}
            assert by_name["自民クラブ"]["for_count"] == 7
            assert by_name["無所属"]["for_count"] == 3
    # Known splits on the divided items.
    def group(number, faction):
        pid = [p["id"] for p in proposals.values()
               if p["proposal_number"] == number][0]
        vid = [v["id"] for v in votes.values()
               if v["proposal_id"] == pid][0]
        return [g for g in by_vote[vid]
                if g["faction_name"] == faction][0]

    assert group("請願第6号", "立憲民主・社民")["position"] == "split"
    assert group("請願第10号", "自民クラブ")["position"] == "split"
    assert group("議員提出議案第13号", "市民クラブ")["position"] == "split"
    assert group("議案第129号", "日本共産党")["position"] == "against"


def test_expenses():
    expenses = load("political_activity_expenses.json")
    validate("political_activity_expense.schema.json", expenses)
    # 28 members received individual grants; the JCP received one
    # faction grant for its four members.
    assert len(expenses) == 29
    assert all(r["fiscal_year"] == 2025 for r in expenses)
    assert all(r["receipt_access"] == "in_person_only" for r in expenses)
    assert all(r["report_status"] == "published" for r in expenses)
    assert sum(1 for r in expenses if r["recipient_type"] == "member") == 28
    assert sum(1 for r in expenses if r["recipient_type"] == "faction") == 1
    for record in expenses:
        assert [i["category"] for i in record["breakdown"]] == CATEGORIES
        assert (
            sum(i["amount_yen"] for i in record["breakdown"])
            == record["spent_yen"]
        ), record["recipient_name"]
        # Printed balances can be negative (overspend); the
        # registered returned amount never goes below zero.
        assert record["returned_yen"] == max(
            record["granted_yen"] - record["spent_yen"], 0
        ), record["recipient_name"]
    by_name = {r["recipient_name"]: r for r in expenses}
    assert by_name["日本共産党"]["granted_yen"] == 4320000
    assert by_name["日本共産党"]["spent_yen"] == 3841246
    assert by_name["日本共産党"]["returned_yen"] == 478754
    # Twelve recipients spent more than the grant; the largest
    # overspend is 澁谷洋子's 464,771 yen.
    over = [r for r in expenses if r["spent_yen"] > r["granted_yen"]]
    assert len(over) == 12
    assert by_name["澁谷洋子"]["spent_yen"] == 1544771
    assert by_name["澁谷洋子"]["returned_yen"] == 0
    # Printed totals across all 29 reports.
    assert sum(r["granted_yen"] for r in expenses) == 34560000
    assert sum(r["spent_yen"] for r in expenses) == 28095779
    assert sum(r["returned_yen"] for r in expenses) == 7756103


def test_inspection_trips():
    trips = load("inspection_trips.json")
    validate("inspection_trip.schema.json", trips)
    # No official publication of the council's own committee
    # inspection reports could be found; the gap is recorded in
    # the disclosure profile and the inspection evidence packet.
    assert trips == []
    packets = load("inspection_evidence_packets.json")
    assert len(packets) == 1
    assert packets[0]["subject_id"] == ASM


def test_disclosure_profile():
    profiles = load("disclosure_profiles.json")
    validate("disclosure_profile.schema.json", profiles)
    assert len(profiles) == 1
    assert profiles[0]["as_of"] == "2026-11-27"
    items = {i["item"]: i for i in profiles[0]["items"]}
    assert len(items) == 12
    assert items["member_votes"]["availability"] == "published"
    assert items["member_votes"]["granularity"] == "member"
    assert items["faction_votes"]["availability"] == "not_published"
    assert (
        items["political_activity_expense_reports"]["granularity"]
        == "member"
    )
    assert (
        items["political_activity_expense_receipts"]["availability"]
        == "restricted"
    )
    assert items["meeting_minutes"]["availability"] == "published"
    assert items["inspection_trip_reports"]["availability"] == "not_found"
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
    assert len(packets) == 66
    vote_packets = load("proposal_vote_evidence_packets.json")
    assert len(vote_packets) == 35
    assert all(p["subject_type"] == "proposal" for p in vote_packets)
    assert all(p["open_questions"] == [] for p in vote_packets)
    # The assembly packet keeps the open questions the primary
    # sources could not settle (the unfinished minutes cross-check
    # for the vote methods, the derived term start, registration
    # of the new 28-seat assembly, and the committee roster).
    assembly_packets = load("assembly_evidence_packets.json")
    assert len(assembly_packets) == 1
    assert len(assembly_packets[0]["open_questions"]) == 4
    expense_packets = load("expense_evidence_packets.json")
    assert len(expense_packets) == 29
    assert all(p["open_questions"] == [] for p in expense_packets)
