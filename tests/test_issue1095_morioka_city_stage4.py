"""Issue #1095: Morioka City assembly (cluster 19 stage 4) checks.

Pins the counts and cross-checks for the Morioka City Council data
taken from the September 2026 regular session (令和8年9月定例会,
2026-09-02 to 2026-09-30), whose official per-member vote table was
cross-checked against the official minutes (all 46 items were
decided by standing vote: personnel items on 2026-09-02, the
resignation-recommendation resolution on 2026-09-08, the rest on
2026-09-30), and the FY2025 political activity expense reports
published per member.
"""

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "reviewed" / "morioka-city" / "assembly"
CATALOG = ROOT / "data" / "catalog" / "morioka_city_assembly_sources.json"
ASM = "jp-local-032018-assembly-2023"
SESSION = f"{ASM}-session-2026-09"
CATEGORIES = ["調査研究費", "研修費", "広報費", "広聴費", "会議費",
              "資料作成費", "資料購入費", "人件費", "事務所費"]
FACTION_COUNTS = {
    "盛友会": 16,
    "創盛会": 7,
    "日本共産党盛岡市議団": 5,
    "市政クラブ": 4,
    "公明党": 3,
    "日本維新の会": 1,
    "いのちの党": 1,
    "無所属": 1,
}
JCP = {"庄子春治", "三田村亜美子", "鈴木努", "髙橋和夫", "神部伸也"}


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
        entry["municipality_key"] == "morioka-city" for entry in records
    )
    # 15 general sources plus one record per published member
    # expense report (37 of 38 members; 細川由香里 declined).
    assert len(records) == 52


def test_assembly_record():
    records = load("assembly_records.json")
    validate("assembly.schema.json", records)
    assert len(records) == 1
    record = records[0]
    assert record["id"] == ASM
    assert record["municipality_id"] == "jp-local-032018"
    assert record["name"] == "盛岡市議会"
    assert record["seat_count"] == 38
    # Term end 2027-08-27 is printed in the Iwate prefectural
    # election commission's term list; the four-year term starts
    # 2023-08-28.
    assert record["term_start"] == "2023-08-28"
    assert record["term_end"] == "2027-08-27"
    by_name = {f["name"]: f["member_count"] for f in record["factions"]}
    assert by_name == FACTION_COUNTS
    assert sum(by_name.values()) == 38
    assert len(record["committees"]) == 9


def test_sessions():
    sessions = load("sessions.json")
    validate("session.schema.json", sessions)
    assert len(sessions) == 1
    session = sessions[0]
    assert session["id"] == SESSION
    assert session["name"] == "令和8年9月定例会"
    assert session["session_type"] == "regular"
    assert session["start_date"] == "2026-09-02"
    assert session["end_date"] == "2026-09-30"


def test_proposals():
    proposals = load("proposals.json")
    validate("proposal.schema.json", proposals)
    assert len(proposals) == 46
    kinds = {}
    for p in proposals:
        kinds[p["kind"]] = kinds.get(p["kind"], 0) + 1
    assert kinds == {
        "budget": 1,
        "ordinance": 4,
        "other": 20,
        "personnel": 4,
        "petition": 2,
        "resolution": 2,
        "settlement": 13,
    }
    assert sum(1 for p in proposals if p["submitted_by"] == "executive") == 41
    assert sum(1 for p in proposals if p["submitted_by"] == "member") == 3
    assert (
        sum(1 for p in proposals if p["submitted_by"] == "resident_petition")
        == 2
    )
    assert all(p["session_id"] == SESSION for p in proposals)
    assert all(p["submitted_at"] is None for p in proposals)
    assert sum(1 for p in proposals if p["outcome"] == "approved") == 45
    assert sum(1 for p in proposals if p["outcome"] == "rejected") == 1
    # All 13 FY2025 settlements were certified; none was rejected
    # or left pending (the stage-0 inventory is confirmed here).
    settlements = [p for p in proposals if p["kind"] == "settlement"]
    assert len(settlements) == 13
    assert all(p["outcome"] == "approved" for p in settlements)
    by_number = {p["proposal_number"]: p for p in proposals}
    # Decision dates follow the minutes: the four personnel items
    # were consented to on the opening day (2026-09-02), the
    # resignation-recommendation resolution on 2026-09-08, and the
    # remaining 41 items on the final day (2026-09-30).
    for n in ("議案第132号", "議案第133号", "議案第134号", "議案第135号"):
        assert by_number[n]["decided_at"] == "2026-09-02"
    assert by_number["発議案第4号"]["decided_at"] == "2026-09-08"
    others = [p for n, p in by_number.items()
              if n not in ("議案第132号", "議案第133号", "議案第134号",
                           "議案第135号", "発議案第4号")]
    assert len(others) == 41
    assert all(p["decided_at"] == "2026-09-30" for p in others)
    # Petitions are decided in Morioka City: one adopted, one
    # rejected. 陳情 are not voted on and are not registered.
    petitions = {p["proposal_number"]: p
                 for p in proposals if p["kind"] == "petition"}
    assert petitions["請願第1号"]["outcome"] == "rejected"
    assert petitions["請願第2号"]["outcome"] == "approved"


