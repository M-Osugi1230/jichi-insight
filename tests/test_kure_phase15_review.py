from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/kure_phase15_completion.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
REVIEWED = ROOT / "data/reviewed/kure-city"
CANDIDATE = ROOT / "data/candidates/kure-city/review_candidate.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_kure_review_package_is_the_fifty_second_completion():
    completion = load(COMPLETION)
    assert completion == {
        "id": "kure-phase15-completion",
        "phase": 15,
        "status": "reviewed_complete",
        "official_code": "342025",
        "name_ja": "呉市",
        "completed_at": "2026-11-16",
        "completion_depth": "declared_review_package_v1",
        "review_package": {
            "source_catalog_path": "data/catalog/kure_phase15_sources.json",
            "plan_review_path": "data/reviewed/kure-city/plan_review.json",
            "policy_structure_path": (
                "data/catalog/kure_current_policy_structure.json"
            ),
            "progress_review_path": (
                "data/catalog/kure_current_progress_review_summary.json"
            ),
            "fiscal_records_path": "data/reviewed/kure-city/fiscal_records.json",
            "fiscal_evidence_path": (
                "data/reviewed/kure-city/evidence_packets.json"
            ),
            "counts": {
                "basic_goals": 8,
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
    assert queue["summary"]["reviewed_complete_count"] == 54
    assert queue["summary"]["pending_record_review_count"] == 13
    assert queue["summary"]["next_official_code"] == "352039"
    entry = next(
        row for row in queue["execution_queue"] if row["official_code"] == "342025"
    )
    assert entry["status"] == "reviewed_complete"
    assert entry["completion_path"] == "data/catalog/kure_phase15_completion.json"


def test_kure_municipality_and_sources_use_only_official_city_pages():
    municipality = load(REVIEWED / "municipality.json")
    assert municipality["id"] == "jp-local-342025"
    assert municipality["official_code"] == "342025"
    assert municipality["name_ja"] == "呉市"
    assert municipality["prefecture_name_ja"] == "広島県"
    assert municipality["municipality_type"] == "core_city"
    assert municipality["official_url"] == "https://www.city.kure.lg.jp/"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert municipality["data_status"] == "reviewed"
    assert municipality["last_verified_at"] == "2026-11-16"
    assert municipality["sources"] == [
        "kure-city-home",
        "kure-budget-2026",
        "kure-settlement-2024",
    ]

    sources = load(ROOT / "data/catalog/kure_phase15_sources.json")["sources"]
    assert len(sources) == 4
    for source in sources:
        assert source["official_url"].startswith("https://www.city.kure.lg.jp/")
        assert "verification_status" not in source


def test_kure_sources_match_the_reviewed_package():
    catalog = load(ROOT / "data/catalog/kure_phase15_sources.json")
    assert catalog["id"] == "kure-phase15-sources"
    assert catalog["name_ja"] == "呉市"
    assert catalog["official_code"] == "342025"
    assert catalog["phase"] == 15
    assert catalog["reviewed_at"] == "2026-11-16"

    by_id = {source["id"]: source for source in catalog["sources"]}
    assert set(by_id) == {
        "kure-fifth-latter-plan",
        "kure-kpi-progress-2026",
        "kure-budget-2026",
        "kure-settlement-2024",
    }
    assert by_id["kure-fifth-latter-plan"]["evidence_role"] == "comprehensive_plan"
    assert by_id["kure-fifth-latter-plan"]["format"] == "html"
    assert by_id["kure-kpi-progress-2026"]["evidence_role"] == "annual_progress"
    assert by_id["kure-budget-2026"]["evidence_role"] == "budget"
    assert by_id["kure-settlement-2024"]["evidence_role"] == "settlement"


def test_kure_fiscal_records_match_budget_and_settlement_sources():
    records = load(REVIEWED / "fiscal_records.json")
    assert len(records) == 3
    for record in records:
        assert record["confidence"] == "high"
        assert record["review_status"] == "reviewed"
        assert record["value_status"] == "available"
        assert record["value"] is None

    budget = next(record for record in records if record["fiscal_year"] == 2026)
    assert budget["id"] == "jp-local-342025-fiscal-2026-total-expenditure"
    assert budget["amount_yen"] == 115_430_000_000
    assert budget["metric"] == "total_expenditure"
    assert budget["metric_label"] == "一般会計当初予算総額"
    assert budget["stage"] == "initial_budget"
    assert budget["sources"] == ["kure-budget-2026"]

    text = json.dumps(records, ensure_ascii=False)
    # Bill 議第1号 was recorded simply as "可決" in the council's own
    # wording; the wording is never upgraded, and the amount stays at
    # the published thousand-yen precision. The vote date was
    # identified from the result page's publication date and still
    # awaits final confirmation against the plenary minutes.
    assert "議第1号" in text
    assert "『可決』" in text
    assert "2026年3月24日" in text
    assert "115,430,000千円" in text
    assert "原案可決" not in text
    assert "修正可決" not in text
    assert "修正議決" not in text

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
    assert revenue["amount_yen"] == 115_037_162_518
    assert expenditure["amount_yen"] == 110_880_880_516
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 4_156_282_002
    assert revenue["stage"] == "settlement"
    assert expenditure["stage"] == "settlement"
    assert revenue["sources"] == ["kure-settlement-2024"]
    assert expenditure["sources"] == ["kure-settlement-2024"]
    # The FY2024 settlement was certified (bill 議第99号), not
    # rejected; the real balance stays at the balance statement's
    # thousand-yen precision.
    assert "議第99号" in text
    assert "2025年9月24日" in text
    assert "2,901,588千円" in text
    assert "本会議録による最終確認は未実施" in text
    assert "不認定" not in text


def test_kure_evidence_packets_confirm_fiscal_claims():
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
        "jp-local-342025-fiscal-2026-total-expenditure",
        "jp-local-342025-fiscal-2024-total-revenue",
        "jp-local-342025-fiscal-2024-total-expenditure",
    }

    text = json.dumps(packets, ensure_ascii=False)
    assert "議第1号" in text
    assert "議第99号" in text
    assert "レビュー済みレコード" in text
    assert "人間による確認待ちステージング" not in text
    assert "原案可決" not in text
    assert "不認定" not in text


def test_kure_plan_review_accepts_fifth_plan_and_keeps_linkage_open():
    plan_review = load(REVIEWED / "plan_review.json")
    assert plan_review["id"] == "phase15-kure-plan-review"
    assert plan_review["review_status"] == "reviewed"
    assert plan_review["reviewed_at"] == "2026-11-16"
    assert plan_review["next_action"]
    assert plan_review["quality_boundary"]

    by_id = {record["id"]: record for record in plan_review["records"]}
    assert by_id["kure-current-plan-period"]["decision"] == "accepted"
    assert "第5次呉市長期総合計画" in by_id["kure-current-plan-period"][
        "statement"
    ]
    assert "2030年度" in by_id["kure-current-plan-period"]["statement"]
    assert by_id["kure-current-policy-structure"]["decision"] == "accepted"
    assert "8つの政策分野" in by_id["kure-current-policy-structure"]["statement"]
    assert by_id["kure-progress-governance-framework"]["decision"] == "accepted"
    assert "構成事業集" in by_id["kure-progress-governance-framework"][
        "statement"
    ]
    assert by_id["kure-plan-transition"]["decision"] == "accepted"
    assert "後期" in by_id["kure-plan-transition"]["statement"]
    linkage = by_id["kure-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["fiscal_year"] == 2024
    assert "版が異なる" in linkage["statement"]


def test_kure_policy_structure_keeps_eight_fields_and_empty_measures():
    structure = load(ROOT / "data/catalog/kure_current_policy_structure.json")
    assert structure["id"] == "kure-current-policy-structure"
    assert structure["review_status"] == "reviewed"
    assert structure["source_id"] == "kure-fifth-latter-plan"
    assert structure["counts"] == {"basic_goals": 8, "basic_plan_measures": 0}

    plan = structure["current_plan"]
    assert plan["title"] == (
        "第5次呉市長期総合計画（基本構想2021年度～2030年度"
        "・後期基本計画2026年度～2030年度）"
    )
    assert plan["start_fiscal_year"] == 2021
    assert plan["end_fiscal_year"] == 2030
    assert plan["period_status"] == "verified_fixed_period"
    assert plan["vision"] == (
        "誰もが住み続けたい，行ってみたい，人を惹きつけるまち「くれ」"
        "〜イキイキと働き，豊かに安心して暮らし，ワクワク生きる〜"
    )
    assert len(plan["policy_fields"]) == 8
    assert plan["policy_fields"][0]["name_ja"] == "子育て・教育"
    assert plan["policy_fields"][-1]["name_ja"] == "行政経営"
    assert all(field["measures"] == [] for field in plan["policy_fields"])
    principles = " ".join(plan["management_principles"])
    assert "構成事業集" in principles
    assert "重要業績評価指標" in principles
    assert "verified_fixed_period" in principles


def test_kure_progress_review_keeps_project_collection_framework():
    progress = load(
        ROOT / "data/catalog/kure_current_progress_review_summary.json"
    )
    assert progress["id"] == "kure-current-progress-review-summary"
    assert progress["review_status"] == "reviewed_with_explicit_deferred_depth"
    assert progress["reviewed_at"] == "2026-11-16"

    framework = progress["current_implementation_plan"]
    assert "構成事業集" in framework["title"]
    assert "後期基本計画期間（2026年度～2030年度）" in framework["period"]
    assert "重要業績評価指標" in framework["rolling_structure"]
    assert framework["current_period_item_actuals"]["status"] == (
        "not_promoted_in_v1"
    )

    assert progress["evaluation_evidence"]["status"] == "not_promoted_in_v1"
    linkage = progress["fiscal_linkage"]
    assert linkage["fiscal_year"] == 2024
    assert linkage["status"] == "not_assessable"
    assert "版が異なる" in linkage["boundary"]
    assert "議第99号・2025年9月24日認定" in linkage["boundary"]


def test_kure_finance_sources_are_reviewed():
    finance = load(ROOT / "data/catalog/kure_city_finance_sources.json")
    assert finance["version"] == "0.1.0"
    assert finance["updated_at"] == "2026-11-16"
    assert finance["scope"] == "phase15-core-capital-review"

    by_id = {record["id"]: record for record in finance["records"]}
    assert set(by_id) == {
        "kure-city-home",
        "kure-budget-2026",
        "kure-settlement-2024",
    }
    for record in finance["records"]:
        assert record["municipality_key"] == "kure-city"
        assert record["source_kind"] == "document"
        assert record["availability"] == "published"
        assert record["review_status"] == "reviewed"
        assert record["confidence"] == "high"
        assert record["url"].startswith("https://www.city.kure.lg.jp/")


def test_kure_completion_marks_every_gate_and_defers_depth():
    completion = load(COMPLETION)
    assert set(completion["quality_gate"].values()) == {True}
    assert len(completion["quality_gate"]) == 13

    deferred = {item["id"]: item for item in completion["deferred_depth"]}
    assert set(deferred) == {
        "current-plan-granular-kpi-and-project-linkage",
        "fiscal-detail-reconciliation",
        "plan-transition-version-depth",
        "policy-outcome-causal-and-cross-city-comparability",
    }
    assert all(
        item["status"] == "deferred_not_required_for_v1_completion"
        for item in deferred.values()
    )

    candidate = load(CANDIDATE)
    candidate_deferred = {item["id"]: item for item in candidate["deferred_depth"]}
    assert set(deferred) == set(candidate_deferred)
    for item_id, item in deferred.items():
        assert item["boundary"] == candidate_deferred[item_id]["boundary"]

    boundary = completion["completion_boundary"]
    assert "議第99号" in boundary
    assert "2,901,588千円" in boundary
    assert "verified_fixed_period" in boundary
    assert "原案可決" not in boundary
    assert "不認定" not in boundary


def test_kure_review_records_delegation_not_owner_review():
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
    assert "議第1号" in note
    assert "議第99号" in note

    serialized = json.dumps(load(COMPLETION), ensure_ascii=False)
    assert "委任" in serialized
    assert "所有者本人が一次資料を直接レビューしたものではない" in serialized
    assert "原案可決" not in serialized
    assert "不認定" not in serialized
