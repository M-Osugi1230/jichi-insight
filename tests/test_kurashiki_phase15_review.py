from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/kurashiki_phase15_completion.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
REVIEWED = ROOT / "data/reviewed/kurashiki-city"
CANDIDATE = ROOT / "data/candidates/kurashiki-city/review_candidate.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_kurashiki_review_package_is_the_fifty_first_completion():
    completion = load(COMPLETION)
    assert completion == {
        "id": "kurashiki-phase15-completion",
        "phase": 15,
        "status": "reviewed_complete",
        "official_code": "332020",
        "name_ja": "倉敷市",
        "completed_at": "2026-11-16",
        "completion_depth": "declared_review_package_v1",
        "review_package": {
            "source_catalog_path": "data/catalog/kurashiki_phase15_sources.json",
            "plan_review_path": "data/reviewed/kurashiki-city/plan_review.json",
            "policy_structure_path": (
                "data/catalog/kurashiki_current_policy_structure.json"
            ),
            "progress_review_path": (
                "data/catalog/kurashiki_current_progress_review_summary.json"
            ),
            "fiscal_records_path": "data/reviewed/kurashiki-city/fiscal_records.json",
            "fiscal_evidence_path": (
                "data/reviewed/kurashiki-city/evidence_packets.json"
            ),
            "counts": {
                "basic_goals": 44,
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
    assert queue["summary"]["reviewed_complete_count"] == 62
    assert queue["summary"]["pending_record_review_count"] == 5
    assert queue["summary"]["next_official_code"] == "422029"
    entry = next(
        row for row in queue["execution_queue"] if row["official_code"] == "332020"
    )
    assert entry["status"] == "reviewed_complete"
    assert entry["completion_path"] == "data/catalog/kurashiki_phase15_completion.json"


def test_kurashiki_municipality_and_sources_use_only_official_city_pages():
    municipality = load(REVIEWED / "municipality.json")
    assert municipality["id"] == "jp-local-332020"
    assert municipality["official_code"] == "332020"
    assert municipality["name_ja"] == "倉敷市"
    assert municipality["prefecture_name_ja"] == "岡山県"
    assert municipality["municipality_type"] == "core_city"
    assert municipality["official_url"] == "https://www.city.kurashiki.okayama.jp/"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert municipality["data_status"] == "reviewed"
    assert municipality["last_verified_at"] == "2026-11-16"
    assert municipality["sources"] == [
        "kurashiki-city-home",
        "kurashiki-budget-2026",
        "kurashiki-settlement-2024",
    ]

    sources = load(ROOT / "data/catalog/kurashiki_phase15_sources.json")["sources"]
    assert len(sources) == 4
    for source in sources:
        assert source["official_url"].startswith(
            "https://www.city.kurashiki.okayama.jp/"
        )
        assert "verification_status" not in source


def test_kurashiki_sources_match_the_reviewed_package():
    catalog = load(ROOT / "data/catalog/kurashiki_phase15_sources.json")
    assert catalog["id"] == "kurashiki-phase15-sources"
    assert catalog["name_ja"] == "倉敷市"
    assert catalog["official_code"] == "332020"
    assert catalog["phase"] == 15
    assert catalog["reviewed_at"] == "2026-11-16"

    by_id = {source["id"]: source for source in catalog["sources"]}
    assert set(by_id) == {
        "kurashiki-seventh-plan",
        "kurashiki-administrative-evaluation-2025",
        "kurashiki-budget-2026",
        "kurashiki-settlement-2024",
    }
    assert by_id["kurashiki-seventh-plan"]["evidence_role"] == "comprehensive_plan"
    assert by_id["kurashiki-seventh-plan"]["format"] == "html"
    assert (
        by_id["kurashiki-administrative-evaluation-2025"]["evidence_role"]
        == "progress_governance"
    )
    assert by_id["kurashiki-budget-2026"]["evidence_role"] == "budget"
    assert by_id["kurashiki-settlement-2024"]["evidence_role"] == "settlement"


def test_kurashiki_fiscal_records_match_budget_and_settlement_sources():
    records = load(REVIEWED / "fiscal_records.json")
    assert len(records) == 3
    for record in records:
        assert record["confidence"] == "high"
        assert record["review_status"] == "reviewed"
        assert record["value_status"] == "available"
        assert record["value"] is None

    budget = next(record for record in records if record["fiscal_year"] == 2026)
    assert budget["id"] == "jp-local-332020-fiscal-2026-total-expenditure"
    assert budget["amount_yen"] == 222_767_966_000
    assert budget["metric"] == "total_expenditure"
    assert budget["metric_label"] == "一般会計当初予算総額"
    assert budget["stage"] == "initial_budget"
    assert budget["sources"] == ["kurashiki-budget-2026"]

    text = json.dumps(records, ensure_ascii=False)
    # Bill 議案第26号 was passed as proposed (原案可決) on 2026-03-18 and
    # the amount stays at the published thousand-yen precision.
    assert "議案第26号" in text
    assert "原案可決" in text
    assert "令和8年3月18日" in text
    assert "222,767,966千円" in text
    assert "修正可決" not in text

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
    assert revenue["amount_yen"] == 232_345_729_550
    assert expenditure["amount_yen"] == 225_142_008_893
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 7_203_720_657
    assert revenue["stage"] == "settlement"
    assert expenditure["stage"] == "settlement"
    assert revenue["sources"] == ["kurashiki-settlement-2024"]
    assert expenditure["sources"] == ["kurashiki-settlement-2024"]
    # The FY2024 settlement was certified (議案第135号) on 2025-09-24, not
    # rejected; the real balance is kept at the published yen precision,
    # and the soundness-ratio opinion's differently based figure is noted.
    assert "議案第135号" in text
    assert "2025年9月24日" in text
    assert "5,803,653,066円" in text
    assert "5,807,097千円" in text
    assert "不認定" not in text


def test_kurashiki_evidence_packets_confirm_fiscal_claims():
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
        "jp-local-332020-fiscal-2026-total-expenditure",
        "jp-local-332020-fiscal-2024-total-revenue",
        "jp-local-332020-fiscal-2024-total-expenditure",
    }

    text = json.dumps(packets, ensure_ascii=False)
    assert "議案第26号" in text
    assert "議案第135号" in text
    assert "レビュー済みレコード" in text
    assert "人間による確認待ちステージング" not in text
    assert "不認定" not in text


def test_kurashiki_plan_review_accepts_seventh_plan_and_keeps_linkage_open():
    plan_review = load(REVIEWED / "plan_review.json")
    assert plan_review["id"] == "phase15-kurashiki-plan-review"
    assert plan_review["review_status"] == "reviewed"
    assert plan_review["reviewed_at"] == "2026-11-16"
    assert plan_review["next_action"]
    assert plan_review["quality_boundary"]

    by_id = {record["id"]: record for record in plan_review["records"]}
    assert by_id["kurashiki-current-plan-period"]["decision"] == "accepted"
    assert "倉敷市第七次総合計画" in by_id["kurashiki-current-plan-period"][
        "statement"
    ]
    assert "2030年度" in by_id["kurashiki-current-plan-period"]["statement"]
    assert by_id["kurashiki-current-policy-structure"]["decision"] == "accepted"
    assert "44のめざすまちの姿" in by_id["kurashiki-current-policy-structure"][
        "statement"
    ]
    assert by_id["kurashiki-progress-governance-framework"]["decision"] == (
        "accepted"
    )
    assert "行政評価" in by_id["kurashiki-progress-governance-framework"][
        "statement"
    ]
    assert by_id["kurashiki-plan-transition"]["decision"] == "accepted"
    assert "2021年度に開始した" in by_id["kurashiki-plan-transition"]["statement"]
    linkage = by_id["kurashiki-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["fiscal_year"] == 2024
    assert "版は現行と同一" in linkage["statement"]


def test_kurashiki_policy_structure_keeps_44_fields_and_empty_measures():
    structure = load(ROOT / "data/catalog/kurashiki_current_policy_structure.json")
    assert structure["id"] == "kurashiki-current-policy-structure"
    assert structure["review_status"] == "reviewed"
    assert structure["source_id"] == "kurashiki-seventh-plan"
    assert structure["counts"] == {"basic_goals": 44, "basic_plan_measures": 0}

    plan = structure["current_plan"]
    assert plan["title"] == (
        "倉敷市第七次総合計画 基本構想・基本計画（2021年度～2030年度）"
    )
    assert plan["start_fiscal_year"] == 2021
    assert plan["end_fiscal_year"] == 2030
    assert plan["period_status"] == "verified_fixed_period"
    assert plan["vision"] == (
        "豊かな自然と紡がれた歴史・文化を次代へ繋ぎ "
        "人と人との絆と慈しみの心で地域を結ぶまち倉敷"
    )
    assert len(plan["policy_fields"]) == 44
    assert plan["policy_fields"][0]["name_ja"] == (
        "子ども・子育て・教育：1-1 だれもがその人らしさ（個性）を尊重され、"
        "幸せに暮らしていくことができている"
    )
    assert plan["policy_fields"][-1]["name_ja"] == (
        "SDGs・市民協働・コミュニティ・行財政：5-7 持続可能な地域をめざすSDGsの理念を、"
        "だれもが理解し、行動している"
    )
    assert all(field["measures"] == [] for field in plan["policy_fields"])
    principles = " ".join(plan["management_principles"])
    assert "実施計画" in principles
    assert "行政評価" in principles
    assert "verified_fixed_period" in principles


def test_kurashiki_progress_review_keeps_pdca_framework():
    progress = load(
        ROOT / "data/catalog/kurashiki_current_progress_review_summary.json"
    )
    assert progress["id"] == "kurashiki-current-progress-review-summary"
    assert progress["review_status"] == "reviewed_with_explicit_deferred_depth"
    assert progress["reviewed_at"] == "2026-11-16"

    framework = progress["current_implementation_plan"]
    assert "実施計画" in framework["title"]
    assert "基本構想・基本計画期間（2021年度～2030年度）" in framework["period"]
    assert "行政評価" in framework["rolling_structure"]
    assert framework["current_period_item_actuals"]["status"] == (
        "not_promoted_in_v1"
    )

    assert progress["evaluation_evidence"]["status"] == "not_promoted_in_v1"
    linkage = progress["fiscal_linkage"]
    assert linkage["fiscal_year"] == 2024
    assert linkage["status"] == "not_assessable"
    assert "版は現行と同一" in linkage["boundary"]
    assert "議案第135号・2025年9月24日認定" in linkage["boundary"]


def test_kurashiki_finance_sources_are_reviewed():
    finance = load(ROOT / "data/catalog/kurashiki_city_finance_sources.json")
    assert finance["version"] == "0.1.0"
    assert finance["updated_at"] == "2026-11-16"
    assert finance["scope"] == "phase15-core-capital-review"

    by_id = {record["id"]: record for record in finance["records"]}
    assert set(by_id) == {
        "kurashiki-city-home",
        "kurashiki-budget-2026",
        "kurashiki-settlement-2024",
    }
    for record in finance["records"]:
        assert record["municipality_key"] == "kurashiki-city"
        assert record["source_kind"] == "document"
        assert record["availability"] == "published"
        assert record["review_status"] == "reviewed"
        assert record["confidence"] == "high"
        assert record["url"].startswith("https://www.city.kurashiki.okayama.jp/")


def test_kurashiki_completion_marks_every_gate_and_defers_depth():
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
    assert "議案第135号" in boundary
    assert "5,803,653,066円" in boundary
    assert "verified_fixed_period" in boundary
    assert "不認定" not in boundary


def test_kurashiki_review_records_delegation_not_owner_review():
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
    assert "議案第26号" in note
    assert "議案第135号" in note

    serialized = json.dumps(load(COMPLETION), ensure_ascii=False)
    assert "委任" in serialized
    assert "所有者本人が一次資料を直接レビューしたものではない" in serialized
    assert "不認定" not in serialized
