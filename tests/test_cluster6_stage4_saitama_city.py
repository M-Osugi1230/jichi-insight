"""Cluster 6 stage 4: Saitama City assembly registration checks.

Pins the counts and cross-checks for the Saitama City Council data taken
from the September 2026 regular session (Reiwa 8), the political
activity expense reports for FY2023-FY2025 (six half-year periods), and
the inspection trips published on the committee activity pages.
"""

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "reviewed" / "saitama-city" / "assembly"
CATALOG = ROOT / "data" / "catalog" / "saitama_city_assembly_sources.json"
ASM = "jp-local-111007-assembly-2023"
SESSION = f"{ASM}-session-2026-09"


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
    assert all(entry["municipality_key"] == "saitama-city" for entry in records)
    assert len(records) == 94


def test_assembly_record():
    records = load("assembly_records.json")
    validate("assembly.schema.json", records)
    assert len(records) == 1
    record = records[0]
    assert record["id"] == ASM
    assert record["municipality_id"] == "jp-local-111007"
    assert record["seat_count"] == 60
    assert record["term_start"] == "2023-05-01"
    assert record["term_end"] == "2027-04-30"
    # Faction composition at the time of the September 2026 session,
    # from the header of the official vote-attitude table.
    assert sum(f["member_count"] for f in record["factions"]) == 59
    by_name = {f["name"]: f["member_count"] for f in record["factions"]}
    assert by_name["自民党"] == 18
    assert by_name["立憲・国民・無所属の会"] == 12
    assert by_name["公明党"] == 11
    assert by_name["日本共産党"] == 6
    assert by_name["日本維新の会"] == 4
    assert by_name["無所属みらい"] == 2
    assert by_name["無所属"] == 6


def test_session():
    sessions = load("sessions.json")
    validate("session.schema.json", sessions)
    assert len(sessions) == 1
    session = sessions[0]
    assert session["id"] == SESSION
    assert session["name"] == "令和8年9月定例会"
    assert session["start_date"] == "2026-09-02"
    assert session["end_date"] == "2026-10-16"


def test_proposals():
    proposals = load("proposals.json")
    validate("proposal.schema.json", proposals)
    assert len(proposals) == 36
    assert sum(1 for p in proposals if p["submitted_by"] == "executive") == 35
    assert sum(1 for p in proposals if p["submitted_by"] == "member") == 1
    by_number = {p["proposal_number"]: p for p in proposals}
    # Settlement bills were decided in this session (no continuation).
    for number in ["議案第152号", "議案第153号", "議案第154号", "議案第155号"]:
        proposal = by_number[number]
        assert proposal["kind"] == "settlement"
        assert proposal["outcome"] == "approved"
        assert proposal["decided_at"] == "2026-10-16"
    # The member-submitted resolution was rejected on 2026-10-15.
    member_bill = by_number["議員提出議案第6号"]
    assert member_bill["kind"] == "resolution"
    assert member_bill["outcome"] == "rejected"
    assert member_bill["submitted_at"] == "2026-10-14"
    assert member_bill["decided_at"] == "2026-10-15"
    # Additional bills submitted on 2026-10-14.
    assert by_number["議案第177号"]["submitted_at"] == "2026-10-14"
    assert by_number["議案第178号"]["submitted_at"] == "2026-10-14"
    # Unanimous bills: decided dates are not publicly fixed, so they
    # stay null rather than being guessed.
    unanimous = [p for p in proposals if p["decided_at"] is None]
    assert len(unanimous) == 24
    assert all(p["outcome"] == "approved" for p in unanimous)


def test_votes_cover_only_divided_proposals():
    votes = load("votes.json")
    validate("vote.schema.json", votes)
    proposals = {p["id"]: p for p in load("proposals.json")}
    assert len(votes) == 12
    for vote in votes:
        assert vote["member_vote_availability"] == "published"
        assert vote["method"] == "unknown"
        assert vote["totals"] is None
        assert proposals[vote["proposal_id"]]["decided_at"] == vote["vote_date"]
    # Only the six independent members have individual columns, plus
    # the two annotated exceptions on proposal 150.
    member_votes = [mv for v in votes for mv in v["member_votes"]]
    assert len(member_votes) == 74
    names = {mv["member_name"] for mv in member_votes}
    assert names == {
        "川村準",
        "佐藤潤",
        "佐藤征治郎",
        "中山淳一",
        "浜口健司",
        "吉田一郎",
        "鳥羽恵",
        "竹腰連",
    }


def test_proposal_150_exception_note():
    proposals = {p["proposal_number"]: p for p in load("proposals.json")}
    votes = {v["proposal_id"]: v for v in load("votes.json")}
    vote = votes[proposals["議案第150号"]["id"]]
    exceptions = [mv for mv in vote["member_votes"] if mv["member_name"] in ("鳥羽恵", "竹腰連")]
    assert len(exceptions) == 2
    assert all(mv["position"] == "against" for mv in exceptions)
    faction_votes = load("faction_votes.json")
    kyosan = [
        fv
        for fv in faction_votes
        if fv["vote_id"] == vote["id"] and fv["faction_name"] == "日本共産党"
    ]
    assert len(kyosan) == 1
    # The faction cell's main symbol is "for"; the two dissenting
    # members are recorded individually above.
    assert kyosan[0]["position"] == "for"


