"""Staging tests for the Wakayama Phase 15 review candidate.

The candidate stays prepared and unpublished until a human checks the
cited primary sources.  These tests pin the package state, the source
catalog, the plan framework, and the verified fiscal values so that a
promotion change has to be deliberate.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = ROOT / "data" / "candidates" / "wakayama-city" / "review_candidate.json"
INVENTORY_PATH = ROOT / "data" / "indexed" / "wakayama-city" / "source_inventory.json"
QUEUE_PATH = ROOT / "data" / "catalog" / "phase15_core_capital_review_queue.json"


def _candidate() -> dict:
    return json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))


def _package() -> dict:
    return _candidate()["candidate_package"]


def test_wakayama_candidate_is_prepared_and_unpublished() -> None:
    candidate = _candidate()
    assert candidate["candidate_id"] == "wakayama-phase15-review-candidate"
    assert candidate["official_code"] == "302015"
    assert candidate["name_ja"] == "和歌山市"
    assert candidate["status"] == "review_candidate"
    assert candidate["package_state"] == "prepared"
    assert candidate["human_review"]["required"] is True
    assert candidate["human_review"]["status"] == "pending"
    assert candidate["human_review"]["reviewed_at"] is None
    assert candidate["human_review"]["reviewer_note"] is None
    assert candidate["publication"]["eligible"] is False


def test_wakayama_candidate_sources_match_phase14_inventory() -> None:
    package_sources = {
        source["id"]: source for source in _package()["source_catalog"]["sources"]
    }
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    inventory_sources = {source["id"]: source for source in inventory["sources"]}
    assert set(package_sources) == set(inventory_sources)
    assert set(package_sources) == {
        "wakayama-fifth-long-term-plan",
        "wakayama-implementation-2024-2026",
        "wakayama-budget-2026",
        "wakayama-settlement-2024",
    }
    for source_id, source in package_sources.items():
        assert source["official_url"] == inventory_sources[source_id]["official_url"]
        assert source["official_url"].startswith(
            "https://www.city.wakayama.wakayama.jp/"
        )
        assert source["verification_status"] == "primary_source_live_verified_2026-11-16"


def test_wakayama_plan_review_records_framework_and_transition() -> None:
    records = {record["id"]: record for record in _package()["plan_review"]["records"]}
    assert set(records) == {
        "wakayama-current-plan-period",
        "wakayama-current-policy-structure",
        "wakayama-progress-governance-framework",
        "wakayama-plan-transition",
        "wakayama-fy2024-settlement-linkage",
    }
    period = records["wakayama-current-plan-period"]
    assert period["decision"] == "needs_review"
    assert period["title"].startswith("第5次和歌山市長期総合計画の構成")
    assert "基本構想・基本計画2017年度～2026年度" in period["value"]
    assert "現行2024年度～2026年度" in period["value"]
    transition = records["wakayama-plan-transition"]
    assert "最終年度" in transition["statement"]
    assert "確認できていない" in transition["statement"]
    linkage = records["wakayama-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["fiscal_year"] == 2024


def test_wakayama_policy_structure_keeps_four_goals_and_26_policies() -> None:
    plan = _package()["policy_structure"]["current_plan"]
    assert plan["title"].startswith("第5次和歌山市長期総合計画 基本計画")
    assert plan["vision"] == "きらり 輝く元気和歌山市"
    assert plan["start_fiscal_year"] == 2017
    assert plan["end_fiscal_year"] == 2026
    assert plan["period_status"] == "transition_or_unresolved"
    field_names = [field["name_ja"] for field in plan["policy_fields"]]
    goal1 = "分野別目標1 安定した雇用を生み出す産業が元気なまち"
    goal2 = "分野別目標2 住みたいと選ばれる魅力があふれるまち"
    goal3 = "分野別目標3 子供たちがいきいきと育つまち"
    goal4 = "分野別目標4 誰もが安心して住み続けられる持続可能なまち"
    assert field_names == [
        f"{goal1}：1-1 地域を支える既存産業の振興",
        f"{goal1}：1-2 新たな事業の創出と産学官金・異業種連携の促進",
        f"{goal1}：1-3 農林水産業の活性化",
        f"{goal1}：1-4 観光の稼ぐ力の強化",
        f"{goal1}：1-5 国際交流の推進",
        f"{goal1}：1-6 産業を支える「人」の確保",
        f"{goal2}：2-1 中心市街地の魅力向上",
        f"{goal2}：2-2 各地域における魅力的なまちづくり",
        f"{goal2}：2-3 魅力ある都市景観の創出",
        f"{goal2}：2-4 自然と共生する環境にやさしい社会の形成",
        f"{goal2}：2-5 郷土に誇りと愛着を育む文化・スポーツの振興と生涯学習の推進",
        f"{goal3}：3-1 安心して子供を生み育てることのできる環境の整備",
        f"{goal3}：3-2 社会を生き抜く子供たちの学力の育成",
        f"{goal3}：3-3 生涯を通じた豊かな心と健やかな体の育成",
        f"{goal3}：3-4 安全・安心な教育環境の整備",
        f"{goal3}：3-5 家庭や地域における教育力の向上",
        f"{goal4}：4-1 コンパクトシティの実現",
        f"{goal4}：4-2 都市機能や市民生活を支える道路網の整備",
        f"{goal4}：4-3 豊かな暮らしを支える住環境の整備",
        f"{goal4}：4-4 防災体制の充実",
        f"{goal4}：4-5 消防力の充実",
        f"{goal4}：4-6 安全で安心な市民生活の確保",
        f"{goal4}：4-7 健康で元気に暮らせる環境づくり",
        f"{goal4}：4-8 人権尊重・男女共同参画の推進",
        f"{goal4}：4-9 将来に向かって希望の持てる福祉社会の形成",
        f"{goal4}：4-10 地域コミュニティの充実",
    ]
    assert all(field["measures"] == [] for field in plan["policy_fields"])
    principles = "".join(plan["management_principles"])
    assert "実施計画" in principles
    assert "transition_or_unresolved" in principles


def test_wakayama_fiscal_records_hold_verified_values_and_vote_facts() -> None:
    records = {record["id"]: record for record in _package()["fiscal_records"]}
    budget = records["jp-local-302015-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 165_768_945_000
    assert budget["sources"] == ["wakayama-budget-2026"]
    assert "議案第31号" in budget["note"]
    assert "可決され成立した" in budget["note"]
    assert "千円単位" in budget["note"]
    assert "2026年3月13日" in budget["note"]
    revenue = records["jp-local-302015-fiscal-2024-total-revenue"]
    assert revenue["stage"] == "settlement"
    assert revenue["amount_yen"] == 171_406_400_509
    assert revenue["sources"] == ["wakayama-settlement-2024"]
    assert "認第6号" in revenue["note"]
    assert "認定された" in revenue["note"]
    assert "2025年12月1日" in revenue["note"]
    assert "171,406,400,509円" in revenue["note"]
    expenditure = records["jp-local-302015-fiscal-2024-total-expenditure"]
    assert expenditure["amount_yen"] == 167_796_054_596
    assert expenditure["sources"] == ["wakayama-settlement-2024"]
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 3_610_345_913


def test_wakayama_fy2026_budget_amount_is_directly_confirmed() -> None:
    records = {record["id"]: record for record in _package()["fiscal_records"]}
    budget = records["jp-local-302015-fiscal-2026-total-expenditure"]
    # The initial budget total is confirmed directly in the official
    # 予算内示資料: the p.5 overview (1,657億6,894万5,000円) and the
    # p.6 budget summary table (単位 千円) both give 165,768,945千円.
    assert budget["amount_yen"] == 165_768_945 * 1000
    assert "予算内示資料" in budget["note"]
    assert "直接確認した" in budget["note"]
    assert "165,768,945千円" in budget["note"]
    # The earlier arithmetic identification from the gazette-published
    # supplementary budget No. 1, article 1 stays as a consistency
    # cross-check: 168,632,712 - 2,863,767 = 165,768,945 (thousand yen).
    assert 168_632_712 - 2_863_767 == 165_768_945
    assert "算術的特定" in budget["note"]
    assert "168,632,712千円" in budget["note"]
    assert "2,863,767千円" in budget["note"]
    assert "未了" not in budget["note"]


def test_wakayama_fy2024_settlement_values_and_real_balance() -> None:
    records = {record["id"]: record for record in _package()["fiscal_records"]}
    revenue = records["jp-local-302015-fiscal-2024-total-revenue"]
    expenditure = records["jp-local-302015-fiscal-2024-total-expenditure"]
    # Values pinned from the official settlement summary table (単位: 円).
    assert revenue["amount_yen"] == 171_406_400_509
    assert expenditure["amount_yen"] == 167_796_054_596
    # 差引残額 (revenue minus expenditure) matches the same table.
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 3_610_345_913
    # 実質収支 is published only at thousand-yen precision in the
    # settlement statement: 3,610,346 - 248,946 = 3,361,400 (千円).
    assert 3_610_346 - 248_946 == 3_361_400
    assert "3,610,345,913円" in expenditure["note"]
    assert "3,361,400千円" in expenditure["note"]
    assert "248,946千円" in expenditure["note"]
    assert "千円精度のまま" in expenditure["note"]


def test_wakayama_fy2024_settlement_certification_is_verified() -> None:
    text = CANDIDATE_PATH.read_text(encoding="utf-8")
    assert "認第6号" in text
    assert "認定された" in text
    assert "令和7年12月定例会" in text
    # The certification vote date is pinned from the council's official
    # 審議結果 (【令和7年12月1日議決分】 table): 認第6号 was certified
    # on 2025-12-01, so the candidate records the date and no longer
    # keeps it unidentified anywhere.
    assert "2025年12月1日" in text
    assert "未特定" not in text
    assert "不認定" not in text
    assert "原案可決" not in text
    assert "修正可決" not in text


def test_wakayama_evidence_packets_cover_the_three_fiscal_records() -> None:
    packets = {packet["id"]: packet for packet in _package()["evidence_packets"]}
    assert set(packets) == {
        "evidence-wakayama-city-2026-total-expenditure",
        "evidence-wakayama-city-2024-total-revenue",
        "evidence-wakayama-city-2024-total-expenditure",
    }
    for packet in packets.values():
        assert packet["review_status"] == "needs_review"
        assert len(packet["claims"]) == 1
        assert packet["claims"][0]["decision"] == "needs_review"
    budget_claim = packets["evidence-wakayama-city-2026-total-expenditure"]["claims"][0]
    assert "議案第31号" in budget_claim["statement"]
    assert "2026年3月13日" in budget_claim["statement"]
    assert "165,768,945千円" in budget_claim["statement"]
    assert "予算内示資料" in budget_claim["statement"]
    assert "直接確認" in budget_claim["statement"]
    budget_packet = packets["evidence-wakayama-city-2026-total-expenditure"]
    assert not any("直接確認" in q for q in budget_packet["open_questions"])
    revenue_claim = packets["evidence-wakayama-city-2024-total-revenue"]["claims"][0]
    assert "認第6号" in revenue_claim["statement"]
    assert "2025年12月1日" in revenue_claim["statement"]
    assert "171,406,400,509円" in revenue_claim["statement"]
    revenue_packet = packets["evidence-wakayama-city-2024-total-revenue"]
    assert not any("議決日" in q for q in revenue_packet["open_questions"])
    expenditure_claim = packets["evidence-wakayama-city-2024-total-expenditure"]["claims"][0]
    assert "167,796,054,596円" in expenditure_claim["statement"]
    assert "3,361,400千円" in expenditure_claim["statement"]


def test_wakayama_progress_review_stays_staging() -> None:
    progress = _package()["progress_review"]
    assert progress["review_status"] == "review_candidate_staging"
    framework = progress["implementation_plan_framework"]
    assert "実施計画" in framework["title"]
    assert "点検・見直し" in framework["evaluation_structure"]


def test_wakayama_candidate_leaves_review_queue_unchanged() -> None:
    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    summary = queue["summary"]
    assert summary["reviewed_complete_count"] == 47
    assert summary["pending_record_review_count"] == 20
    assert summary["next_official_code"] == "302015"
    entry = next(
        item for item in queue["execution_queue"] if item["official_code"] == "302015"
    )
    assert entry["status"] == "pending_record_review"
    assert entry["completion_path"] is None
