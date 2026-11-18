from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "reviewed" / "fukuoka-prefecture" / "assembly"
ASSEMBLY_ID = "jp-local-400009-assembly-2023"
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


def test_stage3_records_match_contracts() -> None:
    sessions = load_json(BASE / "sessions.json")
    proposals = load_json(BASE / "proposals.json")
    votes = load_json(BASE / "votes.json")
    faction_votes = load_json(BASE / "faction_votes.json")
    packets = load_json(BASE / "proposal_vote_evidence_packets.json")

    assert len(sessions) == 1
    assert_valid("schemas/session.schema.json", sessions[0])
    assert sessions[0]["id"] == SESSION_ID
    assert sessions[0]["session_type"] == "regular"
    # Unlike stages 1-2, the prefecture publishes the session schedule:
    # opened 2026-02-20, closed 2026-03-24.
    assert sessions[0]["start_date"] == "2026-02-20"
    assert sessions[0]["end_date"] == "2026-03-24"

    # The whole session as published: 87 executive proposals,
    # 4 committee proposals and 1 consultation. The prefecture publishes
    # no faction breakdown, so there are no faction votes at all.
    assert len(proposals) == 92
    assert len(votes) == 92
    assert faction_votes == []
    for proposal in proposals:
        assert_valid("schemas/proposal.schema.json", proposal)
        assert proposal["assembly_id"] == ASSEMBLY_ID
        assert proposal["session_id"] == SESSION_ID
        # No supplementary resolution was attached to any proposal in
        # this session's published results.
        assert proposal["parent_proposal_id"] is None
    for vote in votes:
        assert_valid("schemas/vote.schema.json", vote)
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


def test_stage3_member_votes_are_explicitly_not_published() -> None:
    votes = load_json(BASE / "votes.json")
    for vote in votes:
        assert vote["member_vote_availability"] == "not_published"
        assert vote["member_votes"] == []
        # The prefecture publishes only collective result wording per
        # decision date: no faction or member breakdown, totals stay null.
        assert vote["totals"] is None


def test_stage3_fy2026_budget_matches_issue6_facts() -> None:
    proposals = load_json(BASE / "proposals.json")
    fiscal_records = load_json(
        ROOT / "data" / "reviewed" / "fukuoka-prefecture" / "fiscal_records.json"
    )

    budget = next(p for p in proposals if p["proposal_number"] == "第1号")
    assert budget["title"] == "令和8年度福岡県一般会計予算"
    assert budget["kind"] == "budget"
    assert budget["decided_at"] == "2026-03-24"
    assert budget["outcome"] == "approved"

    # The prefecture's FY2026 fiscal records registered under Issue #6
    # hold total revenue and local tax only (no total-expenditure record
    # exists), so the link covers exactly those two records.
    fiscal_ids = {record["id"] for record in fiscal_records}
    assert budget["related_fiscal_record_ids"] == [
        "jp-local-400009-fiscal-2026-total-revenue",
        "jp-local-400009-fiscal-2026-local-tax",
    ]
    assert set(budget["related_fiscal_record_ids"]) <= fiscal_ids


def test_stage3_dates_kinds_and_outcome_distribution() -> None:
    proposals = load_json(BASE / "proposals.json")

    outcomes: dict[str, int] = {}
    decided: dict[str, int] = {}
    kinds: dict[str, int] = {}
    for proposal in proposals:
        outcomes[proposal["outcome"]] = outcomes.get(proposal["outcome"], 0) + 1
        decided[proposal["decided_at"]] = decided.get(proposal["decided_at"], 0) + 1
        kinds[proposal["kind"]] = kinds.get(proposal["kind"], 0) + 1
    # Every published item was approved with the collective wording
    # "原案のとおり可決" (2026-03-10 group) or "原案のとおり可決、承認
    # または同意" (2026-03-24 group); the consultation was decided as a
    # recommendation to dismiss the review request.
    assert outcomes == {"approved": 92}
    assert decided == {"2026-03-10": 27, "2026-03-24": 65}
    assert kinds == {"budget": 34, "ordinance": 30, "other": 27, "personnel": 1}

    by_number = {p["proposal_number"]: p for p in proposals}
    # Executive proposals: 第1号-第67号 submitted 2026-02-20,
    # 第68号-第87号 submitted 2026-03-02 (submissions page).
    for num in range(1, 68):
        assert by_number[f"第{num}号"]["submitted_at"] == "2026-02-20"
        assert by_number[f"第{num}号"]["submitted_by"] == "executive"
    for num in range(68, 88):
        assert by_number[f"第{num}号"]["submitted_at"] == "2026-03-02"
    # Early-decision group voted on 2026-03-10.
    for num in (21, 22, 30, 48, *range(68, 88)):
        assert by_number[f"第{num}号"]["decided_at"] == "2026-03-10"
    # Committee proposals carry no published submission date.
    for num in (4, 5, 6, 7):
        committee_proposal = by_number[f"委員会提出第{num}号"]
        assert committee_proposal["submitted_by"] == "committee"
        assert committee_proposal["submitted_at"] is None
    # The consultation was submitted with the opening-day batch and
    # decided in the early-decision group on 2026-03-10.
    consultation = by_number["諮問第1号"]
    assert consultation["submitted_at"] == "2026-02-20"
    assert consultation["decided_at"] == "2026-03-10"
    assert consultation["title"] == (
        "退職手当支給制限処分に対する審査請求に関する諮問について"
    )
