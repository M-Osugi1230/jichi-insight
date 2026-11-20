from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "reviewed" / "kanagawa-prefecture" / "assembly"
ASSEMBLY_ID = "jp-local-140007-assembly-2023"
SESSION_ID = f"{ASSEMBLY_ID}-session-2026-2"
FACTION_NAMES = [
    "自由民主党神奈川県議会議員団",
    "立憲民主党・かながわクラブ神奈川県議会議員団",
    "かながわ未来神奈川県議会議員団",
    "公明党神奈川県議会議員団",
    "県政会・立憲民主神奈川ネット神奈川県議会議員団",
    "日本共産党神奈川県議会議員団",
    "日本維新の会神奈川県議会議員団",
    "中原・高津の会神奈川県議会議員団",
    "わが町",
    "神奈川を変える港南の会",
    "創和会",
    "翼の会",
    "厚木愛川清川の会",
]
EXPENSE_CATEGORIES = [
    "調査研究費",
    "研修費",
    "会合参加費",
    "広報・広聴費",
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
    # 定数105人・現員99人は「議会の組織」（令和8年6月1日現在）に明記され、
    # 会派別現員の合計とも一致する
    assert assembly["seat_count"] == 105
    assert assembly["term_start"] == "2023-04-30"
    assert assembly["term_end"] == "2027-04-29"
    assert [f["name"] for f in assembly["factions"]] == FACTION_NAMES
    assert sum(f["member_count"] for f in assembly["factions"]) == 99
    assert sessions[0]["id"] == SESSION_ID
    assert sessions[0]["name"] == "令和8年第2回定例会"
    assert sessions[0]["start_date"] == "2026-05-18"
    assert sessions[0]["end_date"] == "2026-07-13"


def test_proposals_and_votes() -> None:
    proposals = load_json(BASE / "proposals.json")
    votes = load_json(BASE / "votes.json")
    faction_votes = load_json(BASE / "faction_votes.json")
    # 令和8年第2回定例会の登録対象45件
    # （知事提出31・議員派遣5・意見書7・決議1・請願1）
    assert len(proposals) == 45
    executive = [p for p in proposals if p["submitted_by"] == "executive"]
    member = [p for p in proposals if p["submitted_by"] == "member"]
    petition = [p for p in proposals if p["submitted_by"] == "resident_petition"]
    assert len(executive) == 31
    assert len(member) == 13
    assert len(petition) == 1
    assert petition[0]["proposal_number"] == "請願第36号"
    assert petition[0]["kind"] == "petition"
    kinds = {}
    for p in proposals:
        kinds[p["kind"]] = kinds.get(p["kind"], 0) + 1
    assert kinds == {
        "personnel": 3,
        "budget": 3,
        "ordinance": 13,
        "resolution": 8,
        "petition": 1,
        "other": 17,
    }
    # 全件が印字どおり approved（原案可決・同意・承認・可決・採択）
    assert all(p["outcome"] == "approved" for p in proposals)
    # 意見書・決議は案番号が公表されていないため番号なしで登録
    unnumbered = [p for p in proposals if "番号の公表なし" in p["proposal_number"]]
    assert len(unnumbered) == 8
    assert all(p["kind"] == "resolution" for p in unnumbered)
    for proposal in proposals:
        assert_valid("schemas/proposal.schema.json", proposal)
    assert len(votes) == 45
    vote_by_proposal = {}
    for vote in votes:
        assert_valid("schemas/vote.schema.json", vote)
        # 議員個人別の賛否は公表なし → 内訳は作らない
        assert vote["member_vote_availability"] == "not_published"
        assert vote["member_votes"] == []
        assert vote["totals"] is None
        assert vote["method"] == "unknown"
        vote_by_proposal[vote["proposal_id"]] = vote
    assert set(vote_by_proposal) == {p["id"] for p in proposals}
    # 会派別賛否は知事提出31件＋議員派遣5件 = 36 vote × 13会派 = 468件
    assert len(faction_votes) == 36 * 13
    fv_by_vote: dict[str, list[dict[str, Any]]] = {}
    for fv in faction_votes:
        assert_valid("schemas/faction_vote.schema.json", fv)
        # 人数集計は公表値（会派の現員）のみで、賛否人数は作らない
        assert fv["for_count"] is None
        assert fv["against_count"] is None
        fv_by_vote.setdefault(fv["vote_id"], []).append(fv)
    assert len(fv_by_vote) == 36
    for rows in fv_by_vote.values():
        assert {r["faction_name"] for r in rows} == set(FACTION_NAMES)

    def against_numbers(number: str) -> set[str]:
        prop = next(p for p in proposals if p["proposal_number"] == number)
        rows = fv_by_vote[vote_by_proposal[prop["id"]]["id"]]
        return {r["faction_name"] for r in rows if r["position"] == "against"}

    # 賛否が分かれたのは13件: 共産・翼会の両方反対9件、共産のみ3件、翼会のみ1件
    both = {"日本共産党神奈川県議会議員団", "翼の会"}
    assert against_numbers("県報第1号") == both
    assert against_numbers("定県第42号") == both
    assert against_numbers("議員派遣第35号") == both
    assert against_numbers("県報第2号") == {"日本共産党神奈川県議会議員団"}
    assert against_numbers("定県第57号") == {"日本共産党神奈川県議会議員団"}
    # 議員派遣第33号は原典HTMLで共産のみ反対（棚卸し段階の集計との差異を
    # 証拠パケットに記録済み）
    assert against_numbers("議員派遣第33号") == {"日本共産党神奈川県議会議員団"}
    assert against_numbers("定県第40号") == {"翼の会"}
    split_votes = [vid for vid, rows in fv_by_vote.items()
                   if any(r["position"] == "against" for r in rows)]
    assert len(split_votes) == 13


def test_political_activity_expenses() -> None:
    expenses = load_json(BASE / "political_activity_expenses.json")
    # 令和7年度分の19単位（会派交付6＋議員交付13）
    assert len(expenses) == 19
    factions = [e for e in expenses if e["recipient_type"] == "faction"]
    members = [e for e in expenses if e["recipient_type"] == "member"]
    assert len(factions) == 6
    assert len(members) == 13
    for expense in expenses:
        assert_valid("schemas/political_activity_expense.schema.json", expense)
        assert expense["fiscal_year"] == 2025
        assert expense["report_status"] == "published"
        # 令和7年度分の会計帳簿・証拠書類等は未公開
        assert expense["receipt_access"] == "not_published"
        # 科目別内訳（11区分）が支出合計額と一致する
        breakdown = expense["breakdown"]
        assert [b["category"] for b in breakdown] == EXPENSE_CATEGORIES
        assert sum(b["amount_yen"] for b in breakdown) == expense["spent_yen"]
    # 一覧表（修正版）の総計行と一致する
    assert sum(e["granted_yen"] for e in expenses) == 634940000
    assert sum(e["spent_yen"] for e in expenses) == 655380181
    assert sum(e["returned_yen"] for e in expenses) == 2716464
    by_name = {e["recipient_name"]: e for e in expenses}
    # 支出が収入（交付金＋利息）を上回る最大会派は残額0の印字どおり
    jimin = by_name["自由民主党神奈川県議会議員団"]
    assert jimin["granted_yen"] == 291500000
    assert jimin["spent_yen"] == 309875422
    assert jimin["returned_yen"] == 0
    komei = by_name["公明党神奈川県議会議員団"]
    assert komei["granted_yen"] == 50880000
    assert komei["spent_yen"] == 50107082
    assert komei["returned_yen"] == 773723
    aoki = by_name["青木マキ"]
    assert aoki["returned_yen"] == 1718325


def test_disclosure_profile() -> None:
    profiles = load_json(BASE / "disclosure_profiles.json")
    assert len(profiles) == 1
    profile = profiles[0]
    assert_valid("schemas/disclosure_profile.schema.json", profile)
    items = {item["item"]: item for item in profile["items"]}
    assert len(items) == 12
    # 会派別賛否は審議結果一覧に併記されて公表、議員個人別は公表なし
    assert items["faction_votes"]["availability"] == "published"
    assert items["member_votes"]["availability"] == "not_published"
    # 政活費は収支報告書まで公開、証拠書類等は未公開
    assert items["political_activity_expense_reports"]["availability"] == "published"
    assert items["political_activity_expense_receipts"]["availability"] == "not_published"
    # 請願は採択分のみの一覧で、不採択・継続審査分の一覧がない旨が注記されている
    assert "不採択" in (items["petition_results"]["note"] or "")
    # 委員会調査報告書は集約ページで公開
    assert items["inspection_trip_reports"]["availability"] == "published"


def test_inspection_trips() -> None:
    trips = load_json(BASE / "inspection_trips.json")
    # 現任期分（2023年4月30日以降実施）の79件（県外41・県内38）
    assert len(trips) == 79
    for trip in trips:
        assert_valid("schemas/inspection_trip.schema.json", trip)
        assert trip["start_date"] >= "2023-04-30"
        # 費用は報告書に記載がない
        assert trip["cost_status"] == "not_published"
        assert trip["total_cost_yen"] is None
        assert trip["report_status"] == "published"
        assert trip["participant_count"] == len(trip["participants"])
        assert all(p["participant_type"] == "elected_member" for p in trip["participants"])
    # 海外調査は3件（ベトナム・シンガポール・香港）
    overseas = [t for t in trips if t["trip_type"] == "overseas"]
    assert len(overseas) == 3
    # 出席委員1名の形式で公表された報告書が4件（いずれも井坂新哉）
    solo = [t for t in trips if t["participant_count"] == 1]
    assert len(solo) == 4
    assert all(t["participants"][0]["name"] == "井坂新哉" for t in solo)
    # 代表例: 2023年8月22日の総務政策常任委員会（佐渡・新潟）は13人
    sado = next(t for t in trips
                if t["start_date"] == "2023-08-22" and "総務政策" in t["title"])
    assert sado["participant_count"] == 13
    assert sado["participants"][0]["name"] == "田中徳一郎"
    assert sado["participants"][0]["role"] == "委員長"
    # 2025年2月28日の厚生常任委員会（中井やまゆり園）は欠員1名の委員会で12人
    nakai = next(t for t in trips if t["start_date"] == "2025-02-28")
    assert nakai["participant_count"] == 12
    assert nakai["destinations"] == ["神奈川県中井町"]


def test_evidence_packets_cover_records() -> None:
    proposals = load_json(BASE / "proposals.json")
    votes = load_json(BASE / "votes.json")
    expenses = load_json(BASE / "political_activity_expenses.json")
    trips = load_json(BASE / "inspection_trips.json")
    pv_packets = load_json(BASE / "proposal_vote_evidence_packets.json")
    ex_packets = load_json(BASE / "expense_evidence_packets.json")
    asm_packets = load_json(BASE / "assembly_evidence_packets.json")
    insp_packets = load_json(BASE / "inspection_evidence_packets.json")
    for packet in pv_packets + ex_packets + asm_packets + insp_packets:
        assert_valid("schemas/evidence_packet.schema.json", packet)
    pv_subjects = {p["subject_id"] for p in pv_packets}
    assert pv_subjects == {p["id"] for p in proposals} | {v["id"] for v in votes}
    assert {p["subject_id"] for p in ex_packets} == {e["id"] for e in expenses}
    assert {p["subject_id"] for p in insp_packets} == {t["id"] for t in trips}
    # 会派別賛否を記録した vote のパケットには、確定結果である旨と
    # ▲への変換を行っていない旨が注記されている
    faction_votes = load_json(BASE / "faction_votes.json")
    marked_vote_ids = {fv["vote_id"] for fv in faction_votes}
    vote_packets = [
        p for p in pv_packets
        if p["subject_type"] == "vote" and p["subject_id"] in marked_vote_ids
    ]
    assert len(vote_packets) == 36
    for packet in vote_packets:
        note = packet["claims"][0]["review_note"] or ""
        assert "確定結果" in note
        assert "▲" in note
    assembly_packet = next(p for p in asm_packets if p["subject_type"] == "assembly")
    # 未確認事項7件が open_questions に残っている
    assert len(assembly_packet["open_questions"]) == 7


def test_all_referenced_sources_exist_in_catalog() -> None:
    known = catalog_source_ids()
    files = [
        "assembly_records.json",
        "sessions.json",
        "proposals.json",
        "votes.json",
        "faction_votes.json",
        "political_activity_expenses.json",
        "inspection_trips.json",
        "disclosure_profiles.json",
        "assembly_evidence_packets.json",
        "proposal_vote_evidence_packets.json",
        "expense_evidence_packets.json",
        "inspection_evidence_packets.json",
    ]
    for name in files:
        missing = referenced_sources(load_json(BASE / name)) - known
        assert missing == set(), f"{name}: {missing}"
    catalog = load_json(
        ROOT / "data" / "catalog" / "kanagawa_prefecture_assembly_sources.json"
    )
    records = [r for r in catalog["records"] if r["municipality_key"] == "kanagawa-prefecture"]
    # 汎用10件＋政活費の単位別出典19件＋視察の報告書別出典79件
    assert len(records) == len(catalog["records"]) == 10 + 19 + 79
    assert_valid("schemas/source_catalog.schema.json", catalog)
