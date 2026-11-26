"""Issue #1052: Akita City assembly (cluster 18 stage 4) checks.

Pins the counts and cross-checks for the Akita City Council data
taken from the August 2026 regular session (令和8年8月定例会,
2026-08-31 to 2026-10-07), whose individual vote table was
cross-checked against the official minutes system (electronic
button votes for divided items, no-objection decisions for
unanimous ones), and the FY2025 political activity expense reports
published per faction on 2026-07-01.
"""

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "reviewed" / "akita-city" / "assembly"
CATALOG = ROOT / "data" / "catalog" / "akita_city_assembly_sources.json"
ASM = "jp-local-052019-assembly-2023"
SESSION = f"{ASM}-session-2026-08"
CATEGORIES = ["研究研修費", "調査活動費", "資料作成費", "資料購入費",
              "広報費", "広聴費", "人件費", "事務所費", "事務費"]
FACTION_COUNTS = {
    "秋水会": 8,
    "自民党": 8,
    "フロンティア秋田": 7,
    "公明党秋田市議会": 4,
    "そうせいと維新": 4,
    "日本共産党秋田市議会議員団": 2,
    "市民クラブ": 2,
    "市民のみかた": 1,
}
# Printed deposit interest per faction in the FY2025 expense
# summary; the printed remainder includes this interest, so
# granted - spent does not equal the remainder on its own.
INTEREST = {
    "秋水会": 4477,
    "フロンティア秋田": 432,
    "自民党": 7128,
    "公明党秋田市議会": 277,
    "そうせいと維新": 2222,
    "日本共産党秋田市議会議員団": 1300,
    "市民クラブ": 1262,
    "市民のみかた": 335,
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
        entry["municipality_key"] == "akita-city" for entry in records
    )
    # 15 general sources plus one record per faction expense report.
    assert len(records) == 23


def test_assembly_record():
    records = load("assembly_records.json")
    validate("assembly.schema.json", records)
    assert len(records) == 1
    record = records[0]
    assert record["id"] == ASM
    assert record["municipality_id"] == "jp-local-052019"
    assert record["name"] == "秋田市議会"
    assert record["seat_count"] == 36
    # Term end 2027-05-01 is printed in the prefectural election
    # commission's term list; the four-year term starts 2023-05-02.
    assert record["term_start"] == "2023-05-02"
    assert record["term_end"] == "2027-05-01"
    by_name = {f["name"]: f["member_count"] for f in record["factions"]}
    assert by_name == FACTION_COUNTS
    assert sum(by_name.values()) == 36
    assert len(record["committees"]) == 6


def test_sessions():
    sessions = load("sessions.json")
    validate("session.schema.json", sessions)
    assert len(sessions) == 1
    session = sessions[0]
    assert session["id"] == SESSION
    assert session["name"] == "令和8年8月定例会"
    assert session["session_type"] == "regular"
    assert session["start_date"] == "2026-08-31"
    assert session["end_date"] == "2026-10-07"


def test_proposals():
    proposals = load("proposals.json")
    validate("proposal.schema.json", proposals)
    assert len(proposals) == 27
    kinds = {}
    for p in proposals:
        kinds[p["kind"]] = kinds.get(p["kind"], 0) + 1
    assert kinds == {
        "budget": 4,
        "ordinance": 6,
        "other": 4,
        "personnel": 3,
        "petition": 4,
        "resolution": 2,
        "settlement": 4,
    }
    assert sum(1 for p in proposals if p["submitted_by"] == "executive") == 20
    assert sum(1 for p in proposals if p["submitted_by"] == "member") == 3
    assert (
        sum(1 for p in proposals if p["submitted_by"] == "resident_petition")
        == 4
    )
    assert all(p["session_id"] == SESSION for p in proposals)
    assert sum(1 for p in proposals if p["outcome"] == "approved") == 25
    assert sum(1 for p in proposals if p["outcome"] == "rejected") == 2
    # All four FY2025 settlements were certified; none was rejected.
    settlements = [p for p in proposals if p["kind"] == "settlement"]
    assert len(settlements) == 4
    assert all(p["outcome"] == "approved" for p in settlements)
    by_number = {p["proposal_number"]: p for p in proposals}
    # The three public-enterprise settlements were certified
    # unanimously on 2026-09-28; the general/special-account
    # settlement (議案第120号) was certified on 2026-10-07, as the
    # schedule, the 10/7 vote table and the 10/7 minutes all show.
    for n in ("議案第116号", "議案第117号", "議案第118号"):
        assert by_number[n]["decided_at"] == "2026-09-28"
    assert by_number["議案第120号"]["decided_at"] == "2026-10-07"
    assert by_number["議案第120号"]["submitted_at"] == "2026-09-28"
    # 議案第119号 was additionally submitted on 2026-09-09; other
    # individual submission dates are not published per item.
    assert by_number["議案第119号"]["submitted_at"] == "2026-09-09"
    others = [p for n, p in by_number.items()
              if n not in ("議案第119号", "議案第120号")]
    assert all(p["submitted_at"] is None for p in others)
    # Petitions are decided in Akita City: two adopted, two rejected.
    petitions = {p["proposal_number"]: p
                 for p in proposals if p["kind"] == "petition"}
    assert petitions["陳情第68号"]["outcome"] == "approved"
    assert petitions["陳情第69号"]["outcome"] == "rejected"
    assert petitions["陳情第70号"]["outcome"] == "rejected"
    assert petitions["陳情第72号"]["outcome"] == "approved"


