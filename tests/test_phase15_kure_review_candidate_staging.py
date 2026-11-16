"""Staging tests for the Kure Phase 15 review candidate.

The candidate stays prepared and unpublished until a human checks the
cited primary sources.  These tests pin the package state, the source
catalog, the plan framework, and the verified fiscal values so that a
promotion change has to be deliberate.  The FY2026 initial budget vote
(bill 1, result recorded as "可決" in the council's own wording) and
the FY2024 settlement certification (bill 99, certified) were both read
directly from the council's official bill/result pages; both vote
dates were identified from those pages' publication dates and still
await final confirmation against the plenary minutes.  The FY2024
settlement totals are published at yen precision in the settlement
book, so they are pinned at that precision, while the real balance
stays at the thousand-yen precision of the balance statement.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = ROOT / "data" / "candidates" / "kure-city" / "review_candidate.json"
INVENTORY_PATH = ROOT / "data" / "indexed" / "kure-city" / "source_inventory.json"
QUEUE_PATH = ROOT / "data" / "catalog" / "phase15_core_capital_review_queue.json"


def _candidate() -> dict:
    return json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))


def _package() -> dict:
    return _candidate()["candidate_package"]


def test_kure_candidate_is_prepared_with_delegated_review_approved() -> None:
    candidate = _candidate()
    assert candidate["candidate_id"] == "kure-phase15-review-candidate"
    assert candidate["official_code"] == "342025"
    assert candidate["name_ja"] == "呉市"
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


def test_kure_candidate_sources_match_phase14_inventory() -> None:
    package_sources = {
        source["id"]: source for source in _package()["source_catalog"]["sources"]
    }
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    inventory_sources = {source["id"]: source for source in inventory["sources"]}
    assert set(package_sources) == set(inventory_sources)
    assert set(package_sources) == {
        "kure-fifth-latter-plan",
        "kure-kpi-progress-2026",
        "kure-budget-2026",
        "kure-settlement-2024",
    }
    for source_id, source in package_sources.items():
        assert source["official_url"] == inventory_sources[source_id]["official_url"]
        assert source["official_url"].startswith("https://www.city.kure.lg.jp/")
        assert source["verification_status"] == "primary_source_live_verified_2026-11-16"


def test_kure_plan_review_records_framework_and_transition() -> None:
    records = {record["id"]: record for record in _package()["plan_review"]["records"]}
    assert set(records) == {
        "kure-current-plan-period",
        "kure-current-policy-structure",
        "kure-progress-governance-framework",
        "kure-plan-transition",
        "kure-fy2024-settlement-linkage",
    }
    period = records["kure-current-plan-period"]
    assert period["decision"] == "needs_review"
    assert period["title"].startswith("第5次呉市長期総合計画の構成")
    assert "基本構想2021年度～2030年度" in period["value"]
    assert "後期2026年度～2030年度" in period["value"]
    transition = records["kure-plan-transition"]
    assert "前期" in transition["statement"]
    assert "後期" in transition["statement"]
    assert "未確認" in transition["statement"]
    linkage = records["kure-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["fiscal_year"] == 2024


def test_kure_policy_structure_keeps_eight_policy_fields() -> None:
    plan = _package()["policy_structure"]["current_plan"]
    assert plan["title"].startswith("第5次呉市長期総合計画")
    assert plan["vision"] == (
        "誰もが住み続けたい，行ってみたい，人を惹きつけるまち「くれ」"
        "〜イキイキと働き，豊かに安心して暮らし，ワクワク生きる〜"
    )
    assert plan["start_fiscal_year"] == 2021
    assert plan["end_fiscal_year"] == 2030
    assert plan["period_status"] == "verified_fixed_period"
    field_names = [field["name_ja"] for field in plan["policy_fields"]]
    assert field_names == [
        "子育て・教育",
        "福祉保健",
        "市民生活・防災",
        "文化・スポーツ・生涯学習",
        "産業",
        "都市基盤",
        "環境",
        "行政経営",
    ]
    assert all(field["measures"] == [] for field in plan["policy_fields"])
    principles = "".join(plan["management_principles"])
    assert "構成事業集" in principles
    assert "重要業績評価指標" in principles
    assert "verified_fixed_period" in principles


def test_kure_fiscal_records_hold_verified_values() -> None:
    records = {record["id"]: record for record in _package()["fiscal_records"]}
    budget = records["jp-local-342025-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 115_430_000_000
    assert budget["sources"] == ["kure-budget-2026"]
    assert "議第1号" in budget["note"]
    assert "115,430,000千円" in budget["note"]
    assert "『可決』" in budget["note"]
    assert "千円単位" in budget["note"]
    revenue = records["jp-local-342025-fiscal-2024-total-revenue"]
    assert revenue["stage"] == "settlement"
    assert revenue["amount_yen"] == 115_037_162_518
    assert revenue["sources"] == ["kure-settlement-2024"]
    assert "議第99号" in revenue["note"]
    assert "115,037,162,518円" in revenue["note"]
    assert "2025年9月24日" in revenue["note"]
    expenditure = records["jp-local-342025-fiscal-2024-total-expenditure"]
    assert expenditure["amount_yen"] == 110_880_880_516
    assert expenditure["sources"] == ["kure-settlement-2024"]
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 4_156_282_002


def test_kure_fy2024_settlement_values_and_real_balance() -> None:
    records = {record["id"]: record for record in _package()["fiscal_records"]}
    revenue = records["jp-local-342025-fiscal-2024-total-revenue"]
    expenditure = records["jp-local-342025-fiscal-2024-total-expenditure"]
    # Values pinned from the official settlement book attached to
    # bill 99, whose totals are published at yen precision.
    assert revenue["amount_yen"] == 115_037_162_518
    assert expenditure["amount_yen"] == 110_880_880_516
    # 形式収支 (revenue minus expenditure) matches the printed balance.
    assert 115_037_162_518 - 110_880_880_516 == 4_156_282_002
    # 実質収支 stays at the balance statement's thousand-yen precision:
    # 4,156,282,002 - 1,254,694,000 = 2,901,588,002 yen, published as
    # 2,901,588 thousand yen; no yen figure is synthesized.
    assert 4_156_282_002 - 1_254_694_000 == 2_901_588_002
    assert "4,156,282,002円" in expenditure["note"]
    assert "2,901,588千円" in expenditure["note"]
    assert "1,254,694,000円" in expenditure["note"]
    assert "千円単位のまま" in expenditure["note"]


def test_kure_fy2024_settlement_certification_wording() -> None:
    text = CANDIDATE_PATH.read_text(encoding="utf-8")
    assert "議第99号" in text
    assert "認定" in text
    # Bill 99 was certified at the September 2025 session; the
    # candidate must not carry the opposite outcome.
    assert "不認定" not in text


def test_kure_fy2026_budget_vote_wording() -> None:
    text = CANDIDATE_PATH.read_text(encoding="utf-8")
    packets = {packet["id"]: packet for packet in _package()["evidence_packets"]}
    claim = packets["evidence-kure-city-2026-total-expenditure"]["claims"][0]
    # The council's result column records bill 1 simply as "可決"; the
    # candidate keeps that wording and never upgrades it.
    assert "『可決』" in claim["statement"]
    assert "議第1号" in claim["statement"]
    assert "115,430,000千円" in claim["statement"]
    assert "原案可決" not in text
    assert "修正可決" not in text
    assert "修正議決" not in text


def test_kure_vote_dates_keep_minutes_confirmation_open() -> None:
    text = CANDIDATE_PATH.read_text(encoding="utf-8")
    # Both dates were identified from the official result pages'
    # publication dates; confirmation against the plenary minutes is
    # still outstanding and must stay explicit.
    assert "2026年3月24日" in text
    assert "2025年9月24日" in text
    assert "本会議録による最終確認は未実施" in text


def test_kure_evidence_packets_cover_the_three_fiscal_records() -> None:
    packets = {packet["id"]: packet for packet in _package()["evidence_packets"]}
    assert set(packets) == {
        "evidence-kure-city-2026-total-expenditure",
        "evidence-kure-city-2024-total-revenue",
        "evidence-kure-city-2024-total-expenditure",
    }
    for packet in packets.values():
        assert packet["review_status"] == "needs_review"
        assert len(packet["claims"]) == 1
        assert packet["claims"][0]["decision"] == "needs_review"
    budget_claim = packets["evidence-kure-city-2026-total-expenditure"]["claims"][0]
    assert "議第1号" in budget_claim["statement"]
    assert "115,430,000千円" in budget_claim["statement"]
    revenue_claim = packets["evidence-kure-city-2024-total-revenue"]["claims"][0]
    assert "議第99号" in revenue_claim["statement"]
    assert "115,037,162,518円" in revenue_claim["statement"]
    expenditure_claim = packets["evidence-kure-city-2024-total-expenditure"]["claims"][0]
    assert "110,880,880,516円" in expenditure_claim["statement"]
    assert "2,901,588千円" in expenditure_claim["statement"]


def test_kure_progress_review_stays_staging() -> None:
    progress = _package()["progress_review"]
    assert progress["review_status"] == "review_candidate_staging"
    framework = progress["implementation_plan_framework"]
    assert "構成事業集" in framework["title"]
    assert "重要業績評価指標" in framework["evaluation_structure"]


def test_kure_promotion_is_reflected_in_review_queue() -> None:
    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    summary = queue["summary"]
    assert summary["reviewed_complete_count"] == 66
    assert summary["pending_record_review_count"] == 1
    assert summary["next_official_code"] == "472018"
    entry = next(
        item for item in queue["execution_queue"] if item["official_code"] == "342025"
    )
    assert entry["status"] == "reviewed_complete"
    assert entry["completion_path"] == "data/catalog/kure_phase15_completion.json"
