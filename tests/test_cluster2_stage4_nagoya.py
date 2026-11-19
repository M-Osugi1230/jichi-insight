from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "reviewed" / "nagoya-city" / "assembly"
ASSEMBLY_ID = "jp-local-231002-assembly-2023"
SESSION_ID = f"{ASSEMBLY_ID}-session-2026-06"
DIVIDED_PROPOSAL_ID = f"{ASSEMBLY_ID}-proposal-2026-011"  # 第134号


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


def test_nagoya_catalog_is_valid() -> None:
    catalog = load_json(ROOT / "data" / "catalog" / "nagoya_assembly_sources.json")
    assert_valid("schemas/source_catalog.schema.json", catalog)
    assert len(catalog["records"]) == 24
    assert {r["municipality_key"] for r in catalog["records"]} == {"nagoya-city"}


def test_nagoya_assembly_and_session_match_contracts() -> None:
    assemblies = load_json(BASE / "assembly_records.json")
    sessions = load_json(BASE / "sessions.json")
    packets = load_json(BASE / "assembly_evidence_packets.json")

    assert len(assemblies) == 1
    assembly = assemblies[0]
    assert_valid("schemas/assembly.schema.json", assembly)
    assert assembly["id"] == ASSEMBLY_ID
    assert assembly["seat_count"] == 68
    assert assembly["term_start"] == "2023-04-12"
    assert assembly["term_end"] == "2027-04-11"
    assert sum(f["member_count"] for f in assembly["factions"]) == 68
    assert len(assembly["factions"]) == 9

    assert len(sessions) == 1
    assert_valid("schemas/session.schema.json", sessions[0])
    assert sessions[0]["id"] == SESSION_ID
    assert sessions[0]["start_date"] == "2026-06-19"
    assert sessions[0]["end_date"] == "2026-07-06"

    assert [p["subject_id"] for p in packets] == [ASSEMBLY_ID]
    for packet in packets:
        assert_valid("schemas/evidence_packet.schema.json", packet)


def test_nagoya_proposals_and_votes_match_contracts() -> None:
    proposals = load_json(BASE / "proposals.json")
    votes = load_json(BASE / "votes.json")
    packets = load_json(BASE / "proposal_vote_evidence_packets.json")

    assert len(proposals) == 22
    assert len(votes) == 22
    assert len(packets) == 44
    assert {p["subject_id"] for p in packets} == {p["id"] for p in proposals} | {
        v["id"] for v in votes
    }

    executive = [p for p in proposals if p["submitted_by"] == "executive"]
    member = [p for p in proposals if p["submitted_by"] == "member"]
    assert len(executive) == 17
    assert len(member) == 5
    for proposal in proposals:
        assert_valid("schemas/proposal.schema.json", proposal)
        assert proposal["assembly_id"] == ASSEMBLY_ID
        assert proposal["session_id"] == SESSION_ID
        assert proposal["decided_at"] == "2026-07-06"
        assert proposal["outcome"] == "approved"
    for vote in votes:
        assert_valid("schemas/vote.schema.json", vote)
        assert vote["vote_date"] == "2026-07-06"
        assert vote["outcome"] == "approved"

    divided = next(p for p in proposals if p["id"] == DIVIDED_PROPOSAL_ID)
    assert divided["proposal_number"] == "第134号"
    assert divided["title"] == "契約の一部変更について"


