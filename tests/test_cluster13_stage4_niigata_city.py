"""Cluster 13 stage 4: Niigata City assembly registration checks.

Pins the counts and cross-checks for the Niigata City Council data
taken from the September 2026 regular session (令和8年9月定例会,
2026-09-04 to 2026-09-29), the FY2025 political activity expense
reports (eight faction reports and 41 member reports), and the
FY2025 committee inspection trips (nine domestic committee reports
and two overseas delegation reports).
"""

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "reviewed" / "niigata-city" / "assembly"
CATALOG = ROOT / "data" / "catalog" / "niigata_city_assembly_sources.json"
ASM = "jp-local-151009-assembly-2023"
SESSION = f"{ASM}-session-2026-09"
FACTION_COUNTS = {
    "翔政会": 21,
    "日本共産党新潟市議会議員団": 6,
    "新風にいがた": 5,
    "新潟市公明党": 4,
    "ともに躍動する新潟": 4,
    "無所属の会": 4,
    "市民ネットにいがた": 3,
    "会派に属さない議員": 1,
}
CATEGORIES = ["調査研究費", "研修費", "広報費", "広聴費", "要請・陳情活動費",
              "会議費", "資料作成費", "資料購入費", "人件費", "事務所費"]


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
        entry["municipality_key"] == "niigata-city" for entry in records
    )
    # 19 general sources, five member-bill documents, 49 expense
    # report documents and 11 inspection report documents (the
    # inspection index page is counted among the general sources).
    assert len(records) == 79


def test_assembly_record():
    records = load("assembly_records.json")
    validate("assembly.schema.json", records)
    assert len(records) == 1
    record = records[0]
    assert record["id"] == ASM
    assert record["municipality_id"] == "jp-local-151009"
    assert record["name"] == "新潟市議会"
    assert record["seat_count"] == 50
    # Term end 2027-05-01 and the statutory seat count of 50 are
    # printed in the prefectural election commission's term list;
    # the four-year term starts 2023-05-02.
    assert record["term_start"] == "2023-05-02"
    assert record["term_end"] == "2027-05-01"
    by_name = {f["name"]: f["member_count"] for f in record["factions"]}
    assert by_name == FACTION_COUNTS
    # 48 sitting members at the September 2026 session: two Chuo
    # ward seats were vacant until the 2026-10-25 by-election.
    # The Shoseikai count of 21 includes the speaker; the results
    # table prints 20 with a note excluding the speaker.
    assert sum(by_name.values()) == 48
    assert len(record["committees"]) == 11


def test_sessions():
    sessions = load("sessions.json")
    validate("session.schema.json", sessions)
    assert len(sessions) == 1
    session = sessions[0]
    assert session["id"] == SESSION
    assert session["name"] == "令和8年9月定例会"
    assert session["session_type"] == "regular"
    assert session["start_date"] == "2026-09-04"
    assert session["end_date"] == "2026-09-29"


