"""Cluster 15 stage 4: Kumamoto City assembly registration checks.

Pins the counts and cross-checks for the Kumamoto City Council data
taken from the 3rd regular session of 2026 (令和8年第3回定例会,
2026-08-31 to 2026-09-25), the FY2025 political activity expense
reports (45 member reports and 5 faction reports), and the FY2025
standing-committee inspection trips reported in the council
newsletter (市議会だより第58号).
"""

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "reviewed" / "kumamoto-city" / "assembly"
CATALOG = ROOT / "data" / "catalog" / "kumamoto_city_assembly_sources.json"
ASM = "jp-local-431001-assembly-2023"
SESSION = f"{ASM}-session-2026-08"
CATEGORIES = ["調査研究費", "研修費", "資料作成費", "資料購入費", "広報費",
              "広聴費", "会議費", "人件費", "事務所費", "事務通信費",
              "要請・陳情活動費"]
FACTION_COUNTS = {
    "自由民主党熊本市議団": 21,
    "公明党熊本市議団": 7,
    "市民連合": 6,
    "無所属議員": 3,
    "市民の会": 3,
    "創生熊本市議団": 2,
    "日本共産党熊本市議団": 2,
    "新風熊本市議団": 2,
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
        entry["municipality_key"] == "kumamoto-city" for entry in records
    )
    # 14 general sources plus one record per expense report.
    assert len(records) == 64


def test_assembly_record():
    records = load("assembly_records.json")
    validate("assembly.schema.json", records)
    assert len(records) == 1
    record = records[0]
    assert record["id"] == ASM
    assert record["municipality_id"] == "jp-local-431001"
    assert record["name"] == "熊本市議会"
    assert record["seat_count"] == 48
    # Term end 2027-04-30 is printed in the prefectural election
    # commission's term list (as of 2026-08-01); the four-year term
    # starts 2023-05-01.
    assert record["term_start"] == "2023-05-01"
    assert record["term_end"] == "2027-04-30"
    by_name = {f["name"]: f["member_count"] for f in record["factions"]}
    assert by_name == FACTION_COUNTS
    # 46 members sat in the session; two of the 48 seats were vacant.
    assert sum(by_name.values()) == 46
    assert len(record["committees"]) == 8


def test_sessions():
    sessions = load("sessions.json")
    validate("session.schema.json", sessions)
    assert len(sessions) == 1
    session = sessions[0]
    assert session["id"] == SESSION
    assert session["name"] == "令和8年第3回定例会"
    assert session["session_type"] == "regular"
    assert session["start_date"] == "2026-08-31"
    assert session["end_date"] == "2026-09-25"


def test_proposals():
    proposals = load("proposals.json")
    validate("proposal.schema.json", proposals)
    assert len(proposals) == 60
    kinds = {}
    for p in proposals:
        kinds[p["kind"]] = kinds.get(p["kind"], 0) + 1
    assert kinds == {
        "budget": 10,
        "ordinance": 7,
        "other": 24,
        "petition": 9,
        "resolution": 4,
        "settlement": 6,
    }
    assert sum(1 for p in proposals if p["submitted_by"] == "executive") == 47
    assert sum(1 for p in proposals if p["submitted_by"] == "member") == 4
    assert (
        sum(1 for p in proposals if p["submitted_by"] == "resident_petition")
        == 9
    )
    assert all(p["session_id"] == SESSION for p in proposals)
    assert sum(1 for p in proposals if p["outcome"] == "approved") == 50
    assert sum(1 for p in proposals if p["outcome"] == "rejected") == 1
    assert sum(1 for p in proposals if p["outcome"] == "not_assessable") == 9
    # All six FY2025 settlements (議第257号 to 議第262号) were
    # certified on 2026-09-25; none was rejected.
    settlements = [p for p in proposals if p["kind"] == "settlement"]
    assert len(settlements) == 6
    assert all(p["outcome"] == "approved" for p in settlements)
    assert all(p["decided_at"] == "2026-09-25" for p in settlements)
    by_number = {p["proposal_number"]: p for p in proposals}
    # The 14 road-certification bills are registered individually.
    for n in range(235, 249):
        assert by_number[f"議第{n}号"]["kind"] == "other"
        assert by_number[f"議第{n}号"]["decided_at"] == "2026-09-25"
    assert by_number["議第235号"]["title"] == "市道の認定について（楡木2丁目第8号線）"
    # The earthquake-recovery resolution was decided on the opening
    # day; the nuclear-three-principles opinion paper was rejected.
    assert by_number["発議第6号"]["decided_at"] == "2026-08-31"
    assert by_number["発議第6号"]["outcome"] == "approved"
    assert by_number["発議第9号"]["outcome"] == "rejected"
    # Petitions are never adopted or rejected in Kumamoto City:
    # the council's own guidance says no adoption decision is made.
    petitions = [p for p in proposals if p["kind"] == "petition"]
    assert all(p["outcome"] == "not_assessable" for p in petitions)
    assert all(p["decided_at"] is None for p in petitions)
    # Individual submission dates are not published per item.
    assert all(p["submitted_at"] is None for p in proposals)


