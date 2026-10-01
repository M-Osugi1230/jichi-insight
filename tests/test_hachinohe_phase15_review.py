from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/hachinohe_phase15_completion.json"
COMPLETION_SCHEMA = ROOT / "schemas/phase15_municipality_completion.schema.json"
SOURCE_CATALOG = ROOT / "data/catalog/hachinohe_phase15_sources.json"
SOURCE_CATALOG_SCHEMA = ROOT / "schemas/phase15_source_catalog.schema.json"
PLAN_REVIEW = ROOT / "data/reviewed/hachinohe-city/plan_review.json"
PLAN_REVIEW_SCHEMA = ROOT / "schemas/phase15_plan_review.schema.json"
STRUCTURE = ROOT / "data/catalog/hachinohe_current_policy_structure.json"
PROGRESS = ROOT / "data/catalog/hachinohe_current_progress_review_summary.json"
FISCAL = ROOT / "data/reviewed/hachinohe-city/fiscal_records.json"
EVIDENCE = ROOT / "data/reviewed/hachinohe-city/evidence_packets.json"
MUNICIPALITY = ROOT / "data/reviewed/hachinohe-city/municipality.json"
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


def test_hachinohe_completion_contract_validates():
    completion = load(COMPLETION)

    assert validate(COMPLETION_SCHEMA, completion) == []
    assert completion["phase"] == 15
    assert completion["status"] == "reviewed_complete"
    assert completion["official_code"] == "022039"
    assert completion["name_ja"] == "八戸市"


def test_hachinohe_common_source_and_plan_review_schemas_validate():
    source_catalog = load(SOURCE_CATALOG)
    plan_review = load(PLAN_REVIEW)

    assert validate(SOURCE_CATALOG_SCHEMA, source_catalog) == []
    assert validate(PLAN_REVIEW_SCHEMA, plan_review) == []
    assert source_catalog["official_code"] == plan_review["official_code"] == "022039"
    assert source_catalog["name_ja"] == plan_review["name_ja"] == "八戸市"
    assert len(source_catalog["sources"]) == 8
    assert len(plan_review["records"]) == 5
    assert all(source["evidence_location"] for source in source_catalog["sources"])
    assert all(source["use_boundary"] for source in source_catalog["sources"])
    assert all(record["decision"] == "accepted" for record in plan_review["records"])


def test_hachinohe_reviewed_municipality_validates():
    municipality = load(MUNICIPALITY)

    assert validate(MUNICIPALITY_SCHEMA, municipality) == []
    assert municipality["id"] == "jp-local-022039"
    assert municipality["municipality_type"] == "core_city"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2024, 2026]


def test_hachinohe_policy_structure_matches_declared_depth():
    structure = load(STRUCTURE)
    plan = structure["current_plan"]
    strategy = structure["fy2026_strategy"]
    projects = structure["fy2026_project_list"]
    counts = structure["counts"]

    assert plan["start_fiscal_year"] == 2022
    assert plan["end_fiscal_year"] == 2026
    assert plan["action_guideline_count"] == 3
    assert plan["current_measure_count"] == 55
    assert len(plan["policies"]) == 6
    assert [row["name_ja"] for row in plan["policies"]] == [
        "「ひと」を育む",
        "「経済」を回す",
        "「暮らし」を守る",
        "「ともに生きる社会」をつくる",
        "「まち」を形づくる",
        "「八戸らしさ」を活かす",
    ]

    assert strategy["fiscal_year"] == 2026
    assert len(strategy["strategies"]) == 9
    assert strategy["hierarchy"] == ["戦略", "プロジェクト", "重点事業"]

    assert projects["listed_projects"] == 780
    assert projects["unique_projects_excluding_reposts"] == 691
    assert projects["new_listed"] == 39
    assert projects["new_unique"] == 38
    assert projects["expanded_listed"] == 30
    assert projects["expanded_unique"] == 23
    assert projects["continuing_listed"] == 711
    assert projects["continuing_unique"] == 630

    assert counts == {
        "current_policies": 6,
        "current_measures": 55,
        "action_guidelines": 3,
        "fy2026_strategies": 9,
        "fy2026_listed_projects": 780,
        "fy2026_unique_projects": 691,
    }