def test_proposals():
    proposals = load("proposals.json")
    validate("proposal.schema.json", proposals)
    assert len(proposals) == 38
    kinds = {}
    for p in proposals:
        kinds[p["kind"]] = kinds.get(p["kind"], 0) + 1
    assert kinds == {
        "budget": 4,
        "ordinance": 6,
        "other": 10,
        "personnel": 1,
        "petition": 10,
        "resolution": 5,
        "settlement": 2,
    }
    assert sum(1 for p in proposals if p["submitted_by"] == "executive") == 23
    assert sum(1 for p in proposals if p["submitted_by"] == "member") == 5
    assert (
        sum(1 for p in proposals if p["submitted_by"] == "resident_petition")
        == 10
    )
    assert all(p["session_id"] == SESSION for p in proposals)
    assert sum(1 for p in proposals if p["outcome"] == "approved") == 28
    assert sum(1 for p in proposals if p["outcome"] == "rejected") == 6
    assert sum(1 for p in proposals if p["outcome"] == "pending") == 3
    assert sum(1 for p in proposals if p["outcome"] == "not_assessable") == 1
    by_number = {p["proposal_number"]: p for p in proposals}
    # Mayor's bills 70-91 were submitted on 2026-09-04; bill 92
    # (the FY2025 general and special account settlements) was
    # submitted on 2026-09-15 and is still under continued review.
    assert by_number["議案第70号"]["submitted_at"] == "2026-09-04"
    assert by_number["議案第92号"]["submitted_at"] == "2026-09-15"
    assert by_number["議案第92号"]["outcome"] == "pending"
    assert by_number["議案第92号"]["decided_at"] is None
    # The enterprise account settlements (bill 91) were certified.
    assert by_number["議案第91号"]["kind"] == "settlement"
    assert by_number["議案第91号"]["outcome"] == "approved"
    assert by_number["議案第91号"]["decided_at"] == "2026-09-29"
    # The personnel bill 83 was submitted and agreed on the opening
    # day, together with member bill 48.
    assert by_number["議案第83号"]["kind"] == "personnel"
    assert by_number["議案第83号"]["decided_at"] == "2026-09-04"
    assert by_number["議員議案第48号"]["decided_at"] == "2026-09-04"
    # Member bill 49 (the ICC opinion paper) was the only member
    # bill rejected.
    resolutions = [p for p in proposals if p["kind"] == "resolution"]
    assert sum(1 for p in resolutions if p["outcome"] == "rejected") == 1
    assert by_number["議員議案第49号"]["outcome"] == "rejected"
    # Chenjo 151 was voted item by item with split results (items
    # 1-2 not adopted, item 3 adopted), so the proposal itself
    # carries no single outcome.
    chenjo151 = by_number["陳情第151号"]
    assert chenjo151["outcome"] == "not_assessable"
    assert chenjo151["decided_at"] == "2026-09-29"
    # Chenjo 121 and 127 are under continued review.
    for number in ("陳情第121号", "陳情第127号"):
        assert by_number[number]["outcome"] == "pending"
        assert by_number[number]["decided_at"] is None
    # Petitions and chenjo carry no submission date: the results
    # page does not print acceptance dates.
    for p in proposals:
        if p["submitted_by"] == "resident_petition":
            assert p["submitted_at"] is None


def test_votes():
    votes = load("votes.json")
    validate("vote.schema.json", votes)
    proposals = {p["id"]: p for p in load("proposals.json")}
    assert len(votes) == 50
    pending = {pid for pid, p in proposals.items() if p["outcome"] == "pending"}
    voted = {v["proposal_id"] for v in votes}
    # No vote records exist for the three items under continued
    # review (bill 92, chenjo 121 and 127).
    assert voted == set(proposals) - pending
    assert len(pending) == 3
    for vote in votes:
        # The results table prints each faction's for/against
        # explicitly, but does not establish whether it is a
        # recorded vote tally, so the method stays unknown. Member
        # level positions are not published.
        assert vote["method"] == "unknown"
        assert vote["totals"] is None
        assert vote["member_vote_availability"] == "not_published"
        assert vote["member_votes"] == []
        prop = proposals[vote["proposal_id"]]
        assert prop["decided_at"] == vote["vote_date"]
        if vote["item_scope"] is None:
            assert prop["outcome"] == vote["outcome"]
    # Item-level votes: petition 12 (3 items), chenjo 151 (3),
    # 153 (4), 154 (8) and 156 (2).
    item_votes = [v for v in votes if v["item_scope"] is not None]
    assert len(item_votes) == 20
    chenjo151 = [v for v in votes
                 if v["proposal_id"] == proposals[
                     next(k for k, p in proposals.items()
                          if p["proposal_number"] == "陳情第151号")]["id"]]
    assert [v["outcome"] for v in chenjo151] == [
        "rejected", "rejected", "approved",
    ]


