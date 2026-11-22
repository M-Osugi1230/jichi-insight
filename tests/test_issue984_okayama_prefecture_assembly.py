"""Issue #984: Okayama Prefectural Assembly stage-4 registration checks."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "reviewed" / "okayama-prefecture" / "assembly"
CATALOG = (
    ROOT / "data" / "catalog" / "okayama_prefecture_assembly_sources.json"
)
ASSEMBLY_ID = "jp-local-330001-assembly-2023"
SESSION_ID = "jp-local-330001-assembly-2023-session-2026-09"
FACTIONS = {
    "自由民主党岡山県議団",
    "民主・県民クラブ",
    "公明党岡山県議団",
    "日本共産党岡山県議会議員団",
    "無所属",
}
CATEGORIES = [
    "調査研究費",
    "研修費",
    "広聴広報費",
    "要請陳情等活動費",
    "会議費",
    "資料作成費",
    "資料購入費",
    "事務所費",
    "事務費",
    "人件費",
]


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def source_ids():
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    return {record["id"] for record in catalog["records"]}


def test_catalog_is_okayama_prefecture_only():
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    records = catalog["records"]
    assert len(records) == 19
    assert {r["municipality_key"] for r in records} == {
        "okayama-prefecture"
    }
    assert len(source_ids()) == 19
    categories = {r["category"] for r in records}
    assert {
        "assembly",
        "inspection_trips",
        "political_activity_expenses",
        "proposals",
    } <= categories


def test_assembly_record_matches_official_roster():
    records = load("assembly_records.json")
    assert len(records) == 1
    record = records[0]
    assert record["id"] == ASSEMBLY_ID
    assert record["municipality_id"] == "jp-local-330001"
    assert record["name"] == "岡山県議会"
    assert record["term_start"] == "2023-04-30"
    assert record["term_end"] == "2027-04-29"
    # Statutory strength 55; the official faction roster lists 53
    # current members (two vacancies).
    assert record["seat_count"] == 55
    sizes = [f["member_count"] for f in record["factions"]]
    assert sizes == [31, 11, 6, 3, 2]
    assert sum(sizes) == 53
    assert {f["name"] for f in record["factions"]} == FACTIONS
    assert len(record["committees"]) == 12


def test_session_is_september_2026_regular_session():
    sessions = load("sessions.json")
    assert len(sessions) == 1
    session = sessions[0]
    assert session["id"] == SESSION_ID
    assert session["name"] == "令和8年9月定例会"
    assert session["session_type"] == "regular"
    assert session["start_date"] == "2026-09-03"
    assert session["end_date"] == "2026-10-02"


def test_proposals_cover_all_kinds_and_outcomes():
    proposals = load("proposals.json")
    assert len(proposals) == 25
    assert {p["session_id"] for p in proposals} == {SESSION_ID}
    by_submitter = {}
    for proposal in proposals:
        by_submitter[proposal["submitted_by"]] = (
            by_submitter.get(proposal["submitted_by"], 0) + 1
        )
    assert by_submitter == {
        "executive": 17,
        "member": 2,
        "resident_petition": 6,
    }
    kinds = {}
    for proposal in proposals:
        kinds[proposal["kind"]] = kinds.get(proposal["kind"], 0) + 1
    assert kinds == {
        "budget": 2,
        "ordinance": 5,
        "other": 4,
        "personnel": 2,
        "settlement": 4,
        "resolution": 2,
        "petition": 6,
    }
    outcomes = {}
    for proposal in proposals:
        outcomes[proposal["outcome"]] = (
            outcomes.get(proposal["outcome"], 0) + 1
        )
    assert outcomes == {"approved": 21, "rejected": 3, "pending": 1}
    decided = [p for p in proposals if p["outcome"] != "pending"]
    assert all(p["decided_at"] == "2026-10-02" for p in decided)
    # The three enterprise-account settlements were certified at this
    # session; the general/special-account settlement was not tabled
    # and stays pending under continued committee review.
    settlements = [p for p in proposals if p["kind"] == "settlement"]
    assert len(settlements) == 4
    certified = [p for p in settlements if p["outcome"] == "approved"]
    assert len(certified) == 3
    assert {p["proposal_number"] for p in certified} == {
        "議第108号",
        "議第109号",
        "議第110号",
    }
    pending = [p for p in proposals if p["outcome"] == "pending"]
    assert len(pending) == 1
    assert pending[0]["kind"] == "settlement"
    assert pending[0]["proposal_number"] == "決算認定"
    assert pending[0]["title"] == "令和7年度岡山県歳入歳出決算の認定について"
    assert pending[0]["submitted_at"] is None
    assert pending[0]["decided_at"] is None
    # Petitions: six decided petitions; No. 124 does not appear in
    # the official results table and is not registered.
    petitions = [p for p in proposals if p["kind"] == "petition"]
    assert {p["proposal_number"] for p in petitions} == {
        "陳情第119号",
        "陳情第120号",
        "陳情第121号",
        "陳情第122号",
        "陳情第123号",
        "陳情第125号",
    }
    assert {
        p["proposal_number"] for p in petitions if p["outcome"] == "approved"
    } == {"陳情第121号", "陳情第122号", "陳情第125号"}
    assert {
        p["proposal_number"] for p in petitions if p["outcome"] == "rejected"
    } == {"陳情第119号", "陳情第120号", "陳情第123号"}


def test_votes_are_not_published_model():
    votes = load("votes.json")
    proposals = {p["id"]: p for p in load("proposals.json")}
    decided = {pid for pid, p in proposals.items() if p["outcome"] != "pending"}
    assert len(votes) == 24
    assert {v["proposal_id"] for v in votes} == decided
    for vote in votes:
        # Okayama publishes only bill number / summary / result: no
        # faction or member breakdown exists to register.
        assert vote["method"] == "unknown"
        assert vote["member_vote_availability"] == "not_published"
        assert vote["member_votes"] == []
        assert vote["totals"] is None
        assert vote["vote_date"] == "2026-10-02"
        assert vote["outcome"] == proposals[vote["proposal_id"]]["outcome"]
    assert load("faction_votes.json") == []


def test_expenses_cover_all_member_reports():
    expenses = load("political_activity_expenses.json")
    assert len(expenses) == 55
    assert {e["fiscal_year"] for e in expenses} == {2025}
    assert {e["recipient_type"] for e in expenses} == {"member"}
    assert {e["report_status"] for e in expenses} == {"published"}
    # Reports are public on the web; the originals and receipts are
    # available only in the assembly building reading room.
    assert {e["receipt_access"] for e in expenses} == {"in_person_only"}
    for expense in expenses:
        assert [b["category"] for b in expense["breakdown"]] == CATEGORIES
        assert sum(
            b["amount_yen"] for b in expense["breakdown"]
        ) == expense["spent_yen"]
        assert expense["returned_yen"] == (
            expense["granted_yen"] - expense["spent_yen"]
        )
    # Full-year members received 350,000 yen per month for 12 months.
    full = [e for e in expenses if e["granted_yen"] == 4_200_000]
    assert len(full) == 54
    # The one former member served a single month of FY2025.
    former = [e for e in expenses if e["granted_yen"] != 4_200_000]
    assert len(former) == 1
    assert former[0]["recipient_name"] == "波多洋治"
    assert former[0]["granted_yen"] == 350_000
    assert former[0]["spent_yen"] == 202_717
    assert former[0]["returned_yen"] == 147_283


def test_inspection_trips_not_published():
    assert load("inspection_trips.json") == []
    packets = load("inspection_evidence_packets.json")
    assert len(packets) == 1
    assert packets[0]["subject_id"] == ASSEMBLY_ID
    assert packets[0]["open_questions"]


def test_disclosure_profile_notes():
    profiles = load("disclosure_profiles.json")
    assert len(profiles) == 1
    items = {item["item"]: item for item in profiles[0]["items"]}
    assert len(items) == 12
    assert items["faction_votes"]["availability"] == "not_published"
    assert items["member_votes"]["availability"] == "not_published"
    assert (
        items["political_activity_expense_reports"]["availability"]
        == "published"
    )
    assert items["political_activity_expense_reports"]["granularity"] == "member"
    assert (
        items["political_activity_expense_receipts"]["availability"]
        == "restricted"
    )
    assert "閲覧室" in items["political_activity_expense_receipts"]["note"]
    assert items["inspection_trip_reports"]["availability"] == "not_published"
    assert items["petition_results"]["availability"] == "published"


def test_evidence_packets_cover_every_record():
    proposals = {p["id"] for p in load("proposals.json")}
    pv = load("proposal_vote_evidence_packets.json")
    assert {
        p["subject_id"] for p in pv if p["subject_type"] == "proposal"
    } == proposals
    expenses = {e["id"] for e in load("political_activity_expenses.json")}
    ex = load("expense_evidence_packets.json")
    assert {p["subject_id"] for p in ex} == expenses
    assembly_packets = load("assembly_evidence_packets.json")
    assert {p["subject_id"] for p in assembly_packets} == {ASSEMBLY_ID}
    assert assembly_packets[0]["open_questions"]


def test_all_sources_resolve_to_catalog():
    ids = source_ids()
    for name in (
        "assembly_records.json",
        "sessions.json",
        "proposals.json",
        "votes.json",
        "faction_votes.json",
        "political_activity_expenses.json",
        "inspection_trips.json",
        "disclosure_profiles.json",
    ):
        for record in load(name):
            assert set(record["sources"]) <= ids, (name, record["id"])
    for name in (
        "assembly_evidence_packets.json",
        "proposal_vote_evidence_packets.json",
        "expense_evidence_packets.json",
        "inspection_evidence_packets.json",
    ):
        for packet_record in load(name):
            for claim_record in packet_record["claims"]:
                assert set(claim_record["source_ids"]) <= ids
