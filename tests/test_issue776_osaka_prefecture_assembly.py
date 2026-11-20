from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "reviewed" / "osaka-prefecture" / "assembly"
ASSEMBLY_ID = "jp-local-270008-assembly-2023"
SESSION_ID = f"{ASSEMBLY_ID}-session-2026-3"
FACTION_NAMES = [
    "大阪維新の会大阪府議会議員団",
    "公明党大阪府議会議員団",
    "自由民主党大阪府議会議員団",
    "民主ネット大阪府議会議員団",
    "日本共産党大阪府議会議員団",
    "政策会派 大大阪の和",
    "おおさか未来プロジェクト",
    "せっつ府民の会",
    "大阪つなぐ会",
]
EXPENSE_CATEGORIES_FACTION = [
    "調査研究費",
    "研修費",
    "広聴広報費",
    "要請陳情等活動費",
    "会議費",
    "資料作成費",
    "資料購入費",
    "事務費",
    "人件費",
]
# 議員用の様式には事務所費の行がある（10区分）
EXPENSE_CATEGORIES_MEMBER = [
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
    # 定数79人は府選管の任期満了一覧に条例定数として明記され、
    # 会派構成一覧表の合計とも一致する（二重確認）
    assert assembly["seat_count"] == 79
    assert assembly["term_start"] == "2023-04-30"
    assert assembly["term_end"] == "2027-04-29"
    # 会派名は対象会期の議決結果表の表記どおり（9会派）
    assert [f["name"] for f in assembly["factions"]] == FACTION_NAMES
    assert sum(f["member_count"] for f in assembly["factions"]) == 79
    assert sessions[0]["id"] == SESSION_ID
    assert sessions[0]["name"] == "令和8年9月定例会"
    assert sessions[0]["start_date"] == "2026-09-17"
    assert sessions[0]["end_date"] == "2026-10-20"


def test_proposals_and_votes() -> None:
    proposals = load_json(BASE / "proposals.json")
    votes = load_json(BASE / "votes.json")
    faction_votes = load_json(BASE / "faction_votes.json")
    # 令和8年9月定例会の登録対象79件（議案36・報告37・請願2・意見書案4）
    assert len(proposals) == 79
    bills = [p for p in proposals if p["proposal_number"].startswith("第")]
    reports = [p for p in proposals if p["proposal_number"].startswith("報告")]
    petitions = [p for p in proposals if p["proposal_number"].startswith("請願")]
    resolutions = [p for p in proposals if p["proposal_number"].startswith("意見書案")]
    assert len(bills) == 36
    assert len(reports) == 37
    assert len(petitions) == 2
    assert len(resolutions) == 4
    assert all(p["submitted_by"] == "executive" for p in bills + reports)
    assert all(p["submitted_by"] == "resident_petition" for p in petitions)
    assert all(p["submitted_by"] == "member" for p in resolutions)
    # 決算18件（報告第15〜32号）は継続審査 → pending で登録
    pending = [p for p in proposals if p["outcome"] == "pending"]
    assert len(pending) == 18
    assert all(p["kind"] == "settlement" for p in pending)
    assert {p["proposal_number"] for p in pending} == {f"報告第{n}号" for n in range(15, 33)}
    # 報告のうち議決不要19件は not_assessable
    report_only = [p for p in proposals if p["outcome"] == "not_assessable"]
    assert len(report_only) == 19
    assert all(p["decided_at"] is None for p in report_only)
    # 可決・同意・採択41件、不採択1件（請願第36号）
    assert len([p for p in proposals if p["outcome"] == "approved"]) == 41
    rejected = [p for p in proposals if p["outcome"] == "rejected"]
    assert [p["proposal_number"] for p in rejected] == ["請願第36号"]
    for proposal in proposals:
        assert_valid("schemas/proposal.schema.json", proposal)
    # vote は議案36＋決算18＋請願（第35号1・第36号は項目群2）＋意見書案4の61件
    assert len(votes) == 61
    vote_by_proposal: dict[str, list[dict[str, Any]]] = {}
    for vote in votes:
        assert_valid("schemas/vote.schema.json", vote)
        # 議員個人別の賛否は公表なし → 内訳は作らない
        assert vote["member_vote_availability"] == "not_published"
        assert vote["member_votes"] == []
        assert vote["totals"] is None
        assert vote["method"] == "unknown"
        vote_by_proposal.setdefault(vote["proposal_id"], []).append(vote)
    voted = {p["id"] for p in proposals if p["outcome"] != "not_assessable"}
    assert set(vote_by_proposal) == voted
    for proposal in proposals:
        for vote in vote_by_proposal.get(proposal["id"], []):
            assert vote["outcome"] == proposal["outcome"]
    # 請願第36号のみ項目別採決（第1〜4項／第5項）で vote が2件に分かれる
    petition36 = next(p for p in proposals if p["proposal_number"] == "請願第36号")
    p36_votes = vote_by_proposal[petition36["id"]]
    assert len(p36_votes) == 2
    assert {v["item_scope"] for v in p36_votes} == {
        "第1項、第2項、第3項、第4項",
        "第5項",
    }
    scoped = [v for v in votes if v["item_scope"] is not None]
    assert {v["id"] for v in scoped} == {v["id"] for v in p36_votes}
    # 会派別態度は採決された43 vote × 9会派 = 387件
    assert len(faction_votes) == 43 * 9
    fv_by_vote: dict[str, list[dict[str, Any]]] = {}
    for fv in faction_votes:
        assert_valid("schemas/faction_vote.schema.json", fv)
        # 人数集計は公表値（会派の所属議員数）のみで、賛否人数は作らない
        assert fv["for_count"] is None
        assert fv["against_count"] is None
        fv_by_vote.setdefault(fv["vote_id"], []).append(fv)
    marked = {v["id"] for v in votes if v["outcome"] != "pending"}
    assert set(fv_by_vote) == marked
    for _vote_id, rows in fv_by_vote.items():
        assert {r["faction_name"] for r in rows} == set(FACTION_NAMES)
    # 態度が分かれた代表例: 議案第36号は民主ネットとせっつ府民の会のみ反対
    bill36 = next(p for p in proposals if p["proposal_number"] == "第36号")
    bill36_rows = fv_by_vote[vote_by_proposal[bill36["id"]][0]["id"]]
    assert {r["faction_name"] for r in bill36_rows if r["position"] == "against"} == {
        "民主ネット大阪府議会議員団",
        "せっつ府民の会",
    }
    # 請願第36号は項目群で態度が異なる
    by_scope = {v["item_scope"]: fv_by_vote[v["id"]] for v in p36_votes}
    assert {
        r["faction_name"] for r in by_scope["第1項、第2項、第3項、第4項"] if r["position"] == "for"
    } == {
        "民主ネット大阪府議会議員団",
        "日本共産党大阪府議会議員団",
        "せっつ府民の会",
    }
    assert {r["faction_name"] for r in by_scope["第5項"] if r["position"] == "for"} == {
        "公明党大阪府議会議員団",
        "民主ネット大阪府議会議員団",
        "日本共産党大阪府議会議員団",
        "政策会派 大大阪の和",
        "せっつ府民の会",
    }


def test_political_activity_expenses() -> None:
    expenses = load_json(BASE / "political_activity_expenses.json")
    # 令和7年度分の89単位（会派9＋議員80）を単位ごとに登録
    assert len(expenses) == 89
    factions = [e for e in expenses if e["recipient_type"] == "faction"]
    members = [e for e in expenses if e["recipient_type"] == "member"]
    assert len(factions) == 9
    assert len(members) == 80
    for expense in expenses:
        assert_valid("schemas/political_activity_expense.schema.json", expense)
        assert expense["fiscal_year"] == 2025
        # 収支報告書・領収書ともポータルでオンライン公開
        assert expense["receipt_access"] == "online"
        assert expense["report_status"] == "published"
        # 費目別内訳（会派9区分・議員10区分）が合計と一致する
        breakdown = expense["breakdown"]
        expected = (
            EXPENSE_CATEGORIES_FACTION
            if expense["recipient_type"] == "faction"
            else EXPENSE_CATEGORIES_MEMBER
        )
        assert [b["category"] for b in breakdown] == expected
        assert sum(b["amount_yen"] for b in breakdown) == expense["spent_yen"]
        # 収入−支出=残額（支出超過の単位は残額0として印字どおり登録）
        assert expense["granted_yen"] - expense["spent_yen"] == expense["returned_yen"] or (
            expense["spent_yen"] > expense["granted_yen"] and expense["returned_yen"] == 0
        )
    by_name = {e["recipient_name"]: e for e in expenses}
    # 実物確認済みの代表値（最大会派と支出超過の単位）
    ishin = by_name["大阪維新の会大阪府議会議員団"]
    assert ishin["granted_yen"] == 51981612
    assert ishin["spent_yen"] == 51710390
    assert ishin["returned_yen"] == 271222
    mirai = by_name["おおさか未来プロジェクト"]
    assert mirai["granted_yen"] == 120000
    assert mirai["spent_yen"] == 120645
    assert mirai["returned_yen"] == 0


def test_disclosure_profile_and_inspection_absence() -> None:
    profiles = load_json(BASE / "disclosure_profiles.json")
    assert len(profiles) == 1
    profile = profiles[0]
    assert_valid("schemas/disclosure_profile.schema.json", profile)
    items = {item["item"]: item for item in profile["items"]}
    assert len(items) == 12
    # 会派別態度は議決結果表に併記されて公表、議員個人別は公表なし
    assert items["faction_votes"]["availability"] == "published"
    assert items["member_votes"]["availability"] == "not_published"
    # 政活費は収支報告書・領収書ともポータルで公開
    assert items["political_activity_expense_reports"]["availability"] == "published"
    assert items["political_activity_expense_receipts"]["availability"] == "published"
    # 陳情は委員会審査・本会議決定を行わない制度である旨が注記されている
    assert "陳情" in (items["petition_results"]["note"] or "")
    # 委員会視察の報告書は体系的公表を特定できず → 欠損登録
    assert items["inspection_trip_reports"]["availability"] == "not_published"
    trips = load_json(BASE / "inspection_trips.json")
    assert trips == []
    packets = load_json(BASE / "inspection_evidence_packets.json")
    assert len(packets) == 1
    assert_valid("schemas/evidence_packet.schema.json", packets[0])
    assert packets[0]["subject_id"] == ASSEMBLY_ID
    assert packets[0]["open_questions"]


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
    # 会派別態度を記録した vote のパケットには、確定結果である旨の区別が
    # 注記されている（採決前の確認態度ではない）
    faction_votes = load_json(BASE / "faction_votes.json")
    marked_vote_ids = {fv["vote_id"] for fv in faction_votes}
    vote_packets = [
        p for p in pv_packets if p["subject_type"] == "vote" and p["subject_id"] in marked_vote_ids
    ]
    assert len(vote_packets) == 43
    for packet in vote_packets:
        note = packet["claims"][0]["review_note"] or ""
        assert "確定結果" in note
        assert "確認した態度" in note
    assembly_packet = next(p for p in asm_packets if p["subject_type"] == "assembly")
    # 決算の結論は後続会期で更新する旨が open_questions に残っている
    assert any("継続審査" in q for q in assembly_packet["open_questions"])


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
    catalog = load_json(ROOT / "data" / "catalog" / "osaka_prefecture_assembly_sources.json")
    osaka_records = [r for r in catalog["records"] if r["municipality_key"] == "osaka-prefecture"]
    # 汎用19件＋政活費の単位別出典89件
    assert len(osaka_records) == len(catalog["records"]) == 19 + 89
    assert_valid("schemas/source_catalog.schema.json", catalog)
