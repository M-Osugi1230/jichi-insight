from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/sapporo_phase13_completion.json"
SCHEMA = ROOT / "schemas/sapporo_phase13_completion.schema.json"
QUEUE = ROOT / "data/catalog/phase13_designated_city_review_queue.json"
PROJECT_INDEX = ROOT / "data/catalog/sapporo_action_plan_project_source_index.json"
OUTCOMES = ROOT / "data/catalog/sapporo_outcome_indicator_registry.json"
MEASUREMENTS = ROOT / "data/catalog/sapporo_outcome_indicator_measurement_registry.json"
TARGET_UNIVERSE = ROOT / "data/catalog/sapporo_principal_project_target_universe_registry.json"
TARGET_REVIEW = ROOT / "data/catalog/sapporo_principal_project_target_2025_review_batch1.json"
PUBLICATION_AUDIT = ROOT / (
    "data/catalog/sapporo_principal_project_target_publication_boundary_audit.json"
)
FISCAL = ROOT / "data/reviewed/sapporo-city/fiscal_records.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sapporo_completion_contract_matches_schema_and_declared_paths_exist():
    completion = load(COMPLETION)
    validator = Draft202012Validator(load(SCHEMA), format_checker=FormatChecker())
    assert list(validator.iter_errors(completion)) == []

    package = completion["review_package"]
    for key, value in package.items():
        if key.endswith("_path"):
            assert (ROOT / value).is_file(), (key, value)


def test_sapporo_completion_counts_are_derived_from_reviewed_layers():
    completion = load(COMPLETION)
    counts = completion["review_package"]["counts"]
    project_index = load(PROJECT_INDEX)
    outcomes = load(OUTCOMES)
    measurements = load(MEASUREMENTS)
    universe = load(TARGET_UNIVERSE)
    target_review = load(TARGET_REVIEW)
    fiscal = load(FISCAL)

    fields = project_index["machizukuri_field_sources"]
    assert (
        counts["action_plan_project_identities"]
        == project_index["plan_level_aggregate"]["planned_project_count"]
        == 599
    )
    assert (
        counts["action_plan_main_projects"]
        == sum(row["reviewed_main_project_record_count"] for row in fields)
        == 406
    )
    assert (
        counts["action_plan_other_projects"]
        == sum(row["reviewed_other_project_record_count"] for row in fields)
        == 193
    )
    assert counts["outcome_indicators"] == len(outcomes["records"]) == 26
    assert (
        counts["outcome_objective_or_administrative_lane"]
        == measurements["summary"]["objective_lane_count"]
        == 12
    )
    assert (
        counts["outcome_self_report_lane"]
        == measurements["summary"]["self_report_lane_count"]
        == 14
    )
    assert (
        counts["principal_project_target_universe"]
        == universe["structural_reconciliation"]["principal_project_target_count"]
        == 403
    )
    assert (
        counts["current_individual_target_statuses_reviewed"]
        == target_review["summary"]["individual_target_records_reviewed"]
        == 8
    )
    assert (
        counts[
            "current_individual_target_statuses_deferred_at_central_publication_boundary"
        ]
        == target_review["summary"]["individual_target_records_remaining"]
        == 395
    )
    assert counts["fiscal_top_line_records"] == len(fiscal) == 3


def test_publication_boundary_preserves_exact_403_partition_without_distributing_labels():
    completion = load(COMPLETION)
    audit = load(PUBLICATION_AUDIT)
    review = load(TARGET_REVIEW)
    official = review["official_target_universe"]
    publication_depth = audit["current_2025_publication_depth"]

    assert official["principal_project_target_count"] == 403
    assert official["already_achieved_count"] == 38
    assert official["achievement_expected_count"] == 356
    assert official["achievement_difficult_expected_count"] == 9
    assert 38 + 356 + 9 == 403
    assert len(review["reviewed_individual_target_records"]) == 8
    assert publication_depth["named_individual_status_count"] == 8
    assert publication_depth["unnamed_current_status_count"] == 395
    assert (
        publication_depth[
            "complete_identity_level_status_table_in_central_progress_publication"
        ]
        is False
    )
    assert audit["completion_decision"]["remaining_required_for_v1_completion_count"] == 0
    assert audit["completion_decision"]["deferred_identity_status_count"] == 395
    assert (
        completion["publication_boundary"][
            "aggregate_partition_must_not_be_distributed_to_unnamed_projects"
        ]
        is True
    )


def test_sapporo_completion_deferred_depth_is_not_misrepresented_as_reviewed_403_statuses():
    completion = load(COMPLETION)
    deferred = {item["id"]: item for item in completion["deferred_depth"]}
    target_deferred = deferred[
        "principal-project-target-current-statuses-beyond-central-publication"
    ]

    assert target_deferred["status"] == "deferred_not_required_for_v1_completion"
    assert target_deferred["count"] == 395
    assert (
        completion["review_package"]["counts"][
            "current_individual_target_statuses_reviewed"
        ]
        == 8
    )
    assert "395件" in completion["completion_boundary"]
    assert "38/356/9" in completion["completion_boundary"]
    assert "全公開データ" in completion["completion_boundary"]
    assert "政策達成度" in completion["completion_boundary"]
    assert "因果効果" in completion["completion_boundary"]
    assert "他都市比較可能性" in completion["completion_boundary"]


def test_sapporo_completion_and_queue_are_consistent_and_advance_to_saitama():
    completion = load(COMPLETION)
    queue = load(QUEUE)
    by_code = {row["official_code"]: row for row in queue["execution_queue"]}
    statuses = [row["status"] for row in queue["execution_queue"]]

    assert completion["status"] == "reviewed_complete"
    assert by_code["011002"]["status"] == "reviewed_complete"
    assert by_code["041009"]["status"] == "reviewed_complete"
    assert by_code["111007"]["status"] == "pending_record_review"
    assert queue["summary"]["reviewed_complete_count"] == statuses.count(
        "reviewed_complete"
    ) == 2
    assert queue["summary"]["review_in_progress_count"] == statuses.count(
        "review_in_progress"
    ) == 0
    assert queue["summary"]["next_official_code"] == "111007"


def test_sapporo_completion_quality_gates_are_all_explicitly_true():
    completion = load(COMPLETION)
    assert completion["quality_gate"]
    assert all(value is True for value in completion["quality_gate"].values())
    assert completion["completion_depth"] == "declared_review_package_v1"
