from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/morioka_phase15_completion.json"
COMPLETION_SCHEMA = ROOT / "schemas/phase15_municipality_completion.schema.json"
SOURCE_CATALOG = ROOT / "data/catalog/morioka_phase15_sources.json"
SOURCE_CATALOG_SCHEMA = ROOT / "schemas/phase15_source_catalog.schema.json"
PLAN_REVIEW = ROOT / "data/reviewed/morioka-city/plan_review.json"
PLAN_REVIEW_SCHEMA = ROOT / "schemas/phase15_plan_review.schema.json"
STRUCTURE = ROOT / "data/catalog/morioka_current_policy_structure.json"
PROGRESS = ROOT / "data/catalog/morioka_current_progress_review_summary.json"
FISCAL = ROOT / "data/reviewed/morioka-city/fiscal_records.json"
EVIDENCE = ROOT / "data/reviewed/morioka-city/evidence_packets.json"
MUNICIPALITY = ROOT / "data/reviewed/morioka-city/municipality.json"
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


def test_morioka_completion_contract_validates():
    completion = load(COMPLETION)

    assert validate(COMPLETION_SCHEMA, completion) == []
    assert completion["phase"] == 15
    assert completion["status"] == "reviewed_complete"
    assert completion["official_code"] == "032018"
    assert completion["name_ja"] == "盛岡市"


def test_morioka_common_source_and_plan_review_schemas_validate():
    sources = load(SOURCE_CATALOG)
    plan_review = load(PLAN_REVIEW)

    assert validate(SOURCE_CATALOG_SCHEMA, sources) == []
    assert validate(PLAN_REVIEW_SCHEMA, plan_review) == []
    assert sources["official_code"] == plan_review["official_code"] == "032018"
    assert sources["name_ja"] == plan_review["name_ja"] == "盛岡市"
    assert len(sources["sources"]) == 7
    assert len(plan_review["records"]) == 5
    assert all(row["evidence_location"] for row in sources["sources"])
    assert all(row["use_boundary"] for row in sources["sources"])
    assert all(row["decision"] == "accepted" for row in plan_review["records"])


def test_morioka_reviewed_municipality_validates():
    municipality = load(MUNICIPALITY)

    assert validate(MUNICIPALITY_SCHEMA, municipality) == []
    assert municipality["id"] == "jp-local-032018"
    assert municipality["municipality_type"] == "core_city"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2024, 2026]


def test_morioka_current_policy_structure_is_complete_at_v1_depth():
    structure = load(STRUCTURE)
    plan = structure["current_plan"]

    assert plan["start_fiscal_year"] == 2025
    assert plan["end_fiscal_year"] == 2034
    assert len(plan["basic_goals"]) == 4
    assert [len(goal["measures"]) for goal in plan["basic_goals"]] == [6, 6, 6, 7]
    assert sum(len(goal["measures"]) for goal in plan["basic_goals"]) == 25
    assert plan["municipality_management_principle_count"] == 5

    assert structure["implementation_layer"] == {
        "current_period": "2026年度～2028年度",
        "duration_years": 3,
        "revision_cycle": "毎年度ローリング方式",
        "previous_version": "2025年度～2027年度",
    }
    assert structure["counts"] == {
        "basic_goals": 4,
        "current_plan_measures": 25,
        "municipality_management_principles": 5,
    }


def test_morioka_current_progress_preserves_evaluation_and_survey_semantics():
    progress = load(PROGRESS)
    evaluation = progress["current_evaluation"]["future_creation_project_evaluation"]
    survey = progress["current_evaluation"]["citizen_survey"]

    assert progress["current_evaluation"]["fiscal_year"] == 2025
    assert evaluation["status"] == "official_evaluation_published"
    assert len(evaluation["design"]) == 4
    assert "source-reported evaluation" in evaluation["boundary"]

    assert survey["status"] == "official_result_published"
    assert survey["sample_size"] == 3000
    assert survey["responses"] == 1332
    assert survey["response_rate_percent"] == 44.40
    assert "主観指標" in survey["boundary"]

    assert progress["current_implementation"]["period"] == "2026年度～2028年度"
    assert progress["current_implementation"]["revision_cycle"] == "毎年度ローリング方式"
    assert "旧2015～2024" in progress["historical_fiscal_boundary"]


def test_morioka_fiscal_records_validate_and_preserve_plan_boundary():
    records = load(FISCAL)
    assert len(records) == 3

    for record in records:
        assert validate(FISCAL_SCHEMA, record) == []

    by_id = {record["id"]: record for record in records}

    budget = by_id["jp-local-032018-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 126_510_000_000
    assert "議会可決" in budget["metric_label"]

    revenue = by_id["jp-local-032018-fiscal-2024-total-revenue"]
    expenditure = by_id["jp-local-032018-fiscal-2024-total-expenditure"]
    assert revenue["amount_yen"] == 135_207_433_943
    assert expenditure["amount_yen"] == 132_975_741_966
    assert "旧2015～2024" in revenue["note"]
    assert "旧2015～2024" in expenditure["note"]


def test_morioka_evidence_packets_validate_and_match_fiscal_records():
    packets = load(EVIDENCE)
    fiscal_ids = {record["id"] for record in load(FISCAL)}

    assert len(packets) == 3
    for packet in packets:
        assert validate(EVIDENCE_SCHEMA, packet) == []
        assert packet["subject_id"] in fiscal_ids
        assert packet["review_status"] == "reviewed"
        assert all(claim["decision"] == "accepted" for claim in packet["claims"])
        assert all(claim["location_note"] for claim in packet["claims"])


def test_morioka_completion_quality_and_deferred_depth_are_explicit():
    completion = load(COMPLETION)

    assert all(completion["quality_gate"].values())
    assert completion["review_package"]["counts"] == {
        "basic_goals": 4,
        "current_plan_measures": 25,
        "municipality_management_principles": 5,
        "promoted_small_measure_indicator_rows": 0,
        "fiscal_top_line_records": 3,
    }

    deferred_ids = {row["id"] for row in completion["deferred_depth"]}
    assert "all-small-measure-indicators" in deferred_ids
    assert "future-creation-project-detail" in deferred_ids
    assert "implementation-project-version-detail" in deferred_ids
    assert "fiscal-detail-project-linkage" in deferred_ids

    boundary = completion["completion_boundary"]
    assert "FY2024決算は旧2015～2024総合計画期間" in boundary
    assert "Jichi Insight独自の政策達成度" in boundary
    assert "因果効果" in boundary
    assert "ranking" in boundary


def test_morioka_is_complete_and_akita_is_next():
    queue = load(QUEUE)
    by_code = {row["official_code"]: row for row in queue["execution_queue"]}

    assert by_code["032018"]["status"] == "reviewed_complete"
    assert by_code["032018"]["completion_path"] == (
        "data/catalog/morioka_phase15_completion.json"
    )
    assert by_code["052019"]["status"] == "review_in_progress"
    assert queue["summary"]["reviewed_complete_count"] == 5
    assert queue["summary"]["review_in_progress_count"] == 1
    assert queue["summary"]["pending_record_review_count"] == 61
    assert queue["summary"]["next_official_code"] == "052019"
