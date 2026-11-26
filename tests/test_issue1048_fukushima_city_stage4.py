"""Issue #1048: Fukushima City assembly registration checks (cluster 16 stage 4).

Pins the counts and cross-checks for the Fukushima City Council data
taken from the September 2026 regular session (令和8年9月定例会議,
2026-09-01 to 2026-09-24), the member-by-member votes published by
the electronic voting system PDFs for only three items （議案第92号,
議案第98号 and 陳情第13号）, and the FY2025 political activity
expense results for the eight recipient factions (grants are made
per faction at 100,000 yen per member per month; two factions were
dissolved at the end of July 2025 and are reported for April-July
only).
"""

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "reviewed" / "fukushima-city" / "assembly"
CATALOG = ROOT / "data" / "catalog" / "fukushima_city_assembly_sources.json"
ASM = "jp-local-072010-assembly-2023"
SESSION = f"{ASM}-session-2026-09"
FACTION_COUNTS = {
    "真政会": 11,
    "真結の会": 10,
    "ふくしま市民21": 5,
    "公明党福島市議団": 4,
    "日本共産党福島市議会議員団": 3,
    "無所属": 1,
}
# Members in seat order (roster as of 2026-10-01, with seat 33
# filled by 半沢正典, who still sat in the September session and
# resigned effective 2026-09-30). The chair is seat 17, 白川敏明.
MEMBERS = [
    "三浦由美子", "高木直人", "遠藤幸一", "菅原美智子", "二階堂利枝",
    "鈴木哲", "浦野洋太朗", "佐藤勢", "山田裕", "丹治誠",
    "佐原真紀", "根本雅昭", "斎藤正臣", "川又康彦", "七島奈緒",
    "石山波恵", "白川敏明", "佐々木優", "後藤善次", "沢井和宏",
    "鈴木正実", "二階堂武文", "尾形武", "萩原太郎", "大平洋人",
    "小松良行", "村山国子", "小野京子", "羽田房男", "高木克尚",
    "真田広志", "宍戸一照", "半沢正典", "黒沢仁", "渡辺敏彦",
]
# The same three members opposed bills 92 and 98 and supported the
# petition; everyone else (except the chair) did the opposite.
DISSENTERS = {"山田裕", "佐々木優", "村山国子"}
PUBLISHED_TOTALS = {
    "議案第92号": (31, 3),
    "議案第98号": (31, 3),
    "陳情第13号": (3, 31),
}
# name, granted, spent, returned (収支差引額, includes interest)
EXPENSE_TOTALS = {
    "真政会": (13200000, 12423940, 779989),
    "真結の会": (11600000, 9947410, 1657352),
    "ふくしま市民21": (6200000, 4838205, 1365209),
    "公明党福島市議団": (4800000, 4066409, 735851),
    "日本共産党福島市議会議員団": (3600000, 3227084, 374678),
    "社会民主党・市民連合": (1200000, 569278, 631952),
    "政新会": (400000, 56540, 344202),
    "一心会": (400000, 36080, 364580),
}
INTEREST = {
    "真政会": 3929,
    "真結の会": 4762,
    "ふくしま市民21": 3414,
    "公明党福島市議団": 2260,
    "日本共産党福島市議会議員団": 1762,
    "社会民主党・市民連合": 1230,
    "政新会": 742,
    "一心会": 660,
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
        entry["municipality_key"] == "fukushima-city" for entry in records
    )
    assert len(records) == 24


def test_assembly_record():
    records = load("assembly_records.json")
    validate("assembly.schema.json", records)
    assert len(records) == 1
    record = records[0]
    assert record["id"] == ASM
    assert record["municipality_id"] == "jp-local-072010"
    assert record["name"] == "福島市議会"
    assert record["seat_count"] == 35
    # Term end 2027-07-30 is printed in the Fukushima Prefectural
    # Election Administration Commission's term list (as of
    # 2026-04-01); the four-year term starts 2023-07-31.
    assert record["term_start"] == "2023-07-31"
    assert record["term_end"] == "2027-07-30"
    by_name = {f["name"]: f["member_count"] for f in record["factions"]}
    assert by_name == FACTION_COUNTS
    # The faction counts sum to 34, one below the statutory 35
    # seats: seat 33 fell vacant when 半沢正典 resigned effective
    # 2026-09-30 (see the assembly evidence packet).
    assert sum(by_name.values()) == 34
    assert len(record["committees"]) == 6


