from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "reviewed" / "sapporo-city" / "assembly"
ASSEMBLY_ID = "jp-local-011002-assembly-2023"
SESSION_ID = f"{ASSEMBLY_ID}-session-2026-05"
DIVIDED_PROPOSAL_IDS = {
    f"{ASSEMBLY_ID}-proposal-2026-003": "日本共産党",  # 議案第3号
    f"{ASSEMBLY_ID}-proposal-2026-006": "日本共産党",  # 議案第6号
    f"{ASSEMBLY_ID}-proposal-2026-009": "日本共産党",  # 議案第9号
    f"{ASSEMBLY_ID}-proposal-2026-010": "日本共産党",  # 議案第10号
    f"{ASSEMBLY_ID}-proposal-2026-028": "坂元・荒井",  # 意見書案第4号
}


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def assert_valid(schema_path: str, instance: Any) -> None:
    validator = Draft202012Validator(
        load_json(ROOT / schema_path),
        format_checker=FormatChecker(),
    )
    errors = list(validator.iter_errors(instance))
    assert errors == [], "; ".join(error.message for error in errors)


def catalog_source_ids() -> set[str]:
    ids: set[str] = set()
    for path in (ROOT / "data" / "catalog").glob("*.json"):
        value = load_json(path)
        if isinstance(value, dict) and isinstance(value.get("records"), list):
            ids.update(
                record["id"]
                for record in value["records"]
                if isinstance(record, dict) and isinstance(record.get("id"), str)
            )
    return ids


def referenced_sources(value: Any) -> set[str]:
    result: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"sources", "source_ids"} and isinstance(child, list):
                result.update(item for item in child if isinstance(item, str))
            result.update(referenced_sources(child))
    elif isinstance(value, list):
        for child in value:
            result.update(referenced_sources(child))
    return result


def test_sapporo_catalog_is_valid() -> None:
    catalog = load_json(ROOT / "data" / "catalog" / "sapporo_assembly_sources.json")
    assert_valid("schemas/source_catalog.schema.json", catalog)
    assert len(catalog["records"]) == 101
    assert {r["municipality_key"] for r in catalog["records"]} == {"sapporo-city"}


def test_sapporo_assembly_and_session_match_contracts() -> None:
    assemblies = load_json(BASE / "assembly_records.json")
    sessions = load_json(BASE / "sessions.json")
    packets = load_json(BASE / "assembly_evidence_packets.json")

    assert len(assemblies) == 1
    assembly = assemblies[0]
    assert_valid("schemas/assembly.schema.json", assembly)
    assert assembly["id"] == ASSEMBLY_ID
    assert assembly["seat_count"] == 68
    assert assembly["term_start"] == "2023-05-02"
    assert assembly["term_end"] == "2027-05-01"
    # Session-time composition (June 2026): 11 factions, 67 members,
    # one seat vacant against the statutory 68.
    assert sum(f["member_count"] for f in assembly["factions"]) == 67
    assert len(assembly["factions"]) == 11

    assert len(sessions) == 1
    assert_valid("schemas/session.schema.json", sessions[0])
    assert sessions[0]["id"] == SESSION_ID
    assert sessions[0]["start_date"] == "2026-05-21"
    assert sessions[0]["end_date"] == "2026-06-05"

    assert [p["subject_id"] for p in packets] == [ASSEMBLY_ID]
    for packet in packets:
        assert_valid("schemas/evidence_packet.schema.json", packet)


def test_sapporo_proposals_and_votes_match_contracts() -> None:
    proposals = load_json(BASE / "proposals.json")
    votes = load_json(BASE / "votes.json")
    packets = load_json(BASE / "proposal_vote_evidence_packets.json")

    # 121 decided items (22 bills, 2 consultations, 4 opinion papers,
    # 1 resolution, 2 other items, 90 petitions) plus 13 reports.
    assert len(proposals) == 134
    assert len(votes) == 121
    assert len(packets) == 255
    assert {p["subject_id"] for p in packets} == {p["id"] for p in proposals} | {
        v["id"] for v in votes
    }

    petitions = [p for p in proposals if p["kind"] == "petition"]
    assert len(petitions) == 90
    assert all(p["outcome"] == "rejected" for p in petitions)
    reports = [p for p in proposals if p["outcome"] == "not_assessable"]
    assert len(reports) == 13
    assert {v["proposal_id"] for v in votes} == {
        p["id"] for p in proposals if p["outcome"] != "not_assessable"
    }

    for proposal in proposals:
        assert_valid("schemas/proposal.schema.json", proposal)
        assert proposal["assembly_id"] == ASSEMBLY_ID
        assert proposal["session_id"] == SESSION_ID
    for vote in votes:
        assert_valid("schemas/vote.schema.json", vote)
        # Member-level votes are not published in Sapporo; nothing is
        # reconstructed, and the absence is explicit on every vote.
        assert vote["member_vote_availability"] == "not_published"
        assert vote["member_votes"] == []
        assert vote["totals"] is None