def test_votes():
    votes = load("votes.json")
    validate("vote.schema.json", votes)
    proposals = {p["id"]: p for p in load("proposals.json")}
    assert len(votes) == 51
    per_proposal = {}
    for v in votes:
        per_proposal.setdefault(v["proposal_id"], []).append(v)
    # Every non-petition proposal has exactly one vote record.
    voted = {pid for pid, p in proposals.items() if p["kind"] != "petition"}
    assert set(per_proposal) == voted
    assert all(len(vs) == 1 for vs in per_proposal.values())
    total_members = 0
    for vote in votes:
        # The minutes of this session are not yet in the records
        # system, so the voting method cannot be cross-checked and
        # stays unknown.
        assert vote["method"] == "unknown"
        assert vote["member_vote_availability"] == "published"
        assert len(vote["member_votes"]) == 46
        total_members += len(vote["member_votes"])
        counts = {"for": 0, "against": 0, "abstained": 0, "absent": 0}
        excused = 0
        for m in vote["member_votes"]:
            if m["position"] == "excused":
                excused += 1
            else:
                counts[m["position"]] += 1
        assert vote["totals"] == counts
        # Only the speaker (田中誠一) is marked 未投票 (excused).
        assert excused == 1
        chair = [m for m in vote["member_votes"] if m["position"] == "excused"]
        assert chair[0]["member_name"] == "田中誠一"
        prop = proposals[vote["proposal_id"]]
        assert prop["decided_at"] == vote["vote_date"]
        assert prop["outcome"] == vote["outcome"]
    assert total_members == 51 * 46


def test_divided_votes():
    proposals = {p["proposal_number"]: p for p in load("proposals.json")}
    votes = {v["proposal_id"]: v for v in load("votes.json")}

    def totals(number):
        return votes[proposals[number]["id"]]["totals"]

    def against_names(number):
        vote = votes[proposals[number]["id"]]
        return {
            m["member_name"] for m in vote["member_votes"]
            if m["position"] == "against"
        }

    # The two JCP members alone opposed the supplementary budgets
    # 223/224, contract bill 255, and settlements 257-260.
    for number in ("議第223号", "議第224号", "議第255号", "議第257号",
                   "議第258号", "議第259号", "議第260号"):
        assert totals(number) == {
            "for": 43, "against": 2, "abstained": 0, "absent": 0,
        }
        assert against_names(number) == {"井芹栄次", "上野美恵子"}
    # Opinion paper 8 (earthquake recovery): the three 市民の会
    # members joined the JCP in opposition, but it was approved.
    assert totals("発議第8号") == {
        "for": 40, "against": 5, "abstained": 0, "absent": 0,
    }
    assert against_names("発議第8号") == {
        "菊地渚沙", "井坂隆寛", "吉村健治", "井芹栄次", "上野美恵子",
    }
    # Opinion paper 9 (nuclear three principles) was rejected 18-27.
    assert totals("発議第9号") == {
        "for": 18, "against": 27, "abstained": 0, "absent": 0,
    }
    # The 14 road bills share one joint vote table (45 for).
    for n in range(235, 249):
        vote = votes[proposals[f"議第{n}号"]["id"]]
        assert vote["totals"]["for"] == 45
        assert vote["item_scope"] is not None


def test_faction_votes():
    faction_votes = load("faction_votes.json")
    validate("faction_vote.schema.json", faction_votes)
    votes = {v["id"]: v for v in load("votes.json")}
    # 50 votes with 8 groups, plus the opening-day resolution with 9
    # (the two LDP factions are still shown separately there).
    assert len(faction_votes) == 50 * 8 + 9
    by_vote = {}
    for fv in faction_votes:
        by_vote.setdefault(fv["vote_id"], []).append(fv)
    assert set(by_vote) == set(votes)
    for vote in votes.values():
        groups = by_vote[vote["id"]]
        # Re-aggregate the member votes and compare.
        member_faction = {}
        for fv in groups:
            member_faction[fv["faction_name"]] = fv
        assert sum(g["member_count"] for g in groups) == 46
        assert sum(g["for_count"] for g in groups) == vote["totals"]["for"]
        assert (
            sum(g["against_count"] for g in groups)
            == vote["totals"]["against"]
        )
        for g in groups:
            if g["for_count"] and not g["against_count"]:
                assert g["position"] == "for"
            elif g["against_count"] and not g["for_count"]:
                assert g["position"] == "against"
    # The recovery resolution (decided 2026-08-31) is the only vote
    # whose printed table splits the LDP into 自民党 (14) and
    # 熊本自民 (7); the seven match the FY2025 熊本自由民主党市議団
    # membership after one resignation.
    by_number = {p["proposal_number"]: p for p in load("proposals.json")}
    vote_by_proposal = {v["proposal_id"]: v for v in votes.values()}
    recovery_vote = vote_by_proposal[by_number["発議第6号"]["id"]]
    groups = {g["faction_name"]: g for g in by_vote[recovery_vote["id"]]}
    assert len(groups) == 9
    assert groups["自由民主党熊本市議団"]["member_count"] == 14
    assert groups["熊本自由民主党市議団"]["member_count"] == 7
    # Every other vote uses the merged 21-member LDP group.
    for vote in votes.values():
        if vote["id"] == recovery_vote["id"]:
            continue
        names = {g["faction_name"] for g in by_vote[vote["id"]]}
        assert "熊本自由民主党市議団" not in names
        ldp = [g for g in by_vote[vote["id"]]
               if g["faction_name"] == "自由民主党熊本市議団"]
        assert ldp[0]["member_count"] == 21


