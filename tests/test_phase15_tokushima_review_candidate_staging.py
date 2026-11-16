"""Staging tests for the Tokushima Phase 15 review candidate.

The candidate stays prepared and unpublished until a human checks the
cited primary sources.  These tests pin the package state, the source
catalog, the plan framework, and the verified fiscal values so that a
promotion change has to be deliberate.  Both votes were read directly
from the council's official plenary minutes: the FY2026 initial budget
(bill 1) was adopted as proposed on 2026-03-24 after the committee
reports recommending adoption as proposed were accepted by a standing
majority, and the FY2024 settlement (bill 104) was certified on
2025-12-18 after continued review by the settlement review special
committee during the recess.  The FY2024 settlement totals stay at the
thousand-yen precision printed in the city's official settlement
summary table; no yen figure is synthesized, and ordinary-account
aggregate figures are not used as general-account values.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = (
    ROOT / "data" / "candidates" / "tokushima-city" / "review_candidate.json"
)
INVENTORY_PATH = (
    ROOT / "data" / "indexed" / "tokushima-city" / "source_inventory.json"
)
QUEUE_PATH = ROOT / "data" / "catalog" / "phase15_core_capital_review_queue.json"


def _candidate() -> dict:
    return json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))


def _package() -> dict:
    return _candidate()["candidate_package"]


def test_tokushima_candidate_is_prepared_with_delegated_review_approved() -> None:
    candidate = _candidate()
    assert candidate["candidate_id"] == "tokushima-phase15-review-candidate"
    assert candidate["official_code"] == "362018"
    assert candidate["name_ja"] == "徳島市"
    assert candidate["status"] == "review_candidate"
    assert candidate["package_state"] == "prepared"
    assert candidate["human_review"]["required"] is True
    assert candidate["human_review"]["status"] == "approved"
    assert candidate["human_review"]["reviewed_at"] == "2026-11-17"
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


def test_tokushima_candidate_sources_match_phase14_inventory() -> None:
    package_sources = {
        source["id"]: source for source in _package()["source_catalog"]["sources"]
    }
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    inventory_sources = {source["id"]: source for source in inventory["sources"]}
    assert set(package_sources) == set(inventory_sources)
    assert set(package_sources) == {
        "tokushima-plan-2025",
        "tokushima-evaluation-2026",
        "tokushima-budget-2026",
        "tokushima-settlement-2024",
    }
    for source_id, source in package_sources.items():
        assert source["official_url"] == inventory_sources[source_id]["official_url"]
        assert source["official_url"].startswith(
            "https://www.city.tokushima.tokushima.jp/"
        )
        assert (
            source["verification_status"]
            == "primary_source_live_verified_2026-11-17"
        )


def test_tokushima_plan_review_records_framework_and_transition() -> None:
    records = {record["id"]: record for record in _package()["plan_review"]["records"]}
    assert set(records) == {
        "tokushima-current-plan-period",
        "tokushima-current-policy-structure",
        "tokushima-progress-governance-framework",
        "tokushima-plan-transition",
        "tokushima-fy2024-settlement-linkage",
    }
    period = records["tokushima-current-plan-period"]
    assert period["decision"] == "needs_review"
    assert period["title"].startswith("徳島市総合計画2025の構成")
    assert "2025年度～2029年度" in period["value"]
    assert "令和8年度版" in period["value"]
    transition = records["tokushima-plan-transition"]
    assert "徳島市総合計画2021" in transition["statement"]
    assert "徳島市総合計画2025" in transition["statement"]
    assert "令和7年3月" in transition["statement"]
    linkage = records["tokushima-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["fiscal_year"] == 2024


def test_tokushima_policy_structure_keeps_six_policies() -> None:
    plan = _package()["policy_structure"]["current_plan"]
    assert plan["title"].startswith("徳島市総合計画2025")
    assert plan["vision"] == "おどる街 つながる笑顔 水都とくしま"
    assert plan["start_fiscal_year"] == 2025
    assert plan["end_fiscal_year"] == 2034
    assert plan["period_status"] == "verified_fixed_period"
    field_names = [field["name_ja"] for field in plan["policy_fields"]]
    assert field_names == [
        "魅力あふれる都市空間の創造",
        "持続可能な徳島経済の創出",
        "安全安心な生活環境の整備",
        "生涯健やかな暮らしの実現",
        "こどもまんなか社会の推進",
        "誰もが活躍できる場の提供",
    ]
    assert all(field["measures"] == [] for field in plan["policy_fields"])
    principles = "".join(plan["management_principles"])
    assert "アクションプラン" in principles
    assert "令和8年度版" in principles
    assert "verified_fixed_period" in principles


def test_tokushima_fiscal_records_hold_verified_values() -> None:
    records = {record["id"]: record for record in _package()["fiscal_records"]}
    budget = records["jp-local-362018-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 123_140_000_000
    assert budget["sources"] == ["tokushima-budget-2026"]
    assert "議案第1号" in budget["note"]
    assert "123,140,000千円" in budget["note"]
    assert "原案可決" in budget["note"]
    assert "千円単位" in budget["note"]
    revenue = records["jp-local-362018-fiscal-2024-total-revenue"]
    assert revenue["stage"] == "settlement"
    assert revenue["amount_yen"] == 119_147_339_000
    assert revenue["sources"] == ["tokushima-settlement-2024"]
    assert "議案第104号" in revenue["note"]
    assert "119,147,339千円" in revenue["note"]
    assert "2025年12月18日" in revenue["note"]
    expenditure = records["jp-local-362018-fiscal-2024-total-expenditure"]
    assert expenditure["amount_yen"] == 117_214_965_000
    assert expenditure["sources"] == ["tokushima-settlement-2024"]
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 1_932_374_000


def test_tokushima_fy2024_settlement_values_and_real_balance() -> None:
    records = {record["id"]: record for record in _package()["fiscal_records"]}
    revenue = records["jp-local-362018-fiscal-2024-total-revenue"]
    expenditure = records["jp-local-362018-fiscal-2024-total-expenditure"]
    # Thousand-yen totals printed in the official settlement summary
    # table of the FY2024 accounts.
    assert revenue["amount_yen"] == 119_147_339_000
    assert expenditure["amount_yen"] == 117_214_965_000
    # 歳入歳出差引 (revenue minus expenditure) matches the printed
    # balance.
    assert 119_147_339_000 - 117_214_965_000 == 1_932_374_000
    # 実質収支 stays at the table's thousand-yen precision:
    # 1,932,374 - 802,445 = 1,129,929 thousand yen; no yen figure is
    # synthesized for it.
    assert 1_932_374_000 - 802_445_000 == 1_129_929_000
    assert "1,932,374千円" in expenditure["note"]
    assert "1,129,929千円" in expenditure["note"]
    assert "802,445千円" in expenditure["note"]
    assert "千円単位のまま" in expenditure["note"]


def test_tokushima_fy2024_settlement_certification_wording() -> None:
    text = CANDIDATE_PATH.read_text(encoding="utf-8")
    assert "議案第104号" in text
    assert "認定" in text
    # Bill 104 was certified at the December 2025 session; the
    # candidate must not carry the opposite outcome.
    assert "不認定" not in text


def test_tokushima_fy2026_budget_vote_wording() -> None:
    text = CANDIDATE_PATH.read_text(encoding="utf-8")
    packets = {packet["id"]: packet for packet in _package()["evidence_packets"]}
    claim = packets["evidence-tokushima-city-2026-total-expenditure"]["claims"][0]
    # The plenary minutes record the committee reports (adoption as
    # proposed) being accepted by a standing majority on 2026-03-24;
    # the candidate keeps that outcome and never records an amended
    # adoption.
    assert "原案可決" in claim["statement"]
    assert "議案第1号" in claim["statement"]
    assert "123,140,000千円" in claim["statement"]
    assert "2026年3月24日" in claim["statement"]
    assert "修正可決" not in text
    assert "修正議決" not in text


def test_tokushima_vote_dates_rest_on_plenary_minutes() -> None:
    text = CANDIDATE_PATH.read_text(encoding="utf-8")
    # Both vote dates were read directly from the official plenary
    # minutes, not inferred from session schedules or publication
    # dates, so no minutes-confirmation caveat is carried.
    assert "2026年3月24日" in text
    assert "2025年12月18日" in text
    assert "会議録第6号" in text
    assert "会議録第24号" in text
    assert "本会議録による最終確認は未実施" not in text


def test_tokushima_evidence_packets_cover_the_three_fiscal_records() -> None:
    packets = {packet["id"]: packet for packet in _package()["evidence_packets"]}
    assert set(packets) == {
        "evidence-tokushima-city-2026-total-expenditure",
        "evidence-tokushima-city-2024-total-revenue",
        "evidence-tokushima-city-2024-total-expenditure",
    }
    for packet in packets.values():
        assert packet["review_status"] == "needs_review"
        assert len(packet["claims"]) == 1
        assert packet["claims"][0]["decision"] == "needs_review"
    budget_claim = packets["evidence-tokushima-city-2026-total-expenditure"][
        "claims"
    ][0]
    assert "議案第1号" in budget_claim["statement"]
    assert "123,140,000千円" in budget_claim["statement"]
    revenue_claim = packets["evidence-tokushima-city-2024-total-revenue"]["claims"][0]
    assert "議案第104号" in revenue_claim["statement"]
    assert "119,147,339千円" in revenue_claim["statement"]
    expenditure_claim = packets["evidence-tokushima-city-2024-total-expenditure"][
        "claims"
    ][0]
    assert "117,214,965千円" in expenditure_claim["statement"]
    assert "1,129,929千円" in expenditure_claim["statement"]


def test_tokushima_progress_review_stays_staging() -> None:
    progress = _package()["progress_review"]
    assert progress["review_status"] == "review_candidate_staging"
    framework = progress["implementation_plan_framework"]
    assert "アクションプラン" in framework["title"]
    assert "令和8年度版" in framework["title"]
    assert "評価委員会" in framework["evaluation_structure"]


def test_tokushima_promotion_is_reflected_in_review_queue() -> None:
    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    summary = queue["summary"]
    assert summary["reviewed_complete_count"] == 58
    assert summary["pending_record_review_count"] == 9
    assert summary["next_official_code"] == "392014"
    entry = next(
        item for item in queue["execution_queue"] if item["official_code"] == "362018"
    )
    assert entry["status"] == "reviewed_complete"
    assert (
        entry["completion_path"]
        == "data/catalog/tokushima_phase15_completion.json"
    )
