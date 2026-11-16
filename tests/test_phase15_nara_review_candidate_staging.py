"""Staging tests for the Nara Phase 15 review candidate.

The candidate stays prepared and unpublished until a human checks the
cited primary sources.  These tests pin the package state, the source
catalog, the plan framework, and the verified fiscal values so that a
promotion change has to be deliberate.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = ROOT / "data" / "candidates" / "nara-city" / "review_candidate.json"
INVENTORY_PATH = ROOT / "data" / "indexed" / "nara-city" / "source_inventory.json"
QUEUE_PATH = ROOT / "data" / "catalog" / "phase15_core_capital_review_queue.json"


def _candidate() -> dict:
    return json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))


def _package() -> dict:
    return _candidate()["candidate_package"]


def test_nara_candidate_is_prepared_with_delegated_review_approved() -> None:
    candidate = _candidate()
    assert candidate["candidate_id"] == "nara-phase15-review-candidate"
    assert candidate["official_code"] == "292010"
    assert candidate["name_ja"] == "奈良市"
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


def test_nara_candidate_sources_match_phase14_inventory() -> None:
    package_sources = {
        source["id"]: source for source in _package()["source_catalog"]["sources"]
    }
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    inventory_sources = {source["id"]: source for source in inventory["sources"]}
    assert set(package_sources) == set(inventory_sources)
    for source_id, source in package_sources.items():
        assert source["official_url"] == inventory_sources[source_id]["official_url"]
        assert source["official_url"].startswith("https://www.city.nara.lg.jp/")
        assert source["verification_status"] == "primary_source_live_verified_2026-11-16"


def test_nara_plan_review_records_framework_and_transition() -> None:
    records = {record["id"]: record for record in _package()["plan_review"]["records"]}
    assert set(records) == {
        "nara-current-plan-period",
        "nara-current-policy-structure",
        "nara-progress-governance-framework",
        "nara-plan-transition",
        "nara-fy2024-settlement-linkage",
    }
    period = records["nara-current-plan-period"]
    assert period["decision"] == "needs_review"
    assert period["title"].startswith("奈良市第5次総合計画の構成")
    assert "未来ビジョン2022年度～2031年度" in period["value"]
    assert "前期2022年度～2026年度" in period["value"]
    transition = records["nara-plan-transition"]
    assert "後期推進方針" in transition["statement"]
    assert "策定過程" in transition["statement"]
    linkage = records["nara-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["fiscal_year"] == 2024


def test_nara_policy_structure_keeps_five_chapters_and_29_measures() -> None:
    plan = _package()["policy_structure"]["current_plan"]
    assert plan["title"].startswith("奈良市第5次総合計画 前期推進方針")
    assert plan["vision"] == "「わたし」からはじめる「わたしたち」のまち 奈良"
    assert plan["start_fiscal_year"] == 2022
    assert plan["end_fiscal_year"] == 2026
    assert plan["period_status"] == "verified_fixed_period"
    field_names = [field["name_ja"] for field in plan["policy_fields"]]
    assert field_names == [
        "第1章 ひとづくり：母子保健の推進と子育て家庭への支援の充実",
        "第1章 ひとづくり：子育て環境の充実",
        "第1章 ひとづくり：学校教育の充実",
        "第1章 ひとづくり：教育支援体制の充実",
        "第1章 ひとづくり：人権と平和の尊重",
        "第1章 ひとづくり：男女共同参画社会の実現",
        "第2章 しごとづくり：観光・交流の促進",
        "第2章 しごとづくり：商工・サービス業の活性化",
        "第2章 しごとづくり：農林業の振興",
        "第2章 しごとづくり：雇用・労働環境の充実",
        "第3章 くらしづくり：地域福祉と総合的な生活保障の推進",
        "第3章 くらしづくり：障害者福祉の充実",
        "第3章 くらしづくり：高齢者福祉の充実",
        "第3章 くらしづくり：医療体制の充実と健康の増進",
        "第3章 くらしづくり：地域コミュニティと市民活動の活性化",
        "第3章 くらしづくり：文化・スポーツの振興",
        "第3章 くらしづくり：社会教育の推進",
        "第3章 くらしづくり：文化遺産の保存と活用",
        "第4章 まちづくり：防災対策の充実",
        "第4章 まちづくり：消防・救急救助体制の充実",
        "第4章 まちづくり：防犯対策と消費者保護の推進",
        "第4章 まちづくり：環境の保全",
        "第4章 まちづくり：生活衛生・環境衛生の向上",
        "第4章 まちづくり：土地・景観の整備",
        "第4章 まちづくり：交通基盤の整備と交通安全の確保",
        "第4章 まちづくり：住環境の向上",
        "第4章 まちづくり：利水・治水対策の推進",
        "第5章 しくみづくり：市民参画と開かれた市政の推進",
        "第5章 しくみづくり：行財政改革の推進",
    ]
    assert all(field["measures"] == [] for field in plan["policy_fields"])
    principles = "".join(plan["management_principles"])
    assert "前期推進方針" in principles
    assert "not_assessable" not in principles


def test_nara_fiscal_records_hold_verified_values_and_vote_facts() -> None:
    records = {record["id"]: record for record in _package()["fiscal_records"]}
    budget = records["jp-local-292010-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 193_425_597_000
    assert budget["sources"] == ["nara-budget-2026"]
    assert "議案第16号" in budget["note"]
    assert "修正可決" in budget["note"]
    assert "千円単位" in budget["note"]
    assert "2026年3月26日" in budget["note"]
    assert "195,000,000千円" in budget["note"]
    revenue = records["jp-local-292010-fiscal-2024-total-revenue"]
    assert revenue["stage"] == "settlement"
    assert revenue["amount_yen"] == 161_996_348_913
    assert revenue["sources"] == ["nara-settlement-2024"]
    assert "報告第41号" in revenue["note"]
    assert "認定された" in revenue["note"]
    assert "161,996,348,913円" in revenue["note"]
    assert "2025年9月29日" in revenue["note"]
    expenditure = records["jp-local-292010-fiscal-2024-total-expenditure"]
    assert expenditure["amount_yen"] == 157_827_488_682
    assert expenditure["sources"] == ["nara-settlement-2024"]
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 4_168_860_231


def test_nara_fy2024_settlement_values_at_yen_precision() -> None:
    records = {record["id"]: record for record in _package()["fiscal_records"]}
    revenue = records["jp-local-292010-fiscal-2024-total-revenue"]
    expenditure = records["jp-local-292010-fiscal-2024-total-expenditure"]
    # Values pinned from the official settlement summary table (単位: 円).
    assert revenue["amount_yen"] == 161_996_348_913
    assert expenditure["amount_yen"] == 157_827_488_682
    # 形式収支 (revenue minus expenditure) matches the same table.
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 4_168_860_231
    # 実質収支 = 形式収支 - 繰り越すべき財源 (820,153,000円).
    assert 4_168_860_231 - 820_153_000 == 3_348_707_231
    assert "4,168,860,231円" in expenditure["note"]
    assert "3,348,707,231円" in expenditure["note"]
    assert "820,153,000円" in expenditure["note"]
    # The thousand-yen figures on the finance page are the rounded
    # thousand-yen display of these yen-precise values.
    assert (revenue["amount_yen"] + 500) // 1000 == 161_996_349
    assert (expenditure["amount_yen"] + 500) // 1000 == 157_827_489


def test_nara_fy2024_settlement_certification_is_verified() -> None:
    text = CANDIDATE_PATH.read_text(encoding="utf-8")
    assert "報告第41号" in text
    assert "認定された" in text
    assert "不認定" not in text
    assert "原案可決" not in text
    # Both vote dates are printed in the council's official result tables.
    assert "2025年9月29日" in text
    assert "2026年3月26日" in text


def test_nara_fy2026_budget_was_passed_with_amendments() -> None:
    text = CANDIDATE_PATH.read_text(encoding="utf-8")
    assert "修正可決" in text
    assert "1,574,403千円" in text
    records = {record["id"]: record for record in _package()["fiscal_records"]}
    budget = records["jp-local-292010-fiscal-2026-total-expenditure"]
    # The enacted amount is the amended total, not the original proposal.
    assert budget["amount_yen"] == 193_425_597_000
    assert budget["amount_yen"] != 195_000_000_000
    assert 195_000_000_000 - budget["amount_yen"] == 1_574_403_000


def test_nara_evidence_packets_cover_the_three_fiscal_records() -> None:
    packets = {packet["id"]: packet for packet in _package()["evidence_packets"]}
    assert set(packets) == {
        "evidence-nara-city-2026-total-expenditure",
        "evidence-nara-city-2024-total-revenue",
        "evidence-nara-city-2024-total-expenditure",
    }
    for packet in packets.values():
        assert packet["review_status"] == "needs_review"
        assert len(packet["claims"]) == 1
        assert packet["claims"][0]["decision"] == "needs_review"
    budget_claim = packets["evidence-nara-city-2026-total-expenditure"]["claims"][0]
    assert "議案第16号" in budget_claim["statement"]
    assert "修正可決" in budget_claim["statement"]
    revenue_claim = packets["evidence-nara-city-2024-total-revenue"]["claims"][0]
    assert "報告第41号" in revenue_claim["statement"]
    assert "161,996,348,913円" in revenue_claim["statement"]
    assert "2025年9月29日" in revenue_claim["statement"]
    expenditure_claim = packets["evidence-nara-city-2024-total-expenditure"]["claims"][0]
    assert "157,827,488,682円" in expenditure_claim["statement"]
    assert "3,348,707,231円" in expenditure_claim["statement"]


def test_nara_progress_review_stays_staging() -> None:
    progress = _package()["progress_review"]
    assert progress["review_status"] == "review_candidate_staging"
    framework = progress["implementation_plan_framework"]
    assert "実施状況" in framework["title"]
    assert "報告第52号" in framework["evaluation_structure"]


def test_nara_promotion_is_reflected_in_review_queue() -> None:
    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    summary = queue["summary"]
    assert summary["reviewed_complete_count"] == 64
    assert summary["pending_record_review_count"] == 3
    assert summary["next_official_code"] == "452017"
    entry = next(
        item for item in queue["execution_queue"] if item["official_code"] == "292010"
    )
    assert entry["status"] == "reviewed_complete"
    assert entry["completion_path"] == "data/catalog/nara_phase15_completion.json"
