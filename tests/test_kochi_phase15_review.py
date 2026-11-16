from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/kochi_phase15_completion.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
REVIEWED = ROOT / "data/reviewed/kochi-city"
CANDIDATE = ROOT / "data/candidates/kochi-city/review_candidate.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_kochi_review_package_is_the_fifty_ninth_completion():
    completion = load(COMPLETION)
    assert completion == {
        "id": "kochi-phase15-completion",
        "phase": 15,
        "status": "reviewed_complete",
        "official_code": "392014",
        "name_ja": "高知市",
        "completed_at": "2026-11-17",
        "completion_depth": "declared_review_package_v1",
        "review_package": {
            "source_catalog_path": "data/catalog/kochi_phase15_sources.json",
            "plan_review_path": "data/reviewed/kochi-city/plan_review.json",
            "policy_structure_path": (
                "data/catalog/kochi_current_policy_structure.json"
            ),
            "progress_review_path": (
                "data/catalog/kochi_current_progress_review_summary.json"
            ),
            "fiscal_records_path": (
                "data/reviewed/kochi-city/fiscal_records.json"
            ),
            "fiscal_evidence_path": (
                "data/reviewed/kochi-city/evidence_packets.json"
            ),
            "counts": {
                "basic_goals": 6,
                "basic_plan_measures": 14,
                "promoted_implementation_item_actual_records": 0,
                "fiscal_top_line_records": 3,
            },
        },
        "quality_gate": completion["quality_gate"],
        "deferred_depth": completion["deferred_depth"],
        "completion_boundary": completion["completion_boundary"],
    }

    queue = load(QUEUE)
    assert queue["summary"]["reviewed_complete_count"] == 65
    assert queue["summary"]["pending_record_review_count"] == 2
    assert queue["summary"]["next_official_code"] == "462012"
    entry = next(
        row for row in queue["execution_queue"] if row["official_code"] == "392014"
    )
    assert entry["status"] == "reviewed_complete"
    assert entry["completion_path"] == "data/catalog/kochi_phase15_completion.json"


def test_kochi_municipality_and_sources_use_only_official_city_pages():
    municipality = load(REVIEWED / "municipality.json")
    assert municipality["id"] == "jp-local-392014"
    assert municipality["official_code"] == "392014"
    assert municipality["name_ja"] == "高知市"
    assert municipality["prefecture_name_ja"] == "高知県"
    assert municipality["municipality_type"] == "core_city"
    assert municipality["official_url"] == "https://www.city.kochi.kochi.jp/"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert municipality["data_status"] == "reviewed"
    assert municipality["last_verified_at"] == "2026-11-17"
    assert municipality["sources"] == [
        "kochi-city-home",
        "kochi-budget-2026",
        "kochi-settlement-2024",
    ]

    sources = load(ROOT / "data/catalog/kochi_phase15_sources.json")["sources"]
    assert len(sources) == 5
    for source in sources:
        assert source["official_url"].startswith(
            "https://www.city.kochi.kochi.jp/"
        )
        assert "verification_status" not in source


def test_kochi_sources_match_the_reviewed_package():
    catalog = load(ROOT / "data/catalog/kochi_phase15_sources.json")
    assert catalog["id"] == "kochi-phase15-sources"
    assert catalog["name_ja"] == "高知市"
    assert catalog["official_code"] == "392014"
    assert catalog["phase"] == 15
    assert catalog["reviewed_at"] == "2026-11-17"

    by_id = {source["id"]: source for source in catalog["sources"]}
    assert set(by_id) == {
        "kochi-latter-plan",
        "kochi-second-implementation",
        "kochi-next-plan-transition",
        "kochi-budget-2026",
        "kochi-settlement-2024",
    }
    assert by_id["kochi-latter-plan"]["evidence_role"] == "comprehensive_plan"
    assert by_id["kochi-latter-plan"]["format"] == "html"
    assert by_id["kochi-second-implementation"]["evidence_role"] == (
        "implementation_plan_and_progress"
    )
    assert by_id["kochi-next-plan-transition"]["evidence_role"] == (
        "plan_transition"
    )
    assert by_id["kochi-budget-2026"]["evidence_role"] == "budget"
    assert by_id["kochi-settlement-2024"]["evidence_role"] == "settlement"


