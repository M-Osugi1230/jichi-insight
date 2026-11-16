"""Staging tests for the Matsue Phase 15 review candidate.

The candidate stays prepared and unpublished until a human checks the
cited primary sources.  These tests pin the package state, the source
catalog, the plan framework, and the verified fiscal values so that a
promotion change has to be deliberate.  The FY2026 initial budget vote
(bill 56, adopted as proposed on 2026-03-26) and the FY2024 settlement
certification (settlement bill 1, certified on 2025-10-07) were both
read directly from the council's official bill/result tables by text
fetch, so the candidate records both outcomes in the primary sources'
own wording.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = ROOT / "data" / "candidates" / "matsue-city" / "review_candidate.json"
INVENTORY_PATH = ROOT / "data" / "indexed" / "matsue-city" / "source_inventory.json"
QUEUE_PATH = ROOT / "data" / "catalog" / "phase15_core_capital_review_queue.json"


def _candidate() -> dict:
    return json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))


def _package() -> dict:
    return _candidate()["candidate_package"]


def test_matsue_candidate_is_prepared_with_delegated_review_approved() -> None:
    candidate = _candidate()
    assert candidate["candidate_id"] == "matsue-phase15-review-candidate"
    assert candidate["official_code"] == "322016"
    assert candidate["name_ja"] == "松江市"
    assert candidate["status"] == "review_candidate"
    assert candidate["package_state"] == "prepared"
    assert candidate["human_review"]["required"] is True
    assert candidate["human_review"]["status"] == "approved"
    assert candidate["human_review"]["reviewed_at"] == "2026-11-16"
    assert candidate["human_review"]["reviewer_note"]
    # The owner did not review the primary sources personally: on
    # 2026-11-15 the owner explicitly delegated the review to Muse in
    # chat, and the note must record that delegation rather than
    # claiming an owner review.
    assert "委任" in candidate["human_review"]["reviewer_note"]
    assert "レビューはあなたがやってください" in candidate["human_review"]["reviewer_note"]
    assert candidate["publication"]["eligible"] is False


def test_matsue_candidate_sources_match_phase14_inventory() -> None:
    package_sources = {
        source["id"]: source for source in _package()["source_catalog"]["sources"]
    }
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    inventory_sources = {source["id"]: source for source in inventory["sources"]}
    assert set(package_sources) == set(inventory_sources)
    assert set(package_sources) == {
        "matsue-dreams-2030",
        "matsue-kpi-progress",
        "matsue-budget-2026",
        "matsue-settlement-2024",
    }
    for source_id, source in package_sources.items():
        assert source["official_url"] == inventory_sources[source_id]["official_url"]
        assert source["official_url"].startswith("https://www.city.matsue.lg.jp/")
        assert source["verification_status"] == "primary_source_live_verified_2026-11-16"


def test_matsue_plan_review_records_framework_and_transition() -> None:
    records = {record["id"]: record for record in _package()["plan_review"]["records"]}
    assert set(records) == {
        "matsue-current-plan-period",
        "matsue-current-policy-structure",
        "matsue-progress-governance-framework",
        "matsue-plan-transition",
        "matsue-fy2024-settlement-linkage",
    }
    period = records["matsue-current-plan-period"]
    assert period["decision"] == "needs_review"
    assert period["title"].startswith("松江市総合計画『MATSUE DREAMS 2030』の構成")
    assert "基本構想2022年度～2029年度" in period["value"]
    assert "毎年度見直し" in period["value"]
    transition = records["matsue-plan-transition"]
    assert "2022年度に開始した" in transition["statement"]
    assert "未確認" in transition["statement"]
    linkage = records["matsue-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["fiscal_year"] == 2024


def test_matsue_policy_structure_keeps_five_goals_and_18_measures() -> None:
    plan = _package()["policy_structure"]["current_plan"]
    assert plan["title"].startswith("松江市総合計画『MATSUE DREAMS 2030』基本構想")
    assert plan["vision"] == "夢を実現できるまち 誇れるまち 松江"
    assert plan["start_fiscal_year"] == 2022
    assert plan["end_fiscal_year"] == 2029
    assert plan["period_status"] == "verified_fixed_period"
    goal1 = "基本目標I しごとづくり"
    goal2 = "基本目標II ひとづくり"
    goal3 = "基本目標III つながりづくり"
    goal4 = "基本目標IV どだいづくり"
    goal5 = "基本目標V なかまづくり"
    field_names = [field["name_ja"] for field in plan["policy_fields"]]
    assert field_names == [
        f"{goal1}：1 産業振興、起業・創業",
        f"{goal1}：2 商店街活性化",
        f"{goal1}：3 農林水産業振興",
        f"{goal1}：4 観光振興",
        f"{goal2}：5 ワーク・ライフ・バランス、子育て支援",
        f"{goal2}：6 教育",
        f"{goal2}：7 共生社会・地域コミュニティ",
        f"{goal3}：8 人材育成・還流",
        f"{goal3}：9 関係人口、副業・兼業人材",
        f"{goal3}：10 歴史・伝統・文化・芸術",
        f"{goal3}：11 スポーツ",
        f"{goal4}：12 健康・医療",
        f"{goal4}：13 自然・環境",
        f"{goal4}：14 都市デザイン（水辺・公共交通）",
        f"{goal4}：15 都市デザイン（まちなみ・公園）",
        f"{goal4}：16 安心・安全、社会資本整備",
        f"{goal4}：17 行財政改革、スマート自治体",
        f"{goal5}：18 広域連携",
    ]
    assert all(field["measures"] == [] for field in plan["policy_fields"])
    principles = "".join(plan["management_principles"])
    assert "実施計画" in principles
    assert "verified_fixed_period" in principles


def test_matsue_fiscal_records_hold_verified_values() -> None:
    records = {record["id"]: record for record in _package()["fiscal_records"]}
    budget = records["jp-local-322016-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 119_391_000_000
    assert budget["sources"] == ["matsue-budget-2026"]
    assert "議第56号" in budget["note"]
    assert "119,391,000千円" in budget["note"]
    assert "原案可決" in budget["note"]
    assert "千円単位" in budget["note"]
    revenue = records["jp-local-322016-fiscal-2024-total-revenue"]
    assert revenue["stage"] == "settlement"
    assert revenue["amount_yen"] == 115_607_870_000
    assert revenue["sources"] == ["matsue-settlement-2024"]
    assert "決算第1号" in revenue["note"]
    assert "115,607,870千円" in revenue["note"]
    assert "2025年10月7日" in revenue["note"]
    expenditure = records["jp-local-322016-fiscal-2024-total-expenditure"]
    assert expenditure["amount_yen"] == 113_268_794_000
    assert expenditure["sources"] == ["matsue-settlement-2024"]
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 2_339_076_000


def test_matsue_fy2024_settlement_values_and_real_balance() -> None:
    records = {record["id"]: record for record in _package()["fiscal_records"]}
    revenue = records["jp-local-322016-fiscal-2024-total-revenue"]
    expenditure = records["jp-local-322016-fiscal-2024-total-expenditure"]
    # Values pinned from the official settlement overview and the audit
    # commissioners' opinion (both published at thousand-yen precision).
    assert revenue["amount_yen"] == 115_607_870 * 1000
    assert expenditure["amount_yen"] == 113_268_794 * 1000
    # 形式収支 (revenue minus expenditure) matches both documents.
    assert 115_607_870 - 113_268_794 == 2_339_076
    # 実質収支 at the same published precision:
    # 2,339,076 - 376,090 = 1,962,986 (千円).
    assert 2_339_076 - 376_090 == 1_962_986
    assert "2,339,076千円" in expenditure["note"]
    assert "1,962,986千円" in expenditure["note"]
    assert "376,090千円" in expenditure["note"]
    assert "千円精度のまま" in expenditure["note"]


def test_matsue_fy2024_settlement_certification_wording() -> None:
    text = CANDIDATE_PATH.read_text(encoding="utf-8")
    assert "決算第1号" in text
    assert "認定" in text
    # Settlement bill 1 was certified on 2025-10-07; the candidate must
    # not carry the opposite outcome or an amended-adoption wording.
    assert "不認定" not in text
    assert "修正可決" not in text
    assert "修正議決" not in text


def test_matsue_fy2026_budget_vote_wording() -> None:
    packets = {packet["id"]: packet for packet in _package()["evidence_packets"]}
    claim = packets["evidence-matsue-city-2026-total-expenditure"]["claims"][0]
    # Bill 56 was adopted as proposed; the claim keeps the primary
    # source's own wording and the thousand-yen precision.
    assert "原案可決" in claim["statement"]
    assert "議第56号" in claim["statement"]
    assert "119,391,000千円" in claim["statement"]


def test_matsue_evidence_packets_cover_the_three_fiscal_records() -> None:
    packets = {packet["id"]: packet for packet in _package()["evidence_packets"]}
    assert set(packets) == {
        "evidence-matsue-city-2026-total-expenditure",
        "evidence-matsue-city-2024-total-revenue",
        "evidence-matsue-city-2024-total-expenditure",
    }
    for packet in packets.values():
        assert packet["review_status"] == "needs_review"
        assert len(packet["claims"]) == 1
        assert packet["claims"][0]["decision"] == "needs_review"
    budget_claim = packets["evidence-matsue-city-2026-total-expenditure"]["claims"][0]
    assert "原案可決" in budget_claim["statement"]
    assert "119,391,000千円" in budget_claim["statement"]
    revenue_claim = packets["evidence-matsue-city-2024-total-revenue"]["claims"][0]
    assert "決算第1号" in revenue_claim["statement"]
    assert "115,607,870千円" in revenue_claim["statement"]
    expenditure_claim = packets["evidence-matsue-city-2024-total-expenditure"]["claims"][0]
    assert "113,268,794千円" in expenditure_claim["statement"]
    assert "1,962,986千円" in expenditure_claim["statement"]


def test_matsue_progress_review_stays_staging() -> None:
    progress = _package()["progress_review"]
    assert progress["review_status"] == "review_candidate_staging"
    framework = progress["implementation_plan_framework"]
    assert "実施計画" in framework["title"]
    assert "PDCA" in framework["evaluation_structure"]


def test_matsue_promotion_is_reflected_in_review_queue() -> None:
    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    summary = queue["summary"]
    assert summary["reviewed_complete_count"] == 55
    assert summary["pending_record_review_count"] == 12
    assert summary["next_official_code"] == "362018"
    entry = next(
        item for item in queue["execution_queue"] if item["official_code"] == "322016"
    )
    assert entry["status"] == "reviewed_complete"
    assert entry["completion_path"] == "data/catalog/matsue_phase15_completion.json"
