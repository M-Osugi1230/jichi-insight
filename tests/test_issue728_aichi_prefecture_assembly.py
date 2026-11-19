from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "reviewed" / "aichi-prefecture" / "assembly"
ASSEMBLY_ID = "jp-local-230006-assembly-2023"
SESSION_ID = f"{ASSEMBLY_ID}-session-2026-1"
FACTION_NAMES = [
    "自由民主党愛知県議員団",
    "あいち民主県議団",
    "公明党愛知県議員団",
    "減税日本愛知県議員団",
    "無所属",
]


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


def test_assembly_and_session_match_contracts() -> None:
    assemblies = load_json(BASE / "assembly_records.json")
    sessions = load_json(BASE / "sessions.json")
    assert len(assemblies) == 1
    assert len(sessions) == 1
    assembly = assemblies[0]
    assert_valid("schemas/assembly.schema.json", assembly)
    assert_valid("schemas/session.schema.json", sessions[0])
    assert assembly["id"] == ASSEMBLY_ID
    assert assembly["seat_count"] == 102
    assert assembly["term_start"] == "2023-04-30"
    assert assembly["term_end"] == "2027-04-29"
    assert [f["name"] for f in assembly["factions"]] == FACTION_NAMES
    assert sum(f["member_count"] for f in assembly["factions"]) == 97
    assert sessions[0]["id"] == SESSION_ID
    assert sessions[0]["start_date"] == "2026-06-15"
    assert sessions[0]["end_date"] == "2026-07-02"


def test_proposals_votes_and_faction_votes() -> None:
    proposals = load_json(BASE / "proposals.json")
    votes = load_json(BASE / "votes.json")
    faction_votes = load_json(BASE / "faction_votes.json")
    assert len(proposals) == 58
    assert len(votes) == 58
    assert len(faction_votes) == 290
    bills = [p for p in proposals if p["kind"] != "petition"]
    petitions = [p for p in proposals if p["kind"] == "petition"]
    assert len(bills) == 32
    assert len(petitions) == 26
    assert {p["proposal_number"] for p in bills} == {f"第{n}号" for n in range(100, 132)}
    assert {p["proposal_number"] for p in petitions} == {f"第{n}号" for n in range(1, 27)}
    assert all(p["submitted_by"] == "executive" for p in bills)
    assert all(p["submitted_by"] == "resident_petition" for p in petitions)
    assert all(p["outcome"] == "approved" for p in bills)
    assert all(p["outcome"] == "rejected" for p in petitions)
    assert all(p["decided_at"] == "2026-07-02" for p in proposals)
    # 継続審査中の令和7年度第24号請願は登録対象外
    assert all("選挙区" not in p["title"] for p in proposals)
    for proposal in proposals:
        assert_valid("schemas/proposal.schema.json", proposal)
    vote_by_proposal = {}
    for vote in votes:
        assert_valid("schemas/vote.schema.json", vote)
        assert vote["member_vote_availability"] == "not_published"
        assert vote["member_votes"] == []
        assert vote["totals"] is None
        vote_by_proposal[vote["proposal_id"]] = vote
    assert set(vote_by_proposal) == {p["id"] for p in proposals}
    by_vote: dict[str, list[dict[str, Any]]] = {}
    for fv in faction_votes:
        assert_valid("schemas/faction_vote.schema.json", fv)
        by_vote.setdefault(fv["vote_id"], []).append(fv)
    assert set(by_vote) == {v["id"] for v in votes}
    for proposal in proposals:
        vote = vote_by_proposal[proposal["id"]]
        rows = by_vote[vote["id"]]
        assert [r["faction_name"] for r in rows] == FACTION_NAMES
        for row in rows[:4]:
            expected = "for" if proposal["kind"] != "petition" else "against"
            assert row["position"] == expected
            assert row["for_count"] is None and row["against_count"] is None
        independent = rows[4]
        if independent["position"] == "split":
            # 態度PDFの印字どおり（合計9人。名簿の10名とは一致しない）
            assert independent["for_count"] + independent["against_count"] == 9
        else:
            assert independent["position"] == "for"
            assert proposal["kind"] != "petition"