def test_sapporo_faction_votes_cross_checked() -> None:
    votes = load_json(BASE / "votes.json")
    faction_votes = load_json(BASE / "faction_votes.json")
    proposals = {p["id"]: p for p in load_json(BASE / "proposals.json")}

    assert len(faction_votes) == 121 * 11
    by_vote: dict[str, list[dict[str, Any]]] = {}
    for fv in faction_votes:
        assert_valid("schemas/faction_vote.schema.json", fv)
        by_vote.setdefault(fv["vote_id"], []).append(fv)

    for vote in votes:
        rows = by_vote[vote["id"]]
        assert len(rows) == 11
        assert sum(r["member_count"] for r in rows) == 67
        # Yamaguchi Kazusa was absent for the whole session (sick leave,
        # documented in the May 21 plenary minutes).
        kazusa = next(r for r in rows if r["faction_name"] == "山口かずさ")
        assert kazusa["position"] == "absent"
        against = {r["faction_name"] for r in rows if r["position"] == "against"}
        proposal = proposals[vote["proposal_id"]]
        if vote["proposal_id"] in DIVIDED_PROPOSAL_IDS:
            assert vote["method"] == "standing"
            assert against == {DIVIDED_PROPOSAL_IDS[vote["proposal_id"]]}
        elif proposal["kind"] == "petition":
            # All factions opposed adoption; the rejection was unanimous.
            assert vote["method"] == "unanimous"
            assert against == {r["faction_name"] for r in rows if r["faction_name"] != "山口かずさ"}
        else:
            assert vote["method"] == "unanimous"
            assert against == set()


def test_sapporo_expenses_reconcile() -> None:
    expenses = load_json(BASE / "political_activity_expenses.json")
    packets = load_json(BASE / "expense_evidence_packets.json")

    assert len(expenses) == 47
    assert len(packets) == 47
    assert {p["subject_id"] for p in packets} == {e["id"] for e in expenses}
    per_year: dict[int, int] = {}
    for expense in expenses:
        assert_valid("schemas/political_activity_expense.schema.json", expense)
        assert expense["assembly_id"] == ASSEMBLY_ID
        assert expense["recipient_type"] == "faction"
        assert expense["report_status"] == "published"
        per_year[expense["fiscal_year"]] = per_year.get(expense["fiscal_year"], 0) + 1
        # Sapporo's form prints no interest line: the printed residual is
        # exactly granted - spent, and the breakdown sums to the total.
        assert sum(b["amount_yen"] for b in expense["breakdown"]) == expense["spent_yen"]
        assert expense["returned_yen"] == (expense["granted_yen"] - expense["spent_yen"])
    assert per_year == {2020: 5, 2021: 5, 2022: 6, 2023: 9, 2024: 10, 2025: 12}
    for packet in packets:
        assert_valid("schemas/evidence_packet.schema.json", packet)

    jimin = next(
        e
        for e in expenses
        if e["fiscal_year"] == 2025 and e["recipient_name"] == "札幌市議会自由民主党議員会"
    )
    assert jimin["granted_yen"] == 120_000_000
    assert jimin["spent_yen"] == 119_462_992
    assert jimin["returned_yen"] == 537_008


def test_sapporo_inspection_trips() -> None:
    trips = load_json(BASE / "inspection_trips.json")
    packets = load_json(BASE / "inspection_evidence_packets.json")

    # One report unit per committee per fiscal year, FY2023-FY2026.
    # The General Affairs Committee's FY2024 trip was cancelled (typhoon),
    # so it has no trip record.
    assert len(trips) == 35
    assert len(packets) == 35
    assert {p["subject_id"] for p in packets} == {t["id"] for t in trips}
    for trip in trips:
        assert_valid("schemas/inspection_trip.schema.json", trip)
        assert trip["assembly_id"] == ASSEMBLY_ID
        assert trip["trip_type"] == "domestic"
        assert trip["report_status"] == "published"
        assert trip["cost_status"] == "not_published"
        assert trip["total_cost_yen"] is None
        assert trip["participant_count"] == len(trip["participants"])
        assert trip["participant_count"] >= 8
        assert trip["start_date"] <= trip["end_date"]
    for packet in packets:
        assert_valid("schemas/evidence_packet.schema.json", packet)


def test_sapporo_disclosure_profile() -> None:
    profiles = load_json(BASE / "disclosure_profiles.json")
    assert len(profiles) == 1
    profile = profiles[0]
    assert_valid("schemas/disclosure_profile.schema.json", profile)
    items = {item["item"]: item for item in profile["items"]}
    assert items["faction_votes"]["availability"] == "published"
    assert items["member_votes"]["availability"] == "not_published"
    assert items["political_activity_expense_reports"]["availability"] == "published"
    assert items["political_activity_expense_receipts"]["availability"] == "restricted"
    assert items["inspection_trip_reports"]["availability"] == "published"


def test_sapporo_sources_resolve() -> None:
    ids = catalog_source_ids()
    for name in (
        "assembly_records.json",
        "assembly_evidence_packets.json",
        "sessions.json",
        "proposals.json",
        "votes.json",
        "faction_votes.json",
        "proposal_vote_evidence_packets.json",
        "political_activity_expenses.json",
        "expense_evidence_packets.json",
        "inspection_trips.json",
        "inspection_evidence_packets.json",
        "disclosure_profiles.json",
    ):
        missing = referenced_sources(load_json(BASE / name)) - ids
        assert missing == set(), f"{name}: unresolved sources {missing}"
