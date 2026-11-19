"""Staging tests for the Shimonoseki Phase 15 review candidate.

The candidate stays prepared and unpublished until a human checks the
cited primary sources.  These tests pin the package state, the source
catalog, the plan framework, and the verified fiscal values so that a
promotion change has to be deliberate.  The FY2026 initial budget vote
(bill 16, result recorded as "可決" in the council's own wording) and
the FY2024 settlement certification (bill 116, certified) were both
read directly from the council's official bill-result registers
(議決事件簿), which print the submission date, the vote date, and the
result for every bill, so neither date rests on a session schedule.
The budget total itself was read from Article 1 of the budget book;
that PDF carries no extractable text, so it was rendered to images and
checked visually.  The FY2024 settlement totals are pinned at the yen
precision printed in the settlement book's summary table, while the
real balance stays at the thousand-yen precision of the statement of
real balance.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = (
    ROOT / "data" / "candidates" / "shimonoseki-city" / "review_candidate.json"
)
INVENTORY_PATH = (
    ROOT / "data" / "indexed" / "shimonoseki-city" / "source_inventory.json"
)
QUEUE_PATH = ROOT / "data" / "catalog" / "phase15_core_capital_review_queue.json"


def _candidate() -> dict:
    return json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))


def _package() -> dict:
    return _candidate()["candidate_package"]


def test_shimonoseki_candidate_is_prepared_with_delegated_review_approved() -> None:
    candidate = _candidate()
    assert candidate["candidate_id"] == "shimonoseki-phase15-review-candidate"
    assert candidate["official_code"] == "352012"
    assert candidate["name_ja"] == "下関市"
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
    assert "レビューはあなたがやってください" in candidate["human_review"][
        "reviewer_note"
    ]
    assert candidate["publication"]["eligible"] is False


def test_shimonoseki_candidate_sources_match_phase14_inventory() -> None:
    package_sources = {
        source["id"]: source for source in _package()["source_catalog"]["sources"]
    }
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    inventory_sources = {source["id"]: source for source in inventory["sources"]}
    assert set(package_sources) == set(inventory_sources)
    assert set(package_sources) == {
        "shimonoseki-third-plan",
        "shimonoseki-implementation-2026-2030",
        "shimonoseki-budget-2026",
        "shimonoseki-settlement-2024",
    }
    for source_id, source in package_sources.items():
        assert source["official_url"] == inventory_sources[source_id]["official_url"]
        assert source["official_url"].startswith(
            "https://www.city.shimonoseki.lg.jp/"
        )
        assert (
            source["verification_status"]
            == "primary_source_live_verified_2026-11-16"
        )


def test_shimonoseki_plan_review_records_framework_and_transition() -> None:
    records = {record["id"]: record for record in _package()["plan_review"]["records"]}
    assert set(records) == {
        "shimonoseki-current-plan-period",
        "shimonoseki-current-policy-structure",
        "shimonoseki-progress-governance-framework",
        "shimonoseki-plan-transition",
        "shimonoseki-fy2024-settlement-linkage",
    }
    period = records["shimonoseki-current-plan-period"]
    assert period["decision"] == "needs_review"
    assert period["title"].startswith("第3次下関市総合計画の構成")
    assert "2025年度～2034年度" in period["value"]
    assert "37事業" in period["value"]
    transition = records["shimonoseki-plan-transition"]
    assert "第2次下関市総合計画" in transition["statement"]
    assert "第3次下関市総合計画" in transition["statement"]
    assert "未確認" in transition["statement"]
    linkage = records["shimonoseki-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["fiscal_year"] == 2024


def test_shimonoseki_policy_structure_keeps_eight_chapters() -> None:
    plan = _package()["policy_structure"]["current_plan"]
    assert plan["title"].startswith("第3次下関市総合計画")
    assert plan["vision"] == "可能性を築くまち"
    assert plan["start_fiscal_year"] == 2025
    assert plan["end_fiscal_year"] == 2034
    assert plan["period_status"] == "verified_fixed_period"
    field_names = [field["name_ja"] for field in plan["policy_fields"]]
    assert field_names == [
        "産業・就業",
        "交流・にぎわい",
        "こども・子育て・教育",
        "健康・保健・福祉・医療",
        "都市基盤・生活基盤",
        "環境",
        "安全・安心・共生・協働",
        "行政経営",
    ]
    assert all(field["measures"] == [] for field in plan["policy_fields"])
    principles = "".join(plan["management_principles"])
    assert "実施計画" in principles
    assert "37事業" in principles
    assert "verified_fixed_period" in principles


def test_shimonoseki_fiscal_records_hold_verified_values() -> None:
    records = {record["id"]: record for record in _package()["fiscal_records"]}
    budget = records["jp-local-352012-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 142_580_000_000
    assert budget["sources"] == ["shimonoseki-budget-2026"]
    assert "議案第16号" in budget["note"]
    assert "142,580,000千円" in budget["note"]
    assert "『可決』" in budget["note"]
    assert "千円単位" in budget["note"]
    revenue = records["jp-local-352012-fiscal-2024-total-revenue"]
    assert revenue["stage"] == "settlement"
    assert revenue["amount_yen"] == 154_157_063_123
    assert revenue["sources"] == ["shimonoseki-settlement-2024"]
    assert "議案第116号" in revenue["note"]
    assert "154,157,063,123円" in revenue["note"]
    assert "2025年9月30日" in revenue["note"]
    expenditure = records["jp-local-352012-fiscal-2024-total-expenditure"]
    assert expenditure["amount_yen"] == 147_926_762_467
    assert expenditure["sources"] == ["shimonoseki-settlement-2024"]
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 6_230_300_656


def test_shimonoseki_fy2024_settlement_values_and_real_balance() -> None:
    records = {record["id"]: record for record in _package()["fiscal_records"]}
    revenue = records["jp-local-352012-fiscal-2024-total-revenue"]
    expenditure = records["jp-local-352012-fiscal-2024-total-expenditure"]
    # Yen-precise totals printed in the settlement book's summary table.
    assert revenue["amount_yen"] == 154_157_063_123
    assert expenditure["amount_yen"] == 147_926_762_467
    # 形式収支 (revenue minus expenditure) matches the computed balance
    # and is consistent with the thousand-yen tables (6,230,301千円).
    assert 154_157_063_123 - 147_926_762_467 == 6_230_300_656
    # 実質収支 stays at the statement's thousand-yen precision:
    # 6,230,301 - 2,048,008 = 4,182,293 thousand yen; no yen figure is
    # synthesized for it.
    assert 6_230_301_000 - 2_048_008_000 == 4_182_293_000
    assert "6,230,301千円" in expenditure["note"]
    assert "4,182,293千円" in expenditure["note"]
    assert "2,048,008千円" in expenditure["note"]
    assert "千円単位のまま" in expenditure["note"]


def test_shimonoseki_fy2024_settlement_certification_wording() -> None:
    text = CANDIDATE_PATH.read_text(encoding="utf-8")
    assert "議案第116号" in text
    assert "認定" in text
    # Bill 116 was certified at the September 2025 session; the
    # candidate must not carry the opposite outcome.
    assert "不認定" not in text


def test_shimonoseki_fy2026_budget_vote_wording() -> None:
    text = CANDIDATE_PATH.read_text(encoding="utf-8")
    packets = {packet["id"]: packet for packet in _package()["evidence_packets"]}
    claim = packets["evidence-shimonoseki-city-2026-total-expenditure"]["claims"][0]
    # The council register's result column records bill 16 simply as
    # "可決"; the candidate keeps that wording and never upgrades it.
    assert "『可決』" in claim["statement"]
    assert "議案第16号" in claim["statement"]
    assert "142,580,000千円" in claim["statement"]
    assert "原案可決" not in text
    assert "修正可決" not in text
    assert "修正議決" not in text


def test_shimonoseki_vote_dates_come_from_council_register() -> None:
    text = CANDIDATE_PATH.read_text(encoding="utf-8")
    # Both dates are printed in the council's official bill-result
    # registers (議決事件簿) themselves, so they are recorded as
    # directly confirmed rather than derived from a session schedule.
    assert "2026年3月26日" in text
    assert "2025年9月30日" in text
    assert "議決事件簿" in text


def test_shimonoseki_evidence_packets_cover_the_three_fiscal_records() -> None:
    packets = {packet["id"]: packet for packet in _package()["evidence_packets"]}
    assert set(packets) == {
        "evidence-shimonoseki-city-2026-total-expenditure",
        "evidence-shimonoseki-city-2024-total-revenue",
        "evidence-shimonoseki-city-2024-total-expenditure",
    }
    for packet in packets.values():
        assert packet["review_status"] == "needs_review"
        assert len(packet["claims"]) == 1
        assert packet["claims"][0]["decision"] == "needs_review"
    budget_claim = packets["evidence-shimonoseki-city-2026-total-expenditure"][
        "claims"
    ][0]
    assert "議案第16号" in budget_claim["statement"]
    assert "142,580,000千円" in budget_claim["statement"]
    revenue_claim = packets["evidence-shimonoseki-city-2024-total-revenue"][
        "claims"
    ][0]
    assert "議案第116号" in revenue_claim["statement"]
    assert "154,157,063,123円" in revenue_claim["statement"]
    expenditure_claim = packets[
        "evidence-shimonoseki-city-2024-total-expenditure"
    ]["claims"][0]
    assert "147,926,762,467円" in expenditure_claim["statement"]
    assert "4,182,293千円" in expenditure_claim["statement"]


def test_shimonoseki_progress_review_stays_staging() -> None:
    progress = _package()["progress_review"]
    assert progress["review_status"] == "review_candidate_staging"
    framework = progress["implementation_plan_framework"]
    assert "実施計画" in framework["title"]
    assert "37事業" in framework["title"]
    assert "第2次改定" in framework["evaluation_structure"]


def test_shimonoseki_promotion_is_reflected_in_review_queue() -> None:
    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    summary = queue["summary"]
    assert summary["reviewed_complete_count"] == 69
    assert summary["pending_record_review_count"] == 0
    assert summary["next_official_code"] is None
    entry = next(
        item for item in queue["execution_queue"] if item["official_code"] == "352012"
    )
    assert entry["status"] == "reviewed_complete"
    assert (
        entry["completion_path"]
        == "data/catalog/shimonoseki_phase15_completion.json"
    )
