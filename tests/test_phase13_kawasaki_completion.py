from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
REVIEWED = ROOT / "data/reviewed/kawasaki-city"
MUNICIPALITY = REVIEWED / "municipality.json"
PLAN = REVIEWED / "plan_review.json"
FISCAL = REVIEWED / "fiscal_records.json"
EVIDENCE = REVIEWED / "evidence_packets.json"
SOURCES = ROOT / "data/catalog/kawasaki_phase13_sources.json"
STRUCTURE = ROOT / "data/catalog/kawasaki_current_policy_structure.json"
HISTORICAL = ROOT / "data/catalog/kawasaki_prior_plan_2024_evaluation_summary.json"
MANIFEST = ROOT / "data/catalog/kawasaki_phase13_policy_review_manifest.json"
COMPLETION = ROOT / "data/catalog/kawasaki_phase13_completion.json"
COMPLETION_SCHEMA = ROOT / "schemas/kawasaki_phase13_completion.schema.json"
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


def test_kawasaki_shared_municipality_fiscal_and_evidence_contracts():
    municipality = load(MUNICIPALITY)
    fiscal = load(FISCAL)
    evidence = load(EVIDENCE)

    assert validate("municipality.schema.json", municipality) == []
    assert all(validate("fiscal_record.schema.json", row) == [] for row in fiscal)
    assert all(validate("evidence_packet.schema.json", row) == [] for row in evidence)
    assert municipality["official_code"] == "141305"
    assert municipality["name_ja"] == "川崎市"
    assert municipality["municipality_type"] == "designated_city"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert len(fiscal) == len(evidence) == 3
    assert {packet["subject_id"] for packet in evidence} == {
        row["id"] for row in fiscal
    }


def test_kawasaki_source_catalog_and_municipality_source_set_are_exact():
    municipality = load(MUNICIPALITY)
    sources = load(SOURCES)["records"]

    assert len(sources) == 10
    assert set(municipality["sources"]) == {row["id"] for row in sources}
    assert all(row["organization"] == "川崎市" for row in sources)
    assert all(row["url"].startswith("https://www.city.kawasaki.jp/") for row in sources)
    assert all(row["confidence"] == "high" for row in sources)


def test_kawasaki_current_policy_structure_is_complete_at_declared_level():
    structure = load(STRUCTURE)
    policies = [
        policy
        for basic_policy in structure["basic_policies"]
        for policy in basic_policy["policies"]
    ]
    hierarchy = structure["hierarchy"]

    assert structure["review_status"] == "reviewed_complete_structure_identity"
    assert hierarchy == {
        "basic_policy_count": 5,
        "policy_count": 18,
        "measure_count": 48,
        "administrative_project_count": 350,
    }
    assert len(structure["basic_policies"]) == 5
    assert len(policies) == 18
    assert len({row["policy_code"] for row in policies}) == 18
    assert structure["priority_theme"]["theme_count"] == 1
    assert structure["priority_theme"]["theme_name"] == "少子高齢化・人口減少対策"
    assert len(structure["priority_theme"]["initiative_lanes"]) == 5
    assert "350事務事業の個票" in structure["quality_boundary"]


def test_kawasaki_historical_evaluation_remains_source_reported_and_versioned():
    historical = load(HISTORICAL)
    scope = historical["source_reported_scope"]
    breakdown = historical["source_reported_breakdown"]

    assert historical["historical_plan_period"] == "2022年度～2025年度"
    assert scope == {
        "policy_measure_count": 74,
        "administrative_project_count": 572,
    }
    assert breakdown == {
        "greatly_above_target": 0,
        "above_target": 17,
        "almost_achieved": 462,
        "below_target": 93,
        "greatly_below_target": 0,
        "above_or_almost_achieved_count": 479,
        "above_or_almost_achieved_percent": 83.8,
    }
    assert "現行2026～2029計画のactual" in historical["quality_boundary"]
    assert "Jichi Insight独自の政策達成率" in historical["quality_boundary"]
    assert "因果効果" in historical["quality_boundary"]


def test_kawasaki_fiscal_top_lines_are_exact_and_state_separated():
    records = {row["id"]: row for row in load(FISCAL)}
    budget = records["jp-local-141305-fiscal-2026-total-revenue"]
    revenue = records["jp-local-141305-fiscal-2024-total-revenue"]
    expenditure = records["jp-local-141305-fiscal-2024-total-expenditure"]

    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 937_753_480_000
    assert revenue["stage"] == expenditure["stage"] == "settlement"
    assert revenue["amount_yen"] == 871_327_000_000
    assert expenditure["amount_yen"] == 862_154_000_000


def test_kawasaki_completion_contract_matches_schema_and_declared_paths_exist():
    completion = load(COMPLETION)
    validator = Draft202012Validator(
        load(COMPLETION_SCHEMA), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(completion)) == []

    for key, value in completion["review_package"].items():
        if key.endswith("_path"):
            assert (ROOT / value).is_file(), (key, value)


