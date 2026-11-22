"""Issue #984: Okayama City assembly registration checks (cluster 14 stage 4).

Pins the counts and cross-checks for the Okayama City Council data
taken from the September 2026 regular session (令和8年9月定例会,
2026-09-01 to 2026-10-16), the member-by-member votes published only
for the seven items decided by standing vote, and the FY2025
political activity expense reports, which the city has not published
as of 2026-11-23 (the index page lists the eight faction names for
FY2025 without links to any report).
"""

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "reviewed" / "okayama-city" / "assembly"
CATALOG = ROOT / "data" / "catalog" / "okayama_city_assembly_sources.json"
ASM = "jp-local-331007-assembly-2023"
SESSION = f"{ASM}-session-2026-09"
FACTION_COUNTS = {
    "公明党岡山市議団": 8,
    "日本共産党岡山市議団": 4,
    "自由民主党岡山市議会": 23,
    "懐かしい未来": 2,
    "みらいえ": 2,
    "おかやま創政会": 4,
    "おかやま未来プロジェクト": 1,
    "日本維新の会岡山市議団": 1,
}
# The seven items decided by standing vote in the September 2026
# session, with the totals printed in the city's member-vote tables
# (the chair, 田口裕士, does not vote and is recorded as excused).
STANDING_TOTALS = {
    "決第1号": (39, 5),
    "決第2号": (40, 4),
    "決第10号": (40, 4),
    "決第13号及び甲第166号議案": (40, 4),
    "甲第145号議案": (39, 5),
    "諮問第2号": (38, 6),
    "乙第3号議案": (8, 36),
}
MEMBERS = [
    "則武宣弘", "松田安義", "福吉智徳", "林敏宏", "平元道隆", "桑田桂子",
    "長岡将克", "早野賢一", "林潤", "田中のぞみ", "東毅", "宿女和子",
    "宮武博", "三木亮治", "和氣健", "田口裕士", "成本俊一", "小川信幸",
    "藤原哲之", "森田卓司", "吉本賢二", "赤木一雄", "難波満津留",
    "二嶋宣人", "川本浩一郎", "山田正幸", "松田隆之", "松本好厚",
    "柳井弘", "岡崎隆", "花岡栄太郎", "江田厚志", "大月晴一", "安東真理",
    "髙橋誠一郎", "森山幸治", "川上智美", "鬼木のぞみ", "土田貴行",
    "小林寿雄", "高橋雄大", "太田栄司", "柳迫和夫", "中島純", "前島慶太",
]


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
        entry["municipality_key"] == "okayama-city" for entry in records
    )
    assert len(records) == 12


def test_assembly_record():
    records = load("assembly_records.json")
    validate("assembly.schema.json", records)
    assert len(records) == 1
    record = records[0]
    assert record["id"] == ASM
    assert record["municipality_id"] == "jp-local-331007"
    assert record["name"] == "岡山市議会"
    assert record["seat_count"] == 46
    # Term end 2027-04-30 is printed in the prefectural election
    # commission's term list (as of 2026-05-26); the four-year term
    # starts 2023-05-01.
    assert record["term_start"] == "2023-05-01"
    assert record["term_end"] == "2027-04-30"
    by_name = {f["name"]: f["member_count"] for f in record["factions"]}
    assert by_name == FACTION_COUNTS
    # The faction counts sum to 45, one below the statutory 46 seats:
    # one seat is vacant (see the assembly evidence packet).
    assert sum(by_name.values()) == 45
    assert len(record["committees"]) == 8


def test_sessions():
    sessions = load("sessions.json")
    validate("session.schema.json", sessions)
    assert len(sessions) == 1
    session = sessions[0]
    assert session["id"] == SESSION
    assert session["name"] == "令和8年9月定例会"
    assert session["session_type"] == "regular"
    assert session["start_date"] == "2026-09-01"
    assert session["end_date"] == "2026-10-16"