def test_sessions():
    sessions = load("sessions.json")
    validate("session.schema.json", sessions)
    assert len(sessions) == 1
    session = sessions[0]
    assert session["id"] == SESSION
    assert session["name"] == "令和8年9月定例会議"
    assert session["session_type"] == "regular"
    assert session["start_date"] == "2026-09-01"
    assert session["end_date"] == "2026-09-24"


def test_proposals():
    proposals = load("proposals.json")
    validate("proposal.schema.json", proposals)
    assert len(proposals) == 32
    kinds = {}
    for p in proposals:
        kinds[p["kind"]] = kinds.get(p["kind"], 0) + 1
    assert kinds == {
        "budget": 4,
        "settlement": 4,
        "ordinance": 7,
        "other": 9,
        "resolution": 2,
        "personnel": 5,
        "petition": 1,
    }
    # The city's bill-count table: 29 executive bills, 2 member
    # bills (the two opinion papers), plus one resident petition.
    assert sum(1 for p in proposals if p["submitted_by"] == "executive") == 29
    assert sum(1 for p in proposals if p["submitted_by"] == "member") == 2
    assert (
        sum(1 for p in proposals if p["submitted_by"] == "resident_petition")
        == 1
    )
    assert all(p["session_id"] == SESSION for p in proposals)
    assert all(p["decided_at"] == "2026-09-24" for p in proposals)
    assert sum(1 for p in proposals if p["outcome"] == "approved") == 31
    assert sum(1 for p in proposals if p["outcome"] == "rejected") == 1
    # Submission dates printed on the results page: bills 88-110 on
    # 2026-09-01, bill 111 on 2026-09-10, bills 112-118 on 2026-09-24.
    by_number = {p["proposal_number"]: p for p in proposals}
    assert by_number["議案第88号"]["submitted_at"] == "2026-09-01"
    assert by_number["議案第111号"]["submitted_at"] == "2026-09-10"
    assert by_number["議案第112号"]["submitted_at"] == "2026-09-24"
    assert by_number["議案第112号"]["submitted_by"] == "member"
    assert by_number["議案第113号"]["kind"] == "resolution"
    # All four FY2025 settlements were certified on 2026-09-24;
    # none was rejected (不認定ではない). Bill 94 also carried the
    # surplus disposal, which passed as proposed.
    settlements = [p for p in proposals if p["kind"] == "settlement"]
    assert [p["proposal_number"] for p in settlements] == [
        "議案第92号", "議案第93号", "議案第94号", "議案第95号",
    ]
    assert all(p["outcome"] == "approved" for p in settlements)
    # The only petition of the session was not adopted.
    petition = by_number["陳情第13号"]
    assert petition["kind"] == "petition"
    assert petition["outcome"] == "rejected"


def test_votes():
    votes = load("votes.json")
    validate("vote.schema.json", votes)
    proposals = {p["id"]: p for p in load("proposals.json")}
    assert len(votes) == 32
    per_proposal = {}
    for v in votes:
        per_proposal.setdefault(v["proposal_id"], []).append(v)
    assert set(per_proposal) == set(proposals)
    assert all(len(vs) == 1 for vs in per_proposal.values())
    published = [v for v in votes if v["member_vote_availability"] == "published"]
    others = [v for v in votes if v["member_vote_availability"] != "published"]
    assert len(published) == 3
    assert len(others) == 29
    for vote in others:
        # No voting-system result PDF is published for these items,
        # so no member-level positions or totals are registered.
        assert vote["method"] == "unknown"
        assert vote["member_vote_availability"] == "not_published"
        assert vote["member_votes"] == []
        assert vote["totals"] is None
    for vote in votes:
        prop = proposals[vote["proposal_id"]]
        assert prop["decided_at"] == vote["vote_date"]
        assert prop["outcome"] == vote["outcome"]
    # 3 published items x 35 members (including the chair as excused).
    assert sum(len(v["member_votes"]) for v in published) == 3 * 35


