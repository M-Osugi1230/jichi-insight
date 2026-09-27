from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
REVIEWED = ROOT / "data/reviewed/hamamatsu-city"
MUNICIPALITY = REVIEWED / "municipality.json"
PLAN = REVIEWED / "plan_review.json"
FISCAL = REVIEWED / "fiscal_records.json"
EVIDENCE = REVIEWED / "evidence_packets.json"
SOURCES = ROOT / "data/catalog/hamamatsu_phase13_sources.json"
STRUCTURE = ROOT / "data/catalog/hamamatsu_current_policy_structure.json"
PROGRESS = ROOT / "data/catalog/hamamatsu_current_implementation_review_summary.json"
MANIFEST = ROOT / "data/catalog/hamamatsu_phase13_policy_review_manifest.json"
COMPLETION = ROOT / "data/catalog/hamamatsu_phase13_completion.json"
COMPLETION_SCHEMA = ROOT / "schemas/hamamatsu_phase13_completion.schema.json"
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


def test_hamamatsu_shared_municipality_fiscal_and_evidence_contracts():
    municipality = load(MUNICIPALITY)
    fiscal = load(FISCAL)
    evidence = load(EVIDENCE)

    assert validate("municipality.schema.json", municipality) == []
    assert all(validate("fiscal_record.schema.json", row) == [] for row in fiscal)
    assert all(validate("evidence_packet.schema.json", row) == [] for row in evidence)
    assert municipality["official_code"] == "221309"
    assert municipality["name_ja"] == "浜松市"
    assert municipality["municipality_type"] == "designated_city"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert len(fiscal) == len(evidence) == 3


def test_hamamatsu_source_catalog_matches_municipality_sources():
    municipality = load(MUNICIPALITY)
    sources = load(SOURCES)["records"]

    assert len(sources) == 11
    assert set(municipality["sources"]) == {row["id"] for row in sources}
    assert all(row["organization"] == "浜松市" for row in sources)
    assert all(row["confidence"] == "high" for row in sources)


def test_hamamatsu_current_structure_is_complete_at_declared_level():
    structure = load(STRUCTURE)
    hierarchy = structure["hierarchy"]

    assert structure["review_status"] == "reviewed_current_declared_structure_identity"
    assert structure["basic_plan_period"] == "2025年度～2034年度"
    assert hierarchy == {
        "plan_layer_count": 3,
        "field_count": 7,
        "basic_policy_count": 25,
        "policy_count": 125,
        "outcome_indicator_count": 38,
        "life_satisfaction_overall_indicator_count": 8,
        "life_satisfaction_field_indicator_count": 7,
        "life_satisfaction_individual_indicator_count": 35,
        "life_satisfaction_total_indicator_count": 50,
    }
    assert len(structure["fields"]) == 7
    assert sum(row["outcome_indicator_count"] for row in structure["fields"]) == 38


def test_hamamatsu_2025_current_result_keeps_citizen_perception_semantics():
    progress = load(PROGRESS)
    overall = {row["id"]: row for row in progress["reviewed_2025_overall_results"]}
    fields = {row["id"]: row for row in progress["reviewed_2025_field_results"]}

    assert progress["reviewed_result_year"] == 2025
    assert progress["implementation_plan_year"] == 2026
    assert progress["declared_structure"] == {
        "basic_policy_count": 25,
        "policy_count": 125,
    }
    assert progress["life_satisfaction_indicator_universe"][
        "total_indicator_count"
    ] == 50
    assert len(overall) == 8
    assert len(fields) == 7
    assert overall["wellbeing-overall-1"]["baseline_2024"] == 6.42
    assert overall["wellbeing-overall-1"]["actual_2025"] == 6.40
    assert overall["wellbeing-overall-4"]["baseline_2024"] == 4.05
    assert overall["wellbeing-overall-4"]["actual_2025"] == 4.12
    assert fields["wellbeing-field-2"]["baseline_2024"] == 2.91
    assert fields["wellbeing-field-2"]["actual_2025"] == 2.94
    assert "主観的実感" in progress["quality_boundary"]
    assert "政策達成度" in progress["quality_boundary"]
    assert "因果効果" in progress["quality_boundary"]


def test_hamamatsu_2026_action_and_full_year_result_are_separate():
    progress = load(PROGRESS)

    assert progress["current_2026_full_year_result"]["status"] == "not_yet_complete"
    assert "公式実施計画評価レポート" in progress[
        "current_2026_full_year_result"
    ]["promotion_rule"]
    assert progress["pdca"]["annual_plan_created"] is True
    assert progress["pdca"]["indicators_set_and_evaluated"] is True
    assert progress["pdca"]["summer_review"] is True
    assert progress["pdca"]["deputy_mayor_review"] is True
    assert progress["pdca"]["budget_process_linked"] is True


