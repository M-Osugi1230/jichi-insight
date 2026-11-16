"""Staging tests for the Fukuyama Phase 15 review candidate.

The candidate stays prepared and unpublished until a human checks the
cited primary sources.  These tests pin the package state, the source
catalog, the plan framework, and the verified fiscal values so that a
promotion change has to be deliberate.  The FY2026 initial budget vote
(bill 2, result recorded as "可決" in the council's own wording) and
the FY2024 settlement certification (bill 108, certified) were both
read directly from the council's official bill/result lists; both vote
dates were identified from the council newsletter's session overviews
and still await final confirmation against the plenary minutes.  The
FY2024 settlement totals are published only at thousand-yen precision
in the audit commission's review opinion, so they are pinned at that
precision and no yen figure is synthesized.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = ROOT / "data" / "candidates" / "fukuyama-city" / "review_candidate.json"
INVENTORY_PATH = ROOT / "data" / "indexed" / "fukuyama-city" / "source_inventory.json"
QUEUE_PATH = ROOT / "data" / "catalog" / "phase15_core_capital_review_queue.json"


def _candidate() -> dict:
    return json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))


def _package() -> dict:
    return _candidate()["candidate_package"]


def test_fukuyama_candidate_is_prepared_with_delegated_review_approved() -> None:
    candidate = _candidate()
    assert candidate["candidate_id"] == "fukuyama-phase15-review-candidate"
    assert candidate["official_code"] == "342076"
    assert candidate["name_ja"] == "福山市"
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


def test_fukuyama_candidate_sources_match_phase14_inventory() -> None:
    package_sources = {
        source["id"]: source for source in _package()["source_catalog"]["sources"]
    }
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    inventory_sources = {source["id"]: source for source in inventory["sources"]}
    assert set(package_sources) == set(inventory_sources)
    assert set(package_sources) == {
        "fukuyama-third-vision",
        "fukuyama-progress-governance",
        "fukuyama-budget-2026",
        "fukuyama-settlement-2024",
    }
    for source_id, source in package_sources.items():
        assert source["official_url"] == inventory_sources[source_id]["official_url"]
        assert source["official_url"].startswith(
            "https://www.city.fukuyama.hiroshima.jp/"
        )
        assert source["verification_status"] == "primary_source_live_verified_2026-11-16"


def test_fukuyama_plan_review_records_framework_and_transition() -> None:
    records = {record["id"]: record for record in _package()["plan_review"]["records"]}
    assert set(records) == {
        "fukuyama-current-plan-period",
        "fukuyama-current-policy-structure",
        "fukuyama-progress-governance-framework",
        "fukuyama-plan-transition",
        "fukuyama-fy2024-settlement-linkage",
    }
    period = records["fukuyama-current-plan-period"]
    assert period["decision"] == "needs_review"
    assert period["title"].startswith("第五次福山市総合計画の構成")
    assert "基本構想2017年度～期間の定めなし" in period["value"]
    assert "第3期2026年度～2030年度" in period["value"]
    transition = records["fukuyama-plan-transition"]
    assert "第2期" in transition["statement"]
    assert "第3期" in transition["statement"]
    assert "未確認" in transition["statement"]
    linkage = records["fukuyama-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["fiscal_year"] == 2024


def test_fukuyama_policy_structure_keeps_seven_policy_fields() -> None:
    plan = _package()["policy_structure"]["current_plan"]
    assert plan["title"].startswith("第五次福山市総合計画")
    assert plan["vision"] == "希望、安心、活力ある備後の中核都市"
    assert plan["start_fiscal_year"] == 2026
    assert plan["end_fiscal_year"] == 2030
    assert plan["period_status"] == "verified_fixed_period"
    field_names = [field["name_ja"] for field in plan["policy_fields"]]
    assert field_names == [
        "こども・若者",
        "地域経済",
        "都市基盤",
        "医療・福祉",
        "ばらのまちづくり・文化・スポーツ",
        "地域社会",
        "安心・安全",
    ]
    assert all(field["measures"] == [] for field in plan["policy_fields"])
    principles = "".join(plan["management_principles"])
    assert "福山みらいづくり懇話会" in principles
    assert "重点政策" in principles
    assert "verified_fixed_period" in principles


def test_fukuyama_fiscal_records_hold_verified_values() -> None:
    records = {record["id"]: record for record in _package()["fiscal_records"]}
    budget = records["jp-local-342076-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 207_700_000_000
    assert budget["sources"] == ["fukuyama-budget-2026"]
    assert "議第2号" in budget["note"]
    assert "207,700,000千円" in budget["note"]
    assert "『可決』" in budget["note"]
    assert "千円単位" in budget["note"]
    revenue = records["jp-local-342076-fiscal-2024-total-revenue"]
    assert revenue["stage"] == "settlement"
    assert revenue["amount_yen"] == 220_468_943_000
    assert revenue["sources"] == ["fukuyama-settlement-2024"]
    assert "議第108号" in revenue["note"]
    assert "220,468,943千円" in revenue["note"]
    assert "2025年11月26日" in revenue["note"]
    expenditure = records["jp-local-342076-fiscal-2024-total-expenditure"]
    assert expenditure["amount_yen"] == 212_772_807_000
    assert expenditure["sources"] == ["fukuyama-settlement-2024"]
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 7_696_136_000


def test_fukuyama_fy2024_settlement_values_and_real_balance() -> None:
    records = {record["id"]: record for record in _package()["fiscal_records"]}
    revenue = records["jp-local-342076-fiscal-2024-total-revenue"]
    expenditure = records["jp-local-342076-fiscal-2024-total-expenditure"]
    # Values pinned from the audit commission's review opinion, whose
    # tables are published at thousand-yen precision.
    assert revenue["amount_yen"] == 220_468_943_000
    assert expenditure["amount_yen"] == 212_772_807_000
    # 形式収支 (revenue minus expenditure) matches the printed balance.
    assert 220_468_943_000 - 212_772_807_000 == 7_696_136_000
    # 実質収支 stays at the opinion's thousand-yen precision:
    # 7,696,136 - 2,938,715 = 4,757,421 thousand yen; no yen figure is
    # synthesized.
    assert 7_696_136_000 - 2_938_715_000 == 4_757_421_000
    assert "7,696,136千円" in expenditure["note"]
    assert "4,757,421千円" in expenditure["note"]
    assert "2,938,715千円" in expenditure["note"]
    assert "千円単位のまま" in expenditure["note"]


def test_fukuyama_fy2024_settlement_certification_wording() -> None:
    text = CANDIDATE_PATH.read_text(encoding="utf-8")
    assert "議第108号" in text
    assert "認定" in text
    # Bill 108 was certified at the December 2025 session; the
    # candidate must not carry the opposite outcome.
    assert "不認定" not in text


def test_fukuyama_fy2026_budget_vote_wording() -> None:
    text = CANDIDATE_PATH.read_text(encoding="utf-8")
    packets = {packet["id"]: packet for packet in _package()["evidence_packets"]}
    claim = packets["evidence-fukuyama-city-2026-total-expenditure"]["claims"][0]
    # The council's result column records bill 2 simply as "可決"; the
    # candidate keeps that wording and never upgrades it.
    assert "『可決』" in claim["statement"]
    assert "議第2号" in claim["statement"]
    assert "207,700,000千円" in claim["statement"]
    assert "原案可決" not in text
    assert "修正可決" not in text
    assert "修正議決" not in text


def test_fukuyama_vote_dates_keep_minutes_confirmation_open() -> None:
    text = CANDIDATE_PATH.read_text(encoding="utf-8")
    # Both dates were identified from the council newsletter's session
    # overviews; confirmation against the plenary minutes is still
    # outstanding and must stay explicit.
    assert "2026年3月18日" in text
    assert "2025年11月26日" in text
    assert "本会議録による最終確認は未実施" in text


def test_fukuyama_evidence_packets_cover_the_three_fiscal_records() -> None:
    packets = {packet["id"]: packet for packet in _package()["evidence_packets"]}
    assert set(packets) == {
        "evidence-fukuyama-city-2026-total-expenditure",
        "evidence-fukuyama-city-2024-total-revenue",
        "evidence-fukuyama-city-2024-total-expenditure",
    }
    for packet in packets.values():
        assert packet["review_status"] == "needs_review"
        assert len(packet["claims"]) == 1
        assert packet["claims"][0]["decision"] == "needs_review"
    budget_claim = packets["evidence-fukuyama-city-2026-total-expenditure"]["claims"][0]
    assert "議第2号" in budget_claim["statement"]
    assert "207,700,000千円" in budget_claim["statement"]
    revenue_claim = packets["evidence-fukuyama-city-2024-total-revenue"]["claims"][0]
    assert "議第108号" in revenue_claim["statement"]
    assert "220,468,943千円" in revenue_claim["statement"]
    expenditure_claim = packets[
        "evidence-fukuyama-city-2024-total-expenditure"
    ]["claims"][0]
    assert "212,772,807千円" in expenditure_claim["statement"]
    assert "4,757,421千円" in expenditure_claim["statement"]


def test_fukuyama_progress_review_stays_staging() -> None:
    progress = _package()["progress_review"]
    assert progress["review_status"] == "review_candidate_staging"
    framework = progress["implementation_plan_framework"]
    assert "重点政策" in framework["title"]
    assert "福山みらいづくり懇話会" in framework["evaluation_structure"]


def test_fukuyama_promotion_is_reflected_in_review_queue() -> None:
    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    summary = queue["summary"]
    assert summary["reviewed_complete_count"] == 54
    assert summary["pending_record_review_count"] == 13
    assert summary["next_official_code"] == "352039"
    entry = next(
        item for item in queue["execution_queue"] if item["official_code"] == "342076"
    )
    assert entry["status"] == "reviewed_complete"
    assert entry["completion_path"] == "data/catalog/fukuyama_phase15_completion.json"
