from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
REVIEWED = ROOT / "data/reviewed/nagoya-city"
MUNICIPALITY = REVIEWED / "municipality.json"
PLAN = REVIEWED / "plan_review.json"
FISCAL = REVIEWED / "fiscal_records.json"
EVIDENCE = REVIEWED / "evidence_packets.json"
SOURCES = ROOT / "data/catalog/nagoya_phase13_sources.json"
STRUCTURE = ROOT / "data/catalog/nagoya_current_policy_structure.json"
PROGRESS = ROOT / "data/catalog/nagoya_current_progress_review_summary.json"
MANIFEST = ROOT / "data/catalog/nagoya_phase13_policy_review_manifest.json"
COMPLETION = ROOT / "data/catalog/nagoya_phase13_completion.json"
COMPLETION_SCHEMA = ROOT / "schemas/nagoya_phase13_completion.schema.json"
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


def test_nagoya_shared_municipality_fiscal_and_evidence_contracts():
    municipality = load(MUNICIPALITY)
    fiscal = load(FISCAL)
    evidence = load(EVIDENCE)

    assert validate("municipality.schema.json", municipality) == []
    assert all(validate("fiscal_record.schema.json", row) == [] for row in fiscal)
    assert all(validate("evidence_packet.schema.json", row) == [] for row in evidence)
    assert municipality["official_code"] == "231002"
    assert municipality["name_ja"] == "名古屋市"
    assert municipality["municipality_type"] == "designated_city"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert len(fiscal) == len(evidence) == 3


def test_nagoya_source_catalog_matches_municipality_sources():
    municipality = load(MUNICIPALITY)
    sources = load(SOURCES)["records"]

    assert len(sources) == 10
    assert set(municipality["sources"]) == {row["id"] for row in sources}
    assert all(row["organization"] == "名古屋市" for row in sources)
    assert all(row["confidence"] == "high" for row in sources)


def test_nagoya_current_structure_is_complete_at_declared_level():
    structure = load(STRUCTURE)

    assert structure["review_status"] == "reviewed_declared_plan_structure"
    assert structure["plan_period"] == "2024年度～2028年度"
    assert structure["hierarchy"] == {
        "city_vision_count": 5,
        "measure_count": 42,
        "outcome_indicator_count": 135,
        "listed_project_count": 506,
    }
    assert len(structure["city_visions"]) == 5
    assert structure["implementation_semantics"]["embedded_in_comprehensive_plan"] is True
    assert structure["implementation_semantics"]["annual_progress_publication"] is True


def test_nagoya_2024_indicator_classification_is_source_reported():
    progress = load(PROGRESS)
    evaluation = progress["indicator_evaluation"]
    categories = evaluation["categories"]

    assert progress["scope"] == {
        "measure_count": 42,
        "outcome_indicator_count": 135,
        "listed_project_count": 506,
    }
    assert categories["A"]["count"] == 54
    assert categories["B"]["count"] == 18
    assert categories["C"]["count"] == 23
    assert categories["D"]["count"] == 40
    assert sum(row["count"] for row in categories.values()) == 135
    assert evaluation["A_B_C_count"] == 95
    assert "source-reported" in evaluation["boundary"]
    assert "Jichi Insight独自達成度へ変換しない" in evaluation["boundary"]


def test_nagoya_2024_project_progress_is_source_reported():
    progress = load(PROGRESS)
    project = progress["project_progress"]
    categories = project["categories"]

    assert categories["four_stars"]["count"] == 384
    assert categories["three_stars"]["count"] == 96
    assert categories["two_stars"]["count"] == 20
    assert categories["one_star"]["count"] == 6
    assert categories["revised"]["count"] == 0
    assert sum(row["count"] for row in categories.values()) == 506
    assert project["four_or_three_stars_count"] == 480
    assert "個別未確認事業へ配分しない" in project["boundary"]


def test_nagoya_citizen_survey_is_separate_evidence_role():
    survey = load(PROGRESS)["citizen_survey"]

    assert survey["target_population"] == "名古屋市に居住する4,000人"
    assert survey["survey_period"] == "2025年4月"
    assert survey["valid_response_rate_percent"] == 44.2
    assert "別Evidence role" in survey["boundary"]


def test_nagoya_project_cost_is_approximate_and_separate_from_accounts():
    cost = load(PROGRESS)["project_cost"]

    assert cost["plan_total_approx_yen"] == 2_698_700_000_000
    assert cost["fy2024_actual_estimate_approx_yen"] == 514_500_000_000
    assert "概算・見込み値" in cost["boundary"]
    assert "一般会計決算" in cost["boundary"]


