"""Cluster 12 stage 4: Kyoto City assembly registration checks.

Pins the counts and cross-checks for the Kyoto City Council data
taken from the September 2026 session (令和8年9月市会,
2026-09-17 to 2026-10-30), the FY2025 political activity expense
reports (six faction reports and 67 member reports), and the
FY2025 overseas administrative inspection trip to Vienna.
"""

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "reviewed" / "kyoto-city" / "assembly"
CATALOG = ROOT / "data" / "catalog" / "kyoto_city_assembly_sources.json"
ASM = "jp-local-261009-assembly-2023"
SESSION = f"{ASM}-session-2026-09"
FACTION_COUNTS = {
    "自由民主党京都市会議員団": 19,
    "維新・京都・国民市会議員団": 16,
    "日本共産党京都市会議員団": 14,
    "公明党京都市会議員団": 11,
}
INDEPENDENTS = ["天方ひろゆき", "井﨑敦子", "きくち一秀", "小島信太郎",
                "繁隆夫", "菅谷浩平", "平田圭"]
CATEGORIES = ["調査研究費", "研修費", "広報広聴費", "要請・陳情活動費",
              "会議費", "資料作成費", "資料購入費", "通信運搬費",
              "備品消耗品費", "人件費", "事務所費"]
# Official FY2025 summary table (thousands of yen), faction column.
OFFICIAL_FACTION_K = {
    "調査研究費": 6832, "研修費": 298, "広報広聴費": 29117,
    "要請・陳情活動費": 934, "会議費": 763, "資料作成費": 8,
    "資料購入費": 3142, "通信運搬費": 655, "備品消耗品費": 6481,
    "人件費": 41919, "事務所費": 0,
}
# Official summary table, member column. 資料作成費 and 資料購入費
# differ from the transcribed report sums (see
# test_expenses): the city's table classifies 278 thousand yen
# differently from the printed reports.
OFFICIAL_MEMBER_K = {
    "調査研究費": 4702, "研修費": 1612, "広報広聴費": 79274,
    "要請・陳情活動費": 0, "会議費": 19, "資料作成費": 278,
    "資料購入費": 5213, "通信運搬費": 11160, "備品消耗品費": 8981,
    "人件費": 71047, "事務所費": 45703,
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
        entry["municipality_key"] == "kyoto-city" for entry in records
    )
    # 13 general sources plus one record per expense report PDF.
    assert len(records) == 86


def test_assembly_record():
    records = load("assembly_records.json")
    validate("assembly.schema.json", records)
    assert len(records) == 1
    record = records[0]
    assert record["id"] == ASM
    assert record["municipality_id"] == "jp-local-261009"
    assert record["name"] == "京都市会"
    assert record["seat_count"] == 67
    # Term end 2027-04-29 is printed in the prefectural election
    # commission's term list (as of 2026-04-30, updated 2026-10-23);
    # the four-year term starts 2023-04-30.
    assert record["term_start"] == "2023-04-30"
    assert record["term_end"] == "2027-04-29"
    by_name = {f["name"]: f["member_count"] for f in record["factions"]}
    expected = dict(FACTION_COUNTS)
    expected["無所属"] = 7
    assert by_name == expected
    assert sum(by_name.values()) == 67
    assert len(record["committees"]) == 8


def test_sessions():
    sessions = load("sessions.json")
    validate("session.schema.json", sessions)
    assert len(sessions) == 1
    session = sessions[0]
    assert session["id"] == SESSION
    assert session["name"] == "令和8年9月市会"
    assert session["session_type"] == "regular"
    assert session["start_date"] == "2026-09-17"
    assert session["end_date"] == "2026-10-30"


