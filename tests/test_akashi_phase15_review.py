from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/akashi_phase15_completion.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
REVIEWED = ROOT / "data/reviewed/akashi-city"
CANDIDATE = ROOT / "data/candidates/akashi-city/review_candidate.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_akashi_review_package_is_the_forty_fifth_completion():
    completion = load(COMPLETION)
    assert completion == {
        "id": "akashi-phase15-completion",
        "phase": 15,
        "status": "reviewed_complete",
        "official_code": "282030",
        "name_ja": "明石市",
        "completed_at": "2026-11-16",
        "completion_depth": "declared_review_package_v1",
        "review_package": {
            "source_catalog_path": "data/catalog/akashi_phase15_sources.json",
            "plan_review_path": "data/reviewed/akashi-city/plan_review.json",
            "policy_structure_path": (
                "data/catalog/akashi_current_policy_structure.json"
            ),
            "progress_review_path": (
                "data/catalog/akashi_current_progress_review_summary.json"
            ),
            "fiscal_records_path": (
                "data/reviewed/akashi-city/fiscal_records.json"
            ),
            "fiscal_evidence_path": (
                "data/reviewed/akashi-city/evidence_packets.json"
            ),
            "counts": {
                "basic_goals": 3,
                "basic_plan_measures": 0,
                "promoted_implementation_item_actual_records": 0,
                "fiscal_top_line_records": 3,
            },
        },
        "quality_gate": completion["quality_gate"],
        "deferred_depth": completion["deferred_depth"],
        "completion_boundary": completion["completion_boundary"],
    }

    queue = load(QUEUE)
    assert queue["summary"]["reviewed_complete_count"] == 66
    assert queue["summary"]["pending_record_review_count"] == 1
    assert queue["summary"]["next_official_code"] == "472018"
    entry = next(
        row for row in queue["execution_queue"] if row["official_code"] == "282030"
    )
    assert entry["status"] == "reviewed_complete"
    assert entry["completion_path"] == "data/catalog/akashi_phase15_completion.json"


def test_akashi_municipality_and_sources_use_only_official_city_pages():
    municipality = load(REVIEWED / "municipality.json")
    assert municipality["id"] == "jp-local-282030"
    assert municipality["official_code"] == "282030"
    assert municipality["name_ja"] == "明石市"
    assert municipality["prefecture_name_ja"] == "兵庫県"
    assert municipality["municipality_type"] == "core_city"
    assert municipality["official_url"] == "https://www.city.akashi.lg.jp/"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert municipality["data_status"] == "reviewed"
    assert municipality["last_verified_at"] == "2026-11-16"
    assert municipality["sources"] == [
        "akashi-city-home",
        "akashi-budget-2026",
        "akashi-settlement-2024",
    ]

    sources = load(ROOT / "data/catalog/akashi_phase15_sources.json")["sources"]
    assert len(sources) == 4
    for source in sources:
        assert source["official_url"].startswith("https://www.city.akashi.lg.jp/")
        assert "verification_status" not in source


def test_akashi_sources_match_the_reviewed_package():
    catalog = load(ROOT / "data/catalog/akashi_phase15_sources.json")
    assert catalog["id"] == "akashi-phase15-sources"
    assert catalog["name_ja"] == "明石市"
    assert catalog["official_code"] == "282030"
    assert catalog["phase"] == 15
    assert catalog["reviewed_at"] == "2026-11-16"

    by_id = {source["id"]: source for source in catalog["sources"]}
    assert set(by_id) == {
        "akashi-sdgs-plan",
        "akashi-latter-strategy-action",
        "akashi-budget-2026",
        "akashi-settlement-2024",
    }
    assert by_id["akashi-sdgs-plan"]["evidence_role"] == "comprehensive_plan"
    assert by_id["akashi-sdgs-plan"]["format"] == "html"
    assert by_id["akashi-latter-strategy-action"]["evidence_role"] == (
        "implementation_plan_and_progress"
    )
    assert by_id["akashi-budget-2026"]["evidence_role"] == "budget"
    assert by_id["akashi-settlement-2024"]["evidence_role"] == "settlement"