def test_kawasaki_completion_counts_are_derived_from_reviewed_layers():
    completion = load(COMPLETION)
    counts = completion["review_package"]["counts"]
    structure = load(STRUCTURE)
    historical = load(HISTORICAL)
    fiscal = load(FISCAL)

    assert counts["current_basic_policies"] == structure["hierarchy"][
        "basic_policy_count"
    ] == 5
    assert counts["current_policies"] == structure["hierarchy"]["policy_count"] == 18
    assert counts["current_measures"] == structure["hierarchy"]["measure_count"] == 48
    assert counts["current_administrative_projects_aggregate"] == structure[
        "hierarchy"
    ]["administrative_project_count"] == 350
    assert counts["current_priority_themes"] == 1
    assert counts["current_priority_initiative_lanes"] == len(
        structure["priority_theme"]["initiative_lanes"]
    ) == 5

    assert counts["historical_policy_measures"] == historical[
        "source_reported_scope"
    ]["policy_measure_count"] == 74
    assert counts["historical_administrative_projects"] == historical[
        "source_reported_scope"
    ]["administrative_project_count"] == 572

    breakdown = historical["source_reported_breakdown"]
    assert counts["historical_above_target"] == breakdown["above_target"] == 17
    assert counts["historical_almost_achieved"] == breakdown["almost_achieved"] == 462
    assert counts["historical_below_target"] == breakdown["below_target"] == 93
    assert counts["historical_above_or_almost_achieved_percent"] == breakdown[
        "above_or_almost_achieved_percent"
    ] == 83.8
    assert counts["fiscal_top_line_records"] == len(fiscal) == 3


def test_kawasaki_completion_deferred_depth_is_explicit_and_conservative():
    completion = load(COMPLETION)
    deferred = {row["id"]: row for row in completion["deferred_depth"]}

    project_detail = deferred["current-project-identity-detail"]
    assert project_detail["count"] == 350
    assert "aggregate count" in project_detail["boundary"]
    assert "推測しない" in project_detail["boundary"]

    measures = deferred["current-measure-outcome-indicators"]
    assert measures["measure_count"] == 48
    assert "未確認値を推測しない" in measures["boundary"]

    annual = deferred["current-plan-annual-progress"]
    assert "572事業" in annual["boundary"]
    assert "流用しない" in annual["boundary"]

    linkage = deferred["historical-current-versioned-linkage"]
    assert linkage["historical_project_count"] == 572
    assert linkage["current_project_aggregate_count"] == 350
    assert "名称類似" in linkage["boundary"]

    assert all(
        row["status"] == "deferred_not_required_for_v1_completion"
        for row in deferred.values()
    )

    boundary = completion["completion_boundary"]
    for token in ("5", "18", "48", "350", "74", "572", "17", "462", "93", "83.8"):
        assert token in boundary
    assert "政策達成度" in boundary
    assert "因果効果" in boundary
    assert "他都市比較可能性" in boundary


def test_kawasaki_policy_manifest_keeps_all_non_inference_boundaries():
    manifest = load(MANIFEST)

    assert manifest["status"] == "review_in_progress"
    assert len(manifest["reviewed_facts"]) == 7
    assert len(manifest["remaining_work"]) == 5
    assert "Aggregate project counts are not promoted" in manifest["quality_boundary"]
    assert "Historical evaluation is not reused as current progress" in (
        manifest["quality_boundary"]
    )
    assert "No independent policy-achievement judgment" in manifest[
        "quality_boundary"
    ]
    assert "causal attribution" in manifest["quality_boundary"]
    assert "cross-city comparability" in manifest["quality_boundary"]


def test_kawasaki_completion_advances_queue_to_sagamihara():
    queue = load(QUEUE)
    completion = load(COMPLETION)
    by_code = {row["official_code"]: row for row in queue["execution_queue"]}
    statuses = [row["status"] for row in queue["execution_queue"]]

    assert completion["status"] == "reviewed_complete"
    assert by_code["141305"]["status"] == "reviewed_complete"
    assert by_code["141500"]["status"] == "review_in_progress"
    assert queue["summary"]["reviewed_complete_count"] == statuses.count(
        "reviewed_complete"
    ) == 6
    assert queue["summary"]["review_in_progress_count"] == statuses.count(
        "review_in_progress"
    ) == 1
    assert queue["summary"]["pending_record_review_count"] == statuses.count(
        "pending_record_review"
    ) == 11
    assert queue["summary"]["next_official_code"] == "141500"


def test_kawasaki_completion_quality_gates_are_all_true():
    completion = load(COMPLETION)
    assert completion["quality_gate"]
    assert all(value is True for value in completion["quality_gate"].values())
    assert completion["completion_depth"] == "declared_review_package_v1"
