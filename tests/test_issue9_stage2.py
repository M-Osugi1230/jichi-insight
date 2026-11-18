from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "reviewed" / "kitakyushu-city" / "assembly"
ASSEMBLY_ID = "jp-local-401005-assembly-2025"
SESSION_ID = f"{ASSEMBLY_ID}-session-2026-1"


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


def test_stage2_records_match_contracts() -> None:
    sessions = load_json(BASE / "sessions.json")
    proposals = load_json(BASE / "proposals.json")
    votes = load_json(BASE / "votes.json")
    faction_votes = load_json(BASE / "faction_votes.json")
    packets = load_json(BASE / "proposal_vote_evidence_packets.json")

    assert len(sessions) == 1
    assert_valid("schemas/session.schema.json", sessions[0])
    assert sessions[0]["id"] == SESSION_ID
    assert sessions[0]["session_type"] == "regular"

    # The whole session as published: 68 executive proposals and
    # 11 member proposals, each with a faction row for all 8 factions.
    assert len(proposals) == 79
    assert len(votes) == 79
    assert len(faction_votes) == 79 * 8
    for proposal in proposals:
        assert_valid("schemas/proposal.schema.json", proposal)
        assert proposal["assembly_id"] == ASSEMBLY_ID
        assert proposal["session_id"] == SESSION_ID
        # The results table does not publish submission dates.
        assert proposal["submitted_at"] is None
        # No supplementary resolution was attached to any proposal in
        # this session's published results.
        assert proposal["parent_proposal_id"] is None
    for vote in votes:
        assert_valid("schemas/vote.schema.json", vote)
    for faction_vote in faction_votes:
        assert_valid("schemas/faction_vote.schema.json", faction_vote)
    for packet in packets:
        assert_valid("schemas/evidence_packet.schema.json", packet)

    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in [*proposals, *votes]
    }
    assert {vote["proposal_id"] for vote in votes} == {
        proposal["id"] for proposal in proposals
    }

    references = referenced_sources([sessions, proposals, votes, faction_votes, packets])
    assert references <= catalog_source_ids()


def test_stage2_member_votes_are_explicitly_not_published() -> None:
    votes = load_json(BASE / "votes.json")
    for vote in votes:
        assert vote["member_vote_availability"] == "not_published"
        assert vote["member_votes"] == []
        # No headcount is published (faction marks only), so totals stay null.
        assert vote["totals"] is None


def test_stage2_fy2026_budget_matches_issue6_facts() -> None:
    proposals = load_json(BASE / "proposals.json")
    votes = load_json(BASE / "votes.json")
    faction_votes = load_json(BASE / "faction_votes.json")
    fiscal_records = load_json(
        ROOT / "data" / "reviewed" / "kitakyushu-city" / "fiscal_records.json"
    )

    budget = next(p for p in proposals if p["proposal_number"] == "第1号")
    assert budget["title"] == "令和８年度北九州市一般会計予算"
    assert budget["kind"] == "budget"
    assert budget["decided_at"] == "2026-03-25"
    assert budget["outcome"] == "approved"

    fiscal_ids = {record["id"] for record in fiscal_records}
    assert budget["related_fiscal_record_ids"] == [
        "jp-local-401005-fiscal-2026-total-revenue",
        "jp-local-401005-fiscal-2026-local-tax",
        "jp-local-401005-fiscal-2026-total-expenditure",
    ]
    assert set(budget["related_fiscal_record_ids"]) <= fiscal_ids

    vote = next(v for v in votes if v["proposal_id"] == budget["id"])
    rows = [fv for fv in faction_votes if fv["vote_id"] == vote["id"]]
    assert len(rows) == 8
    against = {row["faction_name"] for row in rows if row["position"] == "against"}
    assert against == {"日本共産党北九州市会議員団", "緑の風"}
    members_for = sum(
        row["member_count"] or 0 for row in rows if row["position"] == "for"
    )
    members_against = sum(
        row["member_count"] or 0 for row in rows if row["position"] == "against"
    )
    # Consistent with the Issue #6 finding: approved on 2026-03-25.
    assert members_for > members_against


def test_stage2_outcome_distribution_and_faction_names() -> None:
    proposals = load_json(BASE / "proposals.json")
    assembly = load_json(BASE / "assembly_records.json")[0]
    faction_votes = load_json(BASE / "faction_votes.json")

    outcomes: dict[str, int] = {}
    for proposal in proposals:
        outcomes[proposal["outcome"]] = outcomes.get(proposal["outcome"], 0) + 1
    # All 68 executive proposals approved (including the one report
    # approval and the two personnel consents); of the 11 member
    # proposals, 5 approved and 6 opinion statements rejected.
    assert outcomes == {"approved": 73, "rejected": 6}

    assert {fv["faction_name"] for fv in faction_votes} == {
        faction["name"] for faction in assembly["factions"]
    }

    counts = {f["name"]: f["member_count"] for f in assembly["factions"]}
    for fv in faction_votes:
        assert fv["member_count"] == counts[fv["faction_name"]]
        # This session's published table uses only for/against marks:
        # no faction is recorded as split or absent.
        assert fv["position"] in {"for", "against"}
        assert fv["for_count"] is None
        assert fv["against_count"] is None