def test_akashi_fiscal_records_match_budget_and_settlement_sources():
    records = load(REVIEWED / "fiscal_records.json")
    assert len(records) == 3
    for record in records:
        assert record["confidence"] == "high"
        assert record["review_status"] == "reviewed"
        assert record["value_status"] == "available"
        assert record["value"] is None

    budget = next(
        record for record in records if record["fiscal_year"] == 2026
    )
    assert budget["id"] == "jp-local-282030-fiscal-2026-total-expenditure"
    assert budget["amount_yen"] == 151_508_494_000
    assert budget["metric"] == "total_expenditure"
    assert budget["metric_label"] == "一般会計当初予算（修正議決）"
    assert budget["stage"] == "initial_budget"
    assert budget["sources"] == ["akashi-budget-2026"]

    text = json.dumps(records, ensure_ascii=False)
    # The FY2026 initial budget was enacted by an amended vote (修正議決),
    # not adopted as proposed: the record must never claim 原案可決.
    assert "修正議決" in text
    assert "原案可決" not in text
    assert "議案第29号" in text
    assert "2026年3月25日" in text
    assert "151,508,494千円" in text

    revenue = next(
        record
        for record in records
        if record["fiscal_year"] == 2024 and record["metric"] == "total_revenue"
    )
    expenditure = next(
        record
        for record in records
        if record["fiscal_year"] == 2024 and record["metric"] == "total_expenditure"
    )
    assert revenue["amount_yen"] == 131_291_999_787
    assert expenditure["amount_yen"] == 130_356_924_686
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 935_075_101
    assert revenue["stage"] == "settlement"
    assert expenditure["stage"] == "settlement"
    assert revenue["sources"] == ["akashi-settlement-2024"]
    assert expenditure["sources"] == ["akashi-settlement-2024"]
    # The FY2024 settlement was certified (認定第1号相当: 議案第58号), not
    # rejected; the real balance is kept at the published yen precision.
    assert "議案第58号" in text
    assert "2025年10月16日" in text
    assert "原案どおり認定" in text
    assert "886,767,101円" in text
    assert "不認定" not in text


def test_akashi_evidence_packets_confirm_fiscal_claims():
    packets = load(REVIEWED / "evidence_packets.json")
    assert len(packets) == 3
    amounts = set()
    for packet in packets:
        assert packet["review_status"] == "reviewed"
        assert packet["subject_type"] == "fiscal_record"
        for claim in packet["claims"]:
            assert claim["decision"] == "accepted"
            amounts.add(packet["subject_id"])
    assert amounts == {
        "jp-local-282030-fiscal-2026-total-expenditure",
        "jp-local-282030-fiscal-2024-total-revenue",
        "jp-local-282030-fiscal-2024-total-expenditure",
    }

    text = json.dumps(packets, ensure_ascii=False)
    assert "修正議決" in text
    assert "原案可決" not in text
    assert "原案どおり認定" in text
    assert "レビュー済みレコード" in text
    assert "人間による確認待ちステージング" not in text


