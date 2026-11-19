"""Staging tests for the Akashi Phase 15 review candidate.

The candidate stays prepared and unpublished until a human checks the
cited primary sources.  These tests pin the package state, the source
catalog, the plan framework, and the verified fiscal values so that a
promotion change has to be deliberate.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = ROOT / "data" / "candidates" / "akashi-city" / "review_candidate.json"
INVENTORY_PATH = ROOT / "data" / "indexed" / "akashi-city" / "source_inventory.json"
QUEUE_PATH = ROOT / "data" / "catalog" / "phase15_core_capital_review_queue.json"


def _candidate() -> dict:
    return json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))


def _package() -> dict:
    return _candidate()["candidate_package"]


def test_akashi_candidate_is_prepared_with_delegated_review_approved() -> None:
    candidate = _candidate()
    assert candidate["candidate_id"] == "akashi-phase15-review-candidate"
    assert candidate["official_code"] == "282030"
    assert candidate["name_ja"] == "明石市"
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


def test_akashi_candidate_sources_match_phase14_inventory() -> None:
    package_sources = {
        source["id"]: source for source in _package()["source_catalog"]["sources"]
    }
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    inventory_sources = {source["id"]: source for source in inventory["sources"]}
    assert set(package_sources) == set(inventory_sources)
    for source_id, source in package_sources.items():
        assert source["official_url"] == inventory_sources[source_id]["official_url"]
        assert source["official_url"].startswith("https://www.city.akashi.lg.jp/")
        assert source["verification_status"] == "primary_source_live_verified_2026-11-16"


def test_akashi_plan_review_records_framework_and_transition() -> None:
    records = {record["id"]: record for record in _package()["plan_review"]["records"]}
    assert set(records) == {
        "akashi-current-plan-period",
        "akashi-current-policy-structure",
        "akashi-progress-governance-framework",
        "akashi-plan-transition",
        "akashi-fy2024-settlement-linkage",
    }
    period = records["akashi-current-plan-period"]
    assert period["decision"] == "needs_review"
    assert period["title"].startswith("あかしSDGs推進計画（明石市第6次長期総合計画）の構成")
    assert "2022年度～2030年度" in period["value"]
    assert "後期2026年度～2030年度" in period["value"]
    linkage = records["akashi-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["fiscal_year"] == 2024


def test_akashi_policy_structure_keeps_three_aspects() -> None:
    plan = _package()["policy_structure"]["current_plan"]
    assert plan["title"].startswith("あかしSDGs推進計画（明石市第6次長期総合計画）")
    assert plan["vision"] == (
        "SDGs未来安心都市・明石 ～いつまでも すべての人に やさしいまちを みんなで～"
    )
    assert plan["start_fiscal_year"] == 2022
    assert plan["end_fiscal_year"] == 2030
    assert plan["period_status"] == "verified_fixed_period"
    field_names = [field["name_ja"] for field in plan["policy_fields"]]
    assert field_names == [
        "経済：にぎわいと活力が持続するまち",
        "社会：すべての人が助け合い安心して暮らせるまち",
        "環境：人にも自然にも地球にもやさしいまち",
    ]
    assert all(field["measures"] == [] for field in plan["policy_fields"])
    principles = "".join(plan["management_principles"])
    assert "PDCA" in principles
    assert "not_assessable" not in principles


def test_akashi_fiscal_records_hold_verified_values_and_vote_facts() -> None:
    records = {record["id"]: record for record in _package()["fiscal_records"]}
    budget = records["jp-local-282030-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 151_508_494_000
    assert budget["sources"] == ["akashi-budget-2026"]
    assert "議案第29号" in budget["note"]
    assert "修正議決" in budget["note"]
    assert "千円単位" in budget["note"]
    assert "会議録による最終確認は未実施" in budget["note"]
    revenue = records["jp-local-282030-fiscal-2024-total-revenue"]
    assert revenue["stage"] == "settlement"
    assert revenue["amount_yen"] == 131_291_999_787
    assert revenue["sources"] == ["akashi-settlement-2024"]
    assert "議案第58号" in revenue["note"]
    assert "原案どおり認定" in revenue["note"]
    expenditure = records["jp-local-282030-fiscal-2024-total-expenditure"]
    assert expenditure["amount_yen"] == 130_356_924_686
    assert expenditure["sources"] == ["akashi-settlement-2024"]
    assert "886,767,101円" in expenditure["note"]
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 935_075_101


def test_akashi_fy2024_settlement_certification_is_verified() -> None:
    text = CANDIDATE_PATH.read_text(encoding="utf-8")
    assert "議案第58号" in text
    assert "認定された" in text
    assert "不認定" not in text


def test_akashi_evidence_packets_cover_the_three_fiscal_records() -> None:
    packets = {packet["id"]: packet for packet in _package()["evidence_packets"]}
    assert set(packets) == {
        "evidence-akashi-city-2026-total-expenditure",
        "evidence-akashi-city-2024-total-revenue",
        "evidence-akashi-city-2024-total-expenditure",
    }
    for packet in packets.values():
        assert packet["review_status"] == "needs_review"
        assert len(packet["claims"]) == 1
        assert packet["claims"][0]["decision"] == "needs_review"
    budget_claim = packets["evidence-akashi-city-2026-total-expenditure"]["claims"][0]
    assert "議案第29号" in budget_claim["statement"]
    assert "修正議決" in budget_claim["statement"]
    revenue_claim = packets["evidence-akashi-city-2024-total-revenue"]["claims"][0]
    assert "議案第58号" in revenue_claim["statement"]


def test_akashi_progress_review_stays_staging() -> None:
    progress = _package()["progress_review"]
    assert progress["review_status"] == "review_candidate_staging"
    framework = progress["implementation_plan_framework"]
    assert framework["title"].startswith("あかしSDGs後期戦略計画")
    assert "PDCA" in framework["evaluation_structure"]


def test_akashi_promotion_is_reflected_in_review_queue() -> None:
    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    summary = queue["summary"]
    assert summary["reviewed_complete_count"] == 68
    assert summary["pending_record_review_count"] == 0
    assert summary["next_official_code"] is None
    entry = next(
        item for item in queue["execution_queue"] if item["official_code"] == "282030"
    )
    assert entry["status"] == "reviewed_complete"
    assert entry["completion_path"] == (
        "data/catalog/akashi_phase15_completion.json"
    )
