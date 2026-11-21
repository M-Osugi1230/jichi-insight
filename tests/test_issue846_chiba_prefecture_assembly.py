from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "reviewed" / "chiba-prefecture" / "assembly"
ASSEMBLY_ID = "jp-local-120006-assembly-2023"
SESSION_ID = f"{ASSEMBLY_ID}-session-2026-3"
FACTION_NAMES = [
    "自由民主党千葉県議会議員会",
    "立憲民主党千葉県議会議員会",
    "公明党千葉県議会議員団",
    "千葉新政策議員団",
    "日本共産党千葉県議会議員団",
    "平和の党",
    "国民民主党千葉県議会議員会",
    "千葉県民の声",
    "リベラル民主",
    "市民力",
    "有志の会",
    "野田民主の会",
    "未来ちば",
    "自立と未来",
]
INDEPENDENT_NAMES = ["栗原直也", "松澤武人"]
EXPENSE_CATEGORIES = [
    "調査研究費",
    "研修費",
    "会議費",
    "資料購入費",
    "資料作成費",
    "広報費",
    "事務所費",
    "事務費",
    "人件費",
    "その他",
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
        ROOT / "data" / "catalog" / "chiba_prefecture_assembly_sources.json"
    )
    assert_valid("schemas/source_catalog.schema.json", catalog)
    # 議会専用カタログ20件
    assert len(catalog["records"]) == 20
    assert all(
        record["municipality_key"] == "chiba-prefecture"
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
    assert assembly["seat_count"] == 95
    assert assembly["term_start"] == "2023-04-30"
    # 任期満了日は柏市選管のページに日単位で明記
    assert assembly["term_end"] == "2027-04-29"
    assert [f["name"] for f in assembly["factions"]] == FACTION_NAMES
    # 令和8年8月17日の変更後の構成（自民49・立憲民12・公明8・千政団5・共産4・
    # 1人会派9）で計87人、無所属議員2人を加えた89人が現員と一致する
    assert sum(f["member_count"] for f in assembly["factions"]) == 87
    assert len(assembly["committees"]) == 11
    assert sessions[0]["id"] == SESSION_ID
    assert sessions[0]["name"] == "令和8年9月定例会"
    assert sessions[0]["start_date"] == "2026-09-04"
    assert sessions[0]["end_date"] == "2026-10-06"


def test_proposals_and_votes() -> None:
    proposals = load_json(BASE / "proposals.json")
    votes = load_json(BASE / "votes.json")
    faction_votes = load_json(BASE / "faction_votes.json")
    # 令和8年9月定例会の登録対象51件
    # （知事提出議案30・決算認定1・発議案17・請願3）
    assert len(proposals) == 51
    executive = [p for p in proposals if p["submitted_by"] == "executive"]
    member = [p for p in proposals if p["submitted_by"] == "member"]
    petition = [p for p in proposals if p["submitted_by"] == "resident_petition"]
    assert len(executive) == 31
    assert len(member) == 17
    assert len(petition) == 3
    kinds: dict[str, int] = {}
    for p in proposals:
        kinds[p["kind"]] = kinds.get(p["kind"], 0) + 1
    assert kinds == {
        "budget": 11,
        "ordinance": 7,
        "settlement": 1,
        "resolution": 14,
        "petition": 3,
        "other": 15,
    }
    # 決算認定のみ継続審査中で、賛否は公表されていない
    pending = [p for p in proposals if p["outcome"] == "pending"]
    assert [p["proposal_number"] for p in pending] == ["決算認定"]
    assert pending[0]["decided_at"] is None
    assert sum(1 for p in proposals if p["outcome"] == "approved") == 32
    assert sum(1 for p in proposals if p["outcome"] == "rejected") == 18
    by_number = {p["proposal_number"]: p for p in proposals}
    # 追加提案（第28〜30号）は9月18日上程
    assert by_number["第1号"]["submitted_at"] == "2026-09-04"
    assert by_number["第28号"]["submitted_at"] == "2026-09-18"
    assert by_number["発議案第1号"]["submitted_at"] == "2026-09-10"
    assert by_number["発議案第3号"]["outcome"] == "approved"
    assert by_number["発議案第2号"]["outcome"] == "rejected"
    for proposal in proposals:
        assert_valid("schemas/proposal.schema.json", proposal)
    assert len(votes) == 51
    vote_by_proposal = {}
    for vote in votes:
        assert_valid("schemas/vote.schema.json", vote)
        assert vote["totals"] is None
        assert vote["method"] == "unknown"
        vote_by_proposal[vote["proposal_id"]] = vote
    assert set(vote_by_proposal) == {p["id"] for p in proposals}
    published = [v for v in votes if v["member_vote_availability"] == "published"]
    unpublished = [v for v in votes if v["member_vote_availability"] == "not_published"]
    assert len(published) == 50
    assert len(unpublished) == 1
    assert all(
        [m["member_name"] for m in v["member_votes"]] == INDEPENDENT_NAMES
        for v in published
    )
    assert sum(len(v["member_votes"]) for v in votes) == 50 * 2
    assert all(v["member_votes"] == [] for v in unpublished)
    # 会派別賛否は50 vote × 14会派 = 700件
    assert len(faction_votes) == 50 * 14
    fv_by_vote: dict[str, list[dict[str, Any]]] = {}
    for fv in faction_votes:
        assert_valid("schemas/faction_vote.schema.json", fv)
        # 人数集計は会派人数のみで、賛否人数は作らない
        assert fv["for_count"] is None
        assert fv["against_count"] is None
        fv_by_vote.setdefault(fv["vote_id"], []).append(fv)
    assert len(fv_by_vote) == 50
    for rows in fv_by_vote.values():
        assert {r["faction_name"] for r in rows} == set(FACTION_NAMES)

    def positions(number: str) -> tuple[set[str], set[str], dict[str, str]]:
        prop = by_number[number]
        vote = vote_by_proposal[prop["id"]]
        rows = fv_by_vote[vote["id"]]
        for_set = {r["faction_name"] for r in rows if r["position"] == "for"}
        against_set = {r["faction_name"] for r in rows if r["position"] == "against"}
        members = {m["member_name"]: m["position"] for m in vote["member_votes"]}
        return for_set, against_set, members

    kyosan = "日本共産党千葉県議会議員団"
    jimin = "自由民主党千葉県議会議員会"
    # 知事提出議案で反対が付いたのは共産党のみ（第1・5・7・9・16・19・20号）
    for number in ("第1号", "第5号", "第7号", "第9号", "第16号", "第19号", "第20号"):
        _, against, _ = positions(number)
        assert against == {kyosan}
    for number in ("第2号", "第13号", "第27号", "第30号"):
        _, against, members = positions(number)
        assert against == set()
        assert set(members.values()) == {"for"}
    # 発議案第3号（自民党提出の定数条例改正）は自民党と松澤議員のみ賛成で可決
    for_set, against_set, members = positions("発議案第3号")
    assert for_set == {jimin}
    assert members == {"栗原直也": "against", "松澤武人": "for"}
    # 発議案第1号は共産党のみ反対で可決
    _, against, _ = positions("発議案第1号")
    assert against == {kyosan}
    # 請願第75号は自民党と松澤議員を除く全会派等が採択に賛成したが不採択
    for_set, against_set, members = positions("第75号")
    assert against_set == {jimin}
    assert members == {"栗原直也": "for", "松澤武人": "against"}
    assert len(for_set) == 13
    # 請願第77号の採択賛成は共産党・リベラル民主・市民力・未来ちばのみ
    for_set, _, _ = positions("第77号")
    assert for_set == {kyosan, "リベラル民主", "市民力", "未来ちば"}
    # 請願第76・77号は「第1項ないし第4項」の一括採決として項目範囲を保持する
    for number in ("第76号", "第77号"):
        vote = vote_by_proposal[by_number[number]["id"]]
        assert vote["item_scope"] == "第1項ないし第4項"


def test_political_activity_expenses() -> None:
    expenses = load_json(BASE / "political_activity_expenses.json")
    # 令和7年度分110単位（会派15・議員95）
    assert len(expenses) == 110
    factions = [e for e in expenses if e["recipient_type"] == "faction"]
    members = [e for e in expenses if e["recipient_type"] == "member"]
    assert len(factions) == 15
    assert len(members) == 95
    for expense in expenses:
        assert_valid("schemas/political_activity_expense.schema.json", expense)
        assert expense["fiscal_year"] == 2025
        assert expense["report_status"] == "published"
        # 領収書等の写しはWeb公開の対象外（議会事務局での閲覧のみ）
        assert expense["receipt_access"] == "in_person_only"
        breakdown = expense["breakdown"]
        assert [b["category"] for b in breakdown] == EXPENSE_CATEGORIES
        # 科目別内訳が支出合計と一致する（全単位で検算済み）
        assert sum(b["amount_yen"] for b in breakdown) == expense["spent_yen"]
    # 残余の検算は、小宮明史議員の単位（脚注で不交付と明記）を除き全単位で一致
    exceptions = [
        e for e in expenses
        if e["granted_yen"] - e["spent_yen"] != e["returned_yen"]
    ]
    assert [e["recipient_name"] for e in exceptions] == ["小宮明史"]
    komiya = exceptions[0]
    assert komiya["granted_yen"] == 350000
    assert komiya["spent_yen"] == 0
    assert komiya["returned_yen"] == 0
    # 合計は公表一覧表の合計欄と一致する
    assert sum(e["granted_yen"] for e in factions) == 52850000
    assert sum(e["spent_yen"] for e in factions) == 47863001
    assert sum(e["granted_yen"] for e in members) == 383250000
    assert sum(e["spent_yen"] for e in members) == 330098775


def test_disclosure_profile() -> None:
    profiles = load_json(BASE / "disclosure_profiles.json")
    assert len(profiles) == 1
    profile = profiles[0]
    assert_valid("schemas/disclosure_profile.schema.json", profile)
    items = {item["item"]: item for item in profile["items"]}
    assert len(items) == 12
    assert items["faction_votes"]["availability"] == "published"
    # 議員個人別の賛否は無所属議員2名のみ個人名の列で公表
    assert items["member_votes"]["availability"] == "published"
    assert "無所属議員2名" in (items["member_votes"]["note"] or "")
    assert items["political_activity_expense_reports"]["availability"] == "published"
    # 領収書の写しは閲覧のみ
    assert items["political_activity_expense_receipts"]["availability"] == "restricted"
    # 陳情は結論を出さない制度である旨が注記されている
    assert "陳情は結論を出さない制度" in (items["petition_results"]["note"] or "")
    assert items["inspection_trip_reports"]["availability"] == "published"


def test_inspection_trips() -> None:
    trips = load_json(BASE / "inspection_trips.json")
    # 県外調査21件（令和5・6・7年度）＋県内調査26件（令和7・8年度実施分）
    assert len(trips) == 47
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
    kengai = [t for t in trips if "県外調査" in t["title"]]
    kennai = [t for t in trips if "県内調査" in t["title"]]
    assert len(kengai) == 21
    assert len(kennai) == 26
    # 令和7年度総務防災常任委員会の県外調査（北海道）
    soumu = next(
        t for t in trips
        if t["title"] == "令和7年度総務防災常任委員会県外調査報告書"
    )
    assert soumu["start_date"] == "2025-10-22"
    assert soumu["end_date"] == "2025-10-24"
    assert "北海道議会（北海道札幌市）" in soumu["destinations"]


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
    # 賛否を記録した vote のパケットには、賛否表の読み方（○の意味）の注記が付く
    faction_votes = load_json(BASE / "faction_votes.json")
    marked_vote_ids = {fv["vote_id"] for fv in faction_votes}
    vote_packets = [
        p for p in pv_packets
        if p["subject_type"] == "vote" and p["subject_id"] in marked_vote_ids
    ]
    assert len(vote_packets) == 50
    for packet in vote_packets:
        note = packet["claims"][0]["review_note"] or ""
        assert "読み取った" in note
    assembly_packet = next(p for p in asm_packets if p["subject_type"] == "assembly")
    # 決算認定の結論更新が Issue #706 の対象である旨が明記されている
    assert any("#706" in q for q in assembly_packet["open_questions"])
    # 決算認定のパケットにも #706 の申し送りがある
    settle_packet = next(
        p for p in pv_packets
        if p["subject_id"].endswith("proposal-2026-3-031")
    )
    assert any("#706" in q for q in settle_packet["open_questions"])


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
