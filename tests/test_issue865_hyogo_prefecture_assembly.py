from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "reviewed" / "hyogo-prefecture" / "assembly"
ASSEMBLY_ID = "jp-local-280003-assembly-2023"
SESSION_ID = f"{ASSEMBLY_ID}-session-2026-376"
FACTION_NAMES = [
    "兵庫県議会自由民主党議員団",
    "維新の会兵庫県議会議員団",
    "兵庫県議会公明党議員団",
    "兵庫県議会ひょうご県民連合議員団",
    "躍動の会・無所属兵庫県議会議員団",
    "日本共産党兵庫県会議員団",
]
INDEPENDENT_NAMES = ["長崎寛親", "赤石まさお", "小林昌彦", "石井秀武", "丸尾牧"]
EXPENSE_CATEGORIES = [
    "調査研究費",
    "研修費",
    "会議費",
    "広報広聴費",
    "要請陳情等活動費",
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


def test_assembly_catalog_matches_contract() -> None:
    catalog = load_json(
        ROOT / "data" / "catalog" / "hyogo_prefecture_assembly_sources.json"
    )
    assert_valid("schemas/source_catalog.schema.json", catalog)
    # 議会専用カタログ14件
    assert len(catalog["records"]) == 14
    assert all(
        record["municipality_key"] == "hyogo-prefecture"
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
    assert assembly["seat_count"] == 86
    assert assembly["term_start"] == "2023-04-30"
    # 任期満了日は県選挙管理委員会の任期満了一覧に明記
    assert assembly["term_end"] == "2027-04-29"
    assert [f["name"] for f in assembly["factions"]] == FACTION_NAMES
    # 会派別人数は令和7年度政務活動費交付名簿の断面（36・18・13・8・3・2）
    # で、会期時点の人数ではない（証拠パケットに明記）
    assert [f["member_count"] for f in assembly["factions"]] == [36, 18, 13, 8, 3, 2]
    assert len(assembly["committees"]) == 9
    assert sessions[0]["id"] == SESSION_ID
    assert sessions[0]["name"] == "令和8年9月第376回定例会"
    assert sessions[0]["start_date"] == "2026-09-17"
    assert sessions[0]["end_date"] == "2026-10-23"


def test_proposals_and_votes() -> None:
    proposals = load_json(BASE / "proposals.json")
    votes = load_json(BASE / "votes.json")
    faction_votes = load_json(BASE / "faction_votes.json")
    # 第376回定例会の登録対象103件
    # （知事提出23・報第5号・認第1〜22号・議員提出1・第67号・請願44・意見書11）
    assert len(proposals) == 103
    executive = [p for p in proposals if p["submitted_by"] == "executive"]
    member = [p for p in proposals if p["submitted_by"] == "member"]
    petition = [p for p in proposals if p["submitted_by"] == "resident_petition"]
    assert len(executive) == 47
    assert len(member) == 12
    assert len(petition) == 44
    kinds: dict[str, int] = {}
    for p in proposals:
        kinds[p["kind"]] = kinds.get(p["kind"], 0) + 1
    assert kinds == {
        "budget": 2,
        "ordinance": 5,
        "other": 16,
        "settlement": 22,
        "personnel": 3,
        "petition": 44,
        "resolution": 11,
    }
    # 決算認定22件は全て認定済み
    settlements = [p for p in proposals if p["kind"] == "settlement"]
    assert all(p["outcome"] == "approved" for p in settlements)
    # 継続審査は第67号（知事給与特例条例）のみで pending
    pending = [p for p in proposals if p["outcome"] == "pending"]
    assert len(pending) == 1
    assert pending[0]["proposal_number"] == "第67号"
    assert pending[0]["kind"] == "ordinance"
    assert pending[0]["decided_at"] == "2026-10-23"
    assert sum(1 for p in proposals if p["outcome"] == "approved") == 63
    assert sum(1 for p in proposals if p["outcome"] == "rejected") == 39
    # 請願の採択は第70・71・76・111・112号の5件
    adopted = {
        p["proposal_number"] for p in petition if p["outcome"] == "approved"
    }
    assert adopted == {"第70号", "第71号", "第76号", "第111号", "第112号"}
    # 意見書11件は全て原案可決
    opinions = [p for p in proposals if p["kind"] == "resolution"]
    assert all(p["outcome"] == "approved" for p in opinions)
    for proposal in proposals:
        assert_valid("schemas/proposal.schema.json", proposal)
    assert len(votes) == 103
    vote_by_proposal = {}
    for vote in votes:
        assert_valid("schemas/vote.schema.json", vote)
        assert vote["totals"] is None
        assert vote["method"] == "unknown"
        vote_by_proposal[vote["proposal_id"]] = vote
    assert set(vote_by_proposal) == {p["id"] for p in proposals}
    # 無所属5人の個人名列が全件に付く（態度が分かれた場合のみ内訳が印字される）
    assert all(
        [m["member_name"] for m in v["member_votes"]] == INDEPENDENT_NAMES
        for v in votes
    )
    assert sum(len(v["member_votes"]) for v in votes) == 103 * 5
    # 会派別態度は103 vote × 6会派 = 618件
    assert len(faction_votes) == 103 * 6
    fv_by_vote: dict[str, list[dict[str, Any]]] = {}
    for fv in faction_votes:
        assert_valid("schemas/faction_vote.schema.json", fv)
        # 会期時点の会派別人数は公式明記がないため人数は登録しない
        assert fv["member_count"] is None
        assert fv["for_count"] is None
        assert fv["against_count"] is None
        fv_by_vote.setdefault(fv["vote_id"], []).append(fv)
    assert len(fv_by_vote) == 103
    for rows in fv_by_vote.values():
        assert {r["faction_name"] for r in rows} == set(FACTION_NAMES)

    def positions(kind: str, number: str) -> tuple[set[str], set[str], dict[str, str]]:
        prop = next(
            p for p in proposals
            if p["proposal_number"] == number and p["kind"] == kind
        )
        vote = vote_by_proposal[prop["id"]]
        rows = fv_by_vote[vote["id"]]
        for_set = {r["faction_name"] for r in rows if r["position"] == "for"}
        against_set = {r["faction_name"] for r in rows if r["position"] == "against"}
        members = {m["member_name"]: m["position"] for m in vote["member_votes"]}
        return for_set, against_set, members

    jimin, ishin, komei, kenmin, yakudo, kyosan = FACTION_NAMES
    # 知事提出第80号（補正予算）は全会派・無所属全員が賛成
    for_set, against_set, members = positions("budget", "第80号")
    assert for_set == set(FACTION_NAMES)
    assert against_set == set()
    assert set(members.values()) == {"for"}
    # 認第1号（一般会計決算認定）は県民連合と共産党が反対
    _, against_set, _ = positions("settlement", "認第1号")
    assert against_set == {kenmin, kyosan}
    # 第67号は継続審査申出への賛否（賛成=自民・公明・県民連合）
    for_set, against_set, members = positions("ordinance", "第67号")
    assert for_set == {jimin, komei, kenmin}
    assert against_set == {ishin, yakudo, kyosan}
    assert members == {
        "長崎寛親": "against",
        "赤石まさお": "against",
        "小林昌彦": "for",
        "石井秀武": "for",
        "丸尾牧": "against",
    }
    # 請願第69号は不採択（採択賛成は県民連合・共産党と丸尾牧）
    for_set, _, members = positions("petition", "第69号")
    assert for_set == {kenmin, kyosan}
    assert members["丸尾牧"] == "for"
    assert members["長崎寛親"] == "against"


def test_political_activity_expenses() -> None:
    expenses = load_json(BASE / "political_activity_expenses.json")
    # 令和7年度分96単位（会派使用分11・議員分85）
    assert len(expenses) == 96
    factions = [e for e in expenses if e["recipient_type"] == "faction"]
    members = [e for e in expenses if e["recipient_type"] == "member"]
    assert len(factions) == 11
    assert len(members) == 85
    for expense in expenses:
        assert_valid("schemas/political_activity_expense.schema.json", expense)
        assert expense["fiscal_year"] == 2025
        assert expense["report_status"] == "published"
        # 領収書等も Web 公開されている
        assert expense["receipt_access"] == "online"
        breakdown = expense["breakdown"]
        assert [b["category"] for b in breakdown] == EXPENSE_CATEGORIES
    # 科目別合計＝支出合計の検算は、小林昌彦議員の単位を除き全単位で一致
    # （当該単位は報告書自体の印字が一致せず、印字どおり登録し証拠パケットに明記）
    mismatched = [
        e for e in expenses
        if sum(b["amount_yen"] for b in e["breakdown"]) != e["spent_yen"]
    ]
    assert [e["recipient_name"] for e in mismatched] == ["小林昌彦"]
    kobayashi = mismatched[0]
    assert kobayashi["granted_yen"] == 5388000
    assert kobayashi["spent_yen"] == 2346286
    assert sum(b["amount_yen"] for b in kobayashi["breakdown"]) == 1960576
    # 年度途中の会派異動で二重に現れる議員は公表の形どおり2単位
    names = [e["recipient_name"] for e in members]
    assert names.count("赤石まさお") == 2
    assert names.count("長崎寛親") == 2
    # 自由民主党会派使用分（使用限度額19,170,000・充当15,420,887）
    jimin = next(
        e for e in factions if e["recipient_name"] == "兵庫県議会自由民主党議員団"
    )
    assert jimin["granted_yen"] == 19170000
    assert jimin["spent_yen"] == 15420887
    assert jimin["returned_yen"] == 19170000 - 15420887
    # 石川憲幸議員（使用限度額4,860,000・支出3,492,010）
    ishikawa = next(e for e in members if e["recipient_name"] == "石川憲幸")
    assert ishikawa["granted_yen"] == 4860000
    assert ishikawa["spent_yen"] == 3492010
    assert ishikawa["returned_yen"] == 4860000 - 3492010


def test_disclosure_profile() -> None:
    profiles = load_json(BASE / "disclosure_profiles.json")
    assert len(profiles) == 1
    profile = profiles[0]
    assert_valid("schemas/disclosure_profile.schema.json", profile)
    items = {item["item"]: item for item in profile["items"]}
    assert len(items) == 12
    assert items["faction_votes"]["availability"] == "published"
    # 会派態度は表決記録ではなく事前に表明された態度の集約である旨が注記されている
    assert "表決そのものの記録ではなく" in (items["faction_votes"]["note"] or "")
    assert items["member_votes"]["availability"] == "published"
    assert "無所属議員5人" in (items["member_votes"]["note"] or "")
    assert items["political_activity_expense_reports"]["availability"] == "published"
    # 領収書も Web 公開（千葉県議会の閲覧のみとは異なる）
    assert items["political_activity_expense_receipts"]["availability"] == "published"
    # 陳情は会期単位の公表がなく本会議で結論を出す制度ではない旨が注記されている
    assert "陳情は会期単位の一覧公表がなく" in (items["petition_results"]["note"] or "")
    assert items["inspection_trip_reports"]["availability"] == "published"


def test_inspection_trips() -> None:
    trips = load_json(BASE / "inspection_trips.json")
    # 令和7年度実施分35件（7常任委員会×管内4回＋管外1回）
    assert len(trips) == 35
    for trip in trips:
        assert_valid("schemas/inspection_trip.schema.json", trip)
        # 費用は報告書に記載がない
        assert trip["cost_status"] == "not_published"
        assert trip["total_cost_yen"] is None
        assert trip["report_status"] == "published"
        assert trip["trip_type"] == "domestic"
        assert trip["participants"] == []
        assert trip["participant_count"] is None
        assert len(trip["destinations"]) >= 1
    kannai = [t for t in trips if "管内調査" in t["title"]]
    kangai = [t for t in trips if "管外調査" in t["title"]]
    assert len(kannai) == 28
    assert len(kangai) == 7
    # 総務常任委員会の管外調査（長野県、2025-10-29〜31）
    soumu = next(
        t for t in trips if t["title"] == "令和7年度総務常任委員会管外調査"
    )
    assert soumu["start_date"] == "2025-10-29"
    assert soumu["end_date"] == "2025-10-31"
    assert "長野県議会（地域創生）" in soumu["destinations"]


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
    # 全 vote のパケットには、会派態度の性質（表決記録ではない）の注記が付く
    vote_packets = [p for p in pv_packets if p["subject_type"] == "vote"]
    assert len(vote_packets) == 103
    for packet in vote_packets:
        note = packet["claims"][0]["review_note"] or ""
        assert "表決そのものの記録ではなく" in note
    # 第67号の継続審査は Issue #706 の更新対象として申し送られている
    assembly_packet = next(p for p in asm_packets if p["subject_type"] == "assembly")
    assert any("#706" in q for q in assembly_packet["open_questions"])
    # 小林昌彦議員の政活費パケットには印字の不一致が未解決事項として残る
    kobayashi_id = next(
        e["id"] for e in expenses if e["recipient_name"] == "小林昌彦"
    )
    kobayashi_packet = next(
        p for p in ex_packets if p["subject_id"] == kobayashi_id
    )
    assert len(kobayashi_packet["open_questions"]) == 1
    assert "一致しない" in kobayashi_packet["open_questions"][0]


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
