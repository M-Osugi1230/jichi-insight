from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/takasaki_phase15_completion.json"
COMPLETION_SCHEMA = ROOT / "schemas/phase15_municipality_completion.schema.json"
SOURCE_CATALOG = ROOT / "data/catalog/takasaki_phase15_sources.json"
SOURCE_CATALOG_SCHEMA = ROOT / "schemas/phase15_source_catalog.schema.json"
PLAN_REVIEW = ROOT / "data/reviewed/takasaki-city/plan_review.json"
PLAN_REVIEW_SCHEMA = ROOT / "schemas/phase15_plan_review.schema.json"
STRUCTURE = ROOT / "data/catalog/takasaki_current_policy_structure.json"
PROGRESS = ROOT / "data/catalog/takasaki_current_progress_review_summary.json"
FISCAL = ROOT / "data/reviewed/takasaki-city/fiscal_records.json"
EVIDENCE = ROOT / "data/reviewed/takasaki-city/evidence_packets.json"
MUNICIPALITY = ROOT / "data/reviewed/takasaki-city/municipality.json"
CANDIDATE = ROOT / "data/candidates/takasaki-city/review_candidate.json"
FISCAL_SCHEMA = ROOT / "schemas/fiscal_record.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"
MUNICIPALITY_SCHEMA = ROOT / "schemas/municipality.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_path: Path, instance):
    validator = Draft202012Validator(
        load(schema_path), format_checker=FormatChecker()
    )
    return list(validator.iter_errors(instance))


def test_takasaki_completion_contract_validates():
    completion = load(COMPLETION)

    assert validate(COMPLETION_SCHEMA, completion) == []
    assert completion["phase"] == 15
    assert completion["status"] == "reviewed_complete"
    assert completion["official_code"] == "102024"
    assert completion["name_ja"] == "高崎市"
    assert completion["completed_at"] == "2026-11-15"


def test_takasaki_completion_paths_exist():
    completion = load(COMPLETION)
    for key, value in completion["review_package"].items():
        if key == "counts":
            continue
        assert (ROOT / value).is_file(), (key, value)


def test_takasaki_reviewed_municipality_validates():
    municipality = load(MUNICIPALITY)

    assert validate(MUNICIPALITY_SCHEMA, municipality) == []
    assert municipality["id"] == "jp-local-102024"
    assert municipality["municipality_type"] == "core_city"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert municipality["last_verified_at"] == "2026-11-15"


def test_takasaki_common_source_and_plan_review_schemas_validate():
    source_catalog = load(SOURCE_CATALOG)
    plan_review = load(PLAN_REVIEW)

    assert validate(SOURCE_CATALOG_SCHEMA, source_catalog) == []
    assert validate(PLAN_REVIEW_SCHEMA, plan_review) == []
    assert source_catalog["official_code"] == plan_review["official_code"] == "102024"
    assert source_catalog["name_ja"] == plan_review["name_ja"] == "高崎市"
    assert len(source_catalog["sources"]) == 6
    assert len(plan_review["records"]) == 5
    assert plan_review["review_status"] == "reviewed"
    assert plan_review["reviewed_at"] == "2026-11-15"

    assert all(
        source["official_url"].startswith("https://www.city.takasaki.gunma.jp/")
        for source in source_catalog["sources"]
    )
    assert all(source["evidence_location"] for source in source_catalog["sources"])
    assert all(source["use_boundary"] for source in source_catalog["sources"])

    decisions = {record["id"]: record["decision"] for record in plan_review["records"]}
    assert decisions == {
        "takasaki-current-plan-period": "accepted",
        "takasaki-current-policy-structure": "accepted",
        "takasaki-implementation-plan-layer": "accepted",
        "takasaki-progress-management-framework": "accepted",
        "takasaki-fy2024-settlement-linkage": "not_assessable",
    }
    assert all(record["evidence_location"] for record in plan_review["records"])
    assert all(
        record["source_url"].startswith("https://www.city.takasaki.gunma.jp/")
        for record in plan_review["records"]
    )


def test_takasaki_current_policy_structure_matches_declared_depth():
    structure = load(STRUCTURE)
    plan = structure["current_plan"]
    counts = structure["counts"]

    assert plan["title"] == "高崎市第6次総合計画"
    assert plan["start_fiscal_year"] == 2018
    assert plan["end_fiscal_year"] == 2027
    assert counts == {"plan_sections": 3, "major_policy_fields": 4}
    # The plan is a three-section structure; it must not be mapped onto
    # a generic basic-concept/basic-plan/implementation-plan model.
    assert "当てはめない" in plan["structure"]
    assert len(plan["components"]) == 3

    fields = plan["major_policy_fields"]
    assert fields["names_enumerated_in_v1"] is True
    assert fields["names"] == ["総務教育", "保健福祉", "市民経済", "建設水道"]
    assert structure["review_status"] == "reviewed"


