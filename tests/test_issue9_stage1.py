from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "reviewed" / "fukuoka-city" / "assembly"
ASSEMBLY_ID = "jp-local-401307-assembly-2023"
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


def test_stage1_records_match_contracts() -> None:
    sessions = load_json(BASE / "sessions.json")
    proposals = load_json(BASE / "proposals.json")
    votes = load_json(BASE / "votes.json")
    faction_votes = load_json(BASE / "faction_votes.json")
    packets = load_json(BASE / "proposal_vote_evidence_packets.json")

    assert len(sessions) == 1
    assert_valid("schemas/session.schema.json", sessions[0])
    assert sessions[0]["id"] == SESSION_ID
    assert sessions[0]["session_type"] == "regular"

    # The whole session as published: 122 executive proposals, 1 opinion
    # statement and 3 resolutions.
    assert len(proposals) == 126
    assert len(votes) == 126
    assert len(faction_votes) == 126 * 12
    for proposal in proposals:
        assert_valid("schemas/proposal.schema.json", proposal)
        assert proposal["assembly_id"] == ASSEMBLY_ID
        assert proposal["session_id"] == SESSION_ID
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


def test_stage1_member_votes_are_explicitly_not_published() -> None:
    votes = load_json(BASE / "votes.json")
    for vote in votes:
        assert vote["member_vote_availability"] == "not_published"
        assert vote["member_votes"] == []
        # No headcount is published (faction marks only), so totals stay null.
        assert vote["totals"] is None


def test_stage1_fy2026_budget_matches_issue6_facts() -> None:
    proposals = load_json(BASE / "proposals.json")
    votes = load_json(BASE / "votes.json")
    faction_votes = load_json(BASE / "faction_votes.json")
    fiscal_records = load_json(
        ROOT / "data" / "reviewed" / "fukuoka-city" / "fiscal_records.json"
    )

    budget = next(p for p in proposals if p["proposal_number"] == "第27号")
    assert budget["title"] == "令和８年度福岡市一般会計予算案"
    assert budget["kind"] == "budget"
    assert budget["decided_at"] == "2026-03-27"
    assert budget["outcome"] == "approved"

    fiscal_ids = {record["id"] for record in fiscal_records}
    assert budget["related_fiscal_record_ids"]
    assert set(budget["related_fiscal_record_ids"]) <= fiscal_ids

    vote = next(v for v in votes if v["proposal_id"] == budget["id"])
    rows = [fv for fv in faction_votes if fv["vote_id"] == vote["id"]]
    assert len(rows) == 12
    against = {row["faction_name"] for row in rows if row["position"] == "against"}
    assert against == {"福岡市民クラブ", "日本共産党福岡市議団", "無所属４"}
    members_for = sum(
        row["member_count"] or 0 for row in rows if row["position"] == "for"
    )
    members_against = sum(
        row["member_count"] or 0 for row in rows if row["position"] == "against"
    )
    # Consistent with the Issue #6 finding: approved by majority on 2026-03-27.
    assert members_for > members_against


def test_stage1_outcome_distribution_and_faction_names() -> None:
    proposals = load_json(BASE / "proposals.json")
    assembly = load_json(BASE / "assembly_records.json")[0]
    faction_votes = load_json(BASE / "faction_votes.json")

    outcomes: dict[str, int] = {}
    for proposal in proposals:
        outcomes[proposal["outcome"]] = outcomes.get(proposal["outcome"], 0) + 1
    # 125 approved (including approvals and consents), 1 rejected opinion.
    assert outcomes == {"approved": 125, "rejected": 1}

    known_factions = {f["name"] for f in assembly["factions"]} - {"無所属"}
    known_factions |= {f"無所属{i}" for i in "１２３４５"}
    assert {fv["faction_name"] for fv in faction_votes} == known_factions

    counts = {f["name"]: f["member_count"] for f in assembly["factions"]}
    for fv in faction_votes:
        if fv["faction_name"] in counts:
            assert fv["member_count"] == counts[fv["faction_name"]]