def test_akashi_plan_review_accepts_sdg_plan_and_keeps_linkage_open():
    plan_review = load(REVIEWED / "plan_review.json")
    assert plan_review["id"] == "phase15-akashi-plan-review"
    assert plan_review["review_status"] == "reviewed"
    assert plan_review["reviewed_at"] == "2026-11-16"
    assert plan_review["next_action"]
    assert plan_review["quality_boundary"]

    by_id = {record["id"]: record for record in plan_review["records"]}
    assert by_id["akashi-current-plan-period"]["decision"] == "accepted"
    assert "あかしSDGs推進計画（明石市第6次長期総合計画）" in by_id[
        "akashi-current-plan-period"
    ]["statement"]
    assert "2022" in by_id["akashi-current-plan-period"]["statement"]
    assert "2030" in by_id["akashi-current-plan-period"]["statement"]
    assert by_id["akashi-current-policy-structure"]["decision"] == "accepted"
    assert "経済・社会・環境の三側面" in by_id["akashi-current-policy-structure"][
        "statement"
    ]
    assert by_id["akashi-progress-governance-framework"]["decision"] == "accepted"
    assert "PDCA" in by_id["akashi-progress-governance-framework"]["statement"]
    assert by_id["akashi-plan-transition"]["decision"] == "accepted"
    assert "第5次長期総合計画" in by_id["akashi-plan-transition"]["statement"]
    linkage = by_id["akashi-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["fiscal_year"] == 2024
    assert "前期戦略計画" in linkage["statement"]


def test_akashi_policy_structure_keeps_three_aspects_and_empty_measures():
    structure = load(ROOT / "data/catalog/akashi_current_policy_structure.json")
    assert structure["id"] == "akashi-current-policy-structure"
    assert structure["review_status"] == "reviewed"
    assert structure["source_id"] == "akashi-sdgs-plan"
    assert structure["counts"] == {"basic_goals": 3, "basic_plan_measures": 0}

    plan = structure["current_plan"]
    assert plan["title"] == "あかしSDGs推進計画（明石市第6次長期総合計画）（2022年度～2030年度）"
    assert plan["start_fiscal_year"] == 2022
    assert plan["end_fiscal_year"] == 2030
    assert plan["period_status"] == "verified_fixed_period"
    assert plan["vision"].startswith("SDGs未来安心都市・明石")
    assert [field["name_ja"] for field in plan["policy_fields"]] == [
        "経済：にぎわいと活力が持続するまち",
        "社会：すべての人が助け合い安心して暮らせるまち",
        "環境：人にも自然にも地球にもやさしいまち",
    ]
    assert all(field["measures"] == [] for field in plan["policy_fields"])
    principles = " ".join(plan["management_principles"])
    assert "前期2022年度～2025年度・後期2026年度～2030年度" in principles
    assert "前期戦略計画" in principles


def test_akashi_progress_review_keeps_latter_strategy_framework():
    progress = load(
        ROOT / "data/catalog/akashi_current_progress_review_summary.json"
    )
    assert progress["id"] == "akashi-current-progress-review-summary"
    assert progress["review_status"] == "reviewed_with_explicit_deferred_depth"
    assert progress["reviewed_at"] == "2026-11-16"

    framework = progress["current_implementation_plan"]
    assert framework["title"].startswith("あかしSDGs後期戦略計画")
    assert "後期戦略計画（2026年度～2030年度）" in framework["period"]
    assert framework["current_period_item_actuals"]["status"] == (
        "not_promoted_in_v1"
    )

    assert progress["evaluation_evidence"]["status"] == "not_promoted_in_v1"
    linkage = progress["fiscal_linkage"]
    assert linkage["fiscal_year"] == 2024
    assert linkage["status"] == "not_assessable"
    assert "前期戦略計画" in linkage["boundary"]
    assert "議案第58号・原案どおり認定" in linkage["boundary"]


def test_akashi_finance_sources_are_staged_only():
    finance = load(ROOT / "data/catalog/akashi_city_finance_sources.json")
    assert finance["version"] == "0.1.0"
    assert finance["updated_at"] == "2026-11-16"
    assert finance["scope"] == "phase15-core-capital-review"

    by_id = {record["id"]: record for record in finance["records"]}
    assert set(by_id) == {
        "akashi-city-home",
        "akashi-budget-2026",
        "akashi-settlement-2024",
    }
    for record in finance["records"]:
        assert record["municipality_key"] == "akashi-city"
        assert record["source_kind"] == "document"
        assert record["availability"] == "published"
        assert record["review_status"] == "reviewed"
        assert record["confidence"] == "high"
        assert record["url"].startswith("https://www.city.akashi.lg.jp/")


def test_akashi_completion_marks_every_gate_and_defers_depth():
    completion = load(COMPLETION)
    assert set(completion["quality_gate"].values()) == {True}
    assert len(completion["quality_gate"]) == 13

    deferred = {item["id"]: item for item in completion["deferred_depth"]}
    assert set(deferred) == {
        "current-plan-granular-kpi-and-project-linkage",
        "fiscal-vote-and-certification-verification",
        "plan-transition-version-depth",
        "policy-outcome-causal-and-cross-city-comparability",
    }
    assert all(
        item["status"] == "deferred_not_required_for_v1_completion"
        for item in deferred.values()
    )

    candidate = load(CANDIDATE)
    candidate_deferred = {
        item["id"]: item for item in candidate["deferred_depth"]
    }
    assert set(deferred) == set(candidate_deferred)
    for item_id, item in deferred.items():
        assert item["boundary"] == candidate_deferred[item_id]["boundary"]

    boundary = completion["completion_boundary"]
    assert "修正議決" in boundary
    assert "原案可決" not in boundary
    assert "886,767,101円" in boundary


def test_akashi_review_records_delegation_not_owner_review():
    candidate = load(CANDIDATE)
    assert candidate["package_state"] == "prepared"
    assert candidate["publication"]["eligible"] is False
    assert candidate["human_review"]["status"] == "approved"
    assert candidate["human_review"]["reviewed_at"] == "2026-11-16"
    note = candidate["human_review"]["reviewer_note"]
    # The promotion rests on the owner's explicit 2026-11-15 delegation of
    # the review to Muse; the record must say so and must not present
    # the review as the owner's personal review of the primary sources.
    assert "委任" in note
    assert "レビューはあなたがやってください" in note
    assert "所有者本人が一次資料を直接レビューしたものではない" in note

    serialized = json.dumps(load(COMPLETION), ensure_ascii=False)
    assert "委任" in serialized
    assert "所有者本人が一次資料を直接レビューしたものではない" in serialized