def test_faction_votes():
    faction_votes = load("faction_votes.json")
    validate("faction_vote.schema.json", faction_votes)
    assert len(faction_votes) == 72
    for fv in faction_votes:
        assert fv["for_count"] is None
        assert fv["against_count"] is None
    votes = {v["id"]: v for v in load("votes.json")}
    proposals = {p["id"]: p for p in load("proposals.json")}
    member_bill_vote = next(
        v
        for v in votes.values()
        if proposals[v["proposal_id"]]["proposal_number"] == "議員提出議案第6号"
    )
    positions = {
        fv["faction_name"]: fv["position"]
        for fv in faction_votes
        if fv["vote_id"] == member_bill_vote["id"]
    }
    assert positions == {
        "自民党": "against",
        "立憲・国民・無所属の会": "for",
        "公明党": "for",
        "日本共産党": "for",
        "日本維新の会": "against",
        "無所属みらい": "for",
    }
    # The Communist Party opposed the budget/settlement bills.
    for vote in votes.values():
        number = proposals[vote["proposal_id"]]["proposal_number"]
        if number in ("議案第144号", "議案第152号", "議案第177号"):
            pos = {
                fv["faction_name"]: fv["position"]
                for fv in faction_votes
                if fv["vote_id"] == vote["id"]
            }
            assert pos["日本共産党"] == "against"


def test_expenses_counts_and_breakdown_sums():
    expenses = load("political_activity_expenses.json")
    validate("political_activity_expense.schema.json", expenses)
    assert len(expenses) == 341
    by_year = {}
    for record in expenses:
        by_year[record["fiscal_year"]] = by_year.get(record["fiscal_year"], 0) + 1
    assert by_year == {2023: 114, 2024: 114, 2025: 113}
    assert all(r["receipt_access"] == "online" for r in expenses)
    assert all(r["report_status"] == "published" for r in expenses)
    # Two reports have a printed total that differs from the sum of
    # the nine printed categories by 300 yen in the source itself;
    # they are registered as printed and documented in their packets.
    sum_exceptions = {
        "jp-local-111007-assembly-2023-political-activity-expense-2023-027",
        "jp-local-111007-assembly-2023-political-activity-expense-2024-104",
    }
    for record in expenses:
        total = sum(item["amount_yen"] for item in record["breakdown"])
        if record["id"] in sum_exceptions:
            assert record["spent_yen"] - total == 300
        else:
            assert total == record["spent_yen"], record["id"]


def test_expenses_negative_balances():
    expenses = load("political_activity_expenses.json")
    by_id = {r["id"]: r for r in expenses}
    # The Communist Party faction FY2025 second-half report prints a
    # balance of -52,131 yen; the schema cannot hold a negative
    # returned amount, so it stays null and the value is documented
    # in the evidence packet.
    kyosan = by_id["jp-local-111007-assembly-2023-political-activity-expense-2025-104"]
    assert kyosan["recipient_name"] == "日本共産党さいたま市議会議員団"
    assert kyosan["granted_yen"] == 12240000
    assert kyosan["spent_yen"] == 13528905
    assert kyosan["returned_yen"] is None
    null_returns = [r for r in expenses if r["returned_yen"] is None]
    assert len(null_returns) == 72
    packets = {p["subject_id"]: p for p in load("expense_evidence_packets.json")}
    for record in null_returns:
        statement = packets[record["id"]]["claims"][0]["statement"]
        assert "マイナス" in statement


def test_inspection_trips():
    trips = load("inspection_trips.json")
    validate("inspection_trip.schema.json", trips)
    assert len(trips) == 22
    domestic = [t for t in trips if t["trip_type"] == "domestic"]
    overseas = [t for t in trips if t["trip_type"] == "overseas"]
    assert len(domestic) == 20
    assert len(overseas) == 2
    for trip in domestic:
        assert trip["participants"] == []
        assert trip["participant_count"] is None
        assert trip["cost_status"] == "not_published"
        assert trip["report_status"] == "published"
    by_id = {t["id"]: t for t in trips}
    zhengzhou = by_id[f"{ASM}-inspection-2025-zhengzhou"]
    assert zhengzhou["start_date"] == "2025-07-24"
    assert zhengzhou["end_date"] == "2025-07-26"
    assert zhengzhou["participant_count"] == 1
    assert zhengzhou["participants"][0]["name"] == "伊藤仕"
    nanaimo = by_id[f"{ASM}-inspection-2026-nanaimo"]
    assert nanaimo["start_date"] == "2026-07-12"
    assert nanaimo["end_date"] == "2026-07-16"
    assert nanaimo["participant_count"] == 6


def test_disclosure_profile():
    profiles = load("disclosure_profiles.json")
    validate("disclosure_profile.schema.json", profiles)
    assert len(profiles) == 1
    items = {item["item"]: item for item in profiles[0]["items"]}
    assert items["faction_votes"]["availability"] == "published"
    assert items["member_votes"]["availability"] == "published"
    assert items["member_votes"]["granularity"] == "member"
    assert items["political_activity_expense_receipts"]["availability"] == "published"
    assert items["petition_results"]["availability"] == "unknown"


def test_evidence_packets():
    validate("evidence_packet.schema.json", load("assembly_evidence_packets.json"))
    validate("evidence_packet.schema.json", load("proposal_vote_evidence_packets.json"))
    validate("evidence_packet.schema.json", load("expense_evidence_packets.json"))
    validate("evidence_packet.schema.json", load("inspection_evidence_packets.json"))
    assembly_packets = load("assembly_evidence_packets.json")
    assert len(assembly_packets) == 1
    assert len(assembly_packets[0]["open_questions"]) == 7
    assert len(load("proposal_vote_evidence_packets.json")) == 36
    assert len(load("expense_evidence_packets.json")) == 341
    assert len(load("inspection_evidence_packets.json")) == 22