def test_hachinohe_latest_completed_progress_and_transition_are_explicit():
    progress = load(PROGRESS)
    latest = progress["latest_completed_review"]
    current = progress["current_fy2026_governance"]
    successor = progress["successor_plan"]

    assert latest["review_fiscal_year"] == 2025
    assert latest["review_date"] == "2025-09-30"
    assert latest["actor"] == "八戸市総合計画等推進市民委員会"
    assert latest["scope"] == {
        "policies": 6,
        "measures": 55,
        "project_implementation_records": 616,
    }
    assert len(latest["evidence_inputs"]) == 4
    assert "独自" in latest["boundary"]

    assert current["status"] == "committee_in_progress"
    assert "FY2025意見書" in current["boundary"]

    assert successor["status"] == "draft_transition_not_adopted"
    assert successor["planned_start_fiscal_year"] == 2027
    assert successor["public_comment_closed_on"] == "2026-09-18"
    assert "採択済みcurrent plan" in successor["boundary"]


def test_hachinohe_fiscal_records_validate_and_preserve_source_precision():
    records = load(FISCAL)
    assert len(records) == 3

    for record in records:
        assert validate(FISCAL_SCHEMA, record) == []

    by_id = {record["id"]: record for record in records}

    budget = by_id["jp-local-022039-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 104_200_000_000
    assert "原案可決" in budget["metric_label"]

    revenue = by_id["jp-local-022039-fiscal-2024-total-revenue"]
    expenditure = by_id["jp-local-022039-fiscal-2024-total-expenditure"]
    assert revenue["stage"] == expenditure["stage"] == "settlement"
    assert revenue["amount_yen"] == 108_585_206_000
    assert expenditure["amount_yen"] == 105_245_944_000
    assert "千円" in revenue["metric_label"]
    assert "千円" in expenditure["metric_label"]
    assert "1,000円precision" in revenue["note"]
    assert "1,000円precision" in expenditure["note"]


def test_hachinohe_evidence_packets_validate_and_match_fiscal_records():
    packets = load(EVIDENCE)
    fiscal_ids = {record["id"] for record in load(FISCAL)}

    assert len(packets) == 3
    for packet in packets:
        assert validate(EVIDENCE_SCHEMA, packet) == []
        assert packet["subject_id"] in fiscal_ids
        assert packet["review_status"] == "reviewed"
        assert all(claim["decision"] == "accepted" for claim in packet["claims"])
        assert all(claim["location_note"] for claim in packet["claims"])

    settlement_packets = [
        packet for packet in packets
        if "2024-total-" in packet["subject_id"]
    ]
    assert len(settlement_packets) == 2
    assert all(
        "source precisionは千円" in packet["claims"][0]["review_note"]
        for packet in settlement_packets
    )


def test_hachinohe_completion_quality_and_deferred_depth_are_explicit():
    completion = load(COMPLETION)

    assert all(completion["quality_gate"].values())
    assert completion["review_package"]["counts"] == {
        "current_policies": 6,
        "current_measures": 55,
        "action_guidelines": 3,
        "fy2026_strategies": 9,
        "fy2026_listed_projects": 780,
        "fy2026_unique_projects": 691,
        "latest_completed_review_project_records": 616,
        "fiscal_top_line_records": 3,
    }

    deferred = {row["id"]: row for row in completion["deferred_depth"]}
    assert deferred["all-55-measure-identities-and-indicators"]["count"] == 55
    assert deferred["fy2026-project-list-detail"]["count"] == 691
    assert deferred["nine-strategy-project-detail"]["count"] == 9
    assert "successor-plan-adoption" in deferred
    assert "fiscal-project-linkage" in deferred

    boundary = completion["completion_boundary"]
    assert "source precision千円" in boundary
    assert "Jichi Insight独自の政策達成度" in boundary
    assert "因果効果" in boundary
    assert "ranking" in boundary


def test_hachinohe_is_complete_and_morioka_is_next():
    queue = load(QUEUE)
    by_code = {row["official_code"]: row for row in queue["execution_queue"]}

    assert by_code["022039"]["status"] == "reviewed_complete"
    assert by_code["022039"]["completion_path"] == (
        "data/catalog/hachinohe_phase15_completion.json"
    )
    assert by_code["032018"]["status"] == "review_in_progress"
    assert queue["summary"]["reviewed_complete_count"] == 4
    assert queue["summary"]["review_in_progress_count"] == 1
    assert queue["summary"]["pending_record_review_count"] == 62
    assert queue["summary"]["next_official_code"] == "032018"