def test_votes():
    votes = load("votes.json")
    validate("vote.schema.json", votes)
    proposals = {p["id"]: p for p in load("proposals.json")}
    # 27 proposals; 陳情第69号 has two item-level votes.
    assert len(votes) == 28
    per_proposal = {}
    for v in votes:
        per_proposal.setdefault(v["proposal_id"], []).append(v)
    assert set(per_proposal) == set(proposals)
    for pid, vs in per_proposal.items():
        number = proposals[pid]["proposal_number"]
        if number == "陳情第69号":
            assert len(vs) == 2
            assert {v["item_scope"] for v in vs} == {"第1項", "第2項"}
        else:
            assert len(vs) == 1
            assert vs[0]["item_scope"] is None
    # The minutes cross-check splits the votes into 12 electronic
    # button votes (recorded) and 16 no-objection decisions
    # (unanimous).
    methods = {}
    for v in votes:
        methods[v["method"]] = methods.get(v["method"], 0) + 1
    assert methods == {"recorded": 12, "unanimous": 16}
    for vote in votes:
        assert vote["member_vote_availability"] == "published"
        assert len(vote["member_votes"]) == 36
        counts = {"for": 0, "against": 0, "abstained": 0, "absent": 0}
        excused = 0
        for m in vote["member_votes"]:
            if m["position"] == "excused":
                excused += 1
            else:
                counts[m["position"]] += 1
        assert vote["totals"] == counts
        # Only the chair (川口雅丈) does not vote.
        assert excused == 1
        chair = [m for m in vote["member_votes"]
                 if m["position"] == "excused"]
        assert chair[0]["member_name"] == "川口雅丈"
        prop = proposals[vote["proposal_id"]]
        assert prop["decided_at"] == vote["vote_date"]
        assert prop["outcome"] == vote["outcome"]
        if vote["method"] == "recorded":
            assert counts["against"] > 0
        else:
            assert counts["against"] == 0 and counts["absent"] == 0


def test_divided_votes():
    proposals = {p["proposal_number"]: p for p in load("proposals.json")}
    votes = {}
    for v in load("votes.json"):
        votes.setdefault(v["proposal_id"], []).append(v)

    def vote_of(number):
        return votes[proposals[number]["id"]][0]

    def names(number, position):
        return {
            m["member_name"] for m in vote_of(number)["member_votes"]
            if m["position"] == position
        }

    # 議案第105号 (nursery ordinance): opposed by the two JCP
    # members and the single 市民のみかた member.
    assert vote_of("議案第105号")["totals"] == {
        "for": 32, "against": 3, "abstained": 0, "absent": 0,
    }
    assert names("議案第105号", "against") == {"奈良順子", "佐藤純子", "佐藤哲治"}
    # 議案第120号 (FY2025 settlement): opposed by the JCP pair,
    # with 後藤良 absent.
    assert vote_of("議案第120号")["totals"] == {
        "for": 32, "against": 2, "abstained": 0, "absent": 1,
    }
    assert names("議案第120号", "against") == {"奈良順子", "佐藤純子"}
    assert names("議案第120号", "absent") == {"後藤良"}
    # 陳情第69号: only three members supported adoption, in both
    # item votes.
    for v in votes[proposals["陳情第69号"]["id"]]:
        assert v["totals"] == {
            "for": 3, "against": 32, "abstained": 0, "absent": 0,
        }
        assert {
            m["member_name"] for m in v["member_votes"]
            if m["position"] == "for"
        } == {"奈良順子", "佐藤純子", "佐藤哲治"}
    # 陳情第70号 was rejected 9-26; 陳情第72号 adopted 25-10.
    assert vote_of("陳情第70号")["totals"]["for"] == 9
    assert vote_of("陳情第72号")["totals"] == {
        "for": 25, "against": 10, "abstained": 0, "absent": 0,
    }