def test_proposals():
    proposals = load("proposals.json")
    validate("proposal.schema.json", proposals)
    assert len(proposals) == 60
    kinds = {}
    for p in proposals:
        kinds[p["kind"]] = kinds.get(p["kind"], 0) + 1
    assert kinds == {
        "settlement": 17,
        "budget": 3,
        "ordinance": 5,
        "amendment": 1,
        "other": 19,
        "personnel": 2,
        "resolution": 3,
        "petition": 10,
    }
    assert sum(1 for p in proposals if p["submitted_by"] == "executive") == 45
    assert sum(1 for p in proposals if p["submitted_by"] == "member") == 5
    assert (
        sum(1 for p in proposals if p["submitted_by"] == "resident_petition")
        == 10
    )
    assert all(p["session_id"] == SESSION for p in proposals)
    assert sum(1 for p in proposals if p["outcome"] == "approved") == 52
    assert sum(1 for p in proposals if p["outcome"] == "rejected") == 8
    # All seventeen FY2025 settlements (決第1号 to 決第17号) were
    # certified on 2026-10-16.
    settlements = [p for p in proposals if p["kind"] == "settlement"]
    assert len(settlements) == 17
    assert all(p["outcome"] == "approved" for p in settlements)
    assert all(p["decided_at"] == "2026-10-16" for p in settlements)
    by_number = {p["proposal_number"]: p for p in proposals}
    assert by_number["決第1号"]["title"].startswith(
        "令和7年度岡山市一般会計歳入歳出決算"
    )
    # Three items were decided mid-session, on 2026-09-17: the
    # accommodation tax ordinance, consultation 2 and member bill
    # 乙第3号 (the arena referendum ordinance, rejected).
    for number in ("甲第145号議案", "諮問第2号", "乙第3号議案"):
        assert by_number[number]["decided_at"] == "2026-09-17"
    assert by_number["甲第145号議案"]["kind"] == "ordinance"
    assert by_number["甲第145号議案"]["outcome"] == "approved"
    assert by_number["乙第3号議案"]["submitted_by"] == "member"
    assert by_number["乙第3号議案"]["outcome"] == "rejected"
    # 甲 bills are the mayor's, 乙 bills are members' bills, and the
    # two consultations split into personnel and other.
    assert by_number["乙第2号議案"]["kind"] == "amendment"
    assert by_number["甲第169号議案"]["kind"] == "personnel"
    assert by_number["諮問第3号"]["kind"] == "personnel"
    assert by_number["諮問第2号"]["kind"] == "other"
    # Petitions: three adopted, seven not adopted.
    petitions = [p for p in proposals if p["kind"] == "petition"]
    assert sum(1 for p in petitions if p["outcome"] == "approved") == 3
    assert sum(1 for p in petitions if p["outcome"] == "rejected") == 7
    assert by_number["令和6年陳情第39号"]["outcome"] == "rejected"


def test_votes():
    votes = load("votes.json")
    validate("vote.schema.json", votes)
    proposals = {p["id"]: p for p in load("proposals.json")}
    assert len(votes) == 60
    per_proposal = {}
    for v in votes:
        per_proposal.setdefault(v["proposal_id"], []).append(v)
    assert set(per_proposal) == set(proposals)
    assert all(len(vs) == 1 for vs in per_proposal.values())
    standing = [v for v in votes if v["method"] == "standing"]
    others = [v for v in votes if v["method"] != "standing"]
    assert len(standing) == 7
    assert len(others) == 53
    for vote in others:
        # Member votes for items not decided by standing vote are not
        # published, so no member-level positions are registered.
        assert vote["method"] == "unknown"
        assert vote["member_vote_availability"] == "not_published"
        assert vote["member_votes"] == []
        assert vote["totals"] is None
    for vote in votes:
        prop = proposals[vote["proposal_id"]]
        assert prop["decided_at"] == vote["vote_date"]
        assert prop["outcome"] == vote["outcome"]
    # 7 standing-vote items x 45 serving members.
    assert sum(len(v["member_votes"]) for v in standing) == 7 * 45


def test_standing_vote_details():
    proposals = {p["proposal_number"]: p for p in load("proposals.json")}
    votes = {v["proposal_id"]: v for v in load("votes.json")}

    def positions(number):
        vote = votes[proposals[number]["id"]]
        return {m["member_name"]: m["position"] for m in vote["member_votes"]}

    for number, (for_count, against_count) in STANDING_TOTALS.items():
        vote = votes[proposals[number]["id"]]
        assert vote["member_vote_availability"] == "published"
        assert vote["totals"] == {
            "for": for_count,
            "against": against_count,
            "abstained": 0,
            "absent": 0,
        }
        # Totals recompute exactly from the member rows, and the
        # member order matches the city's tables in both sittings.
        members = vote["member_votes"]
        assert [m["member_name"] for m in members] == MEMBERS
        recomputed = {
            key: sum(1 for m in members if m["position"] == key)
            for key in ("for", "against", "abstained", "absent")
        }
        assert recomputed == vote["totals"]
        # The chair does not take part in the vote.
        pos = positions(number)
        assert pos["田口裕士"] == "excused"
    # Settlement 1: the four JCP members and 土田貴行 opposed
    # certification; on settlements 2, 10 and 13 only the JCP opposed.
    pos = positions("決第1号")
    assert pos["土田貴行"] == "against"
    assert pos["鬼木のぞみ"] == "for"
    for number in ("決第2号", "決第10号", "決第13号及び甲第166号議案"):
        pos = positions(number)
        assert pos["土田貴行"] == "for"
        assert pos["林潤"] == "against"
    # Accommodation tax ordinance: the JCP four and 鬼木のぞみ opposed.
    pos = positions("甲第145号議案")
    assert pos["鬼木のぞみ"] == "against"
    assert pos["土田貴行"] == "for"
    # Consultation 2: the JCP four, 土田貴行 and 前島慶太 opposed.
    pos = positions("諮問第2号")
    assert pos["土田貴行"] == "against"
    assert pos["前島慶太"] == "against"
    assert pos["鬼木のぞみ"] == "for"
    # Arena referendum ordinance: only eight members in favour.
    pos = positions("乙第3号議案")
    in_favour = {name for name, p in pos.items() if p == "for"}
    assert in_favour == {
        "林潤", "田中のぞみ", "東毅", "宿女和子",
        "川上智美", "鬼木のぞみ", "土田貴行", "前島慶太",
    }


