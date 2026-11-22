"""Cluster 11 stage 4: Hiroshima City assembly registration checks.

Pins the counts and cross-checks for the Hiroshima City Council data
taken from the September 2026 regular session (2026-09-04 to
2026-09-25), the October 2026 extraordinary session that certified
the FY2025 settlements (2026-10-26), and the FY2025 political
activity expense reports of the thirteen factions.
"""

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "reviewed" / "hiroshima-city" / "assembly"
CATALOG = ROOT / "data" / "catalog" / "hiroshima_city_assembly_sources.json"
ASM = "jp-local-341002-assembly-2023"
SESSION_SEP = f"{ASM}-session-2026-09"
SESSION_OCT = f"{ASM}-session-2026-10-extra"
FACTION_COUNTS = {
    "自由民主党・市民クラブ": 14,
    "公明党": 8,
    "市民連合・市民の声": 7,
    "日本共産党": 5,
    "ひろしま清風会": 4,
    "広島維新の会": 3,
    "新政クラブ": 3,
    "無党派クラブ": 2,
    "至誠会": 1,
    "清流クラブ": 1,
    "鈴蘭会": 1,
    "新風クラブ": 1,
    "広島成長フォーラム": 1,
}
# Deposit interest printed in each FY2025 expense report (the balance
# returned is income including interest minus spending).
INTEREST = {
    "自由民主党・市民クラブ": 18834,
    "市民連合・市民の声": 15123,
    "公明党": 20335,
    "日本共産党": 4297,
    "ひろしま清風会": 3806,
    "広島維新の会": 2372,
    "新政クラブ": 3938,
    "無党派クラブ": 3757,
    "至誠会": 0,
    "清流クラブ": 4134,
    "鈴蘭会": 4242,
    "広島成長フォーラム": 0,
    "新風クラブ": 570,
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
        entry["municipality_key"] == "hiroshima-city" for entry in records
    )
    assert len(records) == 23


def test_assembly_record():
    records = load("assembly_records.json")
    validate("assembly.schema.json", records)
    assert len(records) == 1
    record = records[0]
    assert record["id"] == ASM
    assert record["municipality_id"] == "jp-local-341002"
    assert record["seat_count"] == 54
    # Term end 2027-05-01 is printed in the prefectural election
    # commission's term list; the term runs four years from 2023-05-02.
    assert record["term_start"] == "2023-05-02"
    assert record["term_end"] == "2027-05-01"
    # Roster printed with the September 2026 vote table: 51 sitting
    # members in 13 factions (three seats vacant).
    assert sum(f["member_count"] for f in record["factions"]) == 51
    by_name = {f["name"]: f["member_count"] for f in record["factions"]}
    assert by_name == FACTION_COUNTS
    assert len(record["committees"]) == 11


def test_sessions():
    sessions = load("sessions.json")
    validate("session.schema.json", sessions)
    assert len(sessions) == 2
    by_id = {s["id"]: s for s in sessions}
    sep = by_id[SESSION_SEP]
    assert sep["name"] == "令和8年第4回定例会"
    assert sep["session_type"] == "regular"
    assert sep["start_date"] == "2026-09-04"
    assert sep["end_date"] == "2026-09-25"
    october = by_id[SESSION_OCT]
    assert october["name"] == "令和8年第5回臨時会"
    assert october["session_type"] == "extraordinary"
    assert october["start_date"] == "2026-10-26"
    assert october["end_date"] == "2026-10-26"


