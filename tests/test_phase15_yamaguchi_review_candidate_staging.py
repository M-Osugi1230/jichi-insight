"""Staging tests for the Yamaguchi Phase 15 review candidate.

The candidate stays prepared and unpublished until a human checks the
cited primary sources.  These tests pin the package state, the source
catalog, the plan framework, and the verified fiscal values so that a
promotion change has to be deliberate.  The FY2026 initial budget vote
(bill 1, result recorded as "可決" in the council's own wording) and
the FY2024 settlement certification (bill 21, certified) were both
read directly from the council's official vote lists (議案等の賛否
一覧); both dates are identified from the session schedule / session
period rather than from plenary minutes, and that provenance is kept
in the candidate with the minutes confirmation left open.  The FY2024
settlement totals stay at the thousand-yen precision printed in the
official achievement report's settlement summary table; no yen figure
is synthesized, and ordinary-account aggregate figures published in
audit opinions are not used as general-account values.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = (
    ROOT / "data" / "candidates" / "yamaguchi-city" / "review_candidate.json"
)
INVENTORY_PATH = (
    ROOT / "data" / "indexed" / "yamaguchi-city" / "source_inventory.json"
)
QUEUE_PATH = ROOT / "data" / "catalog" / "phase15_core_capital_review_queue.json"


def _candidate() -> dict:
    return json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))


def _package() -> dict:
    return _candidate()["candidate_package"]


def test_yamaguchi_candidate_is_prepared_with_delegated_review_approved() -> None:
    candidate = _candidate()
    assert candidate["candidate_id"] == "yamaguchi-phase15-review-candidate"
    assert candidate["official_code"] == "352039"
    assert candidate["name_ja"] == "山口市"
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


def test_yamaguchi_candidate_sources_match_phase14_inventory() -> None:
    package_sources = {
        source["id"]: source for source in _package()["source_catalog"]["sources"]
    }
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    inventory_sources = {source["id"]: source for source in inventory["sources"]}
    assert set(package_sources) == set(inventory_sources)
    assert set(package_sources) == {
        "yamaguchi-second-latter-plan",
        "yamaguchi-ninth-action-plan",
        "yamaguchi-achievement-report-2024",
        "yamaguchi-budget-2026",
        "yamaguchi-settlement-2024",
    }
    for source_id, source in package_sources.items():
        assert source["official_url"] == inventory_sources[source_id]["official_url"]
        assert source["official_url"].startswith("https://www.city.yamaguchi.lg.jp/")
        assert (
            source["verification_status"]
            == "primary_source_live_verified_2026-11-16"
        )


def test_yamaguchi_plan_review_records_framework_and_transition() -> None:
    records = {record["id"]: record for record in _package()["plan_review"]["records"]}
    assert set(records) == {
        "yamaguchi-current-plan-period",
        "yamaguchi-current-policy-structure",
        "yamaguchi-progress-governance-framework",
        "yamaguchi-plan-transition",
        "yamaguchi-fy2024-settlement-linkage",
    }
    period = records["yamaguchi-current-plan-period"]
    assert period["decision"] == "needs_review"
    assert period["title"].startswith("第二次山口市総合計画の構成")
    assert "2018年度～2027年度" in period["value"]
    assert "第9次" in period["value"]
    transition = records["yamaguchi-plan-transition"]
    assert "第二次山口市総合計画" in transition["statement"]
    assert "第三次山口市総合計画" in transition["statement"]
    assert "2028年度" in transition["statement"]
    linkage = records["yamaguchi-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["fiscal_year"] == 2024


def test_yamaguchi_policy_structure_keeps_five_policies() -> None:
    plan = _package()["policy_structure"]["current_plan"]
    assert plan["title"].startswith("第二次山口市総合計画")
    assert plan["vision"] == "豊かな暮らし 交流と創造のまち 山口 ～これが私のふるさとだ～"
    assert plan["start_fiscal_year"] == 2018
    assert plan["end_fiscal_year"] == 2027
    assert plan["period_status"] == "transition_or_unresolved"
    field_names = [field["name_ja"] for field in plan["policy_fields"]]
    assert field_names == [
        "あらゆる世代が健やかにくらせるまち",
        "学び育み暮らしを楽しむまち",
        "安全・安心で快適に暮らせるまち",
        "地域の魅力があふれる産業と観光のまち",
        "市民と共に創る自立したまち",
    ]
    assert all(field["measures"] == [] for field in plan["policy_fields"])
    principles = "".join(plan["management_principles"])
    assert "実行計画" in principles
    assert "第9次" in principles
    assert "transition_or_unresolved" in principles


def test_yamaguchi_fiscal_records_hold_verified_values() -> None:
    records = {record["id"]: record for record in _package()["fiscal_records"]}
    budget = records["jp-local-352039-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 94_480_000_000
    assert budget["sources"] == ["yamaguchi-budget-2026"]
    assert "議案第1号" in budget["note"]
    assert "94,480,000千円" in budget["note"]
    assert "『可決』" in budget["note"]
    assert "千円単位" in budget["note"]
    revenue = records["jp-local-352039-fiscal-2024-total-revenue"]
    assert revenue["stage"] == "settlement"
    assert revenue["amount_yen"] == 108_548_127_000
    assert revenue["sources"] == ["yamaguchi-settlement-2024"]
    assert "議案第21号" in revenue["note"]
    assert "108,548,127千円" in revenue["note"]
    assert "2025年10月2日" in revenue["note"]
    expenditure = records["jp-local-352039-fiscal-2024-total-expenditure"]
    assert expenditure["amount_yen"] == 107_248_447_000
    assert expenditure["sources"] == ["yamaguchi-settlement-2024"]
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 1_299_680_000


def test_yamaguchi_fy2024_settlement_values_and_real_balance() -> None:
    records = {record["id"]: record for record in _package()["fiscal_records"]}
    revenue = records["jp-local-352039-fiscal-2024-total-revenue"]
    expenditure = records["jp-local-352039-fiscal-2024-total-expenditure"]
    # Thousand-yen totals printed in the achievement report's
    # settlement summary table.
    assert revenue["amount_yen"] == 108_548_127_000
    assert expenditure["amount_yen"] == 107_248_447_000
    # 形式収支 (revenue minus expenditure) matches the printed balance.
    assert 108_548_127_000 - 107_248_447_000 == 1_299_680_000
    # 実質収支 stays at the report's thousand-yen precision:
    # 1,299,680 - 568,386 = 731,294 thousand yen; no yen figure is
    # synthesized for it.
    assert 1_299_680_000 - 568_386_000 == 731_294_000
    assert "1,299,680千円" in expenditure["note"]
    assert "731,294千円" in expenditure["note"]
    assert "568,386千円" in expenditure["note"]
    assert "千円単位のまま" in expenditure["note"]


def test_yamaguchi_fy2024_settlement_certification_wording() -> None:
    text = CANDIDATE_PATH.read_text(encoding="utf-8")
    assert "議案第21号" in text
    assert "認定" in text
    # Bill 21 was certified at the September 2025 session; the
    # candidate must not carry the opposite outcome.
    assert "不認定" not in text


def test_yamaguchi_fy2026_budget_vote_wording() -> None:
    text = CANDIDATE_PATH.read_text(encoding="utf-8")
    packets = {packet["id"]: packet for packet in _package()["evidence_packets"]}
    claim = packets["evidence-yamaguchi-city-2026-total-expenditure"]["claims"][0]
    # The council vote list's result column records bill 1 simply as
    # "可決"; the candidate keeps that wording and never upgrades it.
    assert "『可決』" in claim["statement"]
    assert "議案第1号" in claim["statement"]
    assert "94,480,000千円" in claim["statement"]
    assert "原案可決" not in text
    assert "修正可決" not in text
    assert "修正議決" not in text


def test_yamaguchi_vote_dates_rest_on_schedule_not_minutes() -> None:
    text = CANDIDATE_PATH.read_text(encoding="utf-8")
    # The budget vote date comes from the session schedule's final
    # plenary day and the certification date from the session's final
    # day; both are recorded with the minutes confirmation left open
    # rather than presented as directly confirmed.
    assert "2026年3月13日" in text
    assert "2025年10月2日" in text
    assert "会期日程表" in text
    assert "本会議録による最終確認は未実施" in text


def test_yamaguchi_evidence_packets_cover_the_three_fiscal_records() -> None:
    packets = {packet["id"]: packet for packet in _package()["evidence_packets"]}
    assert set(packets) == {
        "evidence-yamaguchi-city-2026-total-expenditure",
        "evidence-yamaguchi-city-2024-total-revenue",
        "evidence-yamaguchi-city-2024-total-expenditure",
    }
    for packet in packets.values():
        assert packet["review_status"] == "needs_review"
        assert len(packet["claims"]) == 1
        assert packet["claims"][0]["decision"] == "needs_review"
    budget_claim = packets["evidence-yamaguchi-city-2026-total-expenditure"][
        "claims"
    ][0]
    assert "議案第1号" in budget_claim["statement"]
    assert "94,480,000千円" in budget_claim["statement"]
    revenue_claim = packets["evidence-yamaguchi-city-2024-total-revenue"]["claims"][0]
    assert "議案第21号" in revenue_claim["statement"]
    assert "108,548,127千円" in revenue_claim["statement"]
    expenditure_claim = packets["evidence-yamaguchi-city-2024-total-expenditure"][
        "claims"
    ][0]
    assert "107,248,447千円" in expenditure_claim["statement"]
    assert "731,294千円" in expenditure_claim["statement"]


def test_yamaguchi_progress_review_stays_staging() -> None:
    progress = _package()["progress_review"]
    assert progress["review_status"] == "review_candidate_staging"
    framework = progress["implementation_plan_framework"]
    assert "第9次実行計画" in framework["title"]
    assert "2028年度" in framework["title"]
    assert "まちづくり達成状況報告書" in framework["evaluation_structure"]


def test_yamaguchi_promotion_is_reflected_in_review_queue() -> None:
    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    summary = queue["summary"]
    assert summary["reviewed_complete_count"] == 62
    assert summary["pending_record_review_count"] == 5
    assert summary["next_official_code"] == "422029"
    entry = next(
        item for item in queue["execution_queue"] if item["official_code"] == "352039"
    )
    assert entry["status"] == "reviewed_complete"
    assert (
        entry["completion_path"]
        == "data/catalog/yamaguchi_phase15_completion.json"
    )