def test_expenses():
    expenses = load("political_activity_expenses.json")
    validate("political_activity_expense.schema.json", expenses)
    assert len(expenses) == 50
    assert all(r["fiscal_year"] == 2025 for r in expenses)
    assert all(r["receipt_access"] == "online" for r in expenses)
    assert all(r["report_status"] == "published" for r in expenses)
    for record in expenses:
        assert [i["category"] for i in record["breakdown"]] == CATEGORIES
        assert (
            sum(i["amount_yen"] for i in record["breakdown"])
            == record["spent_yen"]
        ), record["recipient_name"]
        if record["spent_yen"] <= record["granted_yen"]:
            assert (
                record["granted_yen"] - record["spent_yen"]
                == record["returned_yen"]
            ), record["recipient_name"]
        else:
            # Overspent reports print a negative remainder; nothing
            # is returned, so returned_yen is 0.
            assert record["returned_yen"] == 0, record["recipient_name"]
    factions = [r for r in expenses if r["recipient_type"] == "faction"]
    members = [r for r in expenses if r["recipient_type"] == "member"]
    assert len(factions) == 5
    assert len(members) == 45
    # Members are granted 200,000 yen per month (2,400,000 per year)
    # unless their term was partial.
    full = [r for r in members if r["granted_yen"] == 2400000]
    assert len(full) >= 40


def test_inspection_trips():
    trips = load("inspection_trips.json")
    validate("inspection_trip.schema.json", trips)
    assert len(trips) == 6
    by_committee = {}
    for trip in trips:
        assert trip["trip_type"] == "domestic"
        assert trip["report_status"] == "published"
        # The newsletter report prints dates, destinations and survey
        # items, but no participants or costs.
        assert trip["cost_status"] == "not_published"
        assert trip["total_cost_yen"] is None
        assert trip["cost_per_person_yen"] is None
        assert trip["participant_count"] is None
        assert trip["participants"] == []
        by_committee[trip["title"]] = trip
    assert by_committee["総務委員会行政視察"]["start_date"] == "2025-11-10"
    assert by_committee["総務委員会行政視察"]["end_date"] == "2025-11-12"
    assert by_committee["総務委員会行政視察"]["destinations"] == [
        "京都市消防活動総合センター", "京都市", "金沢市",
    ]
    assert by_committee["環境水道委員会行政視察"]["start_date"] == "2025-10-21"
    assert by_committee["教育市民委員会行政視察"]["start_date"] == "2025-11-12"
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
    assert items["member_votes"]["availability"] == "published"
    assert items["member_votes"]["granularity"] == "member"
    assert items["faction_votes"]["availability"] == "published"
    assert (
        items["political_activity_expense_reports"]["granularity"]
        == "member"
    )
    assert items["inspection_trip_reports"]["availability"] == "published"
    assert items["meeting_minutes"]["availability"] == "not_found"


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
    assert len(packets) == 112
    vote_packets = load("proposal_vote_evidence_packets.json")
    assert len(vote_packets) == 60
    assert all(p["subject_type"] == "proposal" for p in vote_packets)
    assert all(p["open_questions"] == [] for p in vote_packets)
    # The assembly packet keeps the open questions that the primary
    # sources could not settle (term start date in print, petitions
    # in this session, the LDP factions' merger date).
    assembly_packets = load("assembly_evidence_packets.json")
    assert len(assembly_packets) == 1
    assert len(assembly_packets[0]["open_questions"]) == 3
    expense_packets = load("expense_evidence_packets.json")
    assert len(expense_packets) == 50
    assert all(p["open_questions"] == [] for p in expense_packets)
