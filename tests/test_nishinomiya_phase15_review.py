from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/nishinomiya_phase15_completion.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
REVIEWED = ROOT / "data/reviewed/nishinomiya-city"
CANDIDATE = ROOT / "data/candidates/nishinomiya-city/review_candidate.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_nishinomiya_review_package_is_the_forty_sixth_completion():
    completion = load(COMPLETION)
    assert completion == {
        "id": "nishinomiya-phase15-completion",
        "phase": 15,
        "status": "reviewed_complete",
        "official_code": "282049",
        "name_ja": "西宮市",
        "completed_at": "2026-11-16",
        "completion_depth": "declared_review_package_v1",
        "review_package": {
            "source_catalog_path": "data/catalog/nishinomiya_phase15_sources.json",
            "plan_review_path": "data/reviewed/nishinomiya-city/plan_review.json",
            "policy_structure_path": (
                "data/catalog/nishinomiya_current_policy_structure.json"
            ),
            "progress_review_path": (
                "data/catalog/nishinomiya_current_progress_review_summary.json"
            ),
            "fiscal_records_path": (
                "data/reviewed/nishinomiya-city/fiscal_records.json"
            ),
            "fiscal_evidence_path": (
                "data/reviewed/nishinomiya-city/evidence_packets.json"
            ),
            "counts": {
                "basic_goals": 35,
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
    assert queue["summary"]["reviewed_complete_count"] == 60
    assert queue["summary"]["pending_record_review_count"] == 7
    assert queue["summary"]["next_official_code"] == "412015"
    entry = next(
        row for row in queue["execution_queue"] if row["official_code"] == "282049"
    )
    assert entry["status"] == "reviewed_complete"
    assert entry["completion_path"] == (
        "data/catalog/nishinomiya_phase15_completion.json"
    )


def test_nishinomiya_municipality_and_sources_use_only_official_city_pages():
    municipality = load(REVIEWED / "municipality.json")
    assert municipality["id"] == "jp-local-282049"
    assert municipality["official_code"] == "282049"
    assert municipality["name_ja"] == "西宮市"
    assert municipality["prefecture_name_ja"] == "兵庫県"
    assert municipality["municipality_type"] == "core_city"
    assert municipality["official_url"] == "https://www.nishi.or.jp/"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert municipality["data_status"] == "reviewed"
    assert municipality["last_verified_at"] == "2026-11-16"
    assert municipality["sources"] == [
        "nishinomiya-city-home",
        "nishinomiya-budget-2026",
        "nishinomiya-settlement-2024",
    ]

    sources = load(ROOT / "data/catalog/nishinomiya_phase15_sources.json")["sources"]
    assert len(sources) == 4
    for source in sources:
        assert source["official_url"].startswith("https://www.nishi.or.jp/")
        assert "verification_status" not in source


def test_nishinomiya_sources_match_the_reviewed_package():
    catalog = load(ROOT / "data/catalog/nishinomiya_phase15_sources.json")
    assert catalog["id"] == "nishinomiya-phase15-sources"
    assert catalog["name_ja"] == "西宮市"
    assert catalog["official_code"] == "282049"
    assert catalog["phase"] == 15
    assert catalog["reviewed_at"] == "2026-11-16"

    by_id = {source["id"]: source for source in catalog["sources"]}
    assert set(by_id) == {
        "nishinomiya-fifth-latter-plan",
        "nishinomiya-implementation-plan",
        "nishinomiya-budget-2026",
        "nishinomiya-settlement-2024",
    }
    assert by_id["nishinomiya-fifth-latter-plan"]["evidence_role"] == (
        "comprehensive_plan"
    )
    assert by_id["nishinomiya-fifth-latter-plan"]["format"] == "html"
    assert by_id["nishinomiya-implementation-plan"]["evidence_role"] == (
        "implementation_plan_and_progress"
    )
    assert by_id["nishinomiya-budget-2026"]["evidence_role"] == "budget"
    assert by_id["nishinomiya-settlement-2024"]["evidence_role"] == "settlement"


def test_nishinomiya_fiscal_records_match_budget_and_settlement_sources():
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
    assert budget["id"] == "jp-local-282049-fiscal-2026-total-expenditure"
    assert budget["amount_yen"] == 221_422_490_000
    assert budget["metric"] == "total_expenditure"
    assert budget["metric_label"] == "一般会計当初予算総額"
    assert budget["stage"] == "initial_budget"
    assert budget["sources"] == ["nishinomiya-budget-2026"]

    text = json.dumps(records, ensure_ascii=False)
    # The council's deliberation-results table carries no result-wording
    # column and defines the mark only as passed by majority vote, so the
    # budget must never be recorded with any other result wording.
    assert "議案第493号" in text
    assert "賛成多数" in text
    assert "2026年3月18日" in text
    assert "221,422,490千円" in text
    assert "原案可決" not in text

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
    assert revenue["amount_yen"] == 205_479_435_000
    assert expenditure["amount_yen"] == 204_547_927_000
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 931_508_000
    assert revenue["stage"] == "settlement"
    assert expenditure["stage"] == "settlement"
    assert revenue["sources"] == ["nishinomiya-settlement-2024"]
    assert expenditure["sources"] == ["nishinomiya-settlement-2024"]
    # The FY2024 settlement was certified (認定第15号), not rejected; the
    # real balance is kept at the published sen-yen precision, and the
    # combined general/special real balance is not reused.
    assert "認定第15号" in text
    assert "2025年10月2日" in text
    assert "647,529千円" in text
    assert "283,979千円" in text
    assert "1,861,075千円" in text
    assert "不認定" not in text


def test_nishinomiya_evidence_packets_confirm_fiscal_claims():
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
        "jp-local-282049-fiscal-2026-total-expenditure",
        "jp-local-282049-fiscal-2024-total-revenue",
        "jp-local-282049-fiscal-2024-total-expenditure",
    }

    text = json.dumps(packets, ensure_ascii=False)
    assert "議案第493号" in text
    assert "認定第15号" in text
    assert "原案可決" not in text
    assert "レビュー済みレコード" in text
    assert "人間による確認待ちステージング" not in text


def test_nishinomiya_plan_review_accepts_fifth_plan_and_keeps_linkage_open():
    plan_review = load(REVIEWED / "plan_review.json")
    assert plan_review["id"] == "phase15-nishinomiya-plan-review"
    assert plan_review["review_status"] == "reviewed"
    assert plan_review["reviewed_at"] == "2026-11-16"
    assert plan_review["next_action"]
    assert plan_review["quality_boundary"]

    by_id = {record["id"]: record for record in plan_review["records"]}
    assert by_id["nishinomiya-current-plan-period"]["decision"] == "accepted"
    assert "第5次西宮市総合計画" in by_id["nishinomiya-current-plan-period"][
        "statement"
    ]
    assert "平成31年3月" in by_id["nishinomiya-current-plan-period"]["statement"]
    assert "令和元年度～令和10年度" in by_id["nishinomiya-current-plan-period"][
        "statement"
    ]
    assert by_id["nishinomiya-current-policy-structure"]["decision"] == "accepted"
    assert "35施策分野" in by_id["nishinomiya-current-policy-structure"][
        "statement"
    ]
    assert by_id["nishinomiya-progress-governance-framework"]["decision"] == (
        "accepted"
    )
    assert "ローリング" in by_id["nishinomiya-progress-governance-framework"][
        "statement"
    ]
    assert by_id["nishinomiya-plan-transition"]["decision"] == "accepted"
    assert "第4次西宮市総合計画" in by_id["nishinomiya-plan-transition"][
        "statement"
    ]
    linkage = by_id["nishinomiya-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["fiscal_year"] == 2024
    assert "後期基本計画" in linkage["statement"]


def test_nishinomiya_policy_structure_keeps_35_fields_and_empty_measures():
    structure = load(ROOT / "data/catalog/nishinomiya_current_policy_structure.json")
    assert structure["id"] == "nishinomiya-current-policy-structure"
    assert structure["review_status"] == "reviewed"
    assert structure["source_id"] == "nishinomiya-fifth-latter-plan"
    assert structure["counts"] == {"basic_goals": 35, "basic_plan_measures": 0}

    plan = structure["current_plan"]
    assert plan["title"] == "第5次西宮市総合計画 後期基本計画（2024年度～2028年度）"
    assert plan["start_fiscal_year"] == 2024
    assert plan["end_fiscal_year"] == 2028
    assert plan["period_status"] == "verified_fixed_period"
    assert plan["vision"].startswith("未来を拓く文教住宅都市・西宮")
    assert len(plan["policy_fields"]) == 35
    assert plan["policy_fields"][0]["name_ja"] == "第Ⅰ部 住環境・自然環境：住環境"
    assert plan["policy_fields"][-1]["name_ja"] == "第Ⅵ部 政策推進：執行体制"
    assert all(field["measures"] == [] for field in plan["policy_fields"])
    principles = " ".join(plan["management_principles"])
    assert "後期2024年度～2028年度" in principles
    assert "ローリング" in principles


def test_nishinomiya_progress_review_keeps_rolling_implementation_framework():
    progress = load(
        ROOT / "data/catalog/nishinomiya_current_progress_review_summary.json"
    )
    assert progress["id"] == "nishinomiya-current-progress-review-summary"
    assert progress["review_status"] == "reviewed_with_explicit_deferred_depth"
    assert progress["reviewed_at"] == "2026-11-16"

    framework = progress["current_implementation_plan"]
    assert framework["title"].startswith("第5次西宮市総合計画実施計画")
    assert "後期基本計画（2024年度～2028年度）" in framework["period"]
    assert framework["current_period_item_actuals"]["status"] == (
        "not_promoted_in_v1"
    )

    assert progress["evaluation_evidence"]["status"] == "not_promoted_in_v1"
    linkage = progress["fiscal_linkage"]
    assert linkage["fiscal_year"] == 2024
    assert linkage["status"] == "not_assessable"
    assert "後期基本計画" in linkage["boundary"]
    assert "認定第15号・2025年10月2日認定" in linkage["boundary"]


def test_nishinomiya_finance_sources_are_staged_only():
    finance = load(ROOT / "data/catalog/nishinomiya_city_finance_sources.json")
    assert finance["version"] == "0.1.0"
    assert finance["updated_at"] == "2026-11-16"
    assert finance["scope"] == "phase15-core-capital-review"

    by_id = {record["id"]: record for record in finance["records"]}
    assert set(by_id) == {
        "nishinomiya-city-home",
        "nishinomiya-budget-2026",
        "nishinomiya-settlement-2024",
    }
    for record in finance["records"]:
        assert record["municipality_key"] == "nishinomiya-city"
        assert record["source_kind"] == "document"
        assert record["availability"] == "published"
        assert record["review_status"] == "reviewed"
        assert record["confidence"] == "high"
        assert record["url"].startswith("https://www.nishi.or.jp/")


def test_nishinomiya_completion_marks_every_gate_and_defers_depth():
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
    assert "認定第15号" in boundary
    assert "647,529千円" in boundary
    assert "原案可決" not in boundary


def test_nishinomiya_review_records_delegation_not_owner_review():
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
    assert "原案可決" not in note

    serialized = json.dumps(load(COMPLETION), ensure_ascii=False)
    assert "委任" in serialized
    assert "所有者本人が一次資料を直接レビューしたものではない" in serialized
    assert "原案可決" not in serialized
