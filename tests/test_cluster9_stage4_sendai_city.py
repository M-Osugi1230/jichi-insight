"""Cluster 9 stage 4: Sendai City assembly registration checks.

Pins the counts and cross-checks for the Sendai City Council data taken
from the 3rd regular session of Reiwa 8 (2026-09-04 to 2026-10-08),
the FY2025 political activity expense reports, and the documented
absence of published committee inspection reports and of FY2025
individual political activity expense grants.
"""

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "reviewed" / "sendai-city" / "assembly"
CATALOG = ROOT / "data" / "catalog" / "sendai_city_assembly_sources.json"
ASM = "jp-local-041009-assembly-2023"
SESSION = f"{ASM}-session-2026-09"
FACTION_COUNTS = {
    "自由民主党": 13,
    "公明党仙台市議団": 9,
    "市民フォーラム仙台": 9,
    "せんだい自民・参政の会": 6,
    "日本共産党仙台市議団": 5,
    "立憲民主党仙台": 4,
    "新政SENDAI": 2,
    "日本維新の会": 2,
    "心豊かな社会をつくる会": 1,
    "市民の会": 1,
    "自由民主党フォーラム": 1,
    "持続可能な地域をつくる会": 1,
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
    assert all(entry["municipality_key"] == "sendai-city" for entry in records)
    assert len(records) == 26


def test_assembly_record():
    records = load("assembly_records.json")
    validate("assembly.schema.json", records)
    assert len(records) == 1
    record = records[0]
    assert record["id"] == ASM
    assert record["municipality_id"] == "jp-local-041009"
    assert record["seat_count"] == 55
    assert record["term_start"] == "2023-08-28"
    assert record["term_end"] == "2027-08-27"
    # Roster of 2026-09-01: 54 sitting members in 12 factions. The one
    # vacant seat (Wakabayashi ward) follows the death of Councilor
    # Nihei Satoko on 2026-08-04, per the assembly secretariat's
    # press release of 2026-08-05.
    assert sum(f["member_count"] for f in record["factions"]) == 54
    by_name = {f["name"]: f["member_count"] for f in record["factions"]}
    assert by_name == FACTION_COUNTS
    assert len(record["committees"]) == 13


def test_session():
    sessions = load("sessions.json")
    validate("session.schema.json", sessions)
    assert len(sessions) == 1
    session = sessions[0]
    assert session["id"] == SESSION
    assert session["name"] == "令和8年第3回定例会"
    assert session["start_date"] == "2026-09-04"
    assert session["end_date"] == "2026-10-08"


def test_proposals():
    proposals = load("proposals.json")
    validate("proposal.schema.json", proposals)
    assert len(proposals) == 47
    kinds = {}
    for p in proposals:
        kinds[p["kind"]] = kinds.get(p["kind"], 0) + 1
    assert kinds == {
        "settlement": 7,
        "budget": 3,
        "ordinance": 9,
        "other": 18,
        "personnel": 4,
        "resolution": 6,
    }
    assert sum(1 for p in proposals if p["submitted_by"] == "executive") == 41
    assert sum(1 for p in proposals if p["submitted_by"] == "member") == 6
    # Every item was decided at the final plenary on 2026-10-08.
    assert all(p["decided_at"] == "2026-10-08" for p in proposals)
    assert all(p["submitted_at"] == "2026-09-04"
               for p in proposals if p["submitted_by"] == "executive")
    by_number = {p["proposal_number"]: p for p in proposals}
    # All FY2025 settlements (bills 91-97) were certified.
    for n in range(91, 98):
        assert by_number[f"第{n}号議案"]["outcome"] == "approved"
    # Personnel items: consent for 128-130, no-objection for 131.
    for n in (128, 129, 130, 131):
        assert by_number[f"第{n}号議案"]["kind"] == "personnel"
        assert by_number[f"第{n}号議案"]["outcome"] == "approved"
    # Only opinion no. 13 was rejected.
    assert by_number["意見書第13号"]["outcome"] == "rejected"
    for n in (10, 11, 12):
        assert by_number[f"意見書第{n}号"]["outcome"] == "approved"
    assert by_number["決議第2号"]["outcome"] == "approved"
    assert by_number["決議第3号"]["outcome"] == "approved"
    # No petition was concluded in this session, so none is registered.
    assert not any(p["kind"] == "petition" for p in proposals)


def test_votes():
    votes = load("votes.json")
    validate("vote.schema.json", votes)
    proposals = {p["id"]: p for p in load("proposals.json")}
    assert len(votes) == 48
    # Bill no. 91 carries two votes (general account / special
    # accounts); every other proposal carries exactly one.
    per_proposal = {}
    for v in votes:
        per_proposal.setdefault(v["proposal_id"], []).append(v)
    assert set(per_proposal) == set(proposals)
    bill91 = next(p for p in proposals.values()
                  if p["proposal_number"] == "第91号議案")
    assert len(per_proposal[bill91["id"]]) == 2
    assert {v["item_scope"] for v in per_proposal[bill91["id"]]} == {
        "一般会計歳入歳出", "特別会計歳入歳出"}
    assert all(len(vs) == 1 for pid, vs in per_proposal.items()
               if pid != bill91["id"])
    for vote in votes:
        assert vote["method"] == "unknown"
        assert vote["totals"] is None
        # Individual member votes are not published in Sendai.
        assert vote["member_vote_availability"] == "not_published"
        assert vote["member_votes"] == []
        prop = proposals[vote["proposal_id"]]
        assert prop["decided_at"] == vote["vote_date"] == "2026-10-08"
        assert prop["outcome"] == vote["outcome"]


def test_faction_votes():
    faction_votes = load("faction_votes.json")
    validate("faction_vote.schema.json", faction_votes)
    votes = {v["id"]: v for v in load("votes.json")}
    assert len(faction_votes) == 48 * 12
    for fv in faction_votes:
        assert fv["member_count"] == FACTION_COUNTS[fv["faction_name"]]
        if fv["position"] in ("for", "against", "abstained"):
            assert fv["for_count"] is None
            assert fv["against_count"] is None
    # Every vote has all twelve factions.
    for vote in votes.values():
        count = sum(1 for fv in faction_votes if fv["vote_id"] == vote["id"])
        assert count == 12


def test_divided_votes():
    proposals = {p["proposal_number"]: p for p in load("proposals.json")}
    votes = {v["proposal_id"]: v for v in load("votes.json")}
    faction_votes = load("faction_votes.json")

    def positions(number):
        vote = votes[proposals[number]["id"]]
        return {
            fv["faction_name"]: fv
            for fv in faction_votes
            if fv["vote_id"] == vote["id"]
        }

    # Bill 91, general account: JCP, Ishin, Kokoro and Jizoku opposed.
    bill91 = proposals["第91号議案"]
    general = next(v for v in load("votes.json")
                   if v["proposal_id"] == bill91["id"]
                   and v["item_scope"] == "一般会計歳入歳出")
    pos = {fv["faction_name"]: fv["position"]
           for fv in faction_votes if fv["vote_id"] == general["id"]}
    assert pos["日本共産党仙台市議団"] == "against"
    assert pos["日本維新の会"] == "against"
    assert pos["心豊かな社会をつくる会"] == "against"
    assert pos["持続可能な地域をつくる会"] == "against"
    assert pos["自由民主党"] == "for"
    # Bill 108: only the Ishin faction opposed.
    pos = positions("第108号議案")
    assert pos["日本維新の会"]["position"] == "against"
    assert sum(1 for fv in pos.values() if fv["position"] == "for") == 11
    # Opinion 12: Shimin Forum split 8-1 in favour; the item passed.
    pos = positions("意見書第12号")
    forum = pos["市民フォーラム仙台"]
    assert forum["position"] == "split"
    assert forum["for_count"] == 8
    assert forum["against_count"] == 1
    assert proposals["意見書第12号"]["outcome"] == "approved"
    # Opinion 13: Shimin Forum split 1-8, Shimin no Kai left the
    # chamber; the item was rejected.
    pos = positions("意見書第13号")
    forum = pos["市民フォーラム仙台"]
    assert forum["position"] == "split"
    assert forum["for_count"] == 1
    assert forum["against_count"] == 8
    assert pos["市民の会"]["position"] == "abstained"
    assert proposals["意見書第13号"]["outcome"] == "rejected"
    # Resolution 3: Sendai Jimin / Sansei split 0-5 with one member
    # leaving the chamber; the item passed.
    pos = positions("決議第3号")
    sj = pos["せんだい自民・参政の会"]
    assert sj["position"] == "split"
    assert sj["for_count"] == 0
    assert sj["against_count"] == 5
    assert sj["member_count"] == 6


def test_expenses():
    expenses = load("political_activity_expenses.json")
    validate("political_activity_expense.schema.json", expenses)
    # FY2025 grants were made to eleven factions; the official year
    # page states there were no individual grants.
    assert len(expenses) == 11
    assert all(r["fiscal_year"] == 2025 for r in expenses)
    assert all(r["recipient_type"] == "faction" for r in expenses)
    assert all(r["receipt_access"] == "online" for r in expenses)
    assert all(r["report_status"] == "published" for r in expenses)
    for record in expenses:
        assert (
            sum(i["amount_yen"] for i in record["breakdown"])
            == record["spent_yen"]
        ), record["recipient_name"]
        assert len(record["breakdown"]) == 10
    # Totals match the official execution summary (2026-07-16).
    assert sum(r["granted_yen"] for r in expenses) == 229600000
    assert sum(r["spent_yen"] for r in expenses) == 168265309
    assert sum(r["returned_yen"] for r in expenses) == 61390543
    by_name = {r["recipient_name"]: r for r in expenses}
    jimin = by_name["自由民主党"]
    assert jimin["granted_yen"] == 53200000
    assert jimin["spent_yen"] == 41303337
    assert jimin["returned_yen"] == 11899816
    # Sendai Ishin's report was filed by its then representative,
    # Councilor Nihei Satoko, on 2026-07-01.
    ishin = by_name["仙台維新"]
    assert ishin["granted_yen"] == 12600000
    assert ishin["spent_yen"] == 6249528
    assert ishin["returned_yen"] == 6353367


def test_inspection_trips():
    trips = load("inspection_trips.json")
    validate("inspection_trip.schema.json", trips)
    # No committee inspection reports are published in Sendai; the
    # absence itself is documented in the inspection evidence packet.
    assert trips == []
    packets = load("inspection_evidence_packets.json")
    validate("evidence_packet.schema.json", packets)
    assert len(packets) == 1
    statements = " ".join(
        c["statement"] for c in packets[0]["claims"])
    assert "公表は" in statements and "確認できなかった" in statements


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
    assert items["inspection_trip_reports"]["availability"] == "not_published"
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
    assert len(load("proposal_vote_evidence_packets.json")) == 47
    # Eleven expense packets plus one packet documenting that FY2025
    # had no individual grants.
    assert len(load("expense_evidence_packets.json")) == 12
    # The assembly packet records the 54 vs 55 seat reconciliation.
    claims = " ".join(
        c["statement"] for c in assembly_packets[0]["claims"])
    assert "仁平覚子" in claims
    assert "欠員" in claims
    # Bill 91's packet documents the two-row vote structure.
    packets = {p["subject_id"]: p
               for p in load("proposal_vote_evidence_packets.json")}
    proposals = {p["proposal_number"]: p for p in load("proposals.json")}
    bill91_packet = packets[proposals["第91号議案"]["id"]]
    fields = {c["field"] for c in bill91_packet["claims"]}
    assert "vote_structure" in fields