def test_proposals():
    proposals = load("proposals.json")
    validate("proposal.schema.json", proposals)
    assert len(proposals) == 53
    kinds = {}
    for p in proposals:
        kinds[p["kind"]] = kinds.get(p["kind"], 0) + 1
    assert kinds == {
        "budget": 1,
        "ordinance": 14,
        "other": 11,
        "personnel": 3,
        "settlement": 24,
    }
    assert sum(1 for p in proposals if p["submitted_by"] == "executive") == 50
    assert sum(1 for p in proposals if p["submitted_by"] == "member") == 3
    # Individual submission dates are not published; nothing is
    # reconstructed.
    assert all(p["submitted_at"] is None for p in proposals)
    assert sum(1 for p in proposals if p["outcome"] == "approved") == 52
    assert sum(1 for p in proposals if p["outcome"] == "rejected") == 1
    by_number = {}
    for p in proposals:
        by_number.setdefault(p["proposal_number"], []).append(p)
    sep = [p for p in proposals if p["session_id"] == SESSION_SEP]
    october = [p for p in proposals if p["session_id"] == SESSION_OCT]
    assert len(sep) == 27
    assert len(october) == 26
    assert all(p["decided_at"] == "2026-09-25" for p in sep)
    assert all(p["decided_at"] == "2026-10-26" for p in october)
    # All 24 FY2025 settlements were certified at the extraordinary
    # session.
    settlements = [p for p in proposals if p["kind"] == "settlement"]
    assert len(settlements) == 24
    assert all(p["outcome"] == "approved" for p in settlements)
    for n in range(1, 22):
        assert by_number[f"第{n}号"][0]["kind"] == "settlement"
    # The three enterprise settlements carry no printed number.
    unnumbered = by_number["決算（番号の公表なし）"]
    assert len(unnumbered) == 3
    assert {p["title"] for p in unnumbered} == {
        "令和7年度広島市水道事業決算",
        "令和7年度広島市下水道事業決算",
        "令和7年度広島市安芸市民病院事業決算",
    }
    # The two council-size amendment bills share one printed title;
    # no. 12 (three seats fewer) was rejected, no. 13 (one seat moved
    # between districts) was approved.
    assert by_number["議員提出議案第12号"][0]["outcome"] == "rejected"
    assert by_number["議員提出議案第13号"][0]["outcome"] == "approved"
    assert by_number["諮問第7号"][0]["kind"] == "personnel"


def test_votes():
    votes = load("votes.json")
    validate("vote.schema.json", votes)
    proposals = {p["id"]: p for p in load("proposals.json")}
    assert len(votes) == 53
    per_proposal = {}
    for v in votes:
        per_proposal.setdefault(v["proposal_id"], []).append(v)
    assert set(per_proposal) == set(proposals)
    assert all(len(vs) == 1 for vs in per_proposal.values())
    for vote in votes:
        # The city calls the table the factions' "positions"
        # (sanpi taido); whether it is a post-vote record could not
        # be confirmed against the minutes, so the method stays
        # unknown and is not asserted.
        assert vote["method"] == "unknown"
        assert vote["totals"] is None
        assert vote["member_vote_availability"] == "not_published"
        assert vote["member_votes"] == []
        prop = proposals[vote["proposal_id"]]
        assert prop["decided_at"] == vote["vote_date"]
        assert prop["outcome"] == vote["outcome"]


def test_faction_votes():
    faction_votes = load("faction_votes.json")
    validate("faction_vote.schema.json", faction_votes)
    votes = {v["id"]: v for v in load("votes.json")}
    assert len(faction_votes) == 53 * 13
    for fv in faction_votes:
        assert fv["member_count"] == FACTION_COUNTS[fv["faction_name"]]
        assert fv["for_count"] is None
        assert fv["against_count"] is None
    for vote in votes.values():
        count = sum(1 for fv in faction_votes if fv["vote_id"] == vote["id"])
        assert count == 13


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

    def member_totals(number):
        vote = votes[proposals[number]["id"]]
        totals = {"for": 0, "against": 0}
        for fv in faction_votes:
            if fv["vote_id"] == vote["id"]:
                totals[fv["position"]] += fv["member_count"]
        # The speaker (LDP Citizens' Club) does not vote.
        totals[positions(number)["自由民主党・市民クラブ"]] -= 1
        return totals

    # Member bill 12 (three seats fewer): for 19, against 31, rejected.
    pos = positions("議員提出議案第12号")
    assert pos["自由民主党・市民クラブ"] == "for"
    assert pos["ひろしま清風会"] == "for"
    assert pos["鈴蘭会"] == "for"
    assert pos["広島成長フォーラム"] == "for"
    assert sum(1 for p in pos.values() if p == "against") == 9
    assert member_totals("議員提出議案第12号") == {"for": 19, "against": 31}
    # Member bill 13 (one seat moved): for 29, against 21, approved.
    pos = positions("議員提出議案第13号")
    assert pos["自由民主党・市民クラブ"] == "against"
    assert pos["市民連合・市民の声"] == "against"
    assert pos["広島成長フォーラム"] == "against"
    assert sum(1 for p in pos.values() if p == "for") == 10
    assert member_totals("議員提出議案第13号") == {"for": 29, "against": 21}
    # Settlements 1, 8, 9, 10, 11 and 15: only the JCP opposed, as
    # printed in the grouped rows of the October vote table.
    for n in (1, 8, 9, 10, 11, 15):
        pos = positions(f"第{n}号")
        assert pos["日本共産党"] == "against"
        assert sum(1 for p in pos.values() if p == "for") == 12
    # The other settlements were unanimous by faction.
    for n in (2, 21):
        pos = positions(f"第{n}号")
        assert all(p == "for" for p in pos.values())


