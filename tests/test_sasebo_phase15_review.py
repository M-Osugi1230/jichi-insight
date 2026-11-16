from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/sasebo_phase15_completion.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
REVIEWED = ROOT / "data/reviewed/sasebo-city"
CANDIDATE = ROOT / "data/candidates/sasebo-city/review_candidate.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sasebo_review_package_is_the_sixty_third_completion():
    completion = load(COMPLETION)
    assert completion == {
        "id": "sasebo-phase15-completion",
        "phase": 15,
        "status": "reviewed_complete",
        "official_code": "422029",
        "name_ja": "佐世保市",
        "completed_at": "2026-11-17",
        "completion_depth": "declared_review_package_v1",
        "review_package": {
            "source_catalog_path": "data/catalog/sasebo_phase15_sources.json",
            "plan_review_path": "data/reviewed/sasebo-city/plan_review.json",
            "policy_structure_path": (
                "data/catalog/sasebo_current_policy_structure.json"
            ),
            "progress_review_path": (
                "data/catalog/sasebo_current_progress_review_summary.json"
            ),
            "fiscal_records_path": (
                "data/reviewed/sasebo-city/fiscal_records.json"
            ),
            "fiscal_evidence_path": (
                "data/reviewed/sasebo-city/evidence_packets.json"
            ),
            "counts": {
                "basic_goals": 4,
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
        row for row in queue["execution_queue"] if row["official_code"] == "422029"
    )
    assert entry["status"] == "reviewed_complete"
    assert entry["completion_path"] == "data/catalog/sasebo_phase15_completion.json"


def test_sasebo_municipality_and_sources_use_only_official_city_pages():
    municipality = load(REVIEWED / "municipality.json")
    assert municipality["id"] == "jp-local-422029"
    assert municipality["official_code"] == "422029"
    assert municipality["name_ja"] == "佐世保市"
    assert municipality["prefecture_name_ja"] == "長崎県"
    assert municipality["municipality_type"] == "core_city"
    assert municipality["official_url"] == "https://www.city.sasebo.lg.jp/"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert municipality["data_status"] == "reviewed"
    assert municipality["last_verified_at"] == "2026-11-17"
    assert municipality["sources"] == [
        "sasebo-city-home",
        "sasebo-budget-2026",
        "sasebo-settlement-2024",
    ]

    sources = load(ROOT / "data/catalog/sasebo_phase15_sources.json")["sources"]
    assert len(sources) == 4
    for source in sources:
        assert source["official_url"].startswith("https://www.city.sasebo.lg.jp/")
        assert "verification_status" not in source


def test_sasebo_sources_match_the_reviewed_package():
    catalog = load(ROOT / "data/catalog/sasebo_phase15_sources.json")
    assert catalog["id"] == "sasebo-phase15-sources"
    assert catalog["name_ja"] == "佐世保市"
    assert catalog["official_code"] == "422029"
    assert catalog["phase"] == 15
    assert catalog["reviewed_at"] == "2026-11-17"

    by_id = {source["id"]: source for source in catalog["sources"]}
    assert set(by_id) == {
        "sasebo-seventh-latter-plan",
        "sasebo-budget-policy-2026",
        "sasebo-budget-2026",
        "sasebo-settlement-2024",
    }
    assert by_id["sasebo-seventh-latter-plan"]["evidence_role"] == (
        "comprehensive_plan"
    )
    assert by_id["sasebo-seventh-latter-plan"]["format"] == "html"
    assert by_id["sasebo-budget-policy-2026"]["evidence_role"] == (
        "implementation_and_budget_governance"
    )
    assert by_id["sasebo-budget-2026"]["evidence_role"] == "budget"
    assert by_id["sasebo-settlement-2024"]["evidence_role"] == "settlement"


def test_sasebo_fiscal_records_match_budget_and_settlement_sources():
    records = load(REVIEWED / "fiscal_records.json")
    assert len(records) == 3
    for record in records:
        assert record["confidence"] == "high"
        assert record["review_status"] == "reviewed"
        assert record["value_status"] == "available"
        assert record["value"] is None

    budget = next(record for record in records if record["fiscal_year"] == 2026)
    assert budget["id"] == "jp-local-422029-fiscal-2026-total-expenditure"
    assert budget["amount_yen"] == 133_877_303_000
    assert budget["metric"] == "total_expenditure"
    assert budget["metric_label"] == "一般会計当初予算総額"
    assert budget["stage"] == "initial_budget"
    assert budget["sources"] == ["sasebo-budget-2026"]

    text = json.dumps(records, ensure_ascii=False)
    # Bill No. 18 was adopted as proposed （原案可決） on 2026-03-23
    # according to the council's official March 2026 regular-session
    # results, and that wording is kept verbatim. The amount itself
    # was identified by reverse calculation from the budget
    # explanation document for supplementary budget No. 1, and
    # direct confirmation in the original budget explanation
    # document itself has not been performed.
    assert "第18号議案" in text
    assert "原案可決" in text
    assert "2026年3月23日" in text
    assert "133,877,303千円" in text
    assert "千円単位" in text
    assert "逆算" in text
    assert "直接確認は未実施" in text
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
    assert revenue["amount_yen"] == 130_949_847_225
    assert expenditure["amount_yen"] == 127_473_906_421
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 3_475_940_804
    assert revenue["stage"] == "settlement"
    assert expenditure["stage"] == "settlement"
    assert revenue["sources"] == ["sasebo-settlement-2024"]
    assert expenditure["sources"] == ["sasebo-settlement-2024"]
    # The FY2024 settlement was certified (bill No. 100) on
    # 2025-12-04 at the December 2025 regular session after
    # continued review at the September 2025 session, confirmed by a
    # live-browser supplementary investigation of the council's
    # official session results. The totals stay at the yen precision
    # printed in the audit committee's settlement review opinion,
    # and ordinary-account aggregate figures are not used as
    # general-account values.
    assert "第100号議案" in text
    assert "2025年12月4日" in text
    assert "認定された" in text
    assert "実質収支は2,738,920,535円" in text
    assert "普通会計ベース" in text
    assert "不認定" not in text


def test_sasebo_evidence_packets_confirm_fiscal_claims():
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
        "jp-local-422029-fiscal-2026-total-expenditure",
        "jp-local-422029-fiscal-2024-total-revenue",
        "jp-local-422029-fiscal-2024-total-expenditure",
    }

    text = json.dumps(packets, ensure_ascii=False)
    assert "第18号議案" in text
    assert "第100号議案" in text
    assert "レビュー済みレコード" in text
    assert "人間による確認待ちステージング" not in text
    assert "修正可決" not in text
    assert "修正議決" not in text
    assert "不認定" not in text


def test_sasebo_plan_review_accepts_plan_and_keeps_linkage_open():
    plan_review = load(REVIEWED / "plan_review.json")
    assert plan_review["id"] == "phase15-sasebo-plan-review"
    assert plan_review["review_status"] == "reviewed"
    assert plan_review["reviewed_at"] == "2026-11-17"
    assert plan_review["next_action"]
    assert plan_review["quality_boundary"]

    by_id = {record["id"]: record for record in plan_review["records"]}
    assert by_id["sasebo-current-plan-period"]["decision"] == "accepted"
    assert "第7次佐世保市総合計画" in by_id["sasebo-current-plan-period"][
        "statement"
    ]
    assert "2020年度〜2027年度の8年間" in by_id["sasebo-current-plan-period"][
        "statement"
    ]
    assert "verified_fixed_period" in by_id["sasebo-current-plan-period"][
        "statement"
    ]
    assert by_id["sasebo-current-policy-structure"]["decision"] == "accepted"
    assert "キラっ都" in by_id["sasebo-current-policy-structure"]["statement"]
    assert "活力あふれる国際都市" in by_id["sasebo-current-policy-structure"][
        "statement"
    ]
    assert by_id["sasebo-progress-governance-framework"]["decision"] == (
        "accepted"
    )
    assert "PDCAサイクル" in by_id["sasebo-progress-governance-framework"][
        "statement"
    ]
    assert by_id["sasebo-plan-transition"]["decision"] == "accepted"
    assert "前期基本計画（2020年度〜2023年度" in by_id["sasebo-plan-transition"][
        "statement"
    ]
    linkage = by_id["sasebo-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["fiscal_year"] == 2024
    # FY2024 is the first fiscal year of the latter basic plan and
    # falls within the current basic plan period, but no official
    # total-level mapping to the plan's policy structure exists, so
    # the linkage stays not_assessable.
    assert "後期基本計画" in linkage["statement"]
    assert "not_assessable" in linkage["statement"]


def test_sasebo_policy_structure_keeps_four_fields():
    structure = load(ROOT / "data/catalog/sasebo_current_policy_structure.json")
    assert structure["id"] == "sasebo-current-policy-structure"
    assert structure["review_status"] == "reviewed"
    assert structure["source_id"] == "sasebo-seventh-latter-plan"
    assert structure["counts"] == {"basic_goals": 4, "basic_plan_measures": 0}

    plan = structure["current_plan"]
    assert plan["title"].startswith("佐世保市第7次総合計画")
    assert plan["start_fiscal_year"] == 2020
    assert plan["end_fiscal_year"] == 2027
    assert plan["period_status"] == "verified_fixed_period"
    assert plan["vision"] == "海風薫り 世界へはばたく \"キラっ都\" SASEBO"
    fields = plan["policy_fields"]
    assert [field["name_ja"] for field in fields] == [
        "しごと 活力あふれる国際都市",
        "ひと 育み、学び、認め合う「人財」育成都市",
        "まち 西九州を牽引する創造都市",
        "くらし 地域が社会を築く安心都市",
    ]
    measures = [measure for field in fields for measure in field["measures"]]
    assert measures == []
    principles = " ".join(plan["management_principles"])
    assert "後期基本計画" in principles
    assert "PDCAサイクル" in principles
    assert "流用しない" in principles


def test_sasebo_progress_review_keeps_implementation_plan_framework():
    progress = load(
        ROOT / "data/catalog/sasebo_current_progress_review_summary.json"
    )
    assert progress["id"] == "sasebo-current-progress-review-summary"
    assert progress["review_status"] == "reviewed_with_explicit_deferred_depth"
    assert progress["reviewed_at"] == "2026-11-17"

    framework = progress["current_implementation_plan"]
    assert "実施計画" in framework["title"]
    assert "4年以内" in framework["period"]
    assert "PDCAサイクル" in framework["rolling_structure"]
    assert framework["current_period_item_actuals"]["status"] == (
        "not_promoted_in_v1"
    )

    assert progress["evaluation_evidence"]["status"] == "not_promoted_in_v1"
    linkage = progress["fiscal_linkage"]
    assert linkage["fiscal_year"] == 2024
    assert linkage["status"] == "not_assessable"
    assert "第100号議案" in linkage["boundary"]
    assert "not_assessable" in linkage["boundary"]


def test_sasebo_finance_sources_are_reviewed():
    finance = load(ROOT / "data/catalog/sasebo_city_finance_sources.json")
    assert finance["version"] == "0.1.0"
    assert finance["updated_at"] == "2026-11-17"
    assert finance["scope"] == "phase15-core-capital-review"

    by_id = {record["id"]: record for record in finance["records"]}
    assert set(by_id) == {
        "sasebo-city-home",
        "sasebo-budget-2026",
        "sasebo-settlement-2024",
    }
    for record in finance["records"]:
        assert record["municipality_key"] == "sasebo-city"
        assert record["source_kind"] == "document"
        assert record["availability"] == "published"
        assert record["review_status"] == "reviewed"
        assert record["confidence"] == "high"
        assert record["url"].startswith("https://www.city.sasebo.lg.jp/")


def test_sasebo_completion_marks_every_gate_and_defers_depth():
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
    assert "第18号議案" in boundary
    assert "第100号議案" in boundary
    assert "原案可決" in boundary
    assert "逆算" in boundary
    assert "直接確認は未実施" in boundary
    assert "2,738,920,535円" in boundary
    assert "verified_fixed_period" in boundary
    assert "不認定" not in boundary
    assert "修正可決" not in boundary


def test_sasebo_review_records_delegation_not_owner_review():
    candidate = load(CANDIDATE)
    assert candidate["package_state"] == "prepared"
    assert candidate["publication"]["eligible"] is False
    assert candidate["human_review"]["status"] == "approved"
    assert candidate["human_review"]["reviewed_at"] == "2026-11-17"
    note = candidate["human_review"]["reviewer_note"]
    # The promotion rests on the owner's explicit 2026-11-15 delegation of
    # the review to Muse; the record must say so and must not present
    # the review as the owner's personal review of the primary sources.
    assert "委任" in note
    assert "レビューはあなたがやってください" in note
    assert "所有者本人が一次資料を直接レビューしたものではない" in note
    assert "第18号議案" in note
    assert "第100号議案" in note

    serialized = json.dumps(load(COMPLETION), ensure_ascii=False)
    assert "委任" in serialized
    assert "所有者本人が一次資料を直接レビューしたものではない" in serialized
    assert "不認定" not in serialized
    assert "修正可決" not in serialized
