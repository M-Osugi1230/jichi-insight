from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "data/catalog/sapporo_principal_project_target_2025_review_batch1.json"
EVIDENCE = ROOT / "data/evidence/sapporo_principal_project_target_2025_review_batch1_evidence.json"
READINESS = ROOT / "data/catalog/sapporo_phase13_completion_readiness.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_official_403_target_partition_is_exact():
    batch = load(BATCH)
    universe = batch["official_target_universe"]

    assert universe["final_main_project_count"] == 406
    assert universe["main_projects_without_configured_target_count"] == 3
    assert universe["principal_project_target_count"] == 403
    assert universe["already_achieved_count"] == 38
    assert universe["achievement_expected_count"] == 356
    assert universe["achievement_difficult_expected_count"] == 9
    assert universe["official_expected_or_achieved_count"] == 394
    assert universe["official_expected_or_achieved_ratio_percent"] == 97.8
    assert 38 + 356 + 9 == 403
    assert 38 + 356 == 394


def test_field_aggregates_partition_all_403_targets():
    fields = load(BATCH)["field_aggregates"]

    assert len(fields) == 8
    assert sum(row["target_count"] for row in fields) == 403
    assert sum(row["already_achieved_count"] for row in fields) == 38
    assert sum(row["achievement_expected_count"] for row in fields) == 356
    assert sum(row["achievement_difficult_expected_count"] for row in fields) == 9
    assert [row["target_count"] for row in fields] == [73, 62, 27, 43, 60, 35, 47, 56]


def test_basic_goal_aggregates_partition_all_403_targets():
    goals = load(BATCH)["basic_goal_aggregates"]

    assert [row["goal"] for row in goals] == list(range(1, 21))
    assert sum(row["target_count"] for row in goals) == 403
    assert sum(row["already_achieved_count"] for row in goals) == 38
    assert sum(row["achievement_expected_count"] for row in goals) == 356
    assert sum(row["achievement_difficult_expected_count"] for row in goals) == 9


def test_batch1_reviews_exactly_eight_explicit_individual_examples():
    batch = load(BATCH)
    records = batch["reviewed_individual_target_records"]
    summary = batch["summary"]

    assert len(records) == 8
    assert len({record["project_id"] for record in records}) == 8
    assert Counter(record["official_status"] for record in records) == {
        "already_achieved": 4,
        "achievement_difficult_expected": 4,
    }
    assert summary["official_target_universe_count"] == 403
    assert summary["individual_target_records_reviewed"] == 8
    assert summary["individual_target_records_remaining"] == 395
    assert summary["individual_achievement_expected_examples"] == 0


def test_exact_eight_project_ids_are_locked_to_official_example_page():
    records = load(BATCH)["reviewed_individual_target_records"]

    assert {record["project_id"] for record in records} == {
        "single_parent_medical_expense_subsidy",
        "atsubetsu_athletics_stadium_conservation",
        "fire_response_capacity_strengthening",
        "chuo_ward_complex_government_building",
        "compulsory_education_school_related",
        "sapporo_ict_strategy_promotion",
        "former_sapporo_court_of_appeal_conservation_repair",
        "school_facility_longevity_repair",
    }
    assert all(record["source_page_index_0_based"] == 2 for record in records)


def test_batch1_preserves_representative_current_values_and_forecasts():
    records = {
        record["project_id"]: record
        for record in load(BATCH)["reviewed_individual_target_records"]
    }

    fire = records["fire_response_capacity_strengthening"]
    assert fire["baseline_2022"] == 12
    assert fire["actual_2024"] == 100
    assert fire["target"] == 100

    compulsory = records["compulsory_education_school_related"]
    assert compulsory["actual_2024"] == 0
    assert compulsory["forecast_2027"] == 3
    assert compulsory["target_2027"] == 4

    ict = records["sapporo_ict_strategy_promotion"]
    assert ict["actual_2024"] == 1
    assert ict["forecast_2027"] == 16
    assert ict["target_2027"] == 25

    longevity = records["school_facility_longevity_repair"]
    assert longevity["actual_2024"] == 9
    assert longevity["forecast_2027"] == 15
    assert longevity["target_2027"] == 22


def test_evidence_explicitly_blocks_aggregate_to_individual_inference():
    evidence = load(EVIDENCE)
    boundary = evidence["publication_boundary"]

    assert boundary["all_403_identity_level_statuses_published_in_this_pdf"] is False
    assert boundary["complete_aggregate_partition_published"] is True
    assert boundary["identity_level_examples_published"] == 8
    assert boundary["unresolved_identity_level_statuses_after_this_batch"] == 395
    assert "must never" not in boundary["rule"]
    assert "Do not assign" in boundary["rule"]


def test_readiness_completes_v1_at_publication_boundary_without_inventing_395_labels():
    readiness = load(READINESS)
    gate = next(
        item
        for item in readiness["blocking_gates"]
        if item["id"] == "principal-project-target-records"
    )
    layer = next(
        item
        for item in readiness["verified_reviewed_layers"]
        if item["layer"] == "principal_project_target_records"
    )

    assert gate["required_scope"] == 403
    assert gate["reviewed_scope"] == 8
    assert gate["remaining_scope"] == 395
    assert gate["remaining_scope_for_v1_completion"] == 0
    assert gate["state"] == "complete_to_central_publication_boundary_8_named_395_deferred"
    assert layer["state"] == "complete_to_central_publication_boundary"
    assert layer["reviewed_current_status_record_count"] == 8
    assert layer["unresolved_current_status_record_count"] == 395
    assert layer["remaining_required_for_v1_completion_count"] == 0
    assert readiness["current_status"] == "reviewed_complete"