def test_faction_votes():
    faction_votes = load("faction_votes.json")
    validate("faction_vote.schema.json", faction_votes)
    votes = {v["id"]: v for v in load("votes.json")}
    assert len(faction_votes) == 28 * 8
    by_vote = {}
    for fv in faction_votes:
        by_vote.setdefault(fv["vote_id"], []).append(fv)
    assert set(by_vote) == set(votes)
    for vote in votes.values():
        groups = by_vote[vote["id"]]
        assert {g["faction_name"] for g in groups} == set(FACTION_COUNTS)
        assert sum(g["member_count"] for g in groups) == 36
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
    # The chair belongs to 秋水会: its member_count is 8 while at
    # most 7 of its members can appear in the for/against counts.
    for groups in by_vote.values():
        shusui = [g for g in groups if g["faction_name"] == "秋水会"][0]
        assert shusui["member_count"] == 8
        assert shusui["for_count"] + shusui["against_count"] <= 7


def test_expenses():
    expenses = load("political_activity_expenses.json")
    validate("political_activity_expense.schema.json", expenses)
    assert len(expenses) == 8
    assert all(r["fiscal_year"] == 2025 for r in expenses)
    assert all(r["recipient_type"] == "faction" for r in expenses)
    assert all(r["receipt_access"] == "online" for r in expenses)
    assert all(r["report_status"] == "published" for r in expenses)
    for record in expenses:
        assert [i["category"] for i in record["breakdown"]] == CATEGORIES
        assert (
            sum(i["amount_yen"] for i in record["breakdown"])
            == record["spent_yen"]
        ), record["recipient_name"]
        # The printed remainder is income (grant + deposit
        # interest) minus spending, as printed.
        assert (
            record["granted_yen"] + INTEREST[record["recipient_name"]]
            - record["spent_yen"] == record["returned_yen"]
        ), record["recipient_name"]
    # Printed totals across the eight factions.
    assert sum(r["granted_yen"] for r in expenses) == 43200000
    assert sum(r["spent_yen"] for r in expenses) == 34321289
    assert sum(r["returned_yen"] for r in expenses) == 8896144
    by_name = {r["recipient_name"]: r for r in expenses}
    # 市民のみかた was granted ten monthly instalments; the reason
    # is not stated in the published sources.
    assert by_name["市民のみかた"]["granted_yen"] == 1000000
    # フロンティア秋田's grant reflects a membership change (8 to 7).
    assert by_name["フロンティア秋田"]["granted_yen"] == 8600000


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
    assert items["faction_votes"]["availability"] == "published"
    assert (
        items["political_activity_expense_reports"]["granularity"]
        == "faction"
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
    assert len(packets) == 37
    vote_packets = load("proposal_vote_evidence_packets.json")
    assert len(vote_packets) == 27
    assert all(p["subject_type"] == "proposal" for p in vote_packets)
    assert all(p["open_questions"] == [] for p in vote_packets)
    # The assembly packet keeps the open questions the primary
    # sources could not settle (term start in print, the missing
    # petition number 71, the 議案第120号 date discrepancy in the
    # stage-0 inventory, the 市民のみかた grant reason, and the
    # unregistered procedural vote on continued committee review).
    assembly_packets = load("assembly_evidence_packets.json")
    assert len(assembly_packets) == 1
    assert len(assembly_packets[0]["open_questions"]) == 5
    expense_packets = load("expense_evidence_packets.json")
    assert len(expense_packets) == 8
    assert all(p["open_questions"] == [] for p in expense_packets)