def test_faction_votes_empty():
    # The city publishes member-level positions only; there is no
    # official faction-level tally to register.
    faction_votes = load("faction_votes.json")
    validate("faction_vote.schema.json", faction_votes)
    assert faction_votes == []


def test_expenses_not_published():
    expenses = load("political_activity_expenses.json")
    validate("political_activity_expense.schema.json", expenses)
    assert len(expenses) == 8
    names = [e["recipient_name"] for e in expenses]
    assert names == [
        "公明党岡山市議団",
        "日本共産党岡山市議団",
        "自由民主党岡山市議会",
        "懐かしい未来",
        "みらいえ",
        "おかやま創政会",
        "おかやま未来プロジェクト",
        "日本維新の会岡山市議団",
    ]
    for record in expenses:
        # FY2025 reports are listed by faction name on the index page
        # but no report document is linked or published in the
        # category listing (checked 2026-11-23), so every amount
        # stays null rather than being estimated from the grant
        # formula.
        assert record["fiscal_year"] == 2025
        assert record["recipient_type"] == "faction"
        assert record["report_status"] == "not_published"
        assert record["receipt_access"] == "not_published"
        assert record["granted_yen"] is None
        assert record["spent_yen"] is None
        assert record["returned_yen"] is None
        assert record["breakdown"] == []


def test_inspection_trips_empty():
    trips = load("inspection_trips.json")
    validate("inspection_trip.schema.json", trips)
    assert trips == []
    packets = load("inspection_evidence_packets.json")
    validate("evidence_packet.schema.json", packets)
    assert len(packets) == 1
    assert packets[0]["subject_id"] == ASM


def test_disclosure_profile():
    profiles = load("disclosure_profiles.json")
    validate("disclosure_profile.schema.json", profiles)
    assert len(profiles) == 1
    items = {item["item"]: item for item in profiles[0]["items"]}
    assert len(items) == 12
    assert items["member_votes"]["availability"] == "published"
    assert items["faction_votes"]["availability"] == "not_published"
    assert (
        items["political_activity_expense_reports"]["availability"]
        == "not_published"
    )
    assert items["inspection_trip_reports"]["availability"] == "not_published"
    assert items["meeting_minutes"]["availability"] == "published"


def test_evidence_packets():
    assembly_packets = load("assembly_evidence_packets.json")
    validate("evidence_packet.schema.json", assembly_packets)
    assert len(assembly_packets) == 1
    assert assembly_packets[0]["subject_id"] == ASM
    assert len(assembly_packets[0]["open_questions"]) == 3
    proposal_packets = load("proposal_vote_evidence_packets.json")
    validate("evidence_packet.schema.json", proposal_packets)
    proposals = {p["id"] for p in load("proposals.json")}
    assert {p["subject_id"] for p in proposal_packets} == proposals
    assert len(proposal_packets) == 60
    expense_packets = load("expense_evidence_packets.json")
    validate("evidence_packet.schema.json", expense_packets)
    expenses = {e["id"] for e in load("political_activity_expenses.json")}
    assert {p["subject_id"] for p in expense_packets} == expenses
    assert len(expense_packets) == 8


def test_all_source_ids_exist_in_catalog():
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    catalog_ids = {entry["id"] for entry in catalog["records"]}
    used = set()
    for name in (
        "assembly_records.json",
        "sessions.json",
        "proposals.json",
        "votes.json",
        "political_activity_expenses.json",
        "disclosure_profiles.json",
    ):
        for record in load(name):
            used.update(record["sources"])
    for name in (
        "assembly_evidence_packets.json",
        "proposal_vote_evidence_packets.json",
        "expense_evidence_packets.json",
        "inspection_evidence_packets.json",
    ):
        for packet in load(name):
            for claim in packet["claims"]:
                used.update(claim["source_ids"])
    assert used <= catalog_ids