def test_faction_votes():
    faction_votes = load("faction_votes.json")
    validate("faction_vote.schema.json", faction_votes)
    votes = {v["id"]: v for v in load("votes.json")}
    assert len(faction_votes) == 50 * 8
    for fv in faction_votes:
        assert fv["member_count"] == FACTION_COUNTS[fv["faction_name"]]
    for vote in votes.values():
        rows = [fv for fv in faction_votes if fv["vote_id"] == vote["id"]]
        assert len(rows) == 8
        assert {fv["faction_name"] for fv in rows} == set(FACTION_COUNTS)
    # Only one split faction position is printed in the whole
    # session: Tomoni Yakudo Niigata on item 2 of chenjo 151
    # (1 for, 3 against).
    splits = [fv for fv in faction_votes if fv["position"] == "split"]
    assert len(splits) == 1
    assert splits[0]["faction_name"] == "ともに躍動する新潟"
    assert splits[0]["for_count"] == 1
    assert splits[0]["against_count"] == 3
    others = [fv for fv in faction_votes if fv["position"] != "split"]
    assert all(fv["for_count"] is None for fv in others)
    assert all(fv["against_count"] is None for fv in others)


def test_divided_votes():
    proposals = {p["proposal_number"]: p for p in load("proposals.json")}
    votes = load("votes.json")
    faction_votes = load("faction_votes.json")

    def positions(number, item_index=None):
        pid = proposals[number]["id"]
        vs = [v for v in votes if v["proposal_id"] == pid]
        vote = vs[item_index] if item_index is not None else vs[0]
        return {
            fv["faction_name"]: fv["position"]
            for fv in faction_votes
            if fv["vote_id"] == vote["id"]
        }

    # Member bill 49 (ICC opinion paper): rejected, with the
    # Shoseikai and Shinpu Niigata against and the other six
    # columns in favour.
    pos = positions("議員議案第49号")
    assert pos["翔政会"] == "against"
    assert pos["新風にいがた"] == "against"
    assert sum(1 for p in pos.values() if p == "for") == 6
    # Chenjo 151 item 1: four columns in favour, four against.
    pos = positions("陳情第151号", 0)
    assert sum(1 for p in pos.values() if p == "for") == 4
    assert sum(1 for p in pos.values() if p == "against") == 4
    # Chenjo 151 item 3: adopted with only the Shoseikai against.
    pos = positions("陳情第151号", 2)
    assert pos["翔政会"] == "against"
    assert sum(1 for p in pos.values() if p == "for") == 7
    # Bill 91 (enterprise settlements): all factions in favour.
    assert all(p == "for" for p in positions("議案第91号").values())
    # Chenjo 150: rejected with all factions against.
    assert all(p == "against" for p in positions("陳情第150号").values())


def test_expenses():
    expenses = load("political_activity_expenses.json")
    validate("political_activity_expense.schema.json", expenses)
    assert len(expenses) == 49
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
    assert len(factions) == 8
    assert len(members) == 41
    # Totals over the 49 published reports.
    assert sum(r["granted_yen"] for r in expenses) == 89250000
    assert sum(r["spent_yen"] for r in expenses) == 64476371
    assert sum(r["returned_yen"] for r in expenses) == 24773629
    assert sum(r["granted_yen"] for r in factions) == 30810000
    assert sum(r["spent_yen"] for r in factions) == 27333082
    assert sum(r["returned_yen"] for r in factions) == 3476918
    assert sum(r["granted_yen"] for r in members) == 58440000
    assert sum(r["spent_yen"] for r in members) == 37143289
    assert sum(r["returned_yen"] for r in members) == 21296711
    by_name = {r["recipient_name"]: r for r in expenses}
    # The JCP and Shimin Net Niigata chose faction-only delivery
    # (150,000 yen per member per month) and have no member
    # reports; the JCP returned 1,657,405 yen and Shimin Net
    # spent its grant in full.
    assert by_name["日本共産党新潟市議会議員団"]["granted_yen"] == 10800000
    assert by_name["日本共産党新潟市議会議員団"]["returned_yen"] == 1657405
    assert by_name["市民ネットにいがた"]["granted_yen"] == 5400000
    assert by_name["市民ネットにいがた"]["returned_yen"] == 0
    # Partial-year reports: Uchiyama Ko lost his seat on
    # 2026-01-27 (ten months granted), Shida Tsuneyoshi died on
    # 2026-01-07 (nine months granted), and the Shin Shimin Club
    # faction report covers April 2025 to February 2026 (the
    # faction dissolved on 2026-02-17).
    assert by_name["内山航"]["granted_yen"] == 1200000
    assert by_name["志田常佳"]["granted_yen"] == 1080000
    assert by_name["新市民クラブ"]["granted_yen"] == 1290000
    # Every other member report is a full year at 120,000 yen
    # per month.
    full = [r for r in members
            if r["recipient_name"] not in ("内山航", "志田常佳")]
    assert len(full) == 39
    assert all(r["granted_yen"] == 1440000 for r in full)