def test_votes():
    votes = load("votes.json")
    validate("vote.schema.json", votes)
    proposals = {p["id"]: p for p in load("proposals.json")}
    assert len(votes) == 46
    assert {v["proposal_id"] for v in votes} == set(proposals)
    # The minutes cross-check shows every one of the 46 items was
    # decided by standing vote (起立表決).
    assert {v["method"] for v in votes} == {"standing"}
    for vote in votes:
        assert vote["member_vote_availability"] == "published"
        assert vote["item_scope"] is None
        assert len(vote["member_votes"]) == 38
        counts = {"for": 0, "against": 0, "abstained": 0, "absent": 0}
        excused = []
        for m in vote["member_votes"]:
            if m["position"] == "excused":
                excused.append(m["member_name"])
            else:
                counts[m["position"]] += 1
        assert vote["totals"] == counts
        prop = proposals[vote["proposal_id"]]
        # The chair (櫻裕子) never votes. On 発議案第4号 the member
        # concerned (山崎智樹) also did not take part: his cell in
        # the official table is blank.
        if prop["proposal_number"] == "発議案第4号":
            assert sorted(excused) == ["山崎智樹", "櫻裕子"]
            assert counts == {"for": 36, "against": 0,
                              "abstained": 0, "absent": 0}
        else:
            assert excused == ["櫻裕子"]
        assert prop["decided_at"] == vote["vote_date"]
        assert prop["outcome"] == vote["outcome"]


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

    # Five items were opposed by 佐藤尚弘 (日本維新の会) alone.
    for n in ("議案第110号", "議案第119号", "議案第137号",
              "発議案第6号", "請願第2号"):
        assert vote_of(n)["totals"] == {
            "for": 36, "against": 1, "abstained": 0, "absent": 0,
        }
        assert names(n, "against") == {"佐藤尚弘"}
    # The general-account and national-health-insurance settlements
    # were opposed by the five JCP members and 縄手豊子.
    for n in ("認定第1号", "認定第3号"):
        assert vote_of(n)["totals"]["against"] == 6
        assert names(n, "against") == JCP | {"縄手豊子"}
    # The late-stage elderly medical settlement additionally drew
    # 伊勢志穂's opposition.
    assert vote_of("認定第5号")["totals"]["against"] == 7
    assert names("認定第5号", "against") == JCP | {"縄手豊子", "伊勢志穂"}
    # The sewerage settlement was opposed by the JCP members only.
    assert vote_of("認定第12号")["totals"]["against"] == 5
    assert names("認定第12号", "against") == JCP
    # 請願第1号 was rejected 11-26; its supporters were one 創盛会
    # member, the JCP group, the 市政クラブ group and 縄手豊子.
    assert vote_of("請願第1号")["totals"] == {
        "for": 11, "against": 26, "abstained": 0, "absent": 0,
    }
    assert names("請願第1号", "for") == (
        JCP | {"大畑正二", "中村雅幸", "野中靖志", "中村亨", "伊勢志穂",
               "縄手豊子"}
    )
    # The other 36 items were unanimous among the 37 voting members.
    divided = {"議案第110号", "議案第119号", "議案第137号", "発議案第6号",
               "請願第2号", "認定第1号", "認定第3号", "認定第5号",
               "認定第12号", "請願第1号", "発議案第4号"}
    for number in proposals:
        if number not in divided:
            assert vote_of(number)["totals"] == {
                "for": 37, "against": 0, "abstained": 0, "absent": 0,
            }, number