def test_hamamatsu_fiscal_top_lines_are_exact_and_state_separated():
    records = {row["id"]: row for row in load(FISCAL)}
    budget = records["jp-local-221309-fiscal-2026-total-revenue"]
    revenue = records["jp-local-221309-fiscal-2024-total-revenue"]
    expenditure = records["jp-local-221309-fiscal-2024-total-expenditure"]

    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 440_100_000_000
    assert revenue["stage"] == expenditure["stage"] == "settlement"
    assert revenue["amount_yen"] == 416_537_079_000
    assert expenditure["amount_yen"] == 403_849_303_000


def test_hamamatsu_completion_contract_matches_schema_and_paths_exist():
    completion = load(COMPLETION)
    validator = Draft202012Validator(
        load(COMPLETION_SCHEMA), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(completion)) == []

    for key, value in completion["review_package"].items():
        if key.endswith("_path"):
            assert (ROOT / value).is_file(), (key, value)


def test_hamamatsu_completion_counts_derive_from_reviewed_layers():
    completion = load(COMPLETION)
    counts = completion["review_package"]["counts"]
    structure = load(STRUCTURE)
    progress = load(PROGRESS)
    fiscal = load(FISCAL)

    assert counts["current_plan_layers"] == structure["hierarchy"][
        "plan_layer_count"
    ] == 3
    assert counts["current_fields"] == structure["hierarchy"]["field_count"] == 7
    assert counts["current_basic_policies"] == structure["hierarchy"][
        "basic_policy_count"
    ] == 25
    assert counts["current_policies_aggregate"] == structure["hierarchy"][
        "policy_count"
    ] == 125
    assert counts["current_outcome_indicators_aggregate"] == structure[
        "hierarchy"
    ]["outcome_indicator_count"] == 38
    assert counts["life_satisfaction_indicators_total"] == progress[
        "life_satisfaction_indicator_universe"
    ]["total_indicator_count"] == 50
    assert counts["life_satisfaction_results_reviewed"] == (
        len(progress["reviewed_2025_overall_results"])
        + len(progress["reviewed_2025_field_results"])
    ) == 15
    assert counts["current_implementation_year"] == 2026
    assert counts["fiscal_top_line_records"] == len(fiscal) == 3


def test_hamamatsu_completion_deferred_depth_is_explicit():
    completion = load(COMPLETION)
    deferred = {row["id"]: row for row in completion["deferred_depth"]}

    assert deferred["outcome-indicator-detail"]["count"] == 38
    assert deferred["policy-detail-and-evaluation"]["count"] == 125
    assert deferred["individual-life-satisfaction-detail"]["count"] == 35
    assert "一律評価しない" in deferred["policy-detail-and-evaluation"]["boundary"]
    assert "途中レビューを通年成果とみなさない" in deferred[
        "fy2026-full-year-result"
    ]["boundary"]
    assert all(
        row["status"] == "deferred_not_required_for_v1_completion"
        for row in deferred.values()
    )

    boundary = completion["completion_boundary"]
    for token in (
        "7分野",
        "25基本政策",
        "125政策",
        "38件",
        "50指標",
        "440,100,000,000",
        "416,537,079,000",
        "403,849,303,000",
    ):
        assert token in boundary
    assert "政策達成度" in boundary
    assert "因果効果" in boundary
    assert "他都市比較可能性" in boundary


def test_hamamatsu_policy_manifest_keeps_non_inference_boundaries():
    manifest = load(MANIFEST)

    assert manifest["status"] == "review_in_progress"
    assert len(manifest["reviewed_facts"]) == 9
    assert len(manifest["remaining_work"]) == 6
    assert "citizen-perception measurements" in manifest["quality_boundary"]
    assert "not independent policy-achievement judgments" in manifest[
        "quality_boundary"
    ]
    assert "causal effects" in manifest["quality_boundary"]
    assert "cross-city comparability" in manifest["quality_boundary"]


def test_hamamatsu_completion_remains_stable_as_later_city_reviews_advance():
    queue = load(QUEUE)
    completion = load(COMPLETION)
    by_code = {row["official_code"]: row for row in queue["execution_queue"]}
    statuses = [row["status"] for row in queue["execution_queue"]]

    assert completion["status"] == "reviewed_complete"
    assert by_code["221309"]["status"] == "reviewed_complete"
    assert by_code["231002"]["status"] == "reviewed_complete"
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


def test_hamamatsu_completion_quality_gates_are_all_true():
    completion = load(COMPLETION)
    assert completion["quality_gate"]
    assert all(value is True for value in completion["quality_gate"].values())
    assert completion["completion_depth"] == "declared_review_package_v1"
