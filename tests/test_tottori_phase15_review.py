from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/tottori_phase15_completion.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
REVIEWED = ROOT / "data/reviewed/tottori-city"
CANDIDATE = ROOT / "data/candidates/tottori-city/review_candidate.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_tottori_review_package_is_the_forty_ninth_completion():
    completion = load(COMPLETION)
    assert completion == {
        "id": "tottori-phase15-completion",
        "phase": 15,
        "status": "reviewed_complete",
        "official_code": "312010",
        "name_ja": "鳥取市",
        "completed_at": "2026-11-16",
        "completion_depth": "declared_review_package_v1",
        "review_package": {
            "source_catalog_path": "data/catalog/tottori_phase15_sources.json",
            "plan_review_path": "data/reviewed/tottori-city/plan_review.json",
            "policy_structure_path": (
                "data/catalog/tottori_current_policy_structure.json"
            ),
            "progress_review_path": (
                "data/catalog/tottori_current_progress_review_summary.json"
            ),
            "fiscal_records_path": "data/reviewed/tottori-city/fiscal_records.json",
            "fiscal_evidence_path": (
                "data/reviewed/tottori-city/evidence_packets.json"
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
    assert queue["summary"]["reviewed_complete_count"] == 69
    assert queue["summary"]["pending_record_review_count"] == 0
    assert queue["summary"]["next_official_code"] is None
    entry = next(
        row for row in queue["execution_queue"] if row["official_code"] == "312010"
    )
    assert entry["status"] == "reviewed_complete"
    assert entry["completion_path"] == "data/catalog/tottori_phase15_completion.json"


def test_tottori_municipality_and_sources_use_only_official_city_pages():
    municipality = load(REVIEWED / "municipality.json")
    assert municipality["id"] == "jp-local-312010"
    assert municipality["official_code"] == "312010"
    assert municipality["name_ja"] == "鳥取市"
    assert municipality["prefecture_name_ja"] == "鳥取県"
    assert municipality["municipality_type"] == "core_city"
    assert municipality["official_url"] == "https://www.city.tottori.lg.jp/"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert municipality["data_status"] == "reviewed"
    assert municipality["last_verified_at"] == "2026-11-16"
    assert municipality["sources"] == [
        "tottori-city-home",
        "tottori-budget-2026",
        "tottori-settlement-2024",
    ]

    sources = load(ROOT / "data/catalog/tottori_phase15_sources.json")["sources"]
    assert len(sources) == 4
    for source in sources:
        assert source["official_url"].startswith("https://www.city.tottori.lg.jp/")
        assert "verification_status" not in source


def test_tottori_sources_match_the_reviewed_package():
    catalog = load(ROOT / "data/catalog/tottori_phase15_sources.json")
    assert catalog["id"] == "tottori-phase15-sources"
    assert catalog["name_ja"] == "鳥取市"
    assert catalog["official_code"] == "312010"
    assert catalog["phase"] == 15
    assert catalog["reviewed_at"] == "2026-11-16"

    by_id = {source["id"]: source for source in catalog["sources"]}
    assert set(by_id) == {
        "tottori-twelfth-plan",
        "tottori-action-plan-progress",
        "tottori-budget-2026",
        "tottori-settlement-2024",
    }
    assert by_id["tottori-twelfth-plan"]["evidence_role"] == "comprehensive_plan"
    assert by_id["tottori-twelfth-plan"]["format"] == "html"
    assert by_id["tottori-action-plan-progress"]["evidence_role"] == (
        "progress_governance"
    )
    assert by_id["tottori-budget-2026"]["evidence_role"] == "budget"
    assert by_id["tottori-settlement-2024"]["evidence_role"] == "settlement"


def test_tottori_fiscal_records_match_budget_and_settlement_sources():
    records = load(REVIEWED / "fiscal_records.json")
    assert len(records) == 3
    for record in records:
        assert record["confidence"] == "high"
        assert record["review_status"] == "reviewed"
        assert record["value_status"] == "available"
        assert record["value"] is None

    budget = next(record for record in records if record["fiscal_year"] == 2026)
    assert budget["id"] == "jp-local-312010-fiscal-2026-total-expenditure"
    assert budget["amount_yen"] == 108_700_000_000
    assert budget["metric"] == "total_expenditure"
    assert budget["metric_label"] == "一般会計当初予算総額"
    assert budget["stage"] == "initial_budget"
    assert budget["sources"] == ["tottori-budget-2026"]

    text = json.dumps(records, ensure_ascii=False)
    # Bill 議案第6号 was passed as proposed (原案可決) by majority on
    # 2026-03-19; the budget is a framework budget ahead of the mayoral
    # election and the amount stays at thousand-yen precision.
    assert "議案第6号" in text
    assert "原案可決" in text
    assert "2026年3月19日" in text
    assert "108,700,000千円" in text
    assert "骨格予算" in text
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
    assert revenue["amount_yen"] == 113_544_636_161
    assert expenditure["amount_yen"] == 111_377_983_188
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 2_166_652_973
    assert revenue["stage"] == "settlement"
    assert expenditure["stage"] == "settlement"
    assert revenue["sources"] == ["tottori-settlement-2024"]
    assert expenditure["sources"] == ["tottori-settlement-2024"]
    # The FY2024 settlement was certified (議案第106号) on 2025-10-06 per
    # the council meeting record, not rejected; the real balance stays
    # at the thousand-yen precision of the settlement statement.
    assert "議案第106号" in text
    assert "2025年10月6日" in text
    assert "会議録" in text
    assert "2,017,634千円" in text
    assert "不認定" not in text


def test_tottori_evidence_packets_confirm_fiscal_claims():
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
        "jp-local-312010-fiscal-2026-total-expenditure",
        "jp-local-312010-fiscal-2024-total-revenue",
        "jp-local-312010-fiscal-2024-total-expenditure",
    }

    text = json.dumps(packets, ensure_ascii=False)
    assert "議案第6号" in text
    assert "議案第106号" in text
    assert "会議録" in text
    assert "審議結果』PDFには議案第106号・第107号の行" in text
    assert "レビュー済みレコード" in text
    assert "人間による確認待ちステージング" not in text
    assert "不認定" not in text


def test_tottori_plan_review_accepts_twelfth_plan_and_keeps_linkage_open():
    plan_review = load(REVIEWED / "plan_review.json")
    assert plan_review["id"] == "phase15-tottori-plan-review"
    assert plan_review["review_status"] == "reviewed"
    assert plan_review["reviewed_at"] == "2026-11-16"
    assert plan_review["next_action"]
    assert plan_review["quality_boundary"]

    by_id = {record["id"]: record for record in plan_review["records"]}
    assert by_id["tottori-current-plan-period"]["decision"] == "accepted"
    assert "第12次鳥取市総合計画" in by_id["tottori-current-plan-period"][
        "statement"
    ]
    assert "2026年度～2035年度" in by_id["tottori-current-plan-period"][
        "statement"
    ]
    assert by_id["tottori-current-policy-structure"]["decision"] == "accepted"
    assert "11の政策" in by_id["tottori-current-policy-structure"]["statement"]
    assert by_id["tottori-progress-governance-framework"]["decision"] == (
        "accepted"
    )
    assert "地方創生アクションプラン" in by_id[
        "tottori-progress-governance-framework"
    ]["statement"]
    assert by_id["tottori-plan-transition"]["decision"] == "accepted"
    assert "第11次鳥取市総合計画" in by_id["tottori-plan-transition"]["statement"]
    linkage = by_id["tottori-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["fiscal_year"] == 2024
    assert "第11次" in linkage["statement"]


def test_tottori_policy_structure_keeps_11_fields_and_empty_measures():
    structure = load(ROOT / "data/catalog/tottori_current_policy_structure.json")
    assert structure["id"] == "tottori-current-policy-structure"
    assert structure["review_status"] == "reviewed"
    assert structure["source_id"] == "tottori-twelfth-plan"
    assert structure["counts"] == {"basic_goals": 11, "basic_plan_measures": 0}

    plan = structure["current_plan"]
    assert plan["title"] == "第12次鳥取市総合計画 基本計画（2026年度～2030年度）"
    assert plan["start_fiscal_year"] == 2026
    assert plan["end_fiscal_year"] == 2030
    assert plan["period_status"] == "verified_fixed_period"
    assert plan["vision"] == (
        "一人ひとりが自分の力を発揮でき、支え合いながら "
        "ともに豊かに暮らせる鳥取市〜オアシスとっとり〜"
    )
    assert len(plan["policy_fields"]) == 11
    assert plan["policy_fields"][0]["name_ja"] == (
        "まちづくりの目標1 未来を創る人材を育み、ひとりひとりが活躍するまち"
        "：政策1 こども"
    )
    assert plan["policy_fields"][-1]["name_ja"] == (
        "まちづくりの目標4 豊かな自然と調和して、安全・安心に暮らせるまち"
        "：政策2 環境"
    )
    assert all(field["measures"] == [] for field in plan["policy_fields"])
    principles = " ".join(plan["management_principles"])
    assert "実施計画" in principles
    assert "verified_fixed_period" in principles


def test_tottori_progress_review_keeps_annual_review_framework():
    progress = load(
        ROOT / "data/catalog/tottori_current_progress_review_summary.json"
    )
    assert progress["id"] == "tottori-current-progress-review-summary"
    assert progress["review_status"] == "reviewed_with_explicit_deferred_depth"
    assert progress["reviewed_at"] == "2026-11-16"

    framework = progress["current_implementation_plan"]
    assert "実施計画" in framework["title"]
    assert "実施計画（2026年度～2030年度）" in framework["period"]
    assert "毎年度見直す" in framework["rolling_structure"]
    assert framework["current_period_item_actuals"]["status"] == (
        "not_promoted_in_v1"
    )

    assert progress["evaluation_evidence"]["status"] == "not_promoted_in_v1"
    linkage = progress["fiscal_linkage"]
    assert linkage["fiscal_year"] == 2024
    assert linkage["status"] == "not_assessable"
    assert "第11次" in linkage["boundary"]
    assert "議案第106号・2025年10月6日認定" in linkage["boundary"]


def test_tottori_finance_sources_are_staged_only():
    finance = load(ROOT / "data/catalog/tottori_city_finance_sources.json")
    assert finance["version"] == "0.1.0"
    assert finance["updated_at"] == "2026-11-19"
    assert finance["scope"] == "phase15-core-capital-review"

    by_id = {record["id"]: record for record in finance["records"]}
    assert set(by_id) == {
        "tottori-city-home",
        "tottori-budget-2026",
        "tottori-settlement-2024",
        # Issue #691 fiscal-settlement expansion sources.
        "tottori-city-mic-settlement-card-fy2022",
        "tottori-city-mic-settlement-card-fy2023",
        "tottori-city-mic-settlement-card-fy2024",
        "tottori-city-fiscal-situation-collection-fy2022",
        "tottori-city-fiscal-situation-collection-fy2023",
        "tottori-city-fiscal-situation-collection-fy2024",
    }
    for record in finance["records"]:
        assert record["municipality_key"] == "tottori-city"
        assert record["source_kind"] == "document"
        assert record["availability"] == "published"
        assert record["review_status"] == "reviewed"
        assert record["confidence"] == "high"
        assert record["url"].startswith(
            ("https://www.city.tottori.lg.jp/", "https://www.soumu.go.jp/", "https://www.pref.tottori.lg.jp/")
        )


def test_tottori_completion_marks_every_gate_and_defers_depth():
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
    candidate_deferred = {item["id"]: item for item in candidate["deferred_depth"]}
    assert set(deferred) == set(candidate_deferred)
    for item_id, item in deferred.items():
        assert item["boundary"] == candidate_deferred[item_id]["boundary"]

    boundary = completion["completion_boundary"]
    assert "議案第106号" in boundary
    assert "2,017,634千円" in boundary
    assert "会議録" in boundary
    assert "verified_fixed_period" in boundary
    assert "不認定" not in boundary


def test_tottori_review_records_delegation_not_owner_review():
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
    assert "議案第106号" in note
    assert "会議録" in note

    serialized = json.dumps(load(COMPLETION), ensure_ascii=False)
    assert "委任" in serialized
    assert "所有者本人が一次資料を直接レビューしたものではない" in serialized
    assert "不認定" not in serialized