def test_faction_votes():
    faction_votes = load("faction_votes.json")
    validate("faction_vote.schema.json", faction_votes)
    votes = {v["id"]: v for v in load("votes.json")}
    proposals = {p["id"]: p for p in load("proposals.json")}
    assert len(faction_votes) == 46 * 8
    by_vote = {}
    for fv in faction_votes:
        by_vote.setdefault(fv["vote_id"], []).append(fv)
    assert set(by_vote) == set(votes)
    for vote in votes.values():
        groups = by_vote[vote["id"]]
        assert {g["faction_name"] for g in groups} == set(FACTION_COUNTS)
        assert sum(g["member_count"] for g in groups) == 38
        assert sum(g["for_count"] for g in groups) == vote["totals"]["for"]
        assert (
            sum(g["against_count"] for g in groups)
            == vote["totals"]["against"]
        )
        for g in groups:
            assert g["member_count"] == FACTION_COUNTS[g["faction_name"]]
            if g["for_count"] and not g["against_count"]:
                assert g["position"] == "for"
            elif g["against_count"] and not g["for_count"]:
                assert g["position"] == "against"
            elif g["for_count"] and g["against_count"]:
                assert g["position"] == "split"
    # The chair belongs to 盛友会: its member_count is 16 while at
    # most 15 of its members can appear in the for/against counts.
    for groups in by_vote.values():
        seiyu = [g for g in groups if g["faction_name"] == "盛友会"][0]
        assert seiyu["member_count"] == 16
        assert seiyu["for_count"] + seiyu["against_count"] <= 15
    # On 発議案第4号 the single-member 無所属 group did not take
    # part in the vote at all.
    target = proposals[[p["id"] for p in proposals.values()
                        if p["proposal_number"] == "発議案第4号"][0]]
    groups = by_vote[[v["id"] for v in votes.values()
                      if v["proposal_id"] == target["id"]][0]]
    mushozoku = [g for g in groups if g["faction_name"] == "無所属"][0]
    assert mushozoku["for_count"] == 0
    assert mushozoku["against_count"] == 0
    assert mushozoku["position"] == "absent"
    # 請願第1号 split 創盛会 (1 for, 6 against).
    petition1 = by_vote[[v["id"] for v in votes.values()
                         if proposals[v["proposal_id"]]["proposal_number"]
                         == "請願第1号"][0]]
    sosei = [g for g in petition1 if g["faction_name"] == "創盛会"][0]
    assert (sosei["for_count"], sosei["against_count"]) == (1, 6)
    assert sosei["position"] == "split"


def test_expenses():
    expenses = load("political_activity_expenses.json")
    validate("political_activity_expense.schema.json", expenses)
    assert len(expenses) == 38
    assert all(r["fiscal_year"] == 2025 for r in expenses)
    assert all(r["recipient_type"] == "member" for r in expenses)
    for record in expenses:
        assert [i["category"] for i in record["breakdown"]] == CATEGORIES
        assert (
            sum(i["amount_yen"] for i in record["breakdown"])
            == record["spent_yen"]
        ), record["recipient_name"]
        assert (
            record["granted_yen"] - record["spent_yen"]
            == record["returned_yen"]
        ), record["recipient_name"]
    # Printed totals of the official FY2025 summary sheet.
    assert sum(r["granted_yen"] for r in expenses) == 22200000
    assert sum(r["spent_yen"] for r in expenses) == 16342955
    assert sum(r["returned_yen"] for r in expenses) == 5857045
    by_name = {r["recipient_name"]: r for r in expenses}
    # Every member except 細川由香里 was granted the full annual
    # amount (50,000 yen x 12 months); she declined the grant, so
    # no report was published for her.
    for name, record in by_name.items():
        if name == "細川由香里":
            assert record["granted_yen"] == 0
            assert record["spent_yen"] == 0
            assert record["returned_yen"] == 0
            assert record["report_status"] == "not_published"
            assert record["receipt_access"] == "not_published"
        else:
            assert record["granted_yen"] == 600000, name
            assert record["report_status"] == "published"
            assert record["receipt_access"] == "online"


def test_inspection_trips():
    trips = load("inspection_trips.json")
    validate("inspection_trip.schema.json", trips)
    # The council publishes its committee inspection trips by
    # fiscal year; the FY2025 page lists eight trips, all carried
    # out in January 2026, with destinations and topics but no
    # reports, participants or costs.
    assert len(trips) == 8
    assert all(t["trip_type"] == "domestic" for t in trips)
    assert all(t["cost_status"] == "not_published" for t in trips)
    assert all(t["report_status"] == "not_published" for t in trips)
    assert all(t["start_date"].startswith("2026-01") for t in trips)
    committees = {t["title"].replace("行政視察", "") for t in trips}
    assert committees == {
        "総務常任委員会", "教育福祉常任委員会", "産業環境常任委員会",
        "建設常任委員会", "観光振興特別委員会", "農業地域活性化特別委員会",
        "こどもいきいき特別委員会", "雇用対策特別委員会",
    }
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
    assert items["faction_votes"]["availability"] == "published"
    assert (
        items["political_activity_expense_reports"]["granularity"]
        == "member"
    )
    assert items["meeting_minutes"]["availability"] == "published"
    assert items["inspection_trip_reports"]["availability"] == "published"
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
    assert len(packets) == 86
    vote_packets = load("proposal_vote_evidence_packets.json")
    assert len(vote_packets) == 46
    assert all(p["subject_type"] == "proposal" for p in vote_packets)
    assert all(p["open_questions"] == [] for p in vote_packets)
    # The assembly packet keeps the two points the registration
    # could not fully settle from primary sources alone: the
    # post-session faction change of 細川由香里 and the treatment
    # of 山崎智樹's blank cell on 発議案第4号.
    assembly_packets = load("assembly_evidence_packets.json")
    assert len(assembly_packets) == 1
    assert len(assembly_packets[0]["open_questions"]) == 2
    expense_packets = load("expense_evidence_packets.json")
    assert len(expense_packets) == 38
    assert all(p["open_questions"] == [] for p in expense_packets)
