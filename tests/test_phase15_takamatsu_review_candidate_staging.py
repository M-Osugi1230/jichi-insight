"""Staging tests for the Takamatsu Phase 15 review candidate.

The candidate stays prepared and unpublished until a human checks the
cited primary sources.  These tests pin the package state, the source
catalog, the plan framework, and the verified fiscal values so that a
promotion change has to be deliberate.  The FY2026 initial budget
(bill 2) carries the result wording printed in the council's official
results list (可決); its vote date, 2026-03-23, was identified from
the plenary minutes agenda, while the plenary declaration wording
itself was not directly confirmed by text retrieval and stays an open
question.  The FY2024 settlement certification bill (認定第1号) was
recorded as continued review at the September 2025 session; a
supplementary live-browser investigation then confirmed from the
council's official December 2025 session page, its results list, and
the plenary minutes that the bill was certified on 2025-12-05, so the
candidate records that certification while never recording a
non-certification.  The FY2024
settlement totals stay at the thousand-yen precision printed in the
city's official settlement summary; no yen figure is synthesized, and
ordinary-account aggregate figures are not used as general-account
values.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = (
    ROOT / "data" / "candidates" / "takamatsu-city" / "review_candidate.json"
)
INVENTORY_PATH = (
    ROOT / "data" / "indexed" / "takamatsu-city" / "source_inventory.json"
)
QUEUE_PATH = ROOT / "data" / "catalog" / "phase15_core_capital_review_queue.json"


def _candidate() -> dict:
    return json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))


def _package() -> dict:
    return _candidate()["candidate_package"]


def test_takamatsu_candidate_is_prepared_with_delegated_review_approved() -> None:
    candidate = _candidate()
    assert candidate["candidate_id"] == "takamatsu-phase15-review-candidate"
    assert candidate["official_code"] == "372013"
    assert candidate["name_ja"] == "高松市"
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


def test_takamatsu_candidate_sources_match_phase14_inventory() -> None:
    package_sources = {
        source["id"]: source for source in _package()["source_catalog"]["sources"]
    }
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    inventory_sources = {source["id"]: source for source in inventory["sources"]}
    assert set(package_sources) == set(inventory_sources)
    assert set(package_sources) == {
        "takamatsu-seventh-plan",
        "takamatsu-machizukuri-plans",
        "takamatsu-budget-2026",
        "takamatsu-settlement-2024",
    }
    for source_id, source in package_sources.items():
        assert source["official_url"] == inventory_sources[source_id]["official_url"]
        assert source["official_url"].startswith(
            "https://www.city.takamatsu.kagawa.jp/"
        )
        assert (
            source["verification_status"]
            == "primary_source_live_verified_2026-11-17"
        )


def test_takamatsu_plan_review_records_framework_and_transition() -> None:
    records = {record["id"]: record for record in _package()["plan_review"]["records"]}
    assert set(records) == {
        "takamatsu-current-plan-period",
        "takamatsu-current-policy-structure",
        "takamatsu-progress-governance-framework",
        "takamatsu-plan-transition",
        "takamatsu-fy2024-settlement-linkage",
    }
    period = records["takamatsu-current-plan-period"]
    assert period["decision"] == "needs_review"
    assert period["title"].startswith("第7次高松市総合計画の構成")
    assert "第1期2024年度～2026年度" in period["value"]
    assert "第2期2026年度～2028年度" in period["value"]
    assert "FY2026に第1期と第2期の期間が重なる" in period["value"]
    transition = records["takamatsu-plan-transition"]
    assert "第6次高松市総合計画" in transition["statement"]
    assert "第7次高松市総合計画" in transition["statement"]
    assert "2016年度～2023年度" in transition["statement"]
    linkage = records["takamatsu-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["fiscal_year"] == 2024


def test_takamatsu_policy_structure_keeps_six_goals() -> None:
    plan = _package()["policy_structure"]["current_plan"]
    assert plan["title"].startswith("第7次高松市総合計画")
    assert plan["vision"] == "人がつどい 未来に躍動する 世界都市・高松"
    assert plan["start_fiscal_year"] == 2024
    assert plan["end_fiscal_year"] == 2031
    assert plan["period_status"] == "verified_fixed_period"
    field_names = [field["name_ja"] for field in plan["policy_fields"]]
    assert field_names == [
        "誰もが自分らしく健やかに暮らせるまち",
        "人を育み、多様な生き方が尊重されるまち",
        "魅力ある資源をいかし、都市の活力を創造するまち",
        "安全・安心に暮らせるまち",
        "都市機能と自然が調和し、快適さと利便性を兼ね備えたまち",
        "さまざまな主体がつながり、ともに力を発揮できるまち",
    ]
    assert all(field["measures"] == [] for field in plan["policy_fields"])
    principles = "".join(plan["management_principles"])
    assert "高松まちづくりプラン" in principles
    assert "政策17・施策43" in principles
    assert "第2期で第1期を上書きしない" in principles
    assert "verified_fixed_period" in principles


def test_takamatsu_fiscal_records_hold_verified_values() -> None:
    records = {record["id"]: record for record in _package()["fiscal_records"]}
    budget = records["jp-local-372013-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 192_800_000_000
    assert budget["sources"] == ["takamatsu-budget-2026"]
    assert "議案第2号" in budget["note"]
    assert "192,800,000千円" in budget["note"]
    assert "「可決」" in budget["note"]
    assert "2026年3月23日" in budget["note"]
    assert "千円単位" in budget["note"]
    revenue = records["jp-local-372013-fiscal-2024-total-revenue"]
    assert revenue["stage"] == "settlement"
    assert revenue["amount_yen"] == 183_171_243_000
    assert revenue["sources"] == ["takamatsu-settlement-2024"]
    assert "認定第1号" in revenue["note"]
    assert "183,171,243千円" in revenue["note"]
    assert "継続審査" in revenue["note"]
    assert "2025年12月5日" in revenue["note"]
    assert "認定された" in revenue["note"]
    expenditure = records["jp-local-372013-fiscal-2024-total-expenditure"]
    assert expenditure["amount_yen"] == 177_907_841_000
    assert expenditure["sources"] == ["takamatsu-settlement-2024"]
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 5_263_402_000


def test_takamatsu_fy2024_settlement_values_and_real_balance() -> None:
    records = {record["id"]: record for record in _package()["fiscal_records"]}
    revenue = records["jp-local-372013-fiscal-2024-total-revenue"]
    expenditure = records["jp-local-372013-fiscal-2024-total-expenditure"]
    # Thousand-yen totals printed in the official settlement summary
    # of the FY2024 accounts.
    assert revenue["amount_yen"] == 183_171_243_000
    assert expenditure["amount_yen"] == 177_907_841_000
    # 差引残額 (formal balance) matches the printed balance.
    assert 183_171_243_000 - 177_907_841_000 == 5_263_402_000
    # 実質収支 stays at the summary's thousand-yen precision:
    # 5,263,402 - 1,191,705 = 4,071,697 thousand yen; no yen figure is
    # synthesized for it.
    assert 5_263_402_000 - 1_191_705_000 == 4_071_697_000
    assert "5,263,402千円" in expenditure["note"]
    assert "4,071,697千円" in expenditure["note"]
    assert "1,191,705千円" in expenditure["note"]
    assert "千円単位のまま" in expenditure["note"]


def test_takamatsu_fy2024_settlement_certification_confirmed() -> None:
    text = CANDIDATE_PATH.read_text(encoding="utf-8")
    assert "認定第1号" in text
    assert "継続審査" in text
    assert "2025年12月5日" in text
    assert "認定された" in text
    # The certification was confirmed by a supplementary live-browser
    # investigation of the council's official December 2025 session
    # materials; the candidate must record that basis and must never
    # record a non-certification outcome.
    assert "実ブラウザによる補完調査" in text
    assert "不認定" not in text
    # The formerly open question about the final outcome is resolved.
    assert "認定第1号の継続審査後の最終的な議決結果" not in text
    assert "認定の成否を記録しない" not in text


def test_takamatsu_fy2026_budget_vote_wording() -> None:
    text = CANDIDATE_PATH.read_text(encoding="utf-8")
    packets = {packet["id"]: packet for packet in _package()["evidence_packets"]}
    claim = packets["evidence-takamatsu-city-2026-total-expenditure"]["claims"][0]
    # The council's official results list prints the outcome as 可決;
    # the candidate keeps that wording verbatim and never upgrades it
    # to an as-proposed or amended adoption.
    assert "「可決」" in claim["statement"]
    assert "議案第2号" in claim["statement"]
    assert "192,800,000千円" in claim["statement"]
    assert "2026年3月23日" in claim["statement"]
    assert "原案可決" not in text
    assert "修正可決" not in text
    assert "修正議決" not in text


def test_takamatsu_budget_vote_date_basis_and_caveat() -> None:
    text = CANDIDATE_PATH.read_text(encoding="utf-8")
    # The vote date was identified from the plenary minutes agenda
    # (議事日程第8号), not read from a declaration in the minutes, so
    # the minutes-confirmation caveat must stay in the candidate.
    assert "2026年3月23日" in text
    assert "議事日程" in text
    assert "会議録による最終確認は未実施" in text


def test_takamatsu_evidence_packets_cover_the_three_fiscal_records() -> None:
    packets = {packet["id"]: packet for packet in _package()["evidence_packets"]}
    assert set(packets) == {
        "evidence-takamatsu-city-2026-total-expenditure",
        "evidence-takamatsu-city-2024-total-revenue",
        "evidence-takamatsu-city-2024-total-expenditure",
    }
    for packet in packets.values():
        assert packet["review_status"] == "needs_review"
        assert len(packet["claims"]) == 1
        assert packet["claims"][0]["decision"] == "needs_review"
    budget_claim = packets["evidence-takamatsu-city-2026-total-expenditure"][
        "claims"
    ][0]
    assert "議案第2号" in budget_claim["statement"]
    assert "192,800,000千円" in budget_claim["statement"]
    revenue_claim = packets["evidence-takamatsu-city-2024-total-revenue"]["claims"][0]
    assert "認定第1号" in revenue_claim["statement"]
    assert "183,171,243千円" in revenue_claim["statement"]
    assert "継続審査" in revenue_claim["statement"]
    assert "2025年12月5日" in revenue_claim["statement"]
    assert "認定された" in revenue_claim["statement"]
    revenue_packet = packets["evidence-takamatsu-city-2024-total-revenue"]
    assert revenue_packet["open_questions"] == [
        "確定した決算書および監査委員の令和6年度決算審査意見書の値との突合。"
    ]
    expenditure_claim = packets["evidence-takamatsu-city-2024-total-expenditure"][
        "claims"
    ][0]
    assert "177,907,841千円" in expenditure_claim["statement"]
    assert "4,071,697千円" in expenditure_claim["statement"]


def test_takamatsu_progress_review_stays_staging() -> None:
    progress = _package()["progress_review"]
    assert progress["review_status"] == "review_candidate_staging"
    framework = progress["implementation_plan_framework"]
    assert "高松まちづくりプラン" in framework["title"]
    assert "第2期2026年度～2028年度" in framework["title"]
    assert "総合計画推進会議" in framework["evaluation_structure"]


def test_takamatsu_promotion_is_reflected_in_review_queue() -> None:
    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    summary = queue["summary"]
    assert summary["reviewed_complete_count"] == 57
    assert summary["pending_record_review_count"] == 10
    assert summary["next_official_code"] == "382019"
    entry = next(
        item for item in queue["execution_queue"] if item["official_code"] == "372013"
    )
    assert entry["status"] == "reviewed_complete"
    assert (
        entry["completion_path"]
        == "data/catalog/takamatsu_phase15_completion.json"
    )
