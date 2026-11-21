"""Cluster 7 stage 4: Chiba City assembly registration checks.

Pins the counts and cross-checks for the Chiba City Council data taken
from the 3rd regular session of Reiwa 8 (September-October 2026), the
FY2025 political activity expense reports, and the inspection trips of
the current term published on the committee pages.
"""

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "reviewed" / "chiba-city" / "assembly"
CATALOG = ROOT / "data" / "catalog" / "chiba_city_assembly_sources.json"
ASM = "jp-local-121002-assembly-2023"
SESSION = f"{ASM}-session-2026-09"
INDEPENDENTS = {"黒澤和泉", "大平真弘", "蛭田浩文", "櫻井崇"}


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
    assert all(entry["municipality_key"] == "chiba-city" for entry in records)
    assert len(records) == 116


def test_assembly_record():
    records = load("assembly_records.json")
    validate("assembly.schema.json", records)
    assert len(records) == 1
    record = records[0]
    assert record["id"] == ASM
    assert record["municipality_id"] == "jp-local-121002"
    assert record["seat_count"] == 50
    assert record["term_start"] == "2023-05-01"
    assert record["term_end"] == "2027-04-30"
    # Faction composition as of 2026-04-01 (note on the FY2025
    # political activity expense page), matching the vote tables.
    assert sum(f["member_count"] for f in record["factions"]) == 50
    by_name = {f["name"]: f["member_count"] for f in record["factions"]}
    assert by_name == {
        "自由民主党": 17,
        "立憲民主・無所属": 11,
        "公明党": 8,
        "日本共産党": 7,
        "日本維新の会ちば": 3,
        "無所属": 4,
    }


def test_session():
    sessions = load("sessions.json")
    validate("session.schema.json", sessions)
    assert len(sessions) == 1
    session = sessions[0]
    assert session["id"] == SESSION
    assert session["name"] == "令和8年第3回定例会"
    assert session["start_date"] == "2026-09-07"
    assert session["end_date"] == "2026-10-05"


def test_proposals():
    proposals = load("proposals.json")
    validate("proposal.schema.json", proposals)
    assert len(proposals) == 57
    kinds = {}
    for p in proposals:
        kinds[p["kind"]] = kinds.get(p["kind"], 0) + 1
    assert kinds == {
        "budget": 15,
        "settlement": 18,
        "ordinance": 2,
        "personnel": 6,
        "other": 5,
        "resolution": 6,
        "petition": 5,
    }
    assert sum(1 for p in proposals if p["submitted_by"] == "executive") == 46
    assert sum(1 for p in proposals if p["submitted_by"] == "committee") == 3
    assert sum(1 for p in proposals if p["submitted_by"] == "member") == 3
    assert sum(1 for p in proposals if p["submitted_by"] == "resident_petition") == 5
    assert sum(1 for p in proposals if p["outcome"] == "approved") == 53
    assert sum(1 for p in proposals if p["outcome"] == "rejected") == 4
    by_number = {p["proposal_number"]: p for p in proposals}
    # Initial bills were submitted on the opening day; the submission
    # dates of the additional bills are not printed anywhere, so they
    # stay null rather than being guessed.
    assert by_number["議案第110号"]["submitted_at"] == "2026-09-07"
    assert by_number["議案第140号"]["submitted_at"] == "2026-09-07"
    assert by_number["議案第141号"]["submitted_at"] is None
    assert by_number["議案第155号"]["submitted_at"] is None
    assert by_number["議案第155号"]["decided_at"] == "2026-10-05"
    # Petitions carry their acceptance dates and were all rejected.
    assert by_number["請願第3号"]["submitted_at"] == "2026-08-28"
    assert by_number["請願第4号"]["submitted_at"] == "2026-08-31"
    for number in ("請願第3号", "請願第4号", "請願第5号"):
        assert by_number[number]["outcome"] == "rejected"
        assert by_number[number]["decided_at"] == "2026-09-17"
    # Appeals were concluded in committee on 2026-09-11.
    assert by_number["陳情第3号"]["outcome"] == "rejected"
    assert by_number["陳情第4号"]["outcome"] == "approved"
    assert by_number["陳情第3号"]["decided_at"] == "2026-09-11"
    assert by_number["陳情第4号"]["decided_at"] == "2026-09-11"


