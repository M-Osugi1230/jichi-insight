"""Cluster 10 stage 4: Shizuoka City assembly registration checks.

Pins the counts and cross-checks for the Shizuoka City Council data
taken from the September 2026 regular session (2026-09-15 to
2026-10-15), the FY2025 political activity expense reports of the
eight factions, and the ten committee inspection trips listed in the
FY2025 assembly activity report.
"""

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "reviewed" / "shizuoka-city" / "assembly"
CATALOG = ROOT / "data" / "catalog" / "shizuoka_city_assembly_sources.json"
ASM = "jp-local-221007-assembly-2025"
SESSION = f"{ASM}-session-2026-09"
FACTION_COUNTS = {
    "自由民主党静岡市議会議員団": 22,
    "志政会": 8,
    "公明党静岡市議会": 6,
    "日本共産党静岡市議会議員団": 4,
    "創生静岡": 3,
    "静岡市議会立憲民主党": 2,
    "チェンジングしずおかプロジェクト": 1,
    "緑の党グリーンズジャパン": 1,
    "りっけん静岡": 1,
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
    assert all(entry["municipality_key"] == "shizuoka-city" for entry in records)
    assert len(records) == 21


def test_assembly_record():
    records = load("assembly_records.json")
    validate("assembly.schema.json", records)
    assert len(records) == 1
    record = records[0]
    assert record["id"] == ASM
    assert record["municipality_id"] == "jp-local-221007"
    assert record["seat_count"] == 48
    assert record["term_start"] == "2025-04-01"
    assert record["term_end"] == "2029-03-31"
    # Roster of 2026-09-01: 48 sitting members in 9 factions, no vacancy.
    assert sum(f["member_count"] for f in record["factions"]) == 48
    by_name = {f["name"]: f["member_count"] for f in record["factions"]}
    assert by_name == FACTION_COUNTS
    assert len(record["committees"]) == 10


def test_session():
    sessions = load("sessions.json")
    validate("session.schema.json", sessions)
    assert len(sessions) == 1
    session = sessions[0]
    assert session["id"] == SESSION
    assert session["name"] == "令和8年9月定例会"
    assert session["start_date"] == "2026-09-15"
    assert session["end_date"] == "2026-10-15"


def test_proposals():
    proposals = load("proposals.json")
    validate("proposal.schema.json", proposals)
    assert len(proposals) == 56
    kinds = {}
    for p in proposals:
        kinds[p["kind"]] = kinds.get(p["kind"], 0) + 1
    assert kinds == {
        "budget": 6,
        "settlement": 19,
        "ordinance": 14,
        "other": 13,
        "personnel": 1,
        "resolution": 1,
        "petition": 2,
    }
    assert sum(1 for p in proposals if p["submitted_by"] == "executive") == 53
    assert sum(1 for p in proposals if p["submitted_by"] == "member") == 1
    assert (
        sum(1 for p in proposals if p["submitted_by"] == "resident_petition")
        == 2
    )
    by_number = {p["proposal_number"]: p for p in proposals}
    # All nineteen FY2025 settlements (certification items 1-19) were
    # certified; the inventory's "items 1-14" was corrected against
    # the official result PDF.
    for n in range(1, 20):
        assert by_number[f"認定第{n}号"]["kind"] == "settlement"
        assert by_number[f"認定第{n}号"]["outcome"] == "approved"
    # The four items decided on the opening day (2026-09-15).
    for number in ("議案第215号", "議案第216号", "議案第217号", "諮問第3号"):
        assert by_number[number]["submitted_at"] == "2026-09-15"
        assert by_number[number]["decided_at"] == "2026-09-15"
    assert by_number["諮問第3号"]["kind"] == "personnel"
    # Bill 218 was added on 2026-09-30.
    assert by_number["議案第218号"]["submitted_at"] == "2026-09-30"
    assert by_number["議案第218号"]["decided_at"] == "2026-10-15"
    # The member-submitted opinion paper passed; both the petition and
    # the citizen petition (chinjo) were rejected.
    assert by_number["発議第4号"]["outcome"] == "approved"
    assert by_number["請願第4号"]["outcome"] == "rejected"
    assert by_number["陳情第6号"]["outcome"] == "rejected"
    assert by_number["請願第4号"]["submitted_at"] == "2026-09-17"
    assert by_number["陳情第6号"]["submitted_at"] == "2026-09-17"


def test_votes():
    votes = load("votes.json")
    validate("vote.schema.json", votes)
    proposals = {p["id"]: p for p in load("proposals.json")}
    assert len(votes) == 56
    per_proposal = {}
    for v in votes:
        per_proposal.setdefault(v["proposal_id"], []).append(v)
    assert set(per_proposal) == set(proposals)
    assert all(len(vs) == 1 for vs in per_proposal.values())
    for vote in votes:
        assert vote["method"] == "unknown"
        assert vote["totals"] is None
        # Individual member votes are not published in Shizuoka City.
        assert vote["member_vote_availability"] == "not_published"
        assert vote["member_votes"] == []
        prop = proposals[vote["proposal_id"]]
        assert prop["decided_at"] == vote["vote_date"]
        assert prop["outcome"] == vote["outcome"]


def test_faction_votes():
    faction_votes = load("faction_votes.json")
    validate("faction_vote.schema.json", faction_votes)
    votes = {v["id"]: v for v in load("votes.json")}
    # The citizen petition (chinjo no. 6) has no published faction
    # breakdown, so 55 of the 56 votes carry nine faction rows each.
    assert len(faction_votes) == 55 * 9
    for fv in faction_votes:
        assert fv["member_count"] == FACTION_COUNTS[fv["faction_name"]]
        assert fv["for_count"] is None
        assert fv["against_count"] is None
    proposals = {p["proposal_number"]: p for p in load("proposals.json")}
    chinjo_vote = next(
        v for v in votes.values()
        if v["proposal_id"] == proposals["陳情第6号"]["id"]
    )
    assert not any(fv["vote_id"] == chinjo_vote["id"] for fv in faction_votes)
    for vote in votes.values():
        if vote["id"] == chinjo_vote["id"]:
            continue
        count = sum(1 for fv in faction_votes if fv["vote_id"] == vote["id"])
        assert count == 9


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

    # Certification item 1 (general account): JCP and Greens opposed.
    pos = positions("認定第1号")
    assert pos["日本共産党静岡市議会議員団"] == "against"
    assert pos["緑の党グリーンズジャパン"] == "against"
    assert sum(1 for p in pos.values() if p == "for") == 7
    # Certification item 19 (sewerage): only the JCP opposed.
    pos = positions("認定第19号")
    assert pos["日本共産党静岡市議会議員団"] == "against"
    assert sum(1 for p in pos.values() if p == "for") == 8
    # Bill 198 (Shimizu Hospital ordinance): JCP, Greens and Rikken
    # Shizuoka opposed.
    pos = positions("議案第198号")
    assert pos["日本共産党静岡市議会議員団"] == "against"
    assert pos["緑の党グリーンズジャパン"] == "against"
    assert pos["りっけん静岡"] == "against"
    assert sum(1 for p in pos.values() if p == "for") == 6
    # Bills 195, 197 and 201: only the JCP opposed.
    for number in ("議案第195号", "議案第197号", "議案第201号"):
        pos = positions(number)
        assert pos["日本共産党静岡市議会議員団"] == "against"
        assert sum(1 for p in pos.values() if p == "for") == 8
    # Opening-day items: the Greens' single member was absent.
    for number in ("議案第215号", "議案第216号", "議案第217号", "諮問第3号"):
        pos = positions(number)
        assert pos["緑の党グリーンズジャパン"] == "absent"
        assert sum(1 for p in pos.values() if p == "for") == 8
    # Petition no. 4: JCP, Greens and Rikken Shizuoka supported it;
    # the other six factions opposed, so it was rejected.
    pos = positions("請願第4号")
    assert pos["日本共産党静岡市議会議員団"] == "for"
    assert pos["緑の党グリーンズジャパン"] == "for"
    assert pos["りっけん静岡"] == "for"
    assert sum(1 for p in pos.values() if p == "against") == 6


def test_expenses():
    expenses = load("political_activity_expenses.json")
    validate("political_activity_expense.schema.json", expenses)
    # FY2025 grants were made to eight factions; Rikken Shizuoka did
    # not yet exist in FY2025 and has no report.
    assert len(expenses) == 8
    assert all(r["fiscal_year"] == 2025 for r in expenses)
    assert all(r["recipient_type"] == "faction" for r in expenses)
    assert all(r["receipt_access"] == "online" for r in expenses)
    assert all(r["report_status"] == "published" for r in expenses)
    for record in expenses:
        assert (
            sum(i["amount_yen"] for i in record["breakdown"])
            == record["spent_yen"]
        ), record["recipient_name"]
        assert len(record["breakdown"]) == 9
    assert sum(r["granted_yen"] for r in expenses) == 144000000
    assert sum(r["spent_yen"] for r in expenses) == 115612945
    assert sum(r["returned_yen"] for r in expenses) == 28426851
    by_name = {r["recipient_name"]: r for r in expenses}
    jimin = by_name["自由民主党静岡市議会議員団"]
    assert jimin["granted_yen"] == 66000000
    assert jimin["spent_yen"] == 49563425
    assert jimin["returned_yen"] == 16450036
    # The FY2025 grant of 12,000,000 yen (four members at 250,000 yen
    # per month) shows the CDP faction then had four members.
    assert by_name["静岡市議会立憲民主党"]["granted_yen"] == 12000000


def test_inspection_trips():
    trips = load("inspection_trips.json")
    validate("inspection_trip.schema.json", trips)
    # The FY2025 activity report lists ten committee inspection trips;
    # participants and costs are not published in it.
    assert len(trips) == 10
    for trip in trips:
        assert trip["trip_type"] == "domestic"
        assert trip["cost_status"] == "not_published"
        assert trip["report_status"] == "published"
        assert trip["participant_count"] is None
        assert trip["participants"] == []
    packets = load("inspection_evidence_packets.json")
    validate("evidence_packet.schema.json", packets)
    assert len(packets) == 10


def test_disclosure_profile():
    profiles = load("disclosure_profiles.json")
    validate("disclosure_profile.schema.json", profiles)
    assert len(profiles) == 1
    items = {item["item"]: item for item in profiles[0]["items"]}
    assert len(items) == 12
    assert items["faction_votes"]["availability"] == "published"
    assert items["member_votes"]["availability"] == "not_published"
    assert (
        items["political_activity_expense_receipts"]["availability"]
        == "published"
    )
    assert items["inspection_trip_reports"]["availability"] == "published"
    assert items["petition_results"]["availability"] == "published"


def test_evidence_packets():
    validate("evidence_packet.schema.json", load("assembly_evidence_packets.json"))
    validate(
        "evidence_packet.schema.json", load("proposal_vote_evidence_packets.json")
    )
    validate("evidence_packet.schema.json", load("expense_evidence_packets.json"))
    validate(
        "evidence_packet.schema.json", load("inspection_evidence_packets.json")
    )
    assembly_packets = load("assembly_evidence_packets.json")
    assert len(assembly_packets) == 1
    assert len(assembly_packets[0]["open_questions"]) == 2
    assert len(load("proposal_vote_evidence_packets.json")) == 56
    assert len(load("expense_evidence_packets.json")) == 8
    # The assembly packet records the corrected settlement count.
    claims = " ".join(
        c["statement"] for c in assembly_packets[0]["claims"])
    assert "第19号" in claims
