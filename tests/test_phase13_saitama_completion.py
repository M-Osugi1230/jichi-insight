from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/saitama_phase13_completion.json"
SCHEMA = ROOT / "schemas/saitama_phase13_completion.schema.json"
QUEUE = ROOT / "data/catalog/phase13_designated_city_review_queue.json"
MANIFEST = ROOT / "data/catalog/saitama_phase13_policy_review_manifest.json"
PROJECTS = ROOT / "data/catalog/saitama_current_project_universe_registry.json"
TARGET_EVIDENCE = ROOT / "data/evidence/saitama_current_project_target_identities_chapter52_evidence.json"
PLAN = ROOT / "data/reviewed/saitama-city/plan_review.json"
FISCAL = ROOT / "data/reviewed/saitama-city/fiscal_records.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_saitama_completion_contract_matches_schema_and_declared_paths_exist():
    completion = load(COMPLETION)
    validator = Draft202012Validator(load(SCHEMA), format_checker=FormatChecker())
    assert list(validator.iter_errors(completion)) == []

    package = completion["review_package"]
    for key, value in package.items():
        if key.endswith("_path"):
            assert (ROOT / value).is_file(), (key, value)


def test_saitama_completion_counts_are_derived_from_reviewed_layers():
    completion = load(COMPLETION)
    counts = completion["review_package"]["counts"]
    manifest = load(MANIFEST)
    project_fact = next(
        row for row in manifest["reviewed_facts"]
        if row["id"] == "saitama-current-project-identity-universe"
    )
    outcome_fact = next(
        row for row in manifest["reviewed_facts"]
        if row["id"] == "saitama-current-outcome-identity-universe"
    )
    projects = load(PROJECTS)
    target_evidence = load(TARGET_EVIDENCE)
    fiscal = load(FISCAL)

    assert (
        counts["current_project_identities"]
        == projects["project_universe"]["current_project_code_count"]
        == 258
    )
    assert (
        counts["current_target_identities"]
        == project_fact["total_target_indicator_count"]
        == 531
    )
    assert counts["policy_field_target_identities"] == 451
    assert counts["quality_city_management_target_identities"] == 80
    assert target_evidence["all_current_projects_completion"] == {
        "project_count": 258,
        "target_indicator_identity_count": 531,
        "target_identity_status": "complete",
    }
    assert (
        counts["target_value_projects_reviewed"]
        == project_fact["target_value_projects_reviewed"]
        == 12
    )
    assert (
        counts["target_value_records_reviewed"]
        == project_fact["reviewed_target_value_record_count"]
        == 22
    )
    assert (
        counts["target_value_projects_deferred"]
        == project_fact["target_value_projects_remaining"]
        == 246
    )
    assert counts["target_value_identities_deferred"] == 531 - 22 == 509
    assert counts["current_outcome_indicators"] == outcome_fact["value"] == 97
    assert (
        counts["outcome_self_report_or_perception_lane"]
        == outcome_fact["self_report_or_perception_count"]
        == 62
    )
    assert (
        counts["outcome_objective_or_administrative_lane"]
        == outcome_fact["objective_or_administrative_statistical_count"]
        == 35
    )
    assert counts["fiscal_top_line_records"] == len(fiscal) == 3


def test_saitama_completion_preserves_historical_cycle_and_priority_kpi_boundaries():
    completion = load(COMPLETION)
    counts = completion["review_package"]["counts"]
    projects = load(PROJECTS)
    plan = {row["id"]: row for row in load(PLAN)["records"]}
    historical = plan["saitama-2024-progress-review-universe"]
    kpis = plan["saitama-2024-priority-strategy-kpi-aggregate"]

    assert counts["historical_displayed_project_occurrences"] == historical["value"] == 370
    assert counts["historical_unique_projects"] == historical["unique_project_count"] == 299
    assert counts["historical_measures"] == historical["measure_count"] == 63
    assert counts["priority_strategy_kpis"] == kpis["value"] == 40
    assert (
        counts["priority_strategy_above_baseline"]
        == kpis["source_reported_breakdown"]["above_baseline"]
        == 26
    )
    assert (
        counts["priority_strategy_flat"]
        == kpis["source_reported_breakdown"]["flat_to_baseline"]
        == 2
    )
    assert (
        counts["priority_strategy_below_baseline"]
        == kpis["source_reported_breakdown"]["below_baseline"]
        == 11
    )
    assert (
        counts["priority_strategy_actual_unavailable"]
        == kpis["source_reported_breakdown"]["actual_unavailable"]
        == 1
    )
    assert projects["historical_boundary"]["linkage_status"] == "not_reviewed"
    assert "同一視しない" in projects["historical_boundary"]["rule"]


def test_saitama_completion_deferred_depth_is_explicit_and_not_promoted():
    completion = load(COMPLETION)
    deferred = {item["id"]: item for item in completion["deferred_depth"]}

    assert deferred["current-target-values-beyond-chapter01"]["count"] == 509
    assert deferred["current-target-values-beyond-chapter01"]["project_count"] == 246
    assert deferred["outcome-exact-source-method-provenance"]["count"] == 97
    assert deferred["historical-current-versioned-project-linkage"]["count"] == 299
    assert all(
        item["status"] == "deferred_not_required_for_v1_completion"
        for item in deferred.values()
    )
    boundary = completion["completion_boundary"]
    assert "509" in boundary
    assert "97" in boundary
    assert "299" in boundary
    assert "政策達成度" in boundary
    assert "因果効果" in boundary
    assert "他都市比較可能性" in boundary


def test_saitama_completion_advances_queue_to_chiba():
    completion = load(COMPLETION)
    queue = load(QUEUE)
    by_code = {row["official_code"]: row for row in queue["execution_queue"]}
    statuses = [row["status"] for row in queue["execution_queue"]]

    assert completion["status"] == "reviewed_complete"
    assert by_code["011002"]["status"] == "reviewed_complete"
    assert by_code["041009"]["status"] == "reviewed_complete"
    assert by_code["111007"]["status"] == "reviewed_complete"
    assert by_code["121002"]["status"] == "review_in_progress"
    assert (
        queue["summary"]["reviewed_complete_count"]
        == statuses.count("reviewed_complete")
        == 3
    )
    assert (
        queue["summary"]["review_in_progress_count"]
        == statuses.count("review_in_progress")
        == 1
    )
    assert (
        queue["summary"]["pending_record_review_count"]
        == statuses.count("pending_record_review")
        == 14
    )
    assert queue["summary"]["next_official_code"] == "121002"


def test_saitama_completion_quality_gates_are_all_explicitly_true():
    completion = load(COMPLETION)
    assert completion["quality_gate"]
    assert all(value is True for value in completion["quality_gate"].values())
    assert completion["completion_depth"] == "declared_review_package_v1"
