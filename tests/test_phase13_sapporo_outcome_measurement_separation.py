from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/catalog/sapporo_outcome_indicator_measurement_registry.json"
OUTCOMES = ROOT / "data/catalog/sapporo_outcome_indicator_registry.json"
VALUES = ROOT / "data/catalog/sapporo_outcome_indicator_2025_report_values.json"
EVIDENCE = ROOT / "data/evidence/sapporo_outcome_indicator_measurement_registry_evidence.json"
READINESS = ROOT / "data/catalog/sapporo_phase13_completion_readiness.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_all_26_outcomes_have_exactly_one_measurement_classification():
    registry = load(REGISTRY)
    outcomes = load(OUTCOMES)
    records = registry["records"]

    assert registry["status"] == (
        "measurement_family_review_complete_source_provenance_partial"
    )
    assert len(records) == registry["summary"]["classified_indicator_count"] == 26
    assert registry["summary"]["unique_indicator_count"] == 26
    assert [record["sequence"] for record in records] == list(range(1, 27))
    assert len({record["id"] for record in records}) == 26
    assert {record["id"] for record in records} == {
        record["id"] for record in outcomes["records"]
    }


def test_measurement_lanes_partition_26_without_overlap():
    registry = load(REGISTRY)
    records = registry["records"]
    lanes = Counter(record["measurement_lane"] for record in records)

    assert lanes == {"self_report": 14, "objective": 12}
    assert registry["summary"]["self_report_lane_count"] == 14
    assert registry["summary"]["objective_lane_count"] == 12
    assert sum(lanes.values()) == 26


def test_measurement_family_counts_are_exact():
    registry = load(REGISTRY)
    family_counts = Counter(record["measurement_family"] for record in registry["records"])

    assert family_counts == {
        "official_statistic": 4,
        "administrative_count_or_inventory": 2,
        "derived_official_statistic": 4,
        "tourism_activity_statistic": 1,
        "visitor_survey_derived_estimate": 1,
        "citizen_self_report_survey": 11,
        "target_group_self_report_survey": 3,
    }
    assert dict(family_counts) == registry["summary"]["measurement_family_counts"]


def test_clear_perception_and_behavior_indicators_never_enter_objective_lane():
    records = {record["id"]: record for record in load(REGISTRY)["records"]}
    self_report_ids = {
        "parent_support_access",
        "childcare_service_access",
        "children_with_personal_goals",
        "perceived_barrier_free_progress",
        "understanding_elderly_disabled",
        "lifelong_learning_participation",
        "perceived_digitalization_progress",
        "citizens_feeling_social_role",
        "citizen_machizukuri_participation",
        "citizens_prepared_for_disasters",
        "citizens_doing_sports",
        "culture_arts_participation",
        "daily_walking_minutes",
        "waste_resource_collection_satisfaction",
    }

    assert all(records[indicator_id]["measurement_lane"] == "self_report" for indicator_id in self_report_ids)
    assert all(
        "not" in records[indicator_id]["comparison_boundary"].lower()
        or "self-report" in records[indicator_id]["comparison_boundary"].lower()
        or "self-reported" in records[indicator_id]["comparison_boundary"].lower()
        for indicator_id in self_report_ids
    )


def test_objective_indicators_never_enter_self_report_lane():
    records = {record["id"]: record for record in load(REGISTRY)["records"]}
    objective_ids = {
        "total_fertility_rate",
        "young_adult_outmigration_excess",
        "healthy_life_expectancy",
        "single_operator_snow_removal_machines",
        "gdp_per_capita_nominal",
        "winter_tourist_count",
        "total_tourism_consumption",
        "employment_rate",
        "citywide_ghg_emissions",
        "municipal_facility_ghg_emissions",
        "central_city_effective_far",
        "regional_hub_effective_far",
    }

    assert all(records[indicator_id]["measurement_lane"] == "objective" for indicator_id in objective_ids)


def test_tourism_consumption_is_preserved_as_survey_derived_estimate_not_admin_total():
    records = {record["id"]: record for record in load(REGISTRY)["records"]}
    tourism = records["total_tourism_consumption"]

    assert tourism["measurement_family"] == "visitor_survey_derived_estimate"
    assert tourism["respondent_population"] == "tourists"
    assert tourism["source_instrument_status"] == "exact_instrument_verified"
    assert "アンケート" in tourism["instrument_reference"]
    assert "not a direct administrative revenue total" in tourism["comparison_boundary"]


def test_walking_is_kept_as_self_report_health_behavior():
    records = {record["id"]: record for record in load(REGISTRY)["records"]}
    walking = records["daily_walking_minutes"]

    assert walking["measurement_lane"] == "self_report"
    assert walking["measurement_family"] == "citizen_self_report_survey"
    assert walking["measurement_character"] == "health_behavior_self_report"
    assert walking["source_instrument_status"] == "exact_instrument_verified"
    assert "健康づくり" in walking["instrument_reference"]
    assert "device-measured" in walking["comparison_boundary"]


def test_provenance_gaps_are_explicit_instead_of_guessed():
    registry = load(REGISTRY)
    records = registry["records"]
    statuses = Counter(record["source_instrument_status"] for record in records)

    assert registry["summary"]["exact_instrument_verified_count"] == 4
    assert registry["summary"]["family_verified_exact_instrument_pending_count"] == 11
    assert statuses["exact_instrument_verified"] == 4
    assert statuses["family_verified_exact_instrument_pending"] == 11
    assert statuses["objective_source_family_reviewed"] == 11


def test_measurement_separation_does_not_change_official_values_or_trends():
    registry = load(REGISTRY)
    values = load(VALUES)

    assert len(registry["records"]) == values["summary"]["reviewed_indicator_count"] == 26
    assert values["summary"]["source_reported_up_count"] == 17
    assert values["summary"]["source_reported_down_count"] == 8
    assert values["summary"]["source_reported_unaggregated_count"] == 1
    assert "Existing source-reported trend arrows and numerical values are not changed" in registry["quality_boundary"]


def test_evidence_groups_partition_same_26_ids():
    registry_ids = {record["id"] for record in load(REGISTRY)["records"]}
    evidence = load(EVIDENCE)
    groups = evidence["evidence_groups"]
    grouped_ids = [indicator_id for group in groups for indicator_id in group["project_registry_ids"]]

    assert len(groups) == 2
    assert sum(group["record_count"] for group in groups) == 26
    assert len(grouped_ids) == 26
    assert len(set(grouped_ids)) == 26
    assert set(grouped_ids) == registry_ids


def test_citizen_survey_separation_gate_is_complete_while_target_gate_remains_open():
    readiness = load(READINESS)
    citizen_gate = next(
        gate for gate in readiness["blocking_gates"] if gate["id"] == "citizen-survey-separation"
    )
    target_gate = next(
        gate for gate in readiness["blocking_gates"] if gate["id"] == "principal-project-target-records"
    )

    assert citizen_gate["state"] == "complete_measurement_lane_separation"
    assert citizen_gate["required_scope"] == 26
    assert citizen_gate["reviewed_scope"] == 26
    assert citizen_gate["remaining_scope"] == 0
    assert citizen_gate["exact_instrument_verified_count"] == 4
    assert citizen_gate["family_verified_exact_instrument_pending_count"] == 11

    assert target_gate["reviewed_scope"] == 8
    assert target_gate["remaining_scope"] == 395
    assert readiness["current_status"] == "review_in_progress"