def test_kochi_fiscal_records_match_budget_and_settlement_sources():
    records = load(REVIEWED / "fiscal_records.json")
    assert len(records) == 3
    for record in records:
        assert record["confidence"] == "high"
        assert record["review_status"] == "reviewed"
        assert record["value_status"] == "available"
        assert record["value"] is None

    budget = next(record for record in records if record["fiscal_year"] == 2026)
    assert budget["id"] == "jp-local-392014-fiscal-2026-total-expenditure"
    assert budget["amount_yen"] == 168_400_000_000
    assert budget["metric"] == "total_expenditure"
    assert budget["metric_label"] == "一般会計当初予算総額"
    assert budget["stage"] == "initial_budget"
    assert budget["sources"] == ["kochi-budget-2026"]

    text = json.dumps(records, ensure_ascii=False)
    # Bill 市第4号 was passed by majority (可決（多数）) according to
    # the council's official results for the 512th regular session,
    # and that wording is kept verbatim; the vote date 2026-03-26 is
    # as published on the finance division's FY2026 budget page. The
    # result is never upgraded to an adoption-as-proposed or an
    # amended adoption.
    assert "市第4号" in text
    assert "可決（多数）" in text
    assert "2026年3月26日" in text
    assert "168,400,000千円" in text
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
    assert revenue["amount_yen"] == 163_081_014_000
    assert expenditure["amount_yen"] == 161_832_607_000
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 1_248_407_000
    assert revenue["stage"] == "settlement"
    assert expenditure["stage"] == "settlement"
    assert revenue["sources"] == ["kochi-settlement-2024"]
    assert expenditure["sources"] == ["kochi-settlement-2024"]
    # The FY2024 settlement was certified unanimously (bill 市第165号,
    # 認定（全員）) at the 509th regular session, not rejected; its
    # vote date is not printed in the results document and stays
    # unidentified. The totals and the real balance stay at the
    # thousand-yen precision printed in the audit opinion (the real
    # balance keeps the printed value even though it differs by one
    # thousand yen from the plain thousand-yen subtraction), and
    # ordinary-account aggregate figures are not used as
    # general-account values.
    assert "市第165号" in text
    assert "認定（全員）" in text
    assert "544,453千円" in text
    assert "未特定のまま保持" in text
    assert "不認定" not in text


def test_kochi_evidence_packets_confirm_fiscal_claims():
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
        "jp-local-392014-fiscal-2026-total-expenditure",
        "jp-local-392014-fiscal-2024-total-revenue",
        "jp-local-392014-fiscal-2024-total-expenditure",
    }

    text = json.dumps(packets, ensure_ascii=False)
    assert "市第4号" in text
    assert "市第165号" in text
    assert "レビュー済みレコード" in text
    assert "人間による確認待ちステージング" not in text
    assert "原案可決" not in text
    assert "修正可決" not in text
    assert "修正議決" not in text
    assert "不認定" not in text