def test_political_activity_expenses() -> None:
    expenses = load_json(BASE / "political_activity_expenses.json")
    assert len(expenses) == 103
    factions = [e for e in expenses if e["recipient_type"] == "faction"]
    members = [e for e in expenses if e["recipient_type"] == "member"]
    assert len(factions) == 4
    assert len(members) == 99
    assert {e["recipient_name"] for e in factions} == {
        "自由民主党愛知県議員団",
        "あいち民主県議団",
        "公明党愛知県議員団",
        "日本共産党愛知県議会議員団",
    }
    for expense in expenses:
        assert_valid("schemas/political_activity_expense.schema.json", expense)
        assert expense["fiscal_year"] == 2025
        assert expense["report_status"] == "published"
        assert expense["receipt_access"] == "online"
        total = sum(item["amount_yen"] for item in expense["breakdown"])
        assert total == expense["spent_yen"]
        assert expense["granted_yen"] - expense["spent_yen"] == expense["returned_yen"]


def test_disclosure_profile_and_inspection_absence() -> None:
    profiles = load_json(BASE / "disclosure_profiles.json")
    assert len(profiles) == 1
    profile = profiles[0]
    assert_valid("schemas/disclosure_profile.schema.json", profile)
    items = {item["item"]: item for item in profile["items"]}
    assert len(items) == 12
    assert items["faction_votes"]["availability"] == "published"
    assert items["faction_votes"]["granularity"] == "faction"
    assert "議会運営委員会" in items["faction_votes"]["note"]
    assert items["member_votes"]["availability"] == "not_published"
    assert items["political_activity_expense_receipts"]["availability"] == "published"
    assert items["inspection_trip_reports"]["availability"] == "not_published"
    trips = load_json(BASE / "inspection_trips.json")
    assert trips == []
    packets = load_json(BASE / "inspection_evidence_packets.json")
    assert len(packets) == 1
    assert_valid("schemas/evidence_packet.schema.json", packets[0])
    assert packets[0]["subject_id"] == ASSEMBLY_ID


def test_evidence_packets_cover_records() -> None:
    proposals = load_json(BASE / "proposals.json")
    votes = load_json(BASE / "votes.json")
    expenses = load_json(BASE / "political_activity_expenses.json")
    pv_packets = load_json(BASE / "proposal_vote_evidence_packets.json")
    ex_packets = load_json(BASE / "expense_evidence_packets.json")
    asm_packets = load_json(BASE / "assembly_evidence_packets.json")
    for packet in pv_packets + ex_packets + asm_packets:
        assert_valid("schemas/evidence_packet.schema.json", packet)
    pv_subjects = {p["subject_id"] for p in pv_packets}
    assert pv_subjects == {p["id"] for p in proposals} | {v["id"] for v in votes}
    assert {p["subject_id"] for p in ex_packets} == {e["id"] for e in expenses}
    vote_packets = [p for p in pv_packets if p["subject_type"] == "vote"]
    assert len(vote_packets) == 58
    for packet in vote_packets:
        note = packet["claims"][0]["review_note"] or ""
        assert "投票記録そのものではない" in note
    assembly_packet = next(p for p in asm_packets if p["subject_type"] == "assembly")
    assert any("第24号" in q for q in assembly_packet["open_questions"])


def test_all_referenced_sources_exist_in_catalog() -> None:
    known = catalog_source_ids()
    files = [
        "assembly_records.json",
        "sessions.json",
        "proposals.json",
        "votes.json",
        "faction_votes.json",
        "political_activity_expenses.json",
        "disclosure_profiles.json",
        "assembly_evidence_packets.json",
        "proposal_vote_evidence_packets.json",
        "expense_evidence_packets.json",
        "inspection_evidence_packets.json",
    ]
    for name in files:
        missing = referenced_sources(load_json(BASE / name)) - known
        assert missing == set(), f"{name}: {missing}"
    catalog = load_json(ROOT / "data" / "catalog" / "aichi_assembly_sources.json")
    aichi_records = [r for r in catalog["records"] if r["municipality_key"] == "aichi-prefecture"]
    assert len(aichi_records) == len(catalog["records"]) == 112
    assert_valid("schemas/source_catalog.schema.json", catalog)
