from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "reviewed" / "saitama-prefecture" / "assembly"
ASSEMBLY_ID = "jp-local-110001-assembly-2023"
SESSION_ID = f"{ASSEMBLY_ID}-session-2026-3"
FACTION_NAMES = [
    "埼玉県議会自由民主党議員団",
    "埼玉民主フォーラム",
    "埼玉県議会公明党議員団",
    "無所属県民会議",
    "日本共産党埼玉県議会議員団",
    "無所属改革の会",
    "無所属保守さくらの会",
    "埼玉県市民ネットワーク",
]
INDEPENDENT_NAMES = ["小谷野五雄", "諸井真英", "高木功介"]
EXPENSE_CATEGORIES = [
    "調査研究費",
    "グループ活動費",
    "広聴費",
    "要請・陳情等活動費",
    "広報費",
    "人件費",
    "事務所費",
    "事務費",
    "資料購入・作成費",
    "交通費",
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


def test_assembly_catalog_matches_contract() -> None:
    catalog = load_json(
        ROOT / "data" / "catalog" / "saitama_prefecture_assembly_sources.json"
    )
    assert_valid("schemas/source_catalog.schema.json", catalog)
    # 議会専用カタログ30件（会期・議案10、政活費17、視察3）
    assert len(catalog["records"]) == 30
    assert all(
        record["municipality_key"] == "saitama-prefecture"
        for record in catalog["records"]
    )


def test_assembly_and_session_match_contracts() -> None:
    assemblies = load_json(BASE / "assembly_records.json")
    sessions = load_json(BASE / "sessions.json")
    assert len(assemblies) == 1
    assert len(sessions) == 1
    assembly = assemblies[0]
    assert_valid("schemas/assembly.schema.json", assembly)
    assert_valid("schemas/session.schema.json", sessions[0])
    assert assembly["id"] == ASSEMBLY_ID
    # 定数93人。会派別人数は表決状況確認時のスナップショット（計81人）で、
    # 無所属議員3人を加えた84人が議員名簿の現員と一致する
    assert assembly["seat_count"] == 93
    assert assembly["term_start"] == "2023-04-30"
    # 任期満了日は県選管「任期満了日一覧」に日単位で明記
    assert assembly["term_end"] == "2027-04-29"
    assert [f["name"] for f in assembly["factions"]] == FACTION_NAMES
    assert sum(f["member_count"] for f in assembly["factions"]) == 81
    assert len(assembly["committees"]) == 15
    assert sessions[0]["id"] == SESSION_ID
    assert sessions[0]["name"] == "令和8年9月定例会"
    assert sessions[0]["start_date"] == "2026-09-25"
    assert sessions[0]["end_date"] == "2026-10-17"


def test_proposals_and_votes() -> None:
    proposals = load_json(BASE / "proposals.json")
    votes = load_json(BASE / "votes.json")
    faction_votes = load_json(BASE / "faction_votes.json")
    # 令和8年9月定例会の登録対象54件
    # （知事提出35・意見書14・議員派遣2・懲罰2・請願1）
    assert len(proposals) == 54
    executive = [p for p in proposals if p["submitted_by"] == "executive"]
    member = [p for p in proposals if p["submitted_by"] == "member"]
    petition = [p for p in proposals if p["submitted_by"] == "resident_petition"]
    assert len(executive) == 35
    assert len(member) == 18
    assert len(petition) == 1
    assert petition[0]["proposal_number"] == "請願（番号の公表なし）"
    assert petition[0]["kind"] == "petition"
    kinds: dict[str, int] = {}
    for p in proposals:
        kinds[p["kind"]] = kinds.get(p["kind"], 0) + 1
    assert kinds == {
        "budget": 2,
        "ordinance": 5,
        "settlement": 2,
        "personnel": 21,
        "resolution": 14,
        "petition": 1,
        "other": 9,
    }
    # 継続審査は第115・116・117号の3件のみで、残り51件は印字どおり可決系
    pending = [p for p in proposals if p["outcome"] == "pending"]
    assert {p["proposal_number"] for p in pending} == {"第115号", "第116号", "第117号"}
    assert sum(1 for p in proposals if p["outcome"] == "approved") == 51
    # 決算2件の継続審査の決定日は10月7日、その他は10月16日（懲罰は10月17日）
    by_number = {p["proposal_number"]: p for p in proposals}
    assert by_number["第116号"]["decided_at"] == "2026-10-07"
    assert by_number["第117号"]["decided_at"] == "2026-10-07"
    assert by_number["第104号"]["submitted_at"] == "2026-09-25"
    assert by_number["第118号"]["submitted_at"] == "2026-10-16"
    for proposal in proposals:
        assert_valid("schemas/proposal.schema.json", proposal)
    assert len(votes) == 54
    vote_by_proposal = {}
    for vote in votes:
        assert_valid("schemas/vote.schema.json", vote)
        assert vote["totals"] is None
        assert vote["method"] == "unknown"
        vote_by_proposal[vote["proposal_id"]] = vote
    assert set(vote_by_proposal) == {p["id"] for p in proposals}
    # 賛否が公表されているのは49件で、無所属議員3名の個人別態度が付く
    published = [v for v in votes if v["member_vote_availability"] == "published"]
    unpublished = [v for v in votes if v["member_vote_availability"] == "not_published"]
    assert len(published) == 49
    assert len(unpublished) == 5
    assert all(
        [m["member_name"] for m in v["member_votes"]] == INDEPENDENT_NAMES
        for v in published
    )
    assert sum(len(v["member_votes"]) for v in votes) == 49 * 3
    assert all(v["member_votes"] == [] for v in unpublished)
    # 会派別賛否は49 vote × 8会派 = 392件
    assert len(faction_votes) == 49 * 8
    fv_by_vote: dict[str, list[dict[str, Any]]] = {}
    for fv in faction_votes:
        assert_valid("schemas/faction_vote.schema.json", fv)
        # 人数集計は表決状況確認時の会派人数のみで、賛否人数は作らない
        assert fv["for_count"] is None
        assert fv["against_count"] is None
        fv_by_vote.setdefault(fv["vote_id"], []).append(fv)
    assert len(fv_by_vote) == 49
    for rows in fv_by_vote.values():
        assert {r["faction_name"] for r in rows} == set(FACTION_NAMES)

    def against_factions(number: str) -> set[str]:
        prop = by_number[number]
        rows = fv_by_vote[vote_by_proposal[prop["id"]]["id"]]
        return {r["faction_name"] for r in rows if r["position"] == "against"}

    def member_position(number: str, name: str) -> str:
        prop = by_number[number]
        vote = vote_by_proposal[prop["id"]]
        return next(m["position"] for m in vote["member_votes"]
                    if m["member_name"] == name)

    # 賛否が分かれたのは7件: 共産党が反対した6件と、議第53号
    kyosan = "日本共産党埼玉県議会議員団"
    for number in ("第104号", "第106号", "第108号", "第109号", "議第51号", "議第52号"):
        assert against_factions(number) == {kyosan}
    assert against_factions("議第53号") == {"無所属保守さくらの会"}
    assert member_position("議第53号", "諸井真英") == "against"
    assert member_position("議第53号", "小谷野五雄") == "for"
    assert member_position("議第53号", "高木功介") == "for"
    split_votes = [vid for vid, rows in fv_by_vote.items()
                   if any(r["position"] == "against" for r in rows)]
    assert len(split_votes) == 7
    # 第115号は継続審査だが表決状況には全会派の賛成が印字されている
    p115 = by_number["第115号"]
    rows115 = fv_by_vote[vote_by_proposal[p115["id"]]["id"]]
    assert all(r["position"] == "for" for r in rows115)
    assert vote_by_proposal[p115["id"]]["outcome"] == "pending"


def test_political_activity_expenses() -> None:
    expenses = load_json(BASE / "political_activity_expenses.json")
    # 令和7年度分の11単位（すべて会派単位。構成は現行会派と異なる）
    assert len(expenses) == 11
    assert all(e["recipient_type"] == "faction" for e in expenses)
    for expense in expenses:
        assert_valid("schemas/political_activity_expense.schema.json", expense)
        assert expense["fiscal_year"] == 2025
        assert expense["report_status"] == "published"
        # 領収書等の写しまでWeb公開されている
        assert expense["receipt_access"] == "online"
        breakdown = expense["breakdown"]
        assert [b["category"] for b in breakdown] == EXPENSE_CATEGORIES
        # 科目別内訳が支出合計と一致する（全単位で検算済み）
        assert sum(b["amount_yen"] for b in breakdown) == expense["spent_yen"]
        if expense["spent_yen"] <= expense["granted_yen"]:
            assert expense["granted_yen"] - expense["spent_yen"] == expense["returned_yen"]
        else:
            # 支出が交付額を上回る単位は残余0円の印字どおり
            assert expense["returned_yen"] == 0
    assert sum(e["granted_yen"] for e in expenses) == 531500000
    assert sum(e["spent_yen"] for e in expenses) == 495608449
    assert sum(e["returned_yen"] for e in expenses) == 46630776
    by_name = {e["recipient_name"]: e for e in expenses}
    # 自民は訂正分（令和8年9月18日収受）が正本。当初分の支出合計は339,364,779円
    jimin = by_name["埼玉県議会自由民主党議員団"]
    assert jimin["granted_yen"] == 329500000
    assert jimin["spent_yen"] == 339313979
    assert jimin["returned_yen"] == 0
    assert len(jimin["sources"]) == 2
    # 訂正分が正本の単位は3単位（自民・民主フォーラム・共産党）
    corrected = [e for e in expenses if len(e["sources"]) == 2]
    assert len(corrected) == 3
    minshu = by_name["埼玉民主フォーラム"]
    assert minshu["spent_yen"] == 54536160
    assert minshu["returned_yen"] == 11463840
    kyosan = by_name["日本共産党埼玉県議会議員団"]
    assert kyosan["spent_yen"] == 17571422
    assert kyosan["returned_yen"] == 428578
    # 支出が交付額を上回る単位は6単位
    overspent = [e for e in expenses if e["spent_yen"] > e["granted_yen"]]
    assert len(overspent) == 6


def test_disclosure_profile() -> None:
    profiles = load_json(BASE / "disclosure_profiles.json")
    assert len(profiles) == 1
    profile = profiles[0]
    assert_valid("schemas/disclosure_profile.schema.json", profile)
    items = {item["item"]: item for item in profile["items"]}
    assert len(items) == 12
    assert items["faction_votes"]["availability"] == "published"
    # 議員個人別の賛否は無所属議員3名のみ個人名の列で公表
    assert items["member_votes"]["availability"] == "published"
    assert "無所属議員3名" in (items["member_votes"]["note"] or "")
    # 政活費は収支報告書・領収書の写しまで公開
    assert items["political_activity_expense_reports"]["availability"] == "published"
    assert items["political_activity_expense_receipts"]["availability"] == "published"
    # 陳情は結論を出さない制度である旨が注記されている
    assert "陳情は結論を出さない制度" in (items["petition_results"]["note"] or "")
    assert items["inspection_trip_reports"]["availability"] == "published"


def test_inspection_trips() -> None:
    trips = load_json(BASE / "inspection_trips.json")
    # 委員会調査14件（令和7年度・議会記録「閉会中の委員会活動」）＋
    # 政務活動費による台湾視察2件
    assert len(trips) == 16
    for trip in trips:
        assert_valid("schemas/inspection_trip.schema.json", trip)
        # 費用は報告書・議会記録のいずれにも記載がない
        assert trip["cost_status"] == "not_published"
        assert trip["total_cost_yen"] is None
        assert trip["report_status"] == "published"
        if trip["participant_count"] is not None:
            assert trip["participant_count"] == len(trip["participants"])
    domestic = [t for t in trips if t["trip_type"] == "domestic"]
    overseas = [t for t in trips if t["trip_type"] == "overseas"]
    assert len(domestic) == 14
    assert len(overseas) == 2
    # 委員会調査は参加者氏名が公表範囲にないため参加者を登録しない
    assert all(t["participants"] == [] for t in domestic)
    assert all(t["participant_count"] is None for t in domestic)
    assert all(t["start_date"].startswith("2025-") for t in domestic)
    assert all(len(t["destinations"]) == 2 for t in domestic)
    # 日台友好議員連盟の台湾視察は訪問団員4名が報告書に明記
    nittai = next(t for t in trips if "日台友好議員連盟" in t["title"])
    assert nittai["start_date"] == "2026-02-08"
    assert nittai["end_date"] == "2026-02-11"
    assert nittai["participant_count"] == 4
    assert nittai["participants"][0]["name"] == "鈴木正人"
    assert nittai["participants"][0]["role"] == "団長"
    # 青藍会・周山会の台湾視察は高木功介・諸井真英の2名
    seiran = next(t for t in trips if "青藍会" in t["title"])
    assert seiran["start_date"] == "2025-09-10"
    assert seiran["end_date"] == "2025-09-13"
    assert {p["name"] for p in seiran["participants"]} == {"高木功介", "諸井真英"}


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
    # 賛否を記録した vote のパケットには、議会運営委員会で確認した態度であり
    # 本会議の投票記録そのものではない旨の注記が必ず付く
    faction_votes = load_json(BASE / "faction_votes.json")
    marked_vote_ids = {fv["vote_id"] for fv in faction_votes}
    vote_packets = [
        p for p in pv_packets
        if p["subject_type"] == "vote" and p["subject_id"] in marked_vote_ids
    ]
    assert len(vote_packets) == 49
    for packet in vote_packets:
        note = packet["claims"][0]["review_note"] or ""
        assert "議会運営委員会で確認した内容" in note
        assert "投票記録そのものではない" in note
    # 訂正分を正本とした3単位には訂正の経緯の claim がある
    correction_packets = [
        p for p in ex_packets
        if any(c["field"] == "correction" for c in p["claims"])
    ]
    assert len(correction_packets) == 3
    assembly_packet = next(p for p in asm_packets if p["subject_type"] == "assembly")
    # 未確認事項5件が open_questions に残っている
    assert len(assembly_packet["open_questions"]) == 5
    # 継続審査3件の結論更新が Issue #706 の対象である旨が明記されている
    assert any("#706" in q for q in assembly_packet["open_questions"])


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
        assert missing == set(), f"{name}: {sorted(missing)}"
