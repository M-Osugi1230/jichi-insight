from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
REVIEWED = ROOT / "data/reviewed/niigata-city"
MUNICIPALITY = REVIEWED / "municipality.json"
PLAN = REVIEWED / "plan_review.json"
FISCAL = REVIEWED / "fiscal_records.json"
EVIDENCE = REVIEWED / "evidence_packets.json"
SOURCES = ROOT / "data/catalog/niigata_phase13_sources.json"
STRUCTURE = ROOT / "data/catalog/niigata_current_policy_structure.json"
PROGRESS = ROOT / "data/catalog/niigata_current_progress_review_summary.json"
MANIFEST = ROOT / "data/catalog/niigata_phase13_policy_review_manifest.json"
COMPLETION = ROOT / "data/catalog/niigata_phase13_completion.json"
COMPLETION_SCHEMA = ROOT / "schemas/niigata_phase13_completion.schema.json"
QUEUE = ROOT / "data/catalog/phase13_designated_city_review_queue.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_name: str, instance):
    schema = load(ROOT / "schemas" / schema_name)
    return list(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(
            instance
        )
    )


def test_niigata_shared_municipality_fiscal_and_evidence_contracts():
    municipality = load(MUNICIPALITY)
    fiscal = load(FISCAL)
    evidence = load(EVIDENCE)

    assert validate("municipality.schema.json", municipality) == []
    assert all(validate("fiscal_record.schema.json", row) == [] for row in fiscal)
    assert all(validate("evidence_packet.schema.json", row) == [] for row in evidence)
    assert municipality["official_code"] == "151009"
    assert municipality["name_ja"] == "新潟市"
    assert municipality["municipality_type"] == "designated_city"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert len(fiscal) == len(evidence) == 3
    assert {packet["subject_id"] for packet in evidence} == {
        row["id"] for row in fiscal
    }


def test_niigata_source_catalog_matches_municipality_sources():
    municipality = load(MUNICIPALITY)
    sources = load(SOURCES)["records"]

    assert len(sources) == 13
    assert set(municipality["sources"]) == {row["id"] for row in sources}
    assert {row["organization"] for row in sources} <= {"新潟市", "新潟市議会"}
    assert all(row["confidence"] == "high" for row in sources)


def test_niigata_current_policy_structure_is_complete_at_declared_level():
    structure = load(STRUCTURE)
    policies = [
        policy
        for field in structure["fields"]
        for policy in field["policies"]
    ]

    assert structure["review_status"] == (
        "reviewed_complete_declared_structure_identity"
    )
    assert structure["plan_period"] == "2023年度～2030年度"
    assert structure["implementation_plan_period"] == "2023年度～2026年度"
    assert structure["hierarchy"] == {
        "plan_layer_count": 3,
        "field_count": 8,
        "policy_count": 16,
        "measure_count": 45,
        "priority_strategy_count": 10,
        "sustainable_governance_pillar_count": 3,
        "overall_indicator_count": 4,
    }
    assert len(structure["fields"]) == 8
    assert len(policies) == 16
    assert len({row["policy_code"] for row in policies}) == 16
    assert len(structure["priority_strategies"]) == 10
    assert len(structure["sustainable_governance_pillars"]) == 3
    assert len(structure["overall_indicators"]) == 4
    assert "45施策個別identity" in structure["quality_boundary"]


def test_niigata_progress_preserves_source_reported_results_and_roles():
    progress = load(PROGRESS)
    results = {row["indicator_code"]: row for row in progress["overall_indicator_results"]}
    roles = {row["id"]: row for row in progress["accountability_roles"]}

    assert progress["reporting_year"] == 2025
    assert progress["plan_year_number"] == 3
    assert progress["indicator_universe"]["overall_indicator_count"] == 4
    assert progress["indicator_universe"]["policy_indicator_count"] == 87
    assert len(results) == 4

    assert results["overall-1"]["actual_value"] == "416人転入超過"
    assert results["overall-1"]["source_reported_evaluation"] == "A"
    assert results["overall-2"]["actual_value"] == 1.13
    assert results["overall-2"]["source_reported_evaluation"] == "C"
    assert results["overall-3"]["actual_value"] == 90.9
    assert results["overall-3"]["source_reported_evaluation"] == "A"
    assert results["overall-4"]["actual_value"] == 25.5
    assert results["overall-4"]["source_reported_evaluation"] == "B"

    assert roles["municipal_progress_reporting"]["role"] == (
        "source_reported_progress_evaluation"
    )
    assert roles["external_expert_review"]["role"] == (
        "external_opinion_and_effect_review"
    )
    assert roles["citizen_indicator_survey"]["role"] == (
        "citizen_perception_measurement"
    )
    assert "統合スコア" in progress["quality_boundary"]


def test_niigata_midterm_review_draft_is_not_promoted_to_current_plan():
    plan = load(PLAN)
    records = {row["id"]: row for row in plan["records"]}
    draft = records["niigata-midterm-review-draft-boundary"]

    assert draft["evidence_role"] == "plan_revision_draft"
    assert draft["value"] == "draft_not_adopted"
    assert draft["decision"] == "accepted_as_draft_boundary_only"
    assert "確定値へ自動昇格しない" in draft["review_note"]


