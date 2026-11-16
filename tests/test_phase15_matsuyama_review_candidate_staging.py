"""Staging tests for the Matsuyama Phase 15 review candidate.

The candidate stays prepared and unpublished until a human checks the
cited primary sources.  These tests pin the package state, the source
catalog, the plan framework, and the verified fiscal values so that a
promotion change has to be deliberate.  The FY2026 initial budget
(Bill No. 9) was adopted as proposed (原案可決) on 2026-03-19, read
directly from the council's official per-member vote table for the
March 2026 session.  The FY2024 settlement certification bill
（認定第1号） was placed under continued review at the September 2025
session and then certified at the December 2025 session, with the vote
dated 2025-11-28 in the council's official vote table (replaced
version); the city council newsletter corroborates the certification.
The FY2024 settlement totals stay at the thousand-yen precision
printed in the audit commissioners' opinion and the city's fiscal
circumstances publication; no yen figure is synthesized, and
ordinary-account aggregate figures are not used as general-account
values.  The FY2024 settlement belongs to the previous (6th) plan
period, so its linkage to the 7th plan is not_assessable.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = (
    ROOT / "data" / "candidates" / "matsuyama-city" / "review_candidate.json"
)
INVENTORY_PATH = (
    ROOT / "data" / "indexed" / "matsuyama-city" / "source_inventory.json"
)
QUEUE_PATH = ROOT / "data" / "catalog" / "phase15_core_capital_review_queue.json"


def _candidate() -> dict:
    return json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))


def _package() -> dict:
    return _candidate()["candidate_package"]


def test_matsuyama_candidate_is_prepared_with_delegated_review_approved() -> None:
    candidate = _candidate()
    assert candidate["candidate_id"] == "matsuyama-phase15-review-candidate"
    assert candidate["official_code"] == "382019"
    assert candidate["name_ja"] == "松山市"
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


def test_matsuyama_candidate_sources_match_phase14_inventory() -> None:
    package_sources = {
        source["id"]: source for source in _package()["source_catalog"]["sources"]
    }
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    inventory_sources = {source["id"]: source for source in inventory["sources"]}
    assert set(package_sources) == set(inventory_sources)
    assert set(package_sources) == {
        "matsuyama-seventh-plan",
        "matsuyama-citizen-survey",
        "matsuyama-budget-2026",
        "matsuyama-settlement-audit-2024",
    }
    for source_id, source in package_sources.items():
        assert source["official_url"] == inventory_sources[source_id]["official_url"]
        assert source["official_url"].startswith(
            "https://www.city.matsuyama.ehime.jp/"
        )
        assert (
            source["verification_status"]
            == "primary_source_live_verified_2026-11-17"
        )


def test_matsuyama_plan_review_records_framework_and_transition() -> None:
    records = {record["id"]: record for record in _package()["plan_review"]["records"]}
    assert set(records) == {
        "matsuyama-current-plan-period",
        "matsuyama-current-policy-structure",
        "matsuyama-progress-governance-framework",
        "matsuyama-plan-transition",
        "matsuyama-fy2024-settlement-linkage",
    }
    period = records["matsuyama-current-plan-period"]
    assert period["decision"] == "needs_review"
    assert period["title"].startswith("第7次松山市総合計画の構成")
    assert "前期2025年度～2029年度" in period["value"]
    assert "後期2030年度～2034年度" in period["value"]
    assert "第6次松山市総合計画" in period["value"]
    transition = records["matsuyama-plan-transition"]
    assert "第6次松山市総合計画" in transition["statement"]
    assert "第7次松山市総合計画" in transition["statement"]
    assert "令和6年度末まで" in transition["statement"]
    linkage = records["matsuyama-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["fiscal_year"] == 2024


def test_matsuyama_policy_structure_keeps_eleven_fields() -> None:
    plan = _package()["policy_structure"]["current_plan"]
    assert plan["title"].startswith("第7次松山市総合計画")
    assert plan["vision"] == "人、まち、仕事がつながる SETOUCHIの交流拠点まつやま"
    assert plan["start_fiscal_year"] == 2025
    assert plan["end_fiscal_year"] == 2034
    assert plan["period_status"] == "verified_fixed_period"
    field_names = [field["name_ja"] for field in plan["policy_fields"]]
    assert field_names == [
        "こどもを輝く未来へつなぐ",
        "人と人の支えあいをつなぐ",
        "健康をつなぐ",
        "自分らしさと誇りをつなぐ",
        "ワクワクを全国・世界へつなぐ",
        "人と仕事と暮らしをつなぐ",
        "まちとまちをつなぐ",
        "にぎわいと住みやすいまちをつなぐ",
        "豊かな自然と暮らしをつなぐ",
        "安全と安心をつなぐ",
        "つなぐを支える",
    ]
    assert all(field["measures"] == [] for field in plan["policy_fields"])
    principles = "".join(plan["management_principles"])
    assert "11の政策分野" in principles
    assert "32施策" in principles
    assert "current actualとして流用しない" in principles
    assert "verified_fixed_period" in principles


def test_matsuyama_fiscal_records_hold_verified_values() -> None:
    records = {record["id"]: record for record in _package()["fiscal_records"]}
    budget = records["jp-local-382019-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 235_160_000_000
    assert budget["sources"] == ["matsuyama-budget-2026"]
    assert "議案第9号" in budget["note"]
    assert "235,160,000千円" in budget["note"]
    assert "原案可決" in budget["note"]
    assert "2026年3月19日" in budget["note"]
    assert "千円単位" in budget["note"]
    revenue = records["jp-local-382019-fiscal-2024-total-revenue"]
    assert revenue["stage"] == "settlement"
    assert revenue["amount_yen"] == 232_638_142_000
    assert revenue["sources"] == ["matsuyama-settlement-audit-2024"]
    assert "認定第1号" in revenue["note"]
    assert "232,638,142千円" in revenue["note"]
    assert "継続審査" in revenue["note"]
    expenditure = records["jp-local-382019-fiscal-2024-total-expenditure"]
    assert expenditure["amount_yen"] == 228_347_195_000
    assert expenditure["sources"] == ["matsuyama-settlement-audit-2024"]
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 4_290_947_000


def test_matsuyama_fy2024_settlement_values_and_real_balance() -> None:
    records = {record["id"]: record for record in _package()["fiscal_records"]}
    revenue = records["jp-local-382019-fiscal-2024-total-revenue"]
    expenditure = records["jp-local-382019-fiscal-2024-total-expenditure"]
    # Thousand-yen totals printed in the audit opinion (Book 1) and
    # the city's FY2024 fiscal circumstances publication.
    assert revenue["amount_yen"] == 232_638_142_000
    assert expenditure["amount_yen"] == 228_347_195_000
    # 形式収支 (formal balance) matches the printed balance.
    assert 232_638_142_000 - 228_347_195_000 == 4_290_947_000
    # 実質収支 stays at the printed thousand-yen precision:
    # 4,290,947 - 1,687,093 = 2,603,854 thousand yen; no yen figure
    # is synthesized for it.
    assert 4_290_947_000 - 1_687_093_000 == 2_603_854_000
    assert "4,290,947千円" in expenditure["note"]
    assert "2,603,854千円" in expenditure["note"]
    assert "1,687,093千円" in expenditure["note"]
    assert "千円単位のまま" in expenditure["note"]


def test_matsuyama_fy2024_settlement_certification_is_confirmed() -> None:
    text = CANDIDATE_PATH.read_text(encoding="utf-8")
    assert "認定第1号" in text
    assert "継続審査" in text
    assert "2025年11月28日" in text
    assert "認定された" in text
    # The certification was confirmed from the council's official
    # vote tables; the candidate must not record a non-certification
    # or an amended adoption anywhere.
    assert "不認定" not in text
    assert "修正可決" not in text
    assert "修正議決" not in text


def test_matsuyama_fy2026_budget_vote_wording() -> None:
    text = CANDIDATE_PATH.read_text(encoding="utf-8")
    packets = {packet["id"]: packet for packet in _package()["evidence_packets"]}
    claim = packets["evidence-matsuyama-city-2026-total-expenditure"]["claims"][0]
    # The council's official vote table records Bill No. 9 as adopted
    # as proposed (原案可決) on 2026-03-19; the candidate keeps that
    # wording verbatim.
    assert "原案可決" in claim["statement"]
    assert "議案第9号" in claim["statement"]
    assert "235,160,000千円" in claim["statement"]
    assert "2026年3月19日" in claim["statement"]
    assert "修正可決" not in text
    assert "修正議決" not in text


def test_matsuyama_ordinary_account_aggregates_are_not_used() -> None:
    text = CANDIDATE_PATH.read_text(encoding="utf-8")
    # Ehime Prefecture's ordinary-account (普通会計) settlement
    # aggregates for Matsuyama differ from the general-account
    # totals and must not appear as general-account values.
    assert "233,179,187" not in text
    assert "228,583,457" not in text
    assert "普通会計ベースの集計値は一般会計とは集計範囲が異なるため使用していない" in text


def test_matsuyama_evidence_packets_cover_the_three_fiscal_records() -> None:
    packets = {packet["id"]: packet for packet in _package()["evidence_packets"]}
    assert set(packets) == {
        "evidence-matsuyama-city-2026-total-expenditure",
        "evidence-matsuyama-city-2024-total-revenue",
        "evidence-matsuyama-city-2024-total-expenditure",
    }
    for packet in packets.values():
        assert packet["review_status"] == "needs_review"
        assert len(packet["claims"]) == 1
        assert packet["claims"][0]["decision"] == "needs_review"
    budget_claim = packets["evidence-matsuyama-city-2026-total-expenditure"][
        "claims"
    ][0]
    assert "議案第9号" in budget_claim["statement"]
    assert "235,160,000千円" in budget_claim["statement"]
    revenue_claim = packets["evidence-matsuyama-city-2024-total-revenue"]["claims"][0]
    assert "認定第1号" in revenue_claim["statement"]
    assert "232,638,142千円" in revenue_claim["statement"]
    assert "継続審査" in revenue_claim["statement"]
    expenditure_claim = packets["evidence-matsuyama-city-2024-total-expenditure"][
        "claims"
    ][0]
    assert "228,347,195千円" in expenditure_claim["statement"]
    assert "2,603,854千円" in expenditure_claim["statement"]


def test_matsuyama_progress_review_stays_staging() -> None:
    progress = _package()["progress_review"]
    assert progress["review_status"] == "review_candidate_staging"
    framework = progress["implementation_plan_framework"]
    assert "実施計画" in framework["title"]
    assert "市民意識調査" in framework["evaluation_structure"]


def test_matsuyama_promotion_is_reflected_in_review_queue() -> None:
    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    summary = queue["summary"]
    assert summary["reviewed_complete_count"] == 66
    assert summary["pending_record_review_count"] == 1
    assert summary["next_official_code"] == "472018"
    entry = next(
        item for item in queue["execution_queue"] if item["official_code"] == "382019"
    )
    assert entry["status"] == "reviewed_complete"
    assert (
        entry["completion_path"]
        == "data/catalog/matsuyama_phase15_completion.json"
    )