def test_inspection_trips():
    trips = load("inspection_trips.json")
    validate("inspection_trip.schema.json", trips)
    assert len(trips) == 11
    assert sum(1 for t in trips if t["trip_type"] == "domestic") == 9
    assert sum(1 for t in trips if t["trip_type"] == "overseas") == 2
    for trip in trips:
        assert trip["participant_count"] == len(trip["participants"])
        assert trip["report_status"] == "published"
        # No trip report publishes cost figures.
        assert trip["cost_status"] == "not_published"
        assert trip["total_cost_yen"] is None
        assert trip["cost_per_person_yen"] is None
    by_slug = {t["id"].rsplit("-", 1)[-1]: t for t in trips}
    korea = by_slug["korea"]
    assert korea["start_date"] == "2025-10-15"
    assert korea["end_date"] == "2025-10-18"
    assert korea["participant_count"] == 7
    assert korea["participants"][0]["name"] == "小野清一郎"
    galveston = by_slug["galveston"]
    assert galveston["start_date"] == "2025-11-12"
    assert galveston["end_date"] == "2025-11-18"
    # Only the two council members of the city delegation are
    # registered as participants.
    assert galveston["participant_count"] == 2
    packets = load("inspection_evidence_packets.json")
    assert len(packets) == 11
    assert all(p["subject_type"] == "inspection_trip" for p in packets)


def test_disclosure_profile():
    profiles = load("disclosure_profiles.json")
    validate("disclosure_profile.schema.json", profiles)
    assert len(profiles) == 1
    assert profiles[0]["as_of"] == "2026-11-23"
    items = {i["item"]: i for i in profiles[0]["items"]}
    assert len(items) == 12
    assert items["faction_votes"]["availability"] == "published"
    assert items["faction_votes"]["granularity"] == "faction"
    assert items["member_votes"]["availability"] == "not_published"
    assert (
        items["political_activity_expense_reports"]["granularity"]
        == "member"
    )
    assert items["petition_results"]["availability"] == "published"
    assert items["session_broadcast"]["availability"] == "not_found"


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
    assert len(packets) == 99
    vote_packets = load("proposal_vote_evidence_packets.json")
    assert len(vote_packets) == 38
    assert all(p["subject_type"] == "proposal" for p in vote_packets)
    # The three items under continued review keep an open
    # question each; all other packets are closed.
    with_questions = [p for p in vote_packets if p["open_questions"]]
    assert len(with_questions) == 3
    assembly_packets = load("assembly_evidence_packets.json")
    assert len(assembly_packets) == 1
    assert assembly_packets[0]["open_questions"] == []
    expense_packets = load("expense_evidence_packets.json")
    assert len(expense_packets) == 49
    assert all(p["open_questions"] == [] for p in expense_packets)
