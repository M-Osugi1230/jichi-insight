from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/takamatsu_phase15_completion.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
REVIEWED = ROOT / "data/reviewed/takamatsu-city"
CANDIDATE = ROOT / "data/candidates/takamatsu-city/review_candidate.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_takamatsu_review_package_is_the_fifty_seventh_completion():
    completion = load(COMPLETION)
    assert completion == {
        "id": "takamatsu-phase15-completion",
        "phase": 15,
        "status": "reviewed_complete",
        "official_code": "372013",
        "name_ja": "高松市",
        "completed_at": "2026-11-17",
        "completion_depth": "declared_review_package_v1",
        "review_package": {
            "source_catalog_path": "data/catalog/takamatsu_phase15_sources.json",
            "plan_review_path": "data/reviewed/takamatsu-city/plan_review.json",
            "policy_structure_path": (
                "data/catalog/takamatsu_current_policy_structure.json"
            ),
            "progress_review_path": (
                "data/catalog/takamatsu_current_progress_review_summary.json"
            ),
            "fiscal_records_path": (
                "data/reviewed/takamatsu-city/fiscal_records.json"
            ),
            "fiscal_evidence_path": (
                "data/reviewed/takamatsu-city/evidence_packets.json"
            ),
            "counts": {
                "basic_goals": 6,
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
    assert queue["summary"]["reviewed_complete_count"] == 64
    assert queue["summary"]["pending_record_review_count"] == 3
    assert queue["summary"]["next_official_code"] == "452017"
    entry = next(
        row for row in queue["execution_queue"] if row["official_code"] == "372013"
    )
    assert entry["status"] == "reviewed_complete"
    assert (
        entry["completion_path"]
        == "data/catalog/takamatsu_phase15_completion.json"
    )


def test_takamatsu_municipality_and_sources_use_only_official_city_pages():
    municipality = load(REVIEWED / "municipality.json")
    assert municipality["id"] == "jp-local-372013"
    assert municipality["official_code"] == "372013"
    assert municipality["name_ja"] == "高松市"
    assert municipality["prefecture_name_ja"] == "香川県"
    assert municipality["municipality_type"] == "core_city"
    assert municipality["official_url"] == (
        "https://www.city.takamatsu.kagawa.jp/"
    )
    assert municipality["fiscal_years"] == [2024, 2026]
    assert municipality["data_status"] == "reviewed"
    assert municipality["last_verified_at"] == "2026-11-17"
    assert municipality["sources"] == [
        "takamatsu-city-home",
        "takamatsu-budget-2026",
        "takamatsu-settlement-2024",
    ]

    sources = load(ROOT / "data/catalog/takamatsu_phase15_sources.json")[
        "sources"
    ]
    assert len(sources) == 4
    for source in sources:
        assert source["official_url"].startswith(
            "https://www.city.takamatsu.kagawa.jp/"
        )
        assert "verification_status" not in source


def test_takamatsu_sources_match_the_reviewed_package():
    catalog = load(ROOT / "data/catalog/takamatsu_phase15_sources.json")
    assert catalog["id"] == "takamatsu-phase15-sources"
    assert catalog["name_ja"] == "高松市"
    assert catalog["official_code"] == "372013"
    assert catalog["phase"] == 15
    assert catalog["reviewed_at"] == "2026-11-17"

    by_id = {source["id"]: source for source in catalog["sources"]}
    assert set(by_id) == {
        "takamatsu-seventh-plan",
        "takamatsu-machizukuri-plans",
        "takamatsu-budget-2026",
        "takamatsu-settlement-2024",
    }
    assert by_id["takamatsu-seventh-plan"]["evidence_role"] == (
        "comprehensive_plan"
    )
    assert by_id["takamatsu-seventh-plan"]["format"] == "html"
    assert by_id["takamatsu-machizukuri-plans"]["evidence_role"] == (
        "implementation_plan"
    )
    assert by_id["takamatsu-budget-2026"]["evidence_role"] == "budget"
    assert by_id["takamatsu-settlement-2024"]["evidence_role"] == (
        "settlement"
    )


def test_takamatsu_fiscal_records_match_budget_and_settlement_sources():
    records = load(REVIEWED / "fiscal_records.json")
    assert len(records) == 3
    for record in records:
        assert record["confidence"] == "high"
        assert record["review_status"] == "reviewed"
        assert record["value_status"] == "available"
        assert record["value"] is None

    budget = next(record for record in records if record["fiscal_year"] == 2026)
    assert budget["id"] == "jp-local-372013-fiscal-2026-total-expenditure"
    assert budget["amount_yen"] == 192_800_000_000
    assert budget["metric"] == "total_expenditure"
    assert budget["metric_label"] == "一般会計当初予算総額"
    assert budget["stage"] == "initial_budget"
    assert budget["sources"] == ["takamatsu-budget-2026"]

    text = json.dumps(records, ensure_ascii=False)
    # Bill 議案第2号 carries the result wording printed in the council's
    # official results list (可決); the vote date 2026-03-23 was
    # identified from the plenary minutes agenda, and the amount stays
    # at the published thousand-yen precision. The wording is never
    # upgraded to an as-proposed or amended adoption.
    assert "議案第2号" in text
    assert "「可決」" in text
    assert "2026年3月23日" in text
    assert "192,800,000千円" in text
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
    assert revenue["amount_yen"] == 183_171_243_000
    assert expenditure["amount_yen"] == 177_907_841_000
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 5_263_402_000
    assert revenue["stage"] == "settlement"
    assert expenditure["stage"] == "settlement"
    assert revenue["sources"] == ["takamatsu-settlement-2024"]
    assert expenditure["sources"] == ["takamatsu-settlement-2024"]
    # The FY2024 settlement was certified (bill 認定第1号) on
    # 2025-12-05 after continued review, not rejected; the totals and
    # the real balance stay at the thousand-yen precision printed in
    # the settlement outlook summary, and ordinary-account aggregate
    # figures are not used.
    assert "認定第1号" in text
    assert "2025年12月5日" in text
    assert "4,071,697千円" in text
    assert "不認定" not in text


def test_takamatsu_evidence_packets_confirm_fiscal_claims():
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
        "jp-local-372013-fiscal-2026-total-expenditure",
        "jp-local-372013-fiscal-2024-total-revenue",
        "jp-local-372013-fiscal-2024-total-expenditure",
    }

    text = json.dumps(packets, ensure_ascii=False)
    assert "議案第2号" in text
    assert "認定第1号" in text
    assert "レビュー済みレコード" in text
    assert "人間による確認待ちステージング" not in text
    assert "原案可決" not in text
    assert "修正可決" not in text
    assert "修正議決" not in text
    assert "不認定" not in text


def test_takamatsu_plan_review_accepts_plan_and_keeps_linkage_open():
    plan_review = load(REVIEWED / "plan_review.json")
    assert plan_review["id"] == "phase15-takamatsu-plan-review"
    assert plan_review["review_status"] == "reviewed"
    assert plan_review["reviewed_at"] == "2026-11-17"
    assert plan_review["next_action"]
    assert plan_review["quality_boundary"]

    by_id = {record["id"]: record for record in plan_review["records"]}
    assert by_id["takamatsu-current-plan-period"]["decision"] == "accepted"
    assert "第7次高松市総合計画" in by_id["takamatsu-current-plan-period"][
        "statement"
    ]
    assert "第2期2026年度～2028年度" in by_id[
        "takamatsu-current-plan-period"
    ]["value"]
    assert by_id["takamatsu-current-policy-structure"]["decision"] == (
        "accepted"
    )
    assert "6つのまちづくりの目標" in by_id[
        "takamatsu-current-policy-structure"
    ]["statement"]
    assert "人がつどい 未来に躍動する 世界都市・高松" in by_id[
        "takamatsu-current-policy-structure"
    ]["statement"]
    assert by_id["takamatsu-progress-governance-framework"]["decision"] == (
        "accepted"
    )
    assert "総合計画推進会議" in by_id[
        "takamatsu-progress-governance-framework"
    ]["statement"]
    assert by_id["takamatsu-plan-transition"]["decision"] == "accepted"
    assert "第6次高松市総合計画" in by_id["takamatsu-plan-transition"][
        "statement"
    ]
    linkage = by_id["takamatsu-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["fiscal_year"] == 2024
    # FY2024 is a settlement of the first year of the current plan and
    # the plan version is the same, but no official total-level mapping
    # from the settlement totals to the plan's goal and policy
    # structure exists, so the linkage stays not_assessable.
    assert "対応付けは公式資料にない" in linkage["statement"]


def test_takamatsu_policy_structure_keeps_six_goals_and_empty_measures():
    structure = load(
        ROOT / "data/catalog/takamatsu_current_policy_structure.json"
    )
    assert structure["id"] == "takamatsu-current-policy-structure"
    assert structure["review_status"] == "reviewed"
    assert structure["source_id"] == "takamatsu-seventh-plan"
    assert structure["counts"] == {"basic_goals": 6, "basic_plan_measures": 0}

    plan = structure["current_plan"]
    assert plan["title"] == (
        "第7次高松市総合計画（基本構想「たかまつ未来ビジョン」2024年度～2031年度・"
        "実施計画「高松まちづくりプラン」第1期2024年度～2026年度／第2期2026年度～2028年度）"
    )
    assert plan["start_fiscal_year"] == 2024
    assert plan["end_fiscal_year"] == 2031
    assert plan["period_status"] == "verified_fixed_period"
    assert plan["vision"] == "人がつどい 未来に躍動する 世界都市・高松"
    assert len(plan["policy_fields"]) == 6
    assert plan["policy_fields"][0]["name_ja"] == (
        "誰もが自分らしく健やかに暮らせるまち"
    )
    assert plan["policy_fields"][-1]["name_ja"] == (
        "さまざまな主体がつながり、ともに力を発揮できるまち"
    )
    assert all(field["measures"] == [] for field in plan["policy_fields"])
    principles = " ".join(plan["management_principles"])
    assert "高松まちづくりプラン" in principles
    assert "政策17・施策43" in principles
    assert "verified_fixed_period" in principles


def test_takamatsu_progress_review_keeps_machizukuri_plan_framework():
    progress = load(
        ROOT / "data/catalog/takamatsu_current_progress_review_summary.json"
    )
    assert progress["id"] == "takamatsu-current-progress-review-summary"
    assert progress["review_status"] == "reviewed_with_explicit_deferred_depth"
    assert progress["reviewed_at"] == "2026-11-17"

    framework = progress["current_implementation_plan"]
    assert "高松まちづくりプラン" in framework["title"]
    assert "第2期2026年度～2028年度" in framework["title"]
    assert "第7次計画の初年度" in framework["period"]
    assert "総合計画推進会議" in framework["rolling_structure"]
    assert framework["current_period_item_actuals"]["status"] == (
        "not_promoted_in_v1"
    )

    assert progress["evaluation_evidence"]["status"] == "not_promoted_in_v1"
    linkage = progress["fiscal_linkage"]
    assert linkage["fiscal_year"] == 2024
    assert linkage["status"] == "not_assessable"
    assert "認定第1号" in linkage["boundary"]
    assert "not_assessable" in linkage["boundary"]


def test_takamatsu_finance_sources_are_reviewed():
    finance = load(ROOT / "data/catalog/takamatsu_city_finance_sources.json")
    assert finance["version"] == "0.1.0"
    assert finance["updated_at"] == "2026-11-17"
    assert finance["scope"] == "phase15-core-capital-review"

    by_id = {record["id"]: record for record in finance["records"]}
    assert set(by_id) == {
        "takamatsu-city-home",
        "takamatsu-budget-2026",
        "takamatsu-settlement-2024",
    }
    for record in finance["records"]:
        assert record["municipality_key"] == "takamatsu-city"
        assert record["source_kind"] == "document"
        assert record["availability"] == "published"
        assert record["review_status"] == "reviewed"
        assert record["confidence"] == "high"
        assert record["url"].startswith(
            "https://www.city.takamatsu.kagawa.jp/"
        )


def test_takamatsu_completion_marks_every_gate_and_defers_depth():
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
    assert "議案第2号" in boundary
    assert "認定第1号" in boundary
    assert "「可決」" in boundary
    assert "4,071,697千円" in boundary
    assert "verified_fixed_period" in boundary
    assert "原案可決" not in boundary
    assert "不認定" not in boundary


def test_takamatsu_review_records_delegation_not_owner_review():
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
    assert "議案第2号" in note
    assert "認定第1号" in note

    serialized = json.dumps(load(COMPLETION), ensure_ascii=False)
    assert "委任" in serialized
    assert "所有者本人が一次資料を直接レビューしたものではない" in serialized
    assert "不認定" not in serialized
    assert "原案可決" not in serialized
    assert "修正可決" not in serialized
