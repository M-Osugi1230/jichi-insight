from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
REVIEWED = ROOT / "data/reviewed/sagamihara-city"
MUNICIPALITY = REVIEWED / "municipality.json"
PLAN = REVIEWED / "plan_review.json"
FISCAL = REVIEWED / "fiscal_records.json"
EVIDENCE = REVIEWED / "evidence_packets.json"
SOURCES = ROOT / "data/catalog/sagamihara_phase13_sources.json"
STRUCTURE = ROOT / "data/catalog/sagamihara_current_policy_structure.json"
PROGRESS = ROOT / "data/catalog/sagamihara_current_progress_review_summary.json"
MANIFEST = ROOT / "data/catalog/sagamihara_phase13_policy_review_manifest.json"
COMPLETION = ROOT / "data/catalog/sagamihara_phase13_completion.json"
COMPLETION_SCHEMA = ROOT / "schemas/sagamihara_phase13_completion.schema.json"
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


def test_sagamihara_shared_municipality_fiscal_and_evidence_contracts():
    municipality = load(MUNICIPALITY)
    fiscal = load(FISCAL)
    evidence = load(EVIDENCE)

    assert validate("municipality.schema.json", municipality) == []
    assert all(validate("fiscal_record.schema.json", row) == [] for row in fiscal)
    assert all(validate("evidence_packet.schema.json", row) == [] for row in evidence)
    assert municipality["official_code"] == "141500"
    assert municipality["name_ja"] == "相模原市"
    assert municipality["municipality_type"] == "designated_city"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert len(fiscal) == len(evidence) == 3


def test_sagamihara_source_catalog_matches_municipality_sources():
    municipality = load(MUNICIPALITY)
    sources = load(SOURCES)["records"]

    assert len(sources) == 8
    assert set(municipality["sources"]) == {row["id"] for row in sources}
    assert all(row["organization"] == "相模原市" for row in sources)
    assert all(row["confidence"] == "high" for row in sources)


def test_sagamihara_structure_preserves_basic_plan_and_rolling_program_versions():
    structure = load(STRUCTURE)

    assert structure["review_status"] == (
        "reviewed_structure_aggregate_and_priority_theme_identity"
    )
    assert structure["basic_plan_period"] == "2020年度～2027年度"
    assert structure["rolling_program_period"] == "2026年度～2028年度"
    assert structure["hierarchy"] == {
        "plan_layer_count": 3,
        "vision_group_count": 6,
        "measure_count": 47,
    }
    assert [row["name"] for row in structure["priority_themes"]] == [
        "少子化対策",
        "雇用促進対策",
        "中山間地域対策",
    ]
    assert structure["city_strength_fields"] == ["子育て", "教育", "まちづくり"]
    assert "2028年度" in structure["version_boundary"]
    assert "自動延長しない" in structure["version_boundary"]


def test_sagamihara_progress_roles_remain_separate():
    progress = load(PROGRESS)
    roles = {row["id"]: row for row in progress["evaluation_layers"]}

    assert progress["implementation_period_reviewed"] == "2020年度～2024年度"
    assert progress["scope"]["measure_count"] == 47
    assert progress["scope"]["includes_cross_cutting_priority_themes"] is True
    assert roles["municipal_first_stage"]["role"] == "first_stage_self_evaluation"
    assert roles["planning_council_second_stage"]["role"] == (
        "second_stage_third_party_evaluation"
    )
    assert roles["citizen_survey"]["role"] == "citizen_opinion_input"
    assert "別Evidence role" in progress["quality_boundary"]
    assert "Jichi Insight独自評価へ変換しない" in progress["quality_boundary"]


def test_sagamihara_fiscal_top_lines_are_exact_and_state_separated():
    records = {row["id"]: row for row in load(FISCAL)}
    budget = records["jp-local-141500-fiscal-2026-total-revenue"]
    revenue = records["jp-local-141500-fiscal-2024-total-revenue"]
    expenditure = records["jp-local-141500-fiscal-2024-total-expenditure"]

    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 405_500_000_000
    assert revenue["stage"] == expenditure["stage"] == "settlement"
    assert revenue["amount_yen"] == 359_794_590_156
    assert expenditure["amount_yen"] == 349_624_530_765