def test_proposals():
    proposals = load("proposals.json")
    validate("proposal.schema.json", proposals)
    assert len(proposals) == 55
    kinds = {}
    for p in proposals:
        kinds[p["kind"]] = kinds.get(p["kind"], 0) + 1
    assert kinds == {
        "budget": 2,
        "ordinance": 12,
        "other": 14,
        "personnel": 2,
        "petition": 1,
        "resolution": 9,
        "settlement": 15,
    }
    assert sum(1 for p in proposals if p["submitted_by"] == "executive") == 41
    assert sum(1 for p in proposals if p["submitted_by"] == "member") == 13
    assert (
        sum(1 for p in proposals if p["submitted_by"] == "resident_petition")
        == 1
    )
    assert all(p["session_id"] == SESSION for p in proposals)
    assert sum(1 for p in proposals if p["outcome"] == "approved") == 47
    assert sum(1 for p in proposals if p["outcome"] == "rejected") == 8
    # All fifteen FY2025 settlements (報第2号 to 報第16号) were
    # certified on 2026-10-30.
    settlements = [p for p in proposals if p["kind"] == "settlement"]
    assert len(settlements) == 15
    assert all(p["outcome"] == "approved" for p in settlements)
    assert all(p["decided_at"] == "2026-10-30" for p in settlements)
    by_number = {p["proposal_number"]: p for p in proposals}
    assert by_number["報第2号"]["title"].startswith(
        "令和7年度京都市一般会計歳入歳出決算"
    )
    # The two supplementary budgets were decided early, on 2026-09-30,
    # and the seven independent members' marks include one absence
    # (平田圭) printed as －.
    for number in ("議第103号", "議第104号"):
        assert by_number[number]["kind"] == "budget"
        assert by_number[number]["decided_at"] == "2026-09-30"
    # Personnel bills 107 and 108 were submitted and decided on the
    # closing day.
    for number in ("議第107号", "議第108号"):
        assert by_number[number]["kind"] == "personnel"
        assert by_number[number]["submitted_at"] == "2026-10-30"
        assert by_number[number]["decided_at"] == "2026-10-30"
    # The four JCP ordinance bills were all rejected; of the nine
    # opinion papers, six were approved and three rejected.
    member_bills = [p for p in proposals if p["submitted_by"] == "member"]
    ordinances = [p for p in member_bills if p["kind"] == "ordinance"]
    assert len(ordinances) == 4
    assert all(p["outcome"] == "rejected" for p in ordinances)
    resolutions = [p for p in member_bills if p["kind"] == "resolution"]
    assert len(resolutions) == 9
    assert sum(1 for p in resolutions if p["outcome"] == "approved") == 6
    assert sum(1 for p in resolutions if p["outcome"] == "rejected") == 3
    # Petition 398 was received on 2026-05-25, referred to the
    # General Affairs and Fire Committee, and rejected on 2026-09-17.
    petition = by_number["請願第398号"]
    assert petition["kind"] == "petition"
    assert petition["submitted_at"] == "2026-05-25"
    assert petition["decided_at"] == "2026-09-17"
    assert petition["outcome"] == "rejected"


def test_votes():
    votes = load("votes.json")
    validate("vote.schema.json", votes)
    proposals = {p["id"]: p for p in load("proposals.json")}
    assert len(votes) == 55
    per_proposal = {}
    for v in votes:
        per_proposal.setdefault(v["proposal_id"], []).append(v)
    assert set(per_proposal) == set(proposals)
    assert all(len(vs) == 1 for vs in per_proposal.values())
    for vote in votes:
        # The city publishes the columns as each faction's "attitude"
        # (taido), with the legend 〇 = for, × = against, － = absent
        # printed on the results page itself. Whether the table is a
        # post-vote record cannot be settled until the minutes are
        # published (about four months later), so the method stays
        # unknown, following the Hiroshima model.
        assert vote["method"] == "unknown"
        assert vote["totals"] is None
        # The seven independent members appear as named columns, so
        # member-level positions are published for them; the full
        # member-by-member table appears in the council newsletter,
        # whose September-session issue is not yet published.
        assert vote["member_vote_availability"] == "published"
        assert [m["member_name"] for m in vote["member_votes"]] == INDEPENDENTS
        prop = proposals[vote["proposal_id"]]
        assert prop["decided_at"] == vote["vote_date"]
        assert prop["outcome"] == vote["outcome"]