def test_nagoya_fiscal_top_lines_are_exact_and_use_amended_budget():
    records = {row["id"]: row for row in load(FISCAL)}
    budget = records["jp-local-231002-fiscal-2026-total-revenue"]
    revenue = records["jp-local-231002-fiscal-2024-total-revenue"]
    expenditure = records["jp-local-231002-fiscal-2024-total-expenditure"]

    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 1_696_086_000_000
    assert "議会修正後成立版" in budget["metric_label"]
    assert revenue["stage"] == expenditure["stage"] == "settlement"
    assert revenue["amount_yen"] == 1_505_378_206_754
    assert expenditure["amount_yen"] == 1_486_264_707_319


def test_nagoya_completion_contract_matches_schema_and_paths_exist():
    completion = load(COMPLETION)
    validator = Draft202012Validator(
        load(COMPLETION_SCHEMA), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(completion)) == []

    for key, value in completion["review_package"].items():
        if key.endswith("_path"):
            assert (ROOT / value).is_file(), (key, value)


def test_nagoya_completion_counts_derive_from_reviewed_layers():
    completion = load(COMPLETION)
    counts = completion["review_package"]["counts"]
    structure = load(STRUCTURE)
    progress = load(PROGRESS)
    fiscal = load(FISCAL)

    assert counts["current_city_visions"] == structure["hierarchy"][
        "city_vision_count"
    ] == 5
    assert counts["current_measures_aggregate"] == structure["hierarchy"][
        "measure_count"
    ] == 42
    assert counts["current_outcome_indicators_aggregate"] == structure[
        "hierarchy"
    ]["outcome_indicator_count"] == 135
    assert counts["current_listed_projects_aggregate"] == structure["hierarchy"][
        "listed_project_count"
    ] == 506
    assert counts["source_reported_indicator_A_B_C_count"] == progress[
        "indicator_evaluation"
    ]["A_B_C_count"] == 95
    assert counts["source_reported_projects_four_or_three_stars"] == progress[
        "project_progress"
    ]["four_or_three_stars_count"] == 480
    assert counts["citizen_survey_target_population"] == 4000
    assert counts["fiscal_top_line_records"] == len(fiscal) == 3


def test_nagoya_completion_deferred_depth_is_explicit():
    completion = load(COMPLETION)
    deferred = {row["id"]: row for row in completion["deferred_depth"]}

    assert deferred["measure-detail"]["count"] == 42
    assert deferred["indicator-detail"]["count"] == 135
    assert deferred["listed-project-detail"]["count"] == 506
    assert "A54/B18/C23/D40" in deferred["indicator-detail"]["boundary"]
    assert "384/96/20/6/0" in deferred["listed-project-detail"]["boundary"]
    assert "自動接続しない" in deferred["project-cost-to-fiscal-linkage"]["boundary"]
    assert all(
        row["status"] == "deferred_not_required_for_v1_completion"
        for row in deferred.values()
    )

    boundary = completion["completion_boundary"]
    for token in (
        "42施策",
        "135成果指標",
        "506掲載事業",
        "95件",
        "480件",
        "1,696,086,000,000",
        "1,505,378,206,754",
        "1,486,264,707,319",
    ):
        assert token in boundary
    assert "政策達成度" in boundary
    assert "因果効果" in boundary
    assert "他都市比較可能性" in boundary


def test_nagoya_policy_manifest_keeps_non_inference_boundaries():
    manifest = load(MANIFEST)

    assert manifest["status"] == "review_in_progress"
    assert len(manifest["reviewed_facts"]) == 9
    assert len(manifest["remaining_work"]) == 6
    assert "not allocated to unreviewed individual records" in manifest[
        "quality_boundary"
    ]
    assert "independent Jichi Insight policy-achievement judgments" in manifest[
        "quality_boundary"
    ]
    assert "No causal attribution" in manifest["quality_boundary"]


def test_nagoya_completion_remains_stable_as_later_city_reviews_advance():
    queue = load(QUEUE)
    completion = load(COMPLETION)
    by_code = {row["official_code"]: row for row in queue["execution_queue"]}
    statuses = [row["status"] for row in queue["execution_queue"]]

    assert completion["status"] == "reviewed_complete"
    assert by_code["231002"]["status"] == "reviewed_complete"
    assert by_code["261009"]["status"] == "reviewed_complete"
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


def test_nagoya_completion_quality_gates_are_all_true():
    completion = load(COMPLETION)
    assert completion["quality_gate"]
    assert all(value is True for value in completion["quality_gate"].values())
    assert completion["completion_depth"] == "declared_review_package_v1"