def test_sagamihara_completion_contract_matches_schema_and_declared_paths_exist():
    completion = load(COMPLETION)
    validator = Draft202012Validator(
        load(COMPLETION_SCHEMA), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(completion)) == []

    for key, value in completion["review_package"].items():
        if key.endswith("_path"):
            assert (ROOT / value).is_file(), (key, value)


def test_sagamihara_completion_counts_derive_from_reviewed_layers():
    completion = load(COMPLETION)
    counts = completion["review_package"]["counts"]
    structure = load(STRUCTURE)
    progress = load(PROGRESS)
    fiscal = load(FISCAL)

    assert counts["current_vision_groups"] == structure["hierarchy"][
        "vision_group_count"
    ] == 6
    assert counts["current_measures_aggregate"] == structure["hierarchy"][
        "measure_count"
    ] == 47
    assert counts["current_priority_themes"] == len(
        structure["priority_themes"]
    ) == 3
    assert counts["current_progress_measures_covered"] == progress["scope"][
        "measure_count"
    ] == 47
    assert counts["evaluation_role_count"] == len(
        progress["evaluation_layers"]
    ) == 3
    assert counts["fiscal_top_line_records"] == len(fiscal) == 3


def test_sagamihara_completion_deferred_depth_is_explicit():
    completion = load(COMPLETION)
    deferred = {row["id"]: row for row in completion["deferred_depth"]}

    measure_detail = deferred["current-measure-detail"]
    assert measure_detail["measure_count"] == 47
    assert "推測しない" in measure_detail["boundary"]

    transition = deferred["basic-plan-program-next-plan-version-transition"]
    assert "2020～2027年度" in transition["boundary"]
    assert "2026～2028年度" in transition["boundary"]
    assert "自動延長しない" in transition["boundary"]

    survey = deferred["citizen-survey-detail"]
    assert "行政自己評価" in survey["boundary"]
    assert "審議会評価" in survey["boundary"]

    assert all(
        row["status"] == "deferred_not_required_for_v1_completion"
        for row in deferred.values()
    )

    boundary = completion["completion_boundary"]
    for token in ("6", "47", "3", "405,500,000,000", "359,794,590,156", "349,624,530,765"):
        assert token in boundary
    assert "政策達成度" in boundary
    assert "因果効果" in boundary
    assert "他都市比較可能性" in boundary


def test_sagamihara_policy_manifest_keeps_non_inference_boundaries():
    manifest = load(MANIFEST)

    assert manifest["status"] == "review_in_progress"
    assert len(manifest["reviewed_facts"]) == 8
    assert len(manifest["remaining_work"]) == 5
    assert "Individual measure results" in manifest["quality_boundary"]
    assert "No independent policy-achievement judgment" in manifest[
        "quality_boundary"
    ]
    assert "causal attribution" in manifest["quality_boundary"]
    assert "cross-city comparability" in manifest["quality_boundary"]


def test_sagamihara_completion_advances_queue_to_niigata():
    queue = load(QUEUE)
    completion = load(COMPLETION)
    by_code = {row["official_code"]: row for row in queue["execution_queue"]}
    statuses = [row["status"] for row in queue["execution_queue"]]

    assert completion["status"] == "reviewed_complete"
    assert by_code["141500"]["status"] == "reviewed_complete"
    assert by_code["151009"]["status"] == "review_in_progress"
    assert queue["summary"]["reviewed_complete_count"] == statuses.count(
        "reviewed_complete"
    ) == 7
    assert queue["summary"]["review_in_progress_count"] == statuses.count(
        "review_in_progress"
    ) == 1
    assert queue["summary"]["pending_record_review_count"] == statuses.count(
        "pending_record_review"
    ) == 10
    assert queue["summary"]["next_official_code"] == "151009"


def test_sagamihara_completion_quality_gates_are_all_true():
    completion = load(COMPLETION)
    assert completion["quality_gate"]
    assert all(value is True for value in completion["quality_gate"].values())
    assert completion["completion_depth"] == "declared_review_package_v1"