def test_votes():
    votes = load("votes.json")
    validate("vote.schema.json", votes)
    proposals = {p["id"]: p for p in load("proposals.json")}
    # Every proposal except the two committee-reviewed appeals has a
    # plenary vote record.
    assert len(votes) == 55
    voted = {v["proposal_id"] for v in votes}
    unvoted = {p["proposal_number"] for p in proposals.values() if p["id"] not in voted}
    assert unvoted == {"陳情第3号", "陳情第4号"}
    for vote in votes:
        assert vote["member_vote_availability"] == "published"
        assert vote["method"] == "unknown"
        assert vote["totals"] is None
        assert proposals[vote["proposal_id"]]["decided_at"] == vote["vote_date"]
        assert proposals[vote["proposal_id"]]["outcome"] == vote["outcome"]
    member_votes = [mv for v in votes for mv in v["member_votes"]]
    assert len(member_votes) == 220
    assert {mv["member_name"] for mv in member_votes} == INDEPENDENTS


def test_divided_votes():
    proposals = {p["proposal_number"]: p for p in load("proposals.json")}
    votes = {v["proposal_id"]: v for v in load("votes.json")}
    faction_votes = load("faction_votes.json")

    def positions(number):
        vote = votes[proposals[number]["id"]]
        result = {
            fv["faction_name"]: fv["position"]
            for fv in faction_votes
            if fv["vote_id"] == vote["id"]
        }
        result.update({mv["member_name"]: mv["position"] for mv in vote["member_votes"]})
        return result

    # Settlement bill 123: the Communist Party and one independent
    # opposed; everyone else supported.
    pos = positions("議案第123号")
    assert pos["日本共産党"] == "against"
    assert pos["黒澤和泉"] == "against"
    assert pos["自由民主党"] == "for"
    assert pos["櫻井崇"] == "for"
    # Member bill 10 (opinion on labour legislation): LDP and Ishin
    # opposed, the rest supported.
    pos = positions("発議第10号")
    assert pos["自由民主党"] == "against"
    assert pos["日本維新の会ちば"] == "against"
    assert pos["立憲民主・無所属"] == "for"
    assert pos["公明党"] == "for"
    # Petition 3: only the Communist Party and two independents
    # supported adoption; the petition was rejected.
    pos = positions("請願第3号")
    assert pos["日本共産党"] == "for"
    assert pos["櫻井崇"] == "for"
    assert pos["大平真弘"] == "for"
    assert pos["自由民主党"] == "against"
    assert proposals["請願第3号"]["outcome"] == "rejected"


def test_faction_votes():
    faction_votes = load("faction_votes.json")
    validate("faction_vote.schema.json", faction_votes)
    assert len(faction_votes) == 275
    counts = {"自由民主党": 17, "立憲民主・無所属": 11, "公明党": 8,
              "日本共産党": 7, "日本維新の会ちば": 3}
    for fv in faction_votes:
        assert fv["for_count"] is None
        assert fv["against_count"] is None
        assert fv["member_count"] == counts[fv["faction_name"]]


def test_expenses():
    expenses = load("political_activity_expenses.json")
    validate("political_activity_expense.schema.json", expenses)
    assert len(expenses) == 48
    assert all(r["fiscal_year"] == 2025 for r in expenses)
    assert sum(1 for r in expenses if r["recipient_type"] == "faction") == 5
    assert sum(1 for r in expenses if r["recipient_type"] == "member") == 43
    assert all(r["receipt_access"] == "in_person_only" for r in expenses)
    assert all(r["report_status"] == "published" for r in expenses)
    # In eight member reports, some category amounts are blacked out
    # in the published image; those categories are registered as null
    # and documented in the evidence packets. Every other report's
    # categories sum exactly to the printed expense total.
    redacted = {
        "石井茂隆": {"人件費", "事務・事務所費"},
        "石橋毅": {"人件費", "事務・事務所費"},
        "植草毅": {"人件費", "事務・事務所費"},
        "小松﨑文嘉": {"人件費", "事務・事務所費"},
        "須藤博文": {"事務・事務所費"},
        "麻生紀雄": {"人件費", "事務・事務所費"},
        "三井美和香": {"人件費"},
        "櫻井崇": {"事務・事務所費"},
    }
    for record in expenses:
        nulls = {i["category"] for i in record["breakdown"] if i["amount_yen"] is None}
        expected = redacted.get(record["recipient_name"], set())
        assert nulls == expected, record["recipient_name"]
        visible = sum(i["amount_yen"] for i in record["breakdown"] if i["amount_yen"] is not None)
        if expected:
            assert visible < record["spent_yen"]
        else:
            assert visible == record["spent_yen"], record["recipient_name"]
    by_name = {r["recipient_name"]: r for r in expenses}
    jimin = by_name["自由民主党千葉市議会議員団"]
    assert jimin["granted_yen"] == 4080000
    assert jimin["spent_yen"] == 4152517
    assert jimin["returned_yen"] == 0
    # The Communist Party receives the full amount at faction level,
    # so it has no member-level reports.
    assert "日本共産党千葉市議会議員団" in by_name
    assert by_name["日本共産党千葉市議会議員団"]["recipient_type"] == "faction"


