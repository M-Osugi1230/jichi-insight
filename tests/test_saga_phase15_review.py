from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/saga_phase15_completion.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
REVIEWED = ROOT / "data/reviewed/saga-city"
CANDIDATE = ROOT / "data/candidates/saga-city/review_candidate.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_saga_review_package_is_the_sixty_first_completion():
    completion = load(COMPLETION)
    assert completion == {
        "id": "saga-phase15-completion",
        "phase": 15,
        "status": "reviewed_complete",
        "official_code": "412015",
        "name_ja": "佐賀市",
        "completed_at": "2026-11-17",
        "completion_depth": "declared_review_package_v1",
        "review_package": {
            "source_catalog_path": "data/catalog/saga_phase15_sources.json",
            "plan_review_path": "data/reviewed/saga-city/plan_review.json",
            "policy_structure_path": (
                "data/catalog/saga_current_policy_structure.json"
            ),
            "progress_review_path": (
                "data/catalog/saga_current_progress_review_summary.json"
            ),
            "fiscal_records_path": (
                "data/reviewed/saga-city/fiscal_records.json"
            ),
            "fiscal_evidence_path": (
                "data/reviewed/saga-city/evidence_packets.json"
            ),
            "counts": {
                "basic_goals": 10,
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
    assert queue["summary"]["reviewed_complete_count"] == 68
    assert queue["summary"]["pending_record_review_count"] == 0
    assert queue["summary"]["next_official_code"] is None
    entry = next(
        row for row in queue["execution_queue"] if row["official_code"] == "412015"
    )
    assert entry["status"] == "reviewed_complete"
    assert entry["completion_path"] == "data/catalog/saga_phase15_completion.json"


def test_saga_municipality_and_sources_use_only_official_city_pages():
    municipality = load(REVIEWED / "municipality.json")
    assert municipality["id"] == "jp-local-412015"
    assert municipality["official_code"] == "412015"
    assert municipality["name_ja"] == "佐賀市"
    assert municipality["prefecture_name_ja"] == "佐賀県"
    assert municipality["municipality_type"] == "city"
    assert municipality["official_url"] == "https://www.city.saga.lg.jp/"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert municipality["data_status"] == "reviewed"
    assert municipality["last_verified_at"] == "2026-11-17"
    assert municipality["sources"] == [
        "saga-city-home",
        "saga-budget-2026",
        "saga-settlement-2024",
    ]

    sources = load(ROOT / "data/catalog/saga_phase15_sources.json")["sources"]
    assert len(sources) == 5
    for source in sources:
        assert source["official_url"].startswith("https://www.city.saga.lg.jp/")
        assert "verification_status" not in source


def test_saga_sources_match_the_reviewed_package():
    catalog = load(ROOT / "data/catalog/saga_phase15_sources.json")
    assert catalog["id"] == "saga-phase15-sources"
    assert catalog["name_ja"] == "佐賀市"
    assert catalog["official_code"] == "412015"
    assert catalog["phase"] == 15
    assert catalog["reviewed_at"] == "2026-11-17"

    by_id = {source["id"]: source for source in catalog["sources"]}
    assert set(by_id) == {
        "saga-third-plan",
        "saga-future-co-creation",
        "saga-administrative-evaluation",
        "saga-budget-2026",
        "saga-settlement-2024",
    }
    assert by_id["saga-third-plan"]["evidence_role"] == "comprehensive_plan"
    assert by_id["saga-third-plan"]["format"] == "html"
    assert by_id["saga-future-co-creation"]["evidence_role"] == (
        "implementation_plan"
    )
    assert by_id["saga-administrative-evaluation"]["evidence_role"] == (
        "annual_progress"
    )
    assert by_id["saga-budget-2026"]["evidence_role"] == "budget"
    assert by_id["saga-settlement-2024"]["evidence_role"] == "settlement"


def test_saga_fiscal_records_match_budget_and_settlement_sources():
    records = load(REVIEWED / "fiscal_records.json")
    assert len(records) == 3
    for record in records:
        assert record["confidence"] == "high"
        assert record["review_status"] == "reviewed"
        assert record["value_status"] == "available"
        assert record["value"] is None

    budget = next(record for record in records if record["fiscal_year"] == 2026)
    assert budget["id"] == "jp-local-412015-fiscal-2026-total-expenditure"
    assert budget["amount_yen"] == 119_800_000_000
    assert budget["metric"] == "total_expenditure"
    assert budget["metric_label"] == "一般会計当初予算総額"
    assert budget["stage"] == "initial_budget"
    assert budget["sources"] == ["saga-budget-2026"]

    text = json.dumps(records, ensure_ascii=False)
    # Bill No. 1 was adopted as proposed （原案可決） on 2026-03-24
    # according to the council newsletter's official deliberation
    # results, and that wording is kept verbatim. A member-submitted
    # amendment (reducing the total to 119,749,911 thousand yen) was
    # rejected, so the enacted amount is the original total and the
    # enactment is not an amended adoption.
    assert "第1号議案" in text
    assert "原案可決" in text
    assert "2026年3月24日" in text
    assert "119,800,000千円" in text
    assert "修正案" in text
    assert "119,749,911千円" in text
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
    assert revenue["amount_yen"] == 118_510_118_104
    assert expenditure["amount_yen"] == 116_749_721_609
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 1_760_396_495
    assert revenue["stage"] == "settlement"
    assert expenditure["stage"] == "settlement"
    assert revenue["sources"] == ["saga-settlement-2024"]
    assert expenditure["sources"] == ["saga-settlement-2024"]
    # The FY2024 settlement was certified (bill No. 60) with the vote
    # date 2025-09-16 identified from the session's final day and the
    # standing committees' review report dates; final confirmation in
    # the plenary minutes is still outstanding. The totals stay at
    # the yen precision printed in the audit opinion, and the real
    # balance stays at the thousand-yen precision printed in its
    # summary table; ordinary-account aggregate figures are not used
    # as general-account values.
    assert "第60号議案" in text
    assert "2025年9月16日" in text
    assert "1,161,595千円" in text
    assert "普通会計ベース" in text
    assert "不認定" not in text


def test_saga_evidence_packets_confirm_fiscal_claims():
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
        "jp-local-412015-fiscal-2026-total-expenditure",
        "jp-local-412015-fiscal-2024-total-revenue",
        "jp-local-412015-fiscal-2024-total-expenditure",
    }

    text = json.dumps(packets, ensure_ascii=False)
    assert "第1号議案" in text
    assert "第60号議案" in text
    assert "レビュー済みレコード" in text
    assert "人間による確認待ちステージング" not in text
    assert "修正可決" not in text
    assert "修正議決" not in text
    assert "不認定" not in text


def test_saga_plan_review_accepts_plan_and_keeps_linkage_open():
    plan_review = load(REVIEWED / "plan_review.json")
    assert plan_review["id"] == "phase15-saga-plan-review"
    assert plan_review["review_status"] == "reviewed"
    assert plan_review["reviewed_at"] == "2026-11-17"
    assert plan_review["next_action"]
    assert plan_review["quality_boundary"]

    by_id = {record["id"]: record for record in plan_review["records"]}
    assert by_id["saga-current-plan-period"]["decision"] == "accepted"
    assert "第3次佐賀市総合計画" in by_id["saga-current-plan-period"][
        "statement"
    ]
    assert "基本構想（2025年度〜2040年度・16年間）" in by_id[
        "saga-current-plan-period"
    ]["value"]
    assert "verified_fixed_period" in by_id["saga-current-plan-period"][
        "statement"
    ]
    assert by_id["saga-current-policy-structure"]["decision"] == "accepted"
    assert "10の分野" in by_id["saga-current-policy-structure"]["statement"]
    assert "佐賀らしさでみんなが上を向くまち" in by_id[
        "saga-current-policy-structure"
    ]["statement"]
    assert by_id["saga-progress-governance-framework"]["decision"] == (
        "accepted"
    )
    assert "行政評価" in by_id["saga-progress-governance-framework"][
        "statement"
    ]
    assert by_id["saga-plan-transition"]["decision"] == "accepted"
    assert "第2次佐賀市総合計画" in by_id["saga-plan-transition"]["statement"]
    linkage = by_id["saga-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["fiscal_year"] == 2024
    # FY2024 is the final fiscal year of the previous plan and its
    # plan version differs from the current plan, so the linkage
    # stays not_assessable.
    assert "最終年度" in linkage["statement"]
    assert "not_assessable" in linkage["statement"]


def test_saga_policy_structure_keeps_ten_fields():
    structure = load(ROOT / "data/catalog/saga_current_policy_structure.json")
    assert structure["id"] == "saga-current-policy-structure"
    assert structure["review_status"] == "reviewed"
    assert structure["source_id"] == "saga-third-plan"
    assert structure["counts"] == {"basic_goals": 10, "basic_plan_measures": 0}

    plan = structure["current_plan"]
    assert plan["title"].startswith("第3次佐賀市総合計画")
    assert plan["start_fiscal_year"] == 2025
    assert plan["end_fiscal_year"] == 2040
    assert plan["period_status"] == "verified_fixed_period"
    assert plan["vision"] == "佐賀らしさでみんなが上を向くまち"
    fields = plan["policy_fields"]
    assert [field["name_ja"] for field in fields] == [
        "01 子育て・教育",
        "02 健康・福祉",
        "03 文化・スポーツ",
        "04 経済・観光",
        "05 農林水産",
        "06 生活・環境",
        "07 コミュニティ",
        "08 防災・安全",
        "09 都市・交通",
        "10 行政経営",
    ]
    measures = [measure for field in fields for measure in field["measures"]]
    assert measures == []
    principles = " ".join(plan["management_principles"])
    assert "第2次佐賀市総合計画" in principles
    assert "行政評価" in principles
    assert "流用しない" in principles


def test_saga_progress_review_keeps_implementation_plan_framework():
    progress = load(
        ROOT / "data/catalog/saga_current_progress_review_summary.json"
    )
    assert progress["id"] == "saga-current-progress-review-summary"
    assert progress["review_status"] == "reviewed_with_explicit_deferred_depth"
    assert progress["reviewed_at"] == "2026-11-17"

    framework = progress["current_implementation_plan"]
    assert "未来共創プラン" in framework["title"]
    assert "令和7年4月〜令和11年3月" in framework["period"]
    assert "行政評価" in framework["rolling_structure"]
    assert framework["current_period_item_actuals"]["status"] == (
        "not_promoted_in_v1"
    )

    assert progress["evaluation_evidence"]["status"] == "not_promoted_in_v1"
    linkage = progress["fiscal_linkage"]
    assert linkage["fiscal_year"] == 2024
    assert linkage["status"] == "not_assessable"
    assert "第60号議案" in linkage["boundary"]
    assert "not_assessable" in linkage["boundary"]


def test_saga_finance_sources_are_reviewed():
    finance = load(ROOT / "data/catalog/saga_city_finance_sources.json")
    assert finance["version"] == "0.1.0"
    assert finance["updated_at"] == "2026-11-17"
    assert finance["scope"] == "phase15-core-capital-review"

    by_id = {record["id"]: record for record in finance["records"]}
    assert set(by_id) == {
        "saga-city-home",
        "saga-budget-2026",
        "saga-settlement-2024",
    }
    for record in finance["records"]:
        assert record["municipality_key"] == "saga-city"
        assert record["source_kind"] == "document"
        assert record["availability"] == "published"
        assert record["review_status"] == "reviewed"
        assert record["confidence"] == "high"
        assert record["url"].startswith("https://www.city.saga.lg.jp/")


def test_saga_completion_marks_every_gate_and_defers_depth():
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
    assert "第1号議案" in boundary
    assert "第60号議案" in boundary
    assert "原案可決" in boundary
    assert "修正案は否決され" in boundary
    assert "1,161,595千円" in boundary
    assert "verified_fixed_period" in boundary
    assert "不認定" not in boundary
    assert "修正可決" not in boundary


def test_saga_review_records_delegation_not_owner_review():
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
    assert "第1号議案" in note
    assert "第60号議案" in note

    serialized = json.dumps(load(COMPLETION), ensure_ascii=False)
    assert "委任" in serialized
    assert "所有者本人が一次資料を直接レビューしたものではない" in serialized
    assert "不認定" not in serialized
    assert "修正可決" not in serialized