def test_expenses():
    expenses = load("political_activity_expenses.json")
    validate("political_activity_expense.schema.json", expenses)
    assert len(expenses) == 13
    assert all(r["fiscal_year"] == 2025 for r in expenses)
    assert all(r["recipient_type"] == "faction" for r in expenses)
    assert all(r["receipt_access"] == "online" for r in expenses)
    assert all(r["report_status"] == "published" for r in expenses)
    for record in expenses:
        assert (
            sum(i["amount_yen"] for i in record["breakdown"])
            == record["spent_yen"]
        ), record["recipient_name"]
        # granted + interest - spent = returned, per the printed
        # report form (grants are the two grant lines combined).
        assert (
            record["granted_yen"] + INTEREST[record["recipient_name"]]
            - record["spent_yen"]
            == record["returned_yen"]
        ), record["recipient_name"]
    assert sum(r["granted_yen"] for r in expenses) == 223357062
    assert sum(r["spent_yen"] for r in expenses) == 197755743
    assert sum(r["returned_yen"] for r in expenses) == 25682727
    by_name = {r["recipient_name"]: r for r in expenses}
    jimin = by_name["自由民主党・市民クラブ"]
    assert jimin["granted_yen"] == 61362835
    assert jimin["spent_yen"] == 59368720
    assert jimin["returned_yen"] == 2012949
    # The Citizens' Union report carries a handwritten correction
    # dated 2026-11-12; the corrected figures are registered.
    rengo = by_name["市民連合・市民の声"]
    assert rengo["spent_yen"] == 26909738
    assert rengo["returned_yen"] == 5050481
    # Hiroshima Growth Forum was formed late in FY2025 and received
    # one month of grant.
    assert by_name["広島成長フォーラム"]["granted_yen"] == 300000


def test_inspection_trips():
    trips = load("inspection_trips.json")
    validate("inspection_trip.schema.json", trips)
    # No official list or report of committee inspection trips is
    # published; the absence itself is recorded in the evidence.
    assert trips == []
    packets = load("inspection_evidence_packets.json")
    assert len(packets) == 1
    assert packets[0]["subject_id"] == ASM


def test_disclosure_profile():
    profiles = load("disclosure_profiles.json")
    validate("disclosure_profile.schema.json", profiles)
    assert len(profiles) == 1
    items = {i["item"]: i for i in profiles[0]["items"]}
    assert items["member_votes"]["availability"] == "not_published"
    assert items["inspection_trip_reports"]["availability"] == "not_published"
    assert items["faction_votes"]["availability"] == "published"
    assert (
        items["political_activity_expense_reports"]["granularity"]
        == "faction"
    )


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
    assert len(packets) == 68
    # One vote packet per proposal.
    vote_packets = load("proposal_vote_evidence_packets.json")
    assert len(vote_packets) == 53
    assert all(p["subject_type"] == "proposal" for p in vote_packets)
    assert all(p["open_questions"] == [] for p in vote_packets)
    # The assembly packet keeps one open question: whether the
    # published faction table is a post-vote record, to be settled
    # once the September/October 2026 minutes are indexed.
    assembly_packets = load("assembly_evidence_packets.json")
    assert len(assembly_packets) == 1
    assert len(assembly_packets[0]["open_questions"]) == 1
    expense_packets = load("expense_evidence_packets.json")
    assert len(expense_packets) == 13
    assert all(p["open_questions"] == [] for p in expense_packets)


def test_web_registry_wiring():
    registry = (ROOT / "apps" / "web" / "lib" / "assemblyRegistry.ts").read_text(
        encoding="utf-8"
    )
    assert '"hiroshima-city"' in registry
    assert "hiroshimaCityAssembly" in registry
    assert "hiroshima_city_assembly_sources.json" in registry