def test_niigata_fiscal_top_lines_are_exact_and_state_separated():
    records = {row["id"]: row for row in load(FISCAL)}
    budget = records["jp-local-151009-fiscal-2026-total-revenue"]
    revenue = records["jp-local-151009-fiscal-2024-total-revenue"]
    expenditure = records["jp-local-151009-fiscal-2024-total-expenditure"]

    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 442_500_000_000
    assert revenue["stage"] == expenditure["stage"] == "settlement"
    assert revenue["amount_yen"] == 463_544_553_000
    assert expenditure["amount_yen"] == 452_133_373_000


def test_niigata_completion_contract_matches_schema_and_declared_paths_exist():
    completion = load(COMPLETION)
    validator = Draft202012Validator(
        load(COMPLETION_SCHEMA), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(completion)) == []

    for key, value in completion["review_package"].items():
        if key.endswith("_path"):
            assert (ROOT / value).is_file(), (key, value)


def test_niigata_completion_counts_derive_from_reviewed_layers():
    completion = load(COMPLETION)
    counts = completion["review_package"]["counts"]
    structure = load(STRUCTURE)
    progress = load(PROGRESS)
    fiscal = load(FISCAL)

    assert counts["current_fields"] == structure["hierarchy"]["field_count"] == 8
    assert counts["current_policies"] == structure["hierarchy"]["policy_count"] == 16
    assert counts["current_measures_aggregate"] == structure["hierarchy"][
        "measure_count"
    ] == 45
    assert counts["current_priority_strategies"] == structure["hierarchy"][
        "priority_strategy_count"
    ] == 10
    assert counts["current_sustainable_governance_pillars"] == structure[
        "hierarchy"
    ]["sustainable_governance_pillar_count"] == 3
    assert counts["current_overall_indicators"] == structure["hierarchy"][
        "overall_indicator_count"
    ] == 4
    assert counts["current_overall_indicator_results_reviewed"] == len(
        progress["overall_indicator_results"]
    ) == 4
    assert counts["current_policy_indicators_aggregate"] == progress[
        "indicator_universe"
    ]["policy_indicator_count"] == 87
    assert counts["accountability_role_count"] == len(
        progress["accountability_roles"]
    ) == 3
    assert counts["fiscal_top_line_records"] == len(fiscal) == 3


def test_niigata_completion_deferred_depth_is_explicit_and_conservative():
    completion = load(COMPLETION)
    deferred = {row["id"]: row for row in completion["deferred_depth"]}

    measures = deferred["current-measure-detail"]
    assert measures["count"] == 45
    assert "推測しない" in measures["boundary"]

    indicators = deferred["policy-indicator-detail"]
    assert indicators["count"] == 87
    assert "未抽出値を推測しない" in indicators["boundary"]

    draft = deferred["midterm-review-final-adoption"]
    assert "draft version" in draft["boundary"]
    assert "上書きしない" in draft["boundary"]

    second_plan = deferred["second-implementation-plan-version"]
    assert "2027～2030年度" in second_plan["boundary"]
    assert "自動延長しない" in second_plan["boundary"]

    assert all(
        row["status"] == "deferred_not_required_for_v1_completion"
        for row in deferred.values()
    )

    boundary = completion["completion_boundary"]
    for token in ("8", "16", "45", "10", "4", "87", "442,500,000,000"):
        assert token in boundary
    assert "source-reported evaluation" in boundary
    assert "政策達成度" in boundary
    assert "因果効果" in boundary
    assert "他都市比較可能性" in boundary


def test_niigata_policy_manifest_keeps_non_inference_boundaries():
    manifest = load(MANIFEST)

    assert manifest["status"] == "review_in_progress"
    assert len(manifest["reviewed_facts"]) == 10
    assert len(manifest["remaining_work"]) == 6
    assert "The draft is not promoted" in manifest["quality_boundary"]
    assert "No independent policy-achievement judgment" in manifest[
        "quality_boundary"
    ]
    assert "causal attribution" in manifest["quality_boundary"]
    assert "cross-city comparability" in manifest["quality_boundary"]


def test_niigata_completion_remains_stable_as_later_city_reviews_advance():
    queue = load(QUEUE)
    completion = load(COMPLETION)
    by_code = {row["official_code"]: row for row in queue["execution_queue"]}
    statuses = [row["status"] for row in queue["execution_queue"]]

    assert completion["status"] == "reviewed_complete"
    assert by_code["151009"]["status"] == "reviewed_complete"
    assert by_code["221007"]["status"] == "reviewed_complete"
    assert queue["summary"]["reviewed_complete_count"] == statuses.count(
        "reviewed_complete"
    )
    assert queue["summary"]["review_in_progress_count"] == statuses.count(
        "review_in_progress"
    )
    assert queue["summary"]["pending_record_review_count"] == statuses.count(
        "pending_record_review"
    )
    in_progress = [
        row for row in queue["execution_queue"]
        if row["status"] == "review_in_progress"
    ]
    if in_progress:
        assert queue["summary"]["next_official_code"] == in_progress[0]["official_code"]


def test_niigata_completion_quality_gates_are_all_true():
    completion = load(COMPLETION)
    assert completion["quality_gate"]
    assert all(value is True for value in completion["quality_gate"].values())
    assert completion["completion_depth"] == "declared_review_package_v1"