def test_nagoya_divided_vote_member_positions() -> None:
    votes = load_json(BASE / "votes.json")
    faction_votes = load_json(BASE / "faction_votes.json")
    vote = next(v for v in votes if v["proposal_id"] == DIVIDED_PROPOSAL_ID)

    assert vote["method"] == "standing"
    assert vote["member_vote_availability"] == "published"
    assert len(vote["member_votes"]) == 68
    positions = [mv["position"] for mv in vote["member_votes"]]
    assert positions.count("for") == 64
    assert positions.count("against") == 3
    assert positions.count("excused") == 1
    assert vote["totals"] == {"for": 64, "against": 3, "abstained": 0, "absent": 0}
    assert {mv["member_name"] for mv in vote["member_votes"] if mv["position"] == "against"} == {
        "岡田ゆき子",
        "みつなか美由紀",
        "田口一登",
    }
    assert {mv["member_name"] for mv in vote["member_votes"] if mv["position"] == "excused"} == {
        "小出昭司"
    }

    # Every other vote in the session was unanimous: no member rows are
    # fabricated, and the absence of a per-member publication is explicit.
    for other in votes:
        if other["proposal_id"] == DIVIDED_PROPOSAL_ID:
            continue
        assert other["method"] == "unanimous"
        assert other["member_vote_availability"] == "not_published"
        assert other["member_votes"] == []
        assert other["totals"] is None

    # Faction rows are an aggregation of the published member table.
    assert len(faction_votes) == 9
    for faction_vote in faction_votes:
        assert_valid("schemas/faction_vote.schema.json", faction_vote)
        assert faction_vote["vote_id"] == vote["id"]
    assert sum(fv["for_count"] for fv in faction_votes) == 64
    assert sum(fv["against_count"] for fv in faction_votes) == 3
    assert sum(fv["member_count"] for fv in faction_votes) == 68
    kyousan = next(fv for fv in faction_votes if fv["faction_name"] == "日本共産党名古屋市会議員団")
    assert kyousan["position"] == "against"
    assert kyousan["against_count"] == 3


def test_nagoya_expenses_reconcile() -> None:
    expenses = load_json(BASE / "political_activity_expenses.json")
    packets = load_json(BASE / "expense_evidence_packets.json")

    assert len(expenses) == 9
    assert len(packets) == 9
    assert {p["subject_id"] for p in packets} == {e["id"] for e in expenses}
    for expense in expenses:
        assert_valid("schemas/political_activity_expense.schema.json", expense)
        assert expense["assembly_id"] == ASSEMBLY_ID
        assert expense["fiscal_year"] == 2025
        assert expense["recipient_type"] == "faction"
        assert expense["report_status"] == "published"
        assert expense["receipt_access"] == "in_person_only"
        # The breakdown lists every category printed on the report form
        # (a printed zero is kept), and sums to the printed total spent.
        assert len(expense["breakdown"]) == 9
        assert sum(b["amount_yen"] for b in expense["breakdown"]) == expense["spent_yen"]
        # The residual is the printed one: granted + interest - spent, and
        # interest is never negative, so returned >= granted - spent.
        assert expense["returned_yen"] >= expense["granted_yen"] - expense["spent_yen"]
    for packet in packets:
        assert_valid("schemas/evidence_packet.schema.json", packet)
        assert packet["claims"][0]["source_ids"] == next(
            e["sources"] for e in expenses if e["id"] == packet["subject_id"]
        )

    jimin = next(e for e in expenses if e["recipient_name"] == "自由民主党名古屋市会議員団")
    assert jimin["granted_yen"] == 138_000_000
    assert jimin["spent_yen"] == 124_111_247
    assert jimin["returned_yen"] == 13_888_753


def test_nagoya_disclosure_profile_and_absences() -> None:
    profiles = load_json(BASE / "disclosure_profiles.json")
    assert len(profiles) == 1
    profile = profiles[0]
    assert_valid("schemas/disclosure_profile.schema.json", profile)
    items = {item["item"]: item for item in profile["items"]}
    assert items["member_votes"]["availability"] == "published"
    assert items["faction_votes"]["availability"] == "not_published"
    assert items["petition_results"]["availability"] == "not_published"
    assert items["inspection_trip_reports"]["availability"] == "not_published"
    assert items["political_activity_expense_receipts"]["availability"] == "restricted"

    # Committee inspection trips have no official publication unit, so —
    # following the Kitakyushu precedent — no trip records are created.
    assert not (BASE / "inspection_trips.json").exists()
    assert not (BASE / "inspection_evidence_packets.json").exists()


def test_nagoya_sources_resolve() -> None:
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
        "disclosure_profiles.json",
    ):
        missing = referenced_sources(load_json(BASE / name)) - ids
        assert missing == set(), f"{name}: unresolved sources {missing}"