def test_inspection_trips():
    trips = load("inspection_trips.json")
    validate("inspection_trip.schema.json", trips)
    assert len(trips) == 26
    assert all(t["trip_type"] == "domestic" for t in trips)
    assert all(t["cost_status"] == "not_published" for t in trips)
    assert all(t["report_status"] == "published" for t in trips)
    for trip in trips:
        assert trip["participant_count"] == len(trip["participants"])
        assert trip["participant_count"] >= 5
        assert all(p["participant_type"] == "elected_member" for p in trip["participants"])
    committees = {}
    for trip in trips:
        name = trip["title"].split(" 行政視察")[0]
        committees[name] = committees.get(name, 0) + 1
    assert committees == {
        "総務委員会": 4,
        "保健消防委員会": 9,
        "環境経済委員会": 3,
        "教育未来委員会": 4,
        "都市建設委員会": 3,
        "防災・減災対策調査特別委員会": 1,
        "大都市制度調査特別委員会": 2,
    }
    # The Mihama health centre trip: the committee page prints
    # 2024-10-18 (a Friday) as "Monday"; the report PDF's
    # 2024-11-18 is registered instead.
    mihama = next(t for t in trips if "美浜保健福祉センター" in t["purpose"])
    assert mihama["start_date"] == "2024-11-18"
    # The Yokohama trip was held online and had nine participants.
    online = next(t for t in trips if t["start_date"] == "2024-11-15")
    assert online["destinations"] == ["横浜市"]
    assert online["participant_count"] == 9


def test_disclosure_profile():
    profiles = load("disclosure_profiles.json")
    validate("disclosure_profile.schema.json", profiles)
    assert len(profiles) == 1
    items = {item["item"]: item for item in profiles[0]["items"]}
    assert len(items) == 12
    assert items["faction_votes"]["availability"] == "published"
    assert items["member_votes"]["availability"] == "published"
    # Receipts are not published online; they can only be inspected
    # at the assembly office.
    assert items["political_activity_expense_receipts"]["availability"] == "restricted"
    assert items["petition_results"]["availability"] == "published"


def test_evidence_packets():
    validate("evidence_packet.schema.json", load("assembly_evidence_packets.json"))
    validate("evidence_packet.schema.json", load("proposal_vote_evidence_packets.json"))
    validate("evidence_packet.schema.json", load("expense_evidence_packets.json"))
    validate("evidence_packet.schema.json", load("inspection_evidence_packets.json"))
    assembly_packets = load("assembly_evidence_packets.json")
    assert len(assembly_packets) == 1
    assert len(assembly_packets[0]["open_questions"]) == 3
    assert len(load("proposal_vote_evidence_packets.json")) == 57
    assert len(load("expense_evidence_packets.json")) == 48
    assert len(load("inspection_evidence_packets.json")) == 26
    # Every expense packet for a redacted report documents the
    # blacked-out categories.
    expenses = {r["id"]: r for r in load("political_activity_expenses.json")}
    packets = {p["subject_id"]: p for p in load("expense_evidence_packets.json")}
    for record in expenses.values():
        if any(i["amount_yen"] is None for i in record["breakdown"]):
            statements = " ".join(c["statement"] for c in packets[record["id"]]["claims"])
            assert "黒塗り" in statements
