from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "reviewed" / "hokkaido-prefecture" / "assembly"
ASSEMBLY_ID = "jp-local-010006-assembly-2023"
SESSION_ID = f"{ASSEMBLY_ID}-session-2026-3"
FACTION_NAMES = [
    "自民党・道民会議",
    "民主・道民連合",
    "北海道結志会",
    "公明党",
    "日本共産党",
    "北海道維新の会",
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
    assert assembly["seat_count"] == 100
    # 任期は前任期満了日（歴代議員名簿に公式明記）＋公職選挙法259条ただし書
    # ＋地方自治法140条の構成で確定（段階1の知事任期と同型）
    assert assembly["term_start"] == "2023-04-30"
    assert assembly["term_end"] == "2027-04-29"
    assert [f["name"] for f in assembly["factions"]] == FACTION_NAMES
    # 令和8年8月10日現在の会派別議員数（計96人、定数100人・欠員4人）
    assert sum(f["member_count"] for f in assembly["factions"]) == 96
    assert sessions[0]["id"] == SESSION_ID
    assert sessions[0]["start_date"] == "2026-09-08"
    assert sessions[0]["end_date"] == "2026-10-02"


def test_proposals_and_votes() -> None:
    proposals = load_json(BASE / "proposals.json")
    votes = load_json(BASE / "votes.json")
    faction_votes = load_json(BASE / "faction_votes.json")
    # 議案処理簿の61件（議案32・報告15・諮問2・会議案1・決議案2・意見案9）
    assert len(proposals) == 61
    assert faction_votes == []
    bills = [p for p in proposals if p["proposal_number"].startswith("第")]
    reports = [p for p in proposals if p["proposal_number"].startswith("報告")]
    consultations = [p for p in proposals if p["proposal_number"].startswith("諮問")]
    member_items = [p for p in proposals if p["submitted_by"] == "member"]
    assert len(bills) == 32
    assert len(reports) == 15
    assert len(consultations) == 2
    assert len(member_items) == 12  # 会議案1・決議案2・意見案9
    assert all(p["submitted_by"] == "executive" for p in bills + reports + consultations)
    # 継続審査7件（議案第19号＋決算の報告第1〜6号）は pending として登録
    pending = [p for p in proposals if p["outcome"] == "pending"]
    assert {p["proposal_number"] for p in pending} == {
        "第19号",
        "報告第1号",
        "報告第2号",
        "報告第3号",
        "報告第4号",
        "報告第5号",
        "報告第6号",
    }
    assert all(
        p["kind"] == "settlement" for p in pending if p["proposal_number"].startswith("報告")
    )
    # 報告のみ9件は議決対象外
    report_only = [p for p in proposals if p["outcome"] == "not_assessable"]
    assert len(report_only) == 9
    assert all(p["decided_at"] is None for p in report_only)
    assert len([p for p in proposals if p["outcome"] == "approved"]) == 45
    for proposal in proposals:
        assert_valid("schemas/proposal.schema.json", proposal)
    # 議決対象外の9件を除く52件に vote レコードがある。全件で議員個人別の
    # 賛否は公表なし（not_published）として登録し、内訳は作らない
    assert len(votes) == 52
    vote_by_proposal = {}
    for vote in votes:
        assert_valid("schemas/vote.schema.json", vote)
        assert vote["member_vote_availability"] == "not_published"
        assert vote["member_votes"] == []
        assert vote["totals"] is None
        assert vote["method"] == "unknown"
        vote_by_proposal[vote["proposal_id"]] = vote
    decided = {p["id"] for p in proposals if p["outcome"] != "not_assessable"}
    assert set(vote_by_proposal) == decided
    for proposal in proposals:
        if proposal["id"] in vote_by_proposal:
            assert vote_by_proposal[proposal["id"]]["outcome"] == proposal["outcome"]


def test_political_activity_expenses() -> None:
    expenses = load_json(BASE / "political_activity_expenses.json")
    # Web公表は集計のみのため、登録は年度×区分（会派分・議員分・合計）の6件
    assert len(expenses) == 6
    by_key = {(e["fiscal_year"], e["recipient_type"]): e for e in expenses}
    expected = {
        (2025, "faction"): (118000000, 111209435, 6790565),
        (2025, "member"): (507400000, 457111355, 61607618),
        (2025, "other"): (625400000, 568320790, 68398183),
        (2024, "faction"): (118600000, 109981128, 8618872),
        (2024, "member"): (509980000, 460369954, 58573991),
        (2024, "other"): (628580000, 570351082, 67192863),
    }
    assert set(by_key) == set(expected)
    for key, (granted, spent, returned) in expected.items():
        expense = by_key[key]
        assert_valid("schemas/political_activity_expense.schema.json", expense)
        assert expense["granted_yen"] == granted
        assert expense["spent_yen"] == spent
        assert expense["returned_yen"] == returned
        # 収支報告書自体はWeb公表されず、閲覧室での現地閲覧のみ
        assert expense["receipt_access"] == "in_person_only"
    for year in (2025, 2024):
        total = by_key[(year, "other")]
        parts = [by_key[(year, "faction")], by_key[(year, "member")]]
        for field in ("granted_yen", "spent_yen", "returned_yen"):
            assert total[field] == sum(part[field] for part in parts)


def test_disclosure_profile_and_inspection_absence() -> None:
    profiles = load_json(BASE / "disclosure_profiles.json")
    assert len(profiles) == 1
    profile = profiles[0]
    assert_valid("schemas/disclosure_profile.schema.json", profile)
    items = {item["item"]: item for item in profile["items"]}
    assert len(items) == 12
    # 会派別・議員個人別の賛否はいずれも公式公表なし
    assert items["faction_votes"]["availability"] == "not_published"
    assert items["member_votes"]["availability"] == "not_published"
    # 政活費は集計のみWeb公表、報告書・領収書は現地閲覧のみ
    assert items["political_activity_expense_reports"]["availability"] == "restricted"
    assert items["political_activity_expense_receipts"]["availability"] == "restricted"
    # 委員会視察・議員派遣の報告書は公表なし → 欠損登録
    assert items["inspection_trip_reports"]["availability"] == "not_published"
    trips = load_json(BASE / "inspection_trips.json")
    assert trips == []
    packets = load_json(BASE / "inspection_evidence_packets.json")
    assert len(packets) == 1
    assert_valid("schemas/evidence_packet.schema.json", packets[0])
    assert packets[0]["subject_id"] == ASSEMBLY_ID
    assert any("議員派遣" in q for q in packets[0]["open_questions"])


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
    assert len(vote_packets) == 52
    for packet in vote_packets:
        note = packet["claims"][0]["review_note"] or ""
        assert "公表されていないこと" in note
    assembly_packet = next(p for p in asm_packets if p["subject_type"] == "assembly")
    # 決算の結論は後続会期で更新する旨が open_questions に残っている
    assert any("第4回定例会" in q for q in assembly_packet["open_questions"])
    pending_packets = [
        p for p in pv_packets if p["subject_type"] == "proposal" and p["open_questions"]
    ]
    assert len(pending_packets) == 7


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
    catalog = load_json(ROOT / "data" / "catalog" / "hokkaido_assembly_sources.json")
    hokkaido_records = [
        r for r in catalog["records"] if r["municipality_key"] == "hokkaido-prefecture"
    ]
    assert len(hokkaido_records) == len(catalog["records"]) == 10
    assert_valid("schemas/source_catalog.schema.json", catalog)