def test_faction_votes():
    faction_votes = load("faction_votes.json")
    validate("faction_vote.schema.json", faction_votes)
    votes = {v["id"]: v for v in load("votes.json")}
    assert len(faction_votes) == 55 * 4
    for fv in faction_votes:
        assert fv["member_count"] == FACTION_COUNTS[fv["faction_name"]]
        assert fv["for_count"] is None
        assert fv["against_count"] is None
    for vote in votes.values():
        count = sum(1 for fv in faction_votes if fv["vote_id"] == vote["id"])
        assert count == 4


def test_divided_votes():
    proposals = {p["proposal_number"]: p for p in load("proposals.json")}
    votes = {v["proposal_id"]: v for v in load("votes.json")}
    faction_votes = load("faction_votes.json")

    def positions(number):
        vote = votes[proposals[number]["id"]]
        return {
            fv["faction_name"]: fv["position"]
            for fv in faction_votes
            if fv["vote_id"] == vote["id"]
        }

    def member_positions(number):
        vote = votes[proposals[number]["id"]]
        return {m["member_name"]: m["position"] for m in vote["member_votes"]}

    # JCP ordinance bill 8: only the JCP supported its own bill.
    pos = positions("市会議第8号")
    assert pos["日本共産党京都市会議員団"] == "for"
    assert sum(1 for p in pos.values() if p == "against") == 3
    # Opinion paper 18: only the JCP supported it; it was rejected.
    pos = positions("市会議第18号")
    assert pos["日本共産党京都市会議員団"] == "for"
    assert proposals["市会議第18号"]["outcome"] == "rejected"
    # The general account settlement: the JCP alone opposed
    # certification.
    pos = positions("報第2号")
    assert pos["日本共産党京都市会議員団"] == "against"
    assert sum(1 for p in pos.values() if p == "for") == 3
    # Supplementary budgets 103 and 104: every faction in favour,
    # and the printed － for independent member 平田圭 is an absence.
    for number in ("議第103号", "議第104号"):
        assert all(p == "for" for p in positions(number).values())
        members = member_positions(number)
        assert members["平田圭"] == "absent"
        assert sum(1 for p in members.values() if p == "for") == 6
    # Petition 398: the results table records positions on the
    # conclusion "not adopted", converted here to positions on the
    # petition itself. Only the JCP opposed non-adoption (i.e.
    # supported the petition); independent member 繁隆夫 was absent.
    pos = positions("請願第398号")
    assert pos["日本共産党京都市会議員団"] == "for"
    assert sum(1 for p in pos.values() if p == "against") == 3
    members = member_positions("請願第398号")
    assert members["繁隆夫"] == "absent"
    assert members["井﨑敦子"] == "for"


def test_expenses():
    expenses = load("political_activity_expenses.json")
    validate("political_activity_expense.schema.json", expenses)
    assert len(expenses) == 73
    assert all(r["fiscal_year"] == 2025 for r in expenses)
    assert all(r["receipt_access"] == "online" for r in expenses)
    assert all(r["report_status"] == "published" for r in expenses)
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
    factions = [r for r in expenses if r["recipient_type"] == "faction"]
    members = [r for r in expenses if r["recipient_type"] == "member"]
    assert len(factions) == 6
    assert len(members) == 67
    # Members are granted 400,000 yen per month; one member returned
    # the full grant unspent.
    assert all(r["granted_yen"] == 4800000 for r in members)
    assert sum(1 for r in members if r["spent_yen"] == 0) == 1
    # Totals match the city's official FY2025 summary.
    assert sum(r["granted_yen"] for r in expenses) == 425900000
    assert sum(r["spent_yen"] for r in expenses) == 318140448
    assert sum(r["returned_yen"] for r in expenses) == 107759552
    assert sum(r["granted_yen"] for r in factions) == 104300000
    assert sum(r["spent_yen"] for r in factions) == 90150694
    assert sum(r["returned_yen"] for r in factions) == 14149306
    assert sum(r["granted_yen"] for r in members) == 321600000
    assert sum(r["spent_yen"] for r in members) == 227989754
    assert sum(r["returned_yen"] for r in members) == 93610246

    def category_k(group, category):
        total = sum(
            i["amount_yen"]
            for r in group
            for i in r["breakdown"]
            if i["category"] == category
        )
        return round(total / 1000)

    # The faction column of the official summary matches exactly.
    for category in CATEGORIES:
        assert category_k(factions, category) == OFFICIAL_FACTION_K[category]
    # The member column matches except for the documented
    # 278-thousand-yen classification difference between 資料作成費
    # and 資料購入費: no member report prints any 資料作成費, while
    # the city's table carries 278 thousand yen there. Registration
    # follows the printed reports, the public unit.
    for category in CATEGORIES:
        if category in ("資料作成費", "資料購入費"):
            continue
        assert category_k(members, category) == OFFICIAL_MEMBER_K[category]
    combined = sum(
        i["amount_yen"]
        for r in members
        for i in r["breakdown"]
        if i["category"] in ("資料作成費", "資料購入費")
    )
    assert round(combined / 1000) == (
        OFFICIAL_MEMBER_K["資料作成費"] + OFFICIAL_MEMBER_K["資料購入費"]
    )