def test_kochi_plan_review_accepts_plan_and_keeps_linkage_open():
    plan_review = load(REVIEWED / "plan_review.json")
    assert plan_review["id"] == "phase15-kochi-plan-review"
    assert plan_review["review_status"] == "reviewed"
    assert plan_review["reviewed_at"] == "2026-11-17"
    assert plan_review["next_action"]
    assert plan_review["quality_boundary"]

    by_id = {record["id"]: record for record in plan_review["records"]}
    assert by_id["kochi-current-plan-period"]["decision"] == "accepted"
    assert "2011高知市総合計画" in by_id["kochi-current-plan-period"][
        "statement"
    ]
    assert "後期2021年度～2030年度" in by_id["kochi-current-plan-period"][
        "value"
    ]
    assert "transition_or_unresolved" in by_id["kochi-current-plan-period"][
        "statement"
    ]
    assert by_id["kochi-current-policy-structure"]["decision"] == "accepted"
    assert "6つの環" in by_id["kochi-current-policy-structure"]["statement"]
    assert "森・里・海と人の環" in by_id["kochi-current-policy-structure"][
        "statement"
    ]
    assert by_id["kochi-progress-governance-framework"]["decision"] == (
        "accepted"
    )
    assert "事務事業評価" in by_id["kochi-progress-governance-framework"][
        "statement"
    ]
    assert by_id["kochi-plan-transition"]["decision"] == "accepted"
    assert "高知市未来ビジョン（仮称）" in by_id["kochi-plan-transition"][
        "statement"
    ]
    assert "令和8年度末" in by_id["kochi-plan-transition"]["statement"]
    linkage = by_id["kochi-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["fiscal_year"] == 2024
    # FY2024 is a settlement within the current plan's second basic
    # plan period and the plan version is the same, but no official
    # total-level mapping exists, so the linkage stays not_assessable.
    assert "対応付けは公式資料にない" in linkage["statement"]


def test_kochi_policy_structure_keeps_six_rings_and_fourteen_policies():
    structure = load(ROOT / "data/catalog/kochi_current_policy_structure.json")
    assert structure["id"] == "kochi-current-policy-structure"
    assert structure["review_status"] == "reviewed"
    assert structure["source_id"] == "kochi-latter-plan"
    assert structure["counts"] == {"basic_goals": 6, "basic_plan_measures": 14}

    plan = structure["current_plan"]
    assert plan["title"] == (
        "2011高知市総合計画（基本構想2011年度～2030年度・基本計画 "
        "前期2011年度～2020年度／後期2021年度～2030年度・実施計画 概ね3年）"
    )
    assert plan["start_fiscal_year"] == 2011
    assert plan["end_fiscal_year"] == 2030
    assert plan["period_status"] == "transition_or_unresolved"
    assert plan["vision"] == "森・里・海と人の環 自由と創造の共生都市 高知"
    fields = plan["policy_fields"]
    assert [field["name_ja"] for field in fields] == [
        "共生の環",
        "安心の環",
        "育みの環",
        "地産の環",
        "まちの環",
        "自立の環",
    ]
    measures = [measure for field in fields for measure in field["measures"]]
    assert len(measures) == 14
    assert measures[0] == "政策1 豊かな自然に親しみ、自然と共生するまち"
    assert measures[-1] == "政策14 多様な交流や、新たな人の流れが生まれ、自立したまち"
    principles = " ".join(plan["management_principles"])
    assert "令和8年度末" in principles
    assert "事務事業評価" in principles
    assert "流用しない" in principles


def test_kochi_progress_review_keeps_implementation_plan_framework():
    progress = load(
        ROOT / "data/catalog/kochi_current_progress_review_summary.json"
    )
    assert progress["id"] == "kochi-current-progress-review-summary"
    assert progress["review_status"] == "reviewed_with_explicit_deferred_depth"
    assert progress["reviewed_at"] == "2026-11-17"

    framework = progress["current_implementation_plan"]
    assert "実施計画" in framework["title"]
    assert "事務事業評価" in framework["title"]
    assert "第2次実施計画期間内" in framework["period"]
    assert "PDCA" in framework["rolling_structure"]
    assert framework["current_period_item_actuals"]["status"] == (
        "not_promoted_in_v1"
    )

    assert progress["evaluation_evidence"]["status"] == "not_promoted_in_v1"
    linkage = progress["fiscal_linkage"]
    assert linkage["fiscal_year"] == 2024
    assert linkage["status"] == "not_assessable"
    assert "市第165号" in linkage["boundary"]
    assert "not_assessable" in linkage["boundary"]


def test_kochi_finance_sources_are_reviewed():
    finance = load(ROOT / "data/catalog/kochi_city_finance_sources.json")
    assert finance["version"] == "0.1.0"
    assert finance["updated_at"] == "2026-11-17"
    assert finance["scope"] == "phase15-core-capital-review"

    by_id = {record["id"]: record for record in finance["records"]}
    assert set(by_id) == {
        "kochi-city-home",
        "kochi-budget-2026",
        "kochi-settlement-2024",
    }
    for record in finance["records"]:
        assert record["municipality_key"] == "kochi-city"
        assert record["source_kind"] == "document"
        assert record["availability"] == "published"
        assert record["review_status"] == "reviewed"
        assert record["confidence"] == "high"
        assert record["url"].startswith("https://www.city.kochi.kochi.jp/")


def test_kochi_completion_marks_every_gate_and_defers_depth():
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
    assert "市第4号" in boundary
    assert "市第165号" in boundary
    assert "可決（多数）" in boundary
    assert "544,453千円" in boundary
    assert "transition_or_unresolved" in boundary
    assert "不認定" not in boundary


def test_kochi_review_records_delegation_not_owner_review():
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
    assert "市第4号" in note
    assert "市第165号" in note

    serialized = json.dumps(load(COMPLETION), ensure_ascii=False)
    assert "委任" in serialized
    assert "所有者本人が一次資料を直接レビューしたものではない" in serialized
    assert "不認定" not in serialized
    assert "修正可決" not in serialized
