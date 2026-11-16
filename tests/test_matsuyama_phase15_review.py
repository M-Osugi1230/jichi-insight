from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/matsuyama_phase15_completion.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
REVIEWED = ROOT / "data/reviewed/matsuyama-city"
CANDIDATE = ROOT / "data/candidates/matsuyama-city/review_candidate.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_matsuyama_review_package_is_the_fifty_eighth_completion():
    completion = load(COMPLETION)
    assert completion == {
        "id": "matsuyama-phase15-completion",
        "phase": 15,
        "status": "reviewed_complete",
        "official_code": "382019",
        "name_ja": "松山市",
        "completed_at": "2026-11-17",
        "completion_depth": "declared_review_package_v1",
        "review_package": {
            "source_catalog_path": "data/catalog/matsuyama_phase15_sources.json",
            "plan_review_path": "data/reviewed/matsuyama-city/plan_review.json",
            "policy_structure_path": (
                "data/catalog/matsuyama_current_policy_structure.json"
            ),
            "progress_review_path": (
                "data/catalog/matsuyama_current_progress_review_summary.json"
            ),
            "fiscal_records_path": (
                "data/reviewed/matsuyama-city/fiscal_records.json"
            ),
            "fiscal_evidence_path": (
                "data/reviewed/matsuyama-city/evidence_packets.json"
            ),
            "counts": {
                "basic_goals": 11,
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
    assert queue["summary"]["reviewed_complete_count"] == 58
    assert queue["summary"]["pending_record_review_count"] == 9
    assert queue["summary"]["next_official_code"] == "392014"
    entry = next(
        row for row in queue["execution_queue"] if row["official_code"] == "382019"
    )
    assert entry["status"] == "reviewed_complete"
    assert (
        entry["completion_path"]
        == "data/catalog/matsuyama_phase15_completion.json"
    )


def test_matsuyama_municipality_and_sources_use_only_official_city_pages():
    municipality = load(REVIEWED / "municipality.json")
    assert municipality["id"] == "jp-local-382019"
    assert municipality["official_code"] == "382019"
    assert municipality["name_ja"] == "松山市"
    assert municipality["prefecture_name_ja"] == "愛媛県"
    assert municipality["municipality_type"] == "core_city"
    assert municipality["official_url"] == (
        "https://www.city.matsuyama.ehime.jp/"
    )
    assert municipality["fiscal_years"] == [2024, 2026]
    assert municipality["data_status"] == "reviewed"
    assert municipality["last_verified_at"] == "2026-11-17"
    assert municipality["sources"] == [
        "matsuyama-city-home",
        "matsuyama-budget-2026",
        "matsuyama-settlement-audit-2024",
    ]

    sources = load(ROOT / "data/catalog/matsuyama_phase15_sources.json")[
        "sources"
    ]
    assert len(sources) == 4
    for source in sources:
        assert source["official_url"].startswith(
            "https://www.city.matsuyama.ehime.jp/"
        )
        assert "verification_status" not in source


def test_matsuyama_sources_match_the_reviewed_package():
    catalog = load(ROOT / "data/catalog/matsuyama_phase15_sources.json")
    assert catalog["id"] == "matsuyama-phase15-sources"
    assert catalog["name_ja"] == "松山市"
    assert catalog["official_code"] == "382019"
    assert catalog["phase"] == 15
    assert catalog["reviewed_at"] == "2026-11-17"

    by_id = {source["id"]: source for source in catalog["sources"]}
    assert set(by_id) == {
        "matsuyama-seventh-plan",
        "matsuyama-citizen-survey",
        "matsuyama-budget-2026",
        "matsuyama-settlement-audit-2024",
    }
    assert by_id["matsuyama-seventh-plan"]["evidence_role"] == (
        "comprehensive_plan"
    )
    assert by_id["matsuyama-seventh-plan"]["format"] == "html"
    assert by_id["matsuyama-citizen-survey"]["evidence_role"] == (
        "progress_governance"
    )
    assert by_id["matsuyama-budget-2026"]["evidence_role"] == "budget"
    assert by_id["matsuyama-settlement-audit-2024"]["evidence_role"] == (
        "settlement"
    )


def test_matsuyama_fiscal_records_match_budget_and_settlement_sources():
    records = load(REVIEWED / "fiscal_records.json")
    assert len(records) == 3
    for record in records:
        assert record["confidence"] == "high"
        assert record["review_status"] == "reviewed"
        assert record["value_status"] == "available"
        assert record["value"] is None

    budget = next(record for record in records if record["fiscal_year"] == 2026)
    assert budget["id"] == "jp-local-382019-fiscal-2026-total-expenditure"
    assert budget["amount_yen"] == 235_160_000_000
    assert budget["metric"] == "total_expenditure"
    assert budget["metric_label"] == "一般会計当初予算総額"
    assert budget["stage"] == "initial_budget"
    assert budget["sources"] == ["matsuyama-budget-2026"]

    text = json.dumps(records, ensure_ascii=False)
    # Bill 議案第9号 was adopted as proposed (原案可決) on 2026-03-19
    # according to the council's official per-member vote table, and
    # the amount stays at the published thousand-yen precision. The
    # wording is never upgraded to an amended adoption.
    assert "議案第9号" in text
    assert "原案可決" in text
    assert "2026年3月19日" in text
    assert "235,160,000千円" in text
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
    assert revenue["amount_yen"] == 232_638_142_000
    assert expenditure["amount_yen"] == 228_347_195_000
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 4_290_947_000
    assert revenue["stage"] == "settlement"
    assert expenditure["stage"] == "settlement"
    assert revenue["sources"] == ["matsuyama-settlement-audit-2024"]
    assert expenditure["sources"] == ["matsuyama-settlement-audit-2024"]
    # The FY2024 settlement was certified (bill 認定第1号) on
    # 2025-11-28 after continued review, not rejected; the totals and
    # the real balance stay at the thousand-yen precision printed in
    # the audit opinion, and the Ehime Prefecture ordinary-account
    # aggregate figures are not used as general-account values.
    assert "認定第1号" in text
    assert "2025年11月28日" in text
    assert "2,603,854千円" in text
    assert "不認定" not in text
    assert "233,179,187" not in text
    assert "228,583,457" not in text


def test_matsuyama_evidence_packets_confirm_fiscal_claims():
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
        "jp-local-382019-fiscal-2026-total-expenditure",
        "jp-local-382019-fiscal-2024-total-revenue",
        "jp-local-382019-fiscal-2024-total-expenditure",
    }

    text = json.dumps(packets, ensure_ascii=False)
    assert "議案第9号" in text
    assert "認定第1号" in text
    assert "レビュー済みレコード" in text
    assert "人間による確認待ちステージング" not in text
    assert "修正可決" not in text
    assert "修正議決" not in text
    assert "不認定" not in text


def test_matsuyama_plan_review_accepts_plan_and_keeps_linkage_open():
    plan_review = load(REVIEWED / "plan_review.json")
    assert plan_review["id"] == "phase15-matsuyama-plan-review"
    assert plan_review["review_status"] == "reviewed"
    assert plan_review["reviewed_at"] == "2026-11-17"
    assert plan_review["next_action"]
    assert plan_review["quality_boundary"]

    by_id = {record["id"]: record for record in plan_review["records"]}
    assert by_id["matsuyama-current-plan-period"]["decision"] == "accepted"
    assert "第7次松山市総合計画" in by_id["matsuyama-current-plan-period"][
        "statement"
    ]
    assert "前期2025年度～2029年度" in by_id[
        "matsuyama-current-plan-period"
    ]["value"]
    assert by_id["matsuyama-current-policy-structure"]["decision"] == (
        "accepted"
    )
    assert "11の政策分野" in by_id["matsuyama-current-policy-structure"][
        "statement"
    ]
    assert "人、まち、仕事がつながる SETOUCHIの交流拠点まつやま" in by_id[
        "matsuyama-current-policy-structure"
    ]["statement"]
    assert by_id["matsuyama-progress-governance-framework"]["decision"] == (
        "accepted"
    )
    assert "市民意識調査" in by_id[
        "matsuyama-progress-governance-framework"
    ]["statement"]
    assert by_id["matsuyama-plan-transition"]["decision"] == "accepted"
    assert "第6次松山市総合計画" in by_id["matsuyama-plan-transition"][
        "statement"
    ]
    linkage = by_id["matsuyama-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["fiscal_year"] == 2024
    # FY2024 is a settlement of the final year of the previous (sixth)
    # plan and the plan version differs from the current plan, so the
    # linkage stays not_assessable.
    assert "対応付けは公式資料にない" in linkage["statement"]


def test_matsuyama_policy_structure_keeps_eleven_fields_and_empty_measures():
    structure = load(
        ROOT / "data/catalog/matsuyama_current_policy_structure.json"
    )
    assert structure["id"] == "matsuyama-current-policy-structure"
    assert structure["review_status"] == "reviewed"
    assert structure["source_id"] == "matsuyama-seventh-plan"
    assert structure["counts"] == {"basic_goals": 11, "basic_plan_measures": 0}

    plan = structure["current_plan"]
    assert plan["title"] == (
        "第7次松山市総合計画（基本構想2025年度～2034年度・基本計画 "
        "前期2025年度～2029年度／後期2030年度～2034年度・実施計画3年ローリング方式）"
    )
    assert plan["start_fiscal_year"] == 2025
    assert plan["end_fiscal_year"] == 2034
    assert plan["period_status"] == "verified_fixed_period"
    assert plan["vision"] == "人、まち、仕事がつながる SETOUCHIの交流拠点まつやま"
    assert len(plan["policy_fields"]) == 11
    assert plan["policy_fields"][0]["name_ja"] == (
        "こどもを輝く未来へつなぐ"
    )
    assert plan["policy_fields"][-1]["name_ja"] == "つなぐを支える"
    assert all(field["measures"] == [] for field in plan["policy_fields"])
    principles = " ".join(plan["management_principles"])
    assert "11の政策分野" in principles
    assert "32施策" in principles
    assert "verified_fixed_period" in principles


def test_matsuyama_progress_review_keeps_implementation_plan_framework():
    progress = load(
        ROOT / "data/catalog/matsuyama_current_progress_review_summary.json"
    )
    assert progress["id"] == "matsuyama-current-progress-review-summary"
    assert progress["review_status"] == "reviewed_with_explicit_deferred_depth"
    assert progress["reviewed_at"] == "2026-11-17"

    framework = progress["current_implementation_plan"]
    assert "実施計画" in framework["title"]
    assert "市民意識調査" in framework["title"]
    assert "第6次計画期間" in framework["period"]
    assert "市民意識調査" in framework["rolling_structure"]
    assert framework["current_period_item_actuals"]["status"] == (
        "not_promoted_in_v1"
    )

    assert progress["evaluation_evidence"]["status"] == "not_promoted_in_v1"
    linkage = progress["fiscal_linkage"]
    assert linkage["fiscal_year"] == 2024
    assert linkage["status"] == "not_assessable"
    assert "認定第1号" in linkage["boundary"]
    assert "not_assessable" in linkage["boundary"]


def test_matsuyama_finance_sources_are_reviewed():
    finance = load(ROOT / "data/catalog/matsuyama_city_finance_sources.json")
    assert finance["version"] == "0.1.0"
    assert finance["updated_at"] == "2026-11-17"
    assert finance["scope"] == "phase15-core-capital-review"

    by_id = {record["id"]: record for record in finance["records"]}
    assert set(by_id) == {
        "matsuyama-city-home",
        "matsuyama-budget-2026",
        "matsuyama-settlement-audit-2024",
    }
    for record in finance["records"]:
        assert record["municipality_key"] == "matsuyama-city"
        assert record["source_kind"] == "document"
        assert record["availability"] == "published"
        assert record["review_status"] == "reviewed"
        assert record["confidence"] == "high"
        assert record["url"].startswith(
            "https://www.city.matsuyama.ehime.jp/"
        )


def test_matsuyama_completion_marks_every_gate_and_defers_depth():
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
    assert "議案第9号" in boundary
    assert "認定第1号" in boundary
    assert "原案可決" in boundary
    assert "2,603,854千円" in boundary
    assert "verified_fixed_period" in boundary
    assert "不認定" not in boundary


def test_matsuyama_review_records_delegation_not_owner_review():
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
    assert "議案第9号" in note
    assert "認定第1号" in note

    serialized = json.dumps(load(COMPLETION), ensure_ascii=False)
    assert "委任" in serialized
    assert "所有者本人が一次資料を直接レビューしたものではない" in serialized
    assert "不認定" not in serialized
    assert "修正可決" not in serialized