def test_inspection_trips():
    trips = load("inspection_trips.json")
    validate("inspection_trip.schema.json", trips)
    assert len(trips) == 1
    trip = trips[0]
    assert trip["trip_type"] == "overseas"
    assert trip["start_date"] == "2026-01-25"
    assert trip["end_date"] == "2026-01-30"
    assert trip["destinations"] == ["ウィーン市（オーストリア共和国）"]
    assert trip["participant_count"] == 12
    assert len(trip["participants"]) == 12
    # The report (submitted to the speaker on 2026-07-21) is
    # published, but no actual cost figures are published anywhere;
    # the implementation guideline only caps the cost at one
    # million yen per member, so amounts stay null.
    assert trip["report_status"] == "published"
    assert trip["cost_status"] == "not_published"
    assert trip["total_cost_yen"] is None
    assert trip["cost_per_person_yen"] is None
    packets = load("inspection_evidence_packets.json")
    assert len(packets) == 1
    assert packets[0]["subject_id"] == ASM


def test_disclosure_profile():
    profiles = load("disclosure_profiles.json")
    validate("disclosure_profile.schema.json", profiles)
    assert len(profiles) == 1
    assert profiles[0]["as_of"] == "2026-11-23"
    items = {i["item"]: i for i in profiles[0]["items"]}
    assert len(items) == 12
    assert items["faction_votes"]["availability"] == "published"
    assert items["member_votes"]["availability"] == "published"
    assert items["member_votes"]["granularity"] == "member"
    assert (
        items["political_activity_expense_reports"]["granularity"]
        == "member"
    )
    assert items["inspection_trip_reports"]["availability"] == "published"


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
    assert len(packets) == 130
    vote_packets = load("proposal_vote_evidence_packets.json")
    assert len(vote_packets) == 55
    assert all(p["subject_type"] == "proposal" for p in vote_packets)
    assert all(p["open_questions"] == [] for p in vote_packets)
    # The assembly packet keeps one open question: the committees
    # page was last updated on 2023-05-16, so its composition
    # cannot be confirmed as of the September 2026 session from
    # the official page alone.
    assembly_packets = load("assembly_evidence_packets.json")
    assert len(assembly_packets) == 1
    assert len(assembly_packets[0]["open_questions"]) == 1
    expense_packets = load("expense_evidence_packets.json")
    assert len(expense_packets) == 73
    assert all(p["open_questions"] == [] for p in expense_packets)


def test_web_registry_wiring():
    registry = (ROOT / "apps" / "web" / "lib" / "assemblyRegistry.ts").read_text(
        encoding="utf-8"
    )
    assert '"kyoto-city"' in registry
    assert "kyotoCityAssembly" in registry
    assert "kyoto_city_assembly_sources.json" in registry
