from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/aomori_phase15_completion.json"
COMPLETION_SCHEMA = ROOT / "schemas/phase15_municipality_completion.schema.json"
SOURCE_CATALOG = ROOT / "data/catalog/aomori_phase15_sources.json"
SOURCE_CATALOG_SCHEMA = ROOT / "schemas/phase15_source_catalog.schema.json"
PLAN_REVIEW = ROOT / "data/reviewed/aomori-city/plan_review.json"
PLAN_REVIEW_SCHEMA = ROOT / "schemas/phase15_plan_review.schema.json"
STRUCTURE = ROOT / "data/catalog/aomori_current_policy_structure.json"
PROGRESS = ROOT / "data/catalog/aomori_current_progress_review_summary.json"
FISCAL = ROOT / "data/reviewed/aomori-city/fiscal_records.json"
EVIDENCE = ROOT / "data/reviewed/aomori-city/evidence_packets.json"
MUNICIPALITY = ROOT / "data/reviewed/aomori-city/municipality.json"
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


def test_aomori_completion_contract_validates():
    completion = load(COMPLETION)

    assert validate(COMPLETION_SCHEMA, completion) == []
    assert completion["phase"] == 15
    assert completion["status"] == "reviewed_complete"
    assert completion["official_code"] == "022012"
    assert completion["name_ja"] == "青森市"


def test_aomori_reviewed_municipality_validates():
    municipality = load(MUNICIPALITY)

    assert validate(MUNICIPALITY_SCHEMA, municipality) == []
    assert municipality["id"] == "jp-local-022012"
    assert municipality["municipality_type"] == "core_city"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2024, 2026]


def test_aomori_common_source_and_plan_review_schemas_validate():
    source_catalog = load(SOURCE_CATALOG)
    plan_review = load(PLAN_REVIEW)

    assert validate(SOURCE_CATALOG_SCHEMA, source_catalog) == []
    assert validate(PLAN_REVIEW_SCHEMA, plan_review) == []
    assert source_catalog["official_code"] == plan_review["official_code"] == "022012"
    assert source_catalog["name_ja"] == plan_review["name_ja"] == "青森市"
    assert len(source_catalog["sources"]) == 8
    assert len(plan_review["records"]) == 4

    assert all(
        source["official_url"].startswith("https://www.city.aomori.aomori.jp/")
        for source in source_catalog["sources"]
    )
    assert all(source["evidence_location"] for source in source_catalog["sources"])
    assert all(source["use_boundary"] for source in source_catalog["sources"])
    assert all(record["decision"] == "accepted" for record in plan_review["records"])
    assert all(record["evidence_location"] for record in plan_review["records"])


def test_aomori_current_policy_structure_matches_declared_depth():
    structure = load(STRUCTURE)
    plan = structure["current_plan"]
    counts = structure["counts"]

    assert plan["start_fiscal_year"] == 2024
    assert plan["end_fiscal_year"] == 2028
    assert plan["adopted_on"] == "2024-09-27"
    assert counts == {
        "policy_pillars": 3,
        "current_plan_policies": 17,
        "policy_realization_directions": 5,
    }
    assert len(plan["policy_pillars"]) == 3
    assert [len(pillar["policies"]) for pillar in plan["policy_pillars"]] == [5, 6, 6]
    assert sum(len(pillar["policies"]) for pillar in plan["policy_pillars"]) == 17
    assert len(plan["policy_realization_directions"]) == 5


def test_aomori_fy2024_progress_keeps_city_evaluation_attributed():
    progress = load(PROGRESS)
    current = progress["current_plan_results"]

    assert current["fiscal_year"] == 2024
    assert current["status"] == "official_result_package_published"
    assert current["promoted_indicator_actual_records"] == 0
    assert current["reporting_structure"] == {
        "target_indicator_rows": True,
        "annual_target_values": True,
        "annual_actual_values": True,
        "source_reported_evaluation_classes": True,
        "major_project_results": True,
        "project_settlement_amounts": True,
    }
    classes = current["source_reported_evaluation_semantics"]
    assert set(classes) == {"A", "B", "C", "D"}
    assert "独自" in progress["quality_boundary"]
    assert "ランキング" in progress["quality_boundary"]


def test_aomori_fiscal_records_validate_and_keep_exact_states():
    records = load(FISCAL)
    assert len(records) == 3

    for record in records:
        assert validate(FISCAL_SCHEMA, record) == []

    by_id = {record["id"]: record for record in records}

    budget = by_id["jp-local-022012-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 133_510_000_000
    assert "原案可決" in budget["metric_label"]

    revenue = by_id["jp-local-022012-fiscal-2024-total-revenue"]
    expenditure = by_id["jp-local-022012-fiscal-2024-total-expenditure"]
    assert revenue["stage"] == expenditure["stage"] == "settlement"
    assert revenue["amount_yen"] == 142_517_400_928
    assert expenditure["amount_yen"] == 138_679_303_495


def test_aomori_evidence_packets_validate_and_match_fiscal_records():
    packets = load(EVIDENCE)
    fiscal_ids = {record["id"] for record in load(FISCAL)}

    assert len(packets) == 3
    for packet in packets:
        assert validate(EVIDENCE_SCHEMA, packet) == []
        assert packet["subject_id"] in fiscal_ids
        assert packet["review_status"] == "reviewed"
        assert all(claim["decision"] == "accepted" for claim in packet["claims"])
        assert all(claim["location_note"] for claim in packet["claims"])


def test_aomori_completion_quality_gate_and_deferred_depth_are_explicit():
    completion = load(COMPLETION)

    assert all(completion["quality_gate"].values())
    assert completion["review_package"]["counts"] == {
        "policy_pillars": 3,
        "current_plan_policies": 17,
        "policy_realization_directions": 5,
        "promoted_indicator_actual_records": 0,
        "fiscal_top_line_records": 3,
    }

    deferred_ids = {row["id"] for row in completion["deferred_depth"]}
    assert "current-plan-measure-indicator-detail" in deferred_ids
    assert "fy2024-major-project-detail" in deferred_ids
    assert "fiscal-detail-project-linkage" in deferred_ids
    assert "policy-outcome-causal-and-cross-city-comparability" in deferred_ids

    boundary = completion["completion_boundary"]
    assert "A/B/C/D" in boundary
    assert "Jichi Insight独自の政策達成度" in boundary
    assert "因果効果" in boundary
    assert "ランキング" in boundary


def test_aomori_is_complete_and_hachinohe_is_next():
    queue = load(QUEUE)
    by_code = {row["official_code"]: row for row in queue["execution_queue"]}

    assert by_code["012025"]["status"] == "reviewed_complete"
    assert by_code["012041"]["status"] == "reviewed_complete"
    assert by_code["022012"]["status"] == "reviewed_complete"
    assert by_code["022012"]["completion_path"] == (
        "data/catalog/aomori_phase15_completion.json"
    )
    assert by_code["022039"]["status"] == "review_in_progress"
    assert queue["summary"]["reviewed_complete_count"] == 3
    assert queue["summary"]["review_in_progress_count"] == 1
    assert queue["summary"]["pending_record_review_count"] == 63
    assert queue["summary"]["next_official_code"] == "022039"
