"""Staging tests for the Nishinomiya Phase 15 review candidate.

The candidate stays prepared and unpublished until a human checks the
cited primary sources.  These tests pin the package state, the source
catalog, the plan framework, and the verified fiscal values so that a
promotion change has to be deliberate.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = (
    ROOT / "data" / "candidates" / "nishinomiya-city" / "review_candidate.json"
)
INVENTORY_PATH = ROOT / "data" / "indexed" / "nishinomiya-city" / "source_inventory.json"
QUEUE_PATH = ROOT / "data" / "catalog" / "phase15_core_capital_review_queue.json"


def _candidate() -> dict:
    return json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))


def _package() -> dict:
    return _candidate()["candidate_package"]


def test_nishinomiya_candidate_is_prepared_with_delegated_review_approved() -> None:
    candidate = _candidate()
    assert candidate["candidate_id"] == "nishinomiya-phase15-review-candidate"
    assert candidate["official_code"] == "282049"
    assert candidate["name_ja"] == "西宮市"
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


def test_nishinomiya_candidate_sources_match_phase14_inventory() -> None:
    package_sources = {
        source["id"]: source for source in _package()["source_catalog"]["sources"]
    }
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    inventory_sources = {source["id"]: source for source in inventory["sources"]}
    assert set(package_sources) == set(inventory_sources)
    for source_id, source in package_sources.items():
        assert source["official_url"] == inventory_sources[source_id]["official_url"]
        assert source["official_url"].startswith("https://www.nishi.or.jp/")
        assert source["verification_status"] == "primary_source_live_verified_2026-11-16"


def test_nishinomiya_plan_review_records_framework_and_transition() -> None:
    records = {record["id"]: record for record in _package()["plan_review"]["records"]}
    assert set(records) == {
        "nishinomiya-current-plan-period",
        "nishinomiya-current-policy-structure",
        "nishinomiya-progress-governance-framework",
        "nishinomiya-plan-transition",
        "nishinomiya-fy2024-settlement-linkage",
    }
    period = records["nishinomiya-current-plan-period"]
    assert period["decision"] == "needs_review"
    assert period["title"].startswith("第5次西宮市総合計画の構成")
    assert "基本構想2019年度～2028年度" in period["value"]
    assert "後期2024年度～2028年度" in period["value"]
    linkage = records["nishinomiya-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["fiscal_year"] == 2024


def test_nishinomiya_policy_structure_keeps_six_parts_and_35_fields() -> None:
    plan = _package()["policy_structure"]["current_plan"]
    assert plan["title"].startswith("第5次西宮市総合計画 後期基本計画")
    assert plan["vision"] == (
        "未来を拓く文教住宅都市・西宮 ～憩い、学び、つながりのある美しいまち～"
    )
    assert plan["start_fiscal_year"] == 2024
    assert plan["end_fiscal_year"] == 2028
    assert plan["period_status"] == "verified_fixed_period"
    field_names = [field["name_ja"] for field in plan["policy_fields"]]
    assert field_names == [
        "第Ⅰ部 住環境・自然環境：住環境",
        "第Ⅰ部 住環境・自然環境：緑・自然",
        "第Ⅰ部 住環境・自然環境：景観",
        "第Ⅰ部 住環境・自然環境：市街地",
        "第Ⅰ部 住環境・自然環境：公共交通",
        "第Ⅱ部 子供・教育：子供・子育て支援",
        "第Ⅱ部 子供・教育：学校教育",
        "第Ⅱ部 子供・教育：青少年育成",
        "第Ⅲ部 福祉・健康・共生：地域福祉",
        "第Ⅲ部 福祉・健康・共生：高齢者福祉",
        "第Ⅲ部 福祉・健康・共生：障害のある人の福祉",
        "第Ⅲ部 福祉・健康・共生：生活支援",
        "第Ⅲ部 福祉・健康・共生：医療保険・年金・医療費助成",
        "第Ⅲ部 福祉・健康・共生：医療サービス",
        "第Ⅲ部 福祉・健康・共生：健康増進・公衆衛生",
        "第Ⅲ部 福祉・健康・共生：人権・多文化共生・平和",
        "第Ⅳ部 都市の魅力・産業：生涯学習",
        "第Ⅳ部 都市の魅力・産業：文化芸術",
        "第Ⅳ部 都市の魅力・産業：スポーツ",
        "第Ⅳ部 都市の魅力・産業：都市ブランド",
        "第Ⅳ部 都市の魅力・産業：大学連携",
        "第Ⅳ部 都市の魅力・産業：産業",
        "第Ⅳ部 都市の魅力・産業：農業・食の流通",
        "第Ⅳ部 都市の魅力・産業：就業・労働",
        "第Ⅴ部 環境・都市基盤、安全・安心：環境保全",
        "第Ⅴ部 環境・都市基盤、安全・安心：生活環境",
        "第Ⅴ部 環境・都市基盤、安全・安心：水道",
        "第Ⅴ部 環境・都市基盤、安全・安心：下水道",
        "第Ⅴ部 環境・都市基盤、安全・安心：道路",
        "第Ⅴ部 環境・都市基盤、安全・安心：防災・減災",
        "第Ⅴ部 環境・都市基盤、安全・安心：消防",
        "第Ⅴ部 環境・都市基盤、安全・安心：地域防犯・交通安全・消費者安全",
        "第Ⅵ部 政策推進：住民自治・地域行政",
        "第Ⅵ部 政策推進：政策推進",
        "第Ⅵ部 政策推進：執行体制",
    ]
    assert all(field["measures"] == [] for field in plan["policy_fields"])
    principles = "".join(plan["management_principles"])
    assert "ローリング" in principles
    assert "not_assessable" not in principles


def test_nishinomiya_fiscal_records_hold_verified_values_and_vote_facts() -> None:
    records = {record["id"]: record for record in _package()["fiscal_records"]}
    budget = records["jp-local-282049-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 221_422_490_000
    assert budget["sources"] == ["nishinomiya-budget-2026"]
    assert "議案第493号" in budget["note"]
    assert "賛成多数" in budget["note"]
    assert "千円単位" in budget["note"]
    assert "2026年3月18日" in budget["note"]
    assert "議決結果" in budget["note"]
    revenue = records["jp-local-282049-fiscal-2024-total-revenue"]
    assert revenue["stage"] == "settlement"
    assert revenue["amount_yen"] == 205_479_435_000
    assert revenue["sources"] == ["nishinomiya-settlement-2024"]
    assert "認定第15号" in revenue["note"]
    assert "認定された" in revenue["note"]
    assert "205,479,435千円" in revenue["note"]
    assert "2025年10月2日" in revenue["note"]
    assert "万円精度のまま" not in revenue["note"]
    expenditure = records["jp-local-282049-fiscal-2024-total-expenditure"]
    assert expenditure["amount_yen"] == 204_547_927_000
    assert expenditure["sources"] == ["nishinomiya-settlement-2024"]
    assert "1,861,075千円" in expenditure["note"]
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 931_508_000


def test_nishinomiya_fy2024_settlement_values_at_thousand_yen_precision() -> None:
    records = {record["id"]: record for record in _package()["fiscal_records"]}
    revenue = records["jp-local-282049-fiscal-2024-total-revenue"]
    expenditure = records["jp-local-282049-fiscal-2024-total-expenditure"]
    # Values pinned from the audit opinion's section 6 table (決算収支の状況).
    assert revenue["amount_yen"] == 205_479_435_000
    assert expenditure["amount_yen"] == 204_547_927_000
    # 形式収支 (revenue minus expenditure) matches the same table.
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 931_508_000
    # 実質収支 = 形式収支 - 翌年度へ繰り越すべき財源 (283,979千円).
    assert 931_508_000 - 283_979_000 == 647_529_000
    assert "931,508千円" in expenditure["note"]
    assert "647,529千円" in expenditure["note"]
    assert "283,979千円" in expenditure["note"]
    # The previously recorded man-yen figures are truncations of these values.
    assert revenue["amount_yen"] // 10_000 == 20_547_943
    assert expenditure["amount_yen"] // 10_000 == 20_454_792
    # The combined general/special real balance is not reused as the
    # general account value.
    assert "1,861,075千円" in expenditure["note"]
    assert "流用しない" in expenditure["note"]


def test_nishinomiya_fy2024_settlement_certification_is_verified() -> None:
    text = CANDIDATE_PATH.read_text(encoding="utf-8")
    assert "認定第15号" in text
    assert "認定された" in text
    assert "不認定" not in text
    assert "原案可決" not in text
    # Both vote dates are pinned from the council minutes search system.
    assert "2025年10月2日" in text
    assert "2026年3月18日" in text


def test_nishinomiya_evidence_packets_cover_the_three_fiscal_records() -> None:
    packets = {packet["id"]: packet for packet in _package()["evidence_packets"]}
    assert set(packets) == {
        "evidence-nishinomiya-city-2026-total-expenditure",
        "evidence-nishinomiya-city-2024-total-revenue",
        "evidence-nishinomiya-city-2024-total-expenditure",
    }
    for packet in packets.values():
        assert packet["review_status"] == "needs_review"
        assert len(packet["claims"]) == 1
        assert packet["claims"][0]["decision"] == "needs_review"
    budget_claim = packets["evidence-nishinomiya-city-2026-total-expenditure"]["claims"][0]
    assert "議案第493号" in budget_claim["statement"]
    assert "賛成多数" in budget_claim["statement"]
    revenue_claim = packets["evidence-nishinomiya-city-2024-total-revenue"]["claims"][0]
    assert "認定第15号" in revenue_claim["statement"]
    assert "205,479,435千円" in revenue_claim["statement"]
    assert "2025年10月2日" in revenue_claim["statement"]
    expenditure_claim = packets["evidence-nishinomiya-city-2024-total-expenditure"][
        "claims"
    ][0]
    assert "204,547,927千円" in expenditure_claim["statement"]
    assert "647,529千円" in expenditure_claim["statement"]


def test_nishinomiya_progress_review_stays_staging() -> None:
    progress = _package()["progress_review"]
    assert progress["review_status"] == "review_candidate_staging"
    framework = progress["implementation_plan_framework"]
    assert framework["title"].startswith("第5次西宮市総合計画実施計画")
    assert "ローリング" in framework["evaluation_structure"]


def test_nishinomiya_promotion_is_reflected_in_review_queue() -> None:
    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    summary = queue["summary"]
    assert summary["reviewed_complete_count"] == 58
    assert summary["pending_record_review_count"] == 9
    assert summary["next_official_code"] == "392014"
    entry = next(
        item for item in queue["execution_queue"] if item["official_code"] == "282049"
    )
    assert entry["status"] == "reviewed_complete"
    assert entry["completion_path"] == (
        "data/catalog/nishinomiya_phase15_completion.json"
    )
