from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/catalog/sapporo_action_plan_environment_project_candidates.json"
EVIDENCE = ROOT / "data/evidence/sapporo_action_plan_environment_project_candidates_evidence.json"
DENOMINATORS = ROOT / "data/catalog/sapporo_action_plan_final_field_denominators.json"
SOURCE_INDEX = ROOT / "data/catalog/sapporo_action_plan_project_source_index.json"
QUEUE_REGISTRY = ROOT / "data/catalog/sapporo_action_plan_candidate_queue_registry.json"
FINAL = ROOT / "data/catalog/sapporo_action_plan_environment_final_reconciliation.json"
FINAL_EVIDENCE = ROOT / "data/evidence/sapporo_action_plan_environment_final_evidence.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_environment_historical_candidate_inventory_has_exact_74_rows():
    catalog = load(CATALOG)
    records = catalog["records"]
    summary = catalog["summary"]
    assert len(records) == summary["candidate_record_count"] == 74
    assert summary["main_project_candidate_count"] == 47
    assert summary["other_project_candidate_count"] == 27
    assert summary["goal16_candidate_count"] == 48
    assert summary["goal17_candidate_count"] == 26
    assert [record["candidate_order"] for record in records] == list(range(1, 75))
    assert Counter(record["record_type"] for record in records) == {
        "main_project": 47,
        "other_project": 27,
    }


def test_environment_candidates_preserve_representative_cost_anchors():
    records = {record["id"]: record for record in load(CATALOG)["records"]}
    assert records["gx_investment_promotion"]["planned_project_cost_yen"] is None
    assert records["hydrogen_utilization_promotion"]["planned_project_cost_yen"] == 3_953_000_000
    assert records["school_lighting_led_conversion"]["planned_project_cost_yen"] == 9_387_000_000
    assert (
        records["komaoka_incineration_plant_renewal"]["planned_project_cost_yen"] == 46_197_000_000
    )
    assert records["community_park_redevelopment"]["planned_project_cost_yen"] == 6_890_000_000


def test_environment_historical_candidates_have_exact_one_to_one_evidence_order():
    catalog = load(CATALOG)
    evidence = load(EVIDENCE)
    packets = evidence["evidence_packets"]
    assert len(packets) == len(catalog["records"]) == 74
    assert [packet["candidate_order"] for packet in packets] == list(range(1, 75))
    assert len({packet["evidence_id"] for packet in packets}) == 74


def test_environment_final_review_promotes_all_74_rows_with_five_department_corrections():
    final = load(FINAL)
    evidence = load(FINAL_EVIDENCE)
    denominators = load(DENOMINATORS)
    environment_denominator = next(
        field for field in denominators["field_denominators"] if field["field_id"] == "environment"
    )

    assert environment_denominator["final_project_count"] == 74
    assert (
        final["status"] == "final_field_direct_visual_review_complete_with_department_corrections"
    )
    assert final["final_source"]["direct_visual_confirmation"] is True
    assert final["summary"]["reviewed_project_record_count"] == 74
    assert final["summary"]["main_project_record_count"] == 47
    assert final["summary"]["other_project_record_count"] == 27
    assert final["reconciliation"]["changed_identity_count"] == 0
    assert final["reconciliation"]["changed_cost_count"] == 0
    assert final["reconciliation"]["changed_department_count"] == 5
    assert evidence["document_boundary"]["department_corrections"] == 5


def test_environment_exact_final_department_corrections_are_locked():
    final = load(FINAL)
    corrections = {item["id"]: item for item in final["reconciliation"]["department_corrections"]}
    assert corrections["gx_investment_promotion"]["final_department_ja"] == "政)政策企画部"
    assert (
        corrections["yard_vehicle_electrification_study"]["final_department_ja"]
        == "経)中央卸売市場"
    )
    assert (
        corrections["combined_treatment_septic_tank_subsidy"]["final_department_ja"]
        == "環)環境事業部"
    )
    assert (
        corrections["water_facility_hydropower_installation"]["final_department_ja"] == "水)総務部"
    )
    assert (
        corrections["river_environment_improvement_for_life_and_nature"]["final_department_ja"]
        == "下)事業推進部"
    )
    assert {item["candidate_order"] for item in corrections.values()} == {1, 4, 8, 48, 74}


def test_environment_final_review_is_reflected_in_global_metadata():
    queue = load(QUEUE_REGISTRY)
    index = load(SOURCE_INDEX)
    environment = next(
        field for field in index["machizukuri_field_sources"] if field["field_id"] == "environment"
    )

    assert queue["candidate_fields"] == []
    assert queue["final_reviewed_identity_count"] == 599
    assert environment["reviewed_project_record_count"] == 74
    assert environment["reviewed_main_project_record_count"] == 47
    assert environment["reviewed_other_project_record_count"] == 27
    assert environment["final_department_correction_count"] == 5
    assert environment["unresolved_project_record_count"] == 0
    assert index["summary"]["individual_project_records_reviewed"] == 599