def test_takasaki_progress_keeps_evaluation_and_linkage_explicit():
    progress = load(PROGRESS)

    current = progress["current_implementation_plan"]
    assert "指定事業" in current["title"]
    assert current["current_period_item_actuals"]["status"] == "not_promoted_in_v1"

    evaluation = progress["evaluation_evidence"]
    assert evaluation["status"] == "not_promoted_in_v1"
    assert "進行管理" in evaluation["boundary"]

    linkage = progress["fiscal_linkage"]
    assert linkage["fiscal_year"] == 2024
    assert linkage["status"] == "not_assessable"
    assert "7年目" in linkage["boundary"]

    assert progress["review_status"] == "reviewed_with_explicit_deferred_depth"


def test_takasaki_fiscal_records_validate_and_keep_exact_states():
    records = load(FISCAL)
    assert len(records) == 3

    for record in records:
        assert validate(FISCAL_SCHEMA, record) == []
        assert record["review_status"] == "reviewed"
        assert record["confidence"] == "high"

    by_id = {record["id"]: record for record in records}

    budget = by_id["jp-local-102024-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 175_220_000_000
    assert "可決" in budget["metric_label"]
    assert budget["sources"] == [
        "takasaki-budget-2026",
        "takasaki-budget-2026-enactment",
    ]

    revenue = by_id["jp-local-102024-fiscal-2024-total-revenue"]
    expenditure = by_id["jp-local-102024-fiscal-2024-total-expenditure"]
    assert revenue["stage"] == expenditure["stage"] == "settlement"
    # Thousand-yen precision from the comprehensive audit report; the
    # candidate's man-yen-rounded values are not used.
    assert revenue["amount_yen"] == 183_362_219_000
    assert expenditure["amount_yen"] == 177_037_888_000
    assert "普通会計" in revenue["note"]


def test_takasaki_evidence_packets_validate_and_match_fiscal_records():
    packets = load(EVIDENCE)
    fiscal_ids = {record["id"] for record in load(FISCAL)}

    assert len(packets) == 3
    for packet in packets:
        assert validate(EVIDENCE_SCHEMA, packet) == []
        assert packet["subject_id"] in fiscal_ids
        assert packet["review_status"] == "reviewed"
        assert all(claim["decision"] == "accepted" for claim in packet["claims"])
        assert all(claim["location_note"] for claim in packet["claims"])

    revenue_packet = next(
        packet
        for packet in packets
        if packet["subject_id"] == "jp-local-102024-fiscal-2024-total-revenue"
    )
    assert revenue_packet["open_questions"] == []
    assert "検証値" in revenue_packet["claims"][0]["review_note"]


def test_takasaki_completion_quality_gate_and_deferred_depth_are_explicit():
    completion = load(COMPLETION)

    assert all(completion["quality_gate"].values())
    assert completion["quality_gate"]["budget_enactment_state_preserved"] is True
    assert completion["quality_gate"]["settlement_source_precision_preserved"] is True
    assert completion["review_package"]["counts"] == {
        "plan_sections": 3,
        "major_policy_fields": 4,
        "promoted_implementation_item_actual_records": 0,
        "fiscal_top_line_records": 3,
    }

    deferred_ids = {row["id"] for row in completion["deferred_depth"]}
    assert "current-plan-granular-kpi-and-project-linkage" in deferred_ids
    assert "current-plan-full-text-confirmation" in deferred_ids
    assert "settlement-yen-precision" in deferred_ids
    assert "current-plan-annual-progress-evidence" in deferred_ids
    assert "fiscal-detail-and-vote-date-precision" in deferred_ids
    assert "policy-outcome-causal-and-cross-city-comparability" in deferred_ids
    assert all(
        row["status"] == "deferred_not_required_for_v1_completion"
        for row in completion["deferred_depth"]
    )

    boundary = completion["completion_boundary"]
    assert "公開責任者" in boundary
    assert "2026-11-15" in boundary
    assert "not_assessable" in boundary
    assert "千円" in boundary
    assert "Jichi Insight独自の政策達成度" in boundary
    assert "ランキング" in boundary


def test_takasaki_candidate_approval_record_remains_pending_until_merge():
    candidate = load(CANDIDATE)

    # The owner's approval is given on the promotion PR; the approval
    # record is added to the candidate's human_review at merge time.
    assert candidate["human_review"]["required"] is True
    assert candidate["human_review"]["status"] == "pending"
    assert candidate["human_review"]["reviewed_at"] is None
    assert candidate["human_review"]["reviewer_note"] is None
    assert candidate["publication"]["eligible"] is False


def test_takasaki_and_previous_nine_are_reviewed_complete_and_iwaki_is_next():
    queue = load(QUEUE)
    by_code = {row["official_code"]: row for row in queue["execution_queue"]}

    takasaki = by_code["102024"]
    assert takasaki["status"] == "reviewed_complete"
    assert takasaki["completion_path"] == "data/catalog/takasaki_phase15_completion.json"
    assert (ROOT / takasaki["completion_path"]).is_file()

    for code in (
        "012025", "012041", "022012", "022039", "032018",
        "052019", "062014", "072010", "072036",
    ):
        assert by_code[code]["status"] == "reviewed_complete"

    assert queue["summary"]["reviewed_complete_count"] == 10
    assert queue["summary"]["review_in_progress_count"] == 0
    assert queue["summary"]["pending_record_review_count"] == 57
    assert queue["summary"]["next_official_code"] == "072044"
    assert by_code["072044"]["status"] == "pending_record_review"