def test_published_vote_details():
    proposals = {p["proposal_number"]: p for p in load("proposals.json")}
    votes = {v["proposal_id"]: v for v in load("votes.json")}
    for number, (for_count, against_count) in PUBLISHED_TOTALS.items():
        vote = votes[proposals[number]["id"]]
        # The minutes cross-check for the nature of the published
        # tables is still outstanding, so the method stays unknown
        # (see the proposal evidence packets' open questions).
        assert vote["method"] == "unknown"
        assert vote["totals"] == {
            "for": for_count,
            "against": against_count,
            "abstained": 0,
            "absent": 0,
        }
        members = vote["member_votes"]
        assert [m["member_name"] for m in members] == MEMBERS
        recomputed = {
            key: sum(1 for m in members if m["position"] == key)
            for key in ("for", "against", "abstained", "absent")
        }
        assert recomputed == vote["totals"]
        pos = {m["member_name"]: m["position"] for m in members}
        # The chair does not take part in the vote.
        assert pos["白川敏明"] == "excused"
        if number == "陳情第13号":
            assert {n for n, p in pos.items() if p == "for"} == DISSENTERS
        else:
            assert {n for n, p in pos.items() if p == "against"} == DISSENTERS
        # 半沢正典 still sat and voted in the September session; his
        # resignation took effect on 2026-09-30.
        assert pos["半沢正典"] == (
            "against" if number == "陳情第13号" else "for"
        )


def test_faction_votes_empty():
    # The city publishes member-level positions only; there is no
    # official faction-level tally to register.
    faction_votes = load("faction_votes.json")
    validate("faction_vote.schema.json", faction_votes)
    assert faction_votes == []


def test_expenses():
    expenses = load("political_activity_expenses.json")
    validate("political_activity_expense.schema.json", expenses)
    assert len(expenses) == 8
    names = [e["recipient_name"] for e in expenses]
    assert names == list(EXPENSE_TOTALS)
    for record in expenses:
        granted, spent, returned = EXPENSE_TOTALS[record["recipient_name"]]
        assert record["fiscal_year"] == 2025
        assert record["recipient_type"] == "faction"
        assert record["report_status"] == "published"
        assert record["receipt_access"] == "online"
        assert record["granted_yen"] == granted
        assert record["spent_yen"] == spent
        assert record["returned_yen"] == returned
        # Breakdown (10 printed categories) sums to the spent total.
        assert len(record["breakdown"]) == 10
        assert sum(b["amount_yen"] for b in record["breakdown"]) == spent
        # The printed balance (収支差引額) is granted + interest -
        # spent; the interest amounts are pinned in INTEREST.
        interest = INTEREST[record["recipient_name"]]
        assert granted + interest - spent == returned
    # City-wide totals printed in the summary table.
    assert sum(e["granted_yen"] for e in expenses) == 41400000
    assert sum(e["spent_yen"] for e in expenses) == 35164946
    assert sum(e["returned_yen"] for e in expenses) == 6253813


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
        == "published"
    )
    assert (
        items["political_activity_expense_receipts"]["availability"]
        == "published"
    )
    assert items["inspection_trip_reports"]["availability"] == "not_published"
    assert items["meeting_minutes"]["availability"] == "published"
    assert items["petition_results"]["availability"] == "published"


def test_evidence_packets():
    assembly_packets = load("assembly_evidence_packets.json")
    validate("evidence_packet.schema.json", assembly_packets)
    assert len(assembly_packets) == 1
    assert assembly_packets[0]["subject_id"] == ASM
    assert len(assembly_packets[0]["open_questions"]) == 2
    proposal_packets = load("proposal_vote_evidence_packets.json")
    validate("evidence_packet.schema.json", proposal_packets)
    proposals = {p["id"] for p in load("proposals.json")}
    assert {p["subject_id"] for p in proposal_packets} == proposals
    assert len(proposal_packets) == 32
    # Only the three items with published member votes carry the
    # outstanding minutes cross-check as an open question.
    with_open = [
        p for p in proposal_packets if p["open_questions"]
    ]
    assert len(with_open) == 3
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
