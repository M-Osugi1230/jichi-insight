from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
REVIEWED = ROOT / "data/reviewed/yokohama-city"
MUNICIPALITY = REVIEWED / "municipality.json"
PLAN = REVIEWED / "plan_review.json"
FISCAL = REVIEWED / "fiscal_records.json"
EVIDENCE = REVIEWED / "evidence_packets.json"
SOURCES = ROOT / "data/catalog/yokohama_phase13_sources.json"
STRUCTURE = ROOT / "data/catalog/yokohama_current_policy_structure.json"
POLICY_SNAPSHOT = (
    ROOT / "data/catalog/yokohama_policy_monitoring_indicator_proposal_snapshot.json"
)
HISTORICAL = ROOT / "data/catalog/yokohama_prior_plan_final_review_summary.json"
MANIFEST = ROOT / "data/catalog/yokohama_phase13_policy_review_manifest.json"
COMPLETION = ROOT / "data/catalog/yokohama_phase13_completion.json"
COMPLETION_SCHEMA = ROOT / "schemas/yokohama_phase13_completion.schema.json"
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


def test_yokohama_shared_municipality_fiscal_and_evidence_contracts():
    municipality = load(MUNICIPALITY)
    fiscal = load(FISCAL)
    evidence = load(EVIDENCE)

    assert validate("municipality.schema.json", municipality) == []
    assert all(validate("fiscal_record.schema.json", row) == [] for row in fiscal)
    assert all(validate("evidence_packet.schema.json", row) == [] for row in evidence)
    assert municipality["official_code"] == "141003"
    assert municipality["name_ja"] == "横浜市"
    assert municipality["municipality_type"] == "designated_city"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert len(fiscal) == len(evidence) == 3
    assert {packet["subject_id"] for packet in evidence} == {
        row["id"] for row in fiscal
    }


def test_yokohama_source_catalog_and_municipality_source_set_are_exact():
    municipality = load(MUNICIPALITY)
    sources = load(SOURCES)["records"]

    assert len(sources) == 8
    assert set(municipality["sources"]) == {row["id"] for row in sources}
    assert all(row["organization"] in {"横浜市", "横浜市会"} for row in sources)
    assert all(row["url"].startswith("https://www.city.yokohama.lg.jp/") for row in sources)
    assert all(row["confidence"] == "high" for row in sources)


def test_yokohama_adopted_policy_measure_structure_is_complete_and_unique():
    structure = load(STRUCTURE)
    groups = structure["policy_groups"]
    measures = [
        measure
        for group in groups
        for measure in group["measure_groups"]
    ]

    assert structure["review_status"] == "reviewed_complete_structure_identity"
    assert structure["policy_group_count"] == len(groups) == 14
    assert structure["measure_group_count"] == len(measures) == 33
    assert [group["policy_group_code"] for group in groups] == [
        f"{i:02d}" for i in range(1, 15)
    ]
    assert [row["measure_group_number"] for row in measures] == list(range(1, 34))
    assert len({row["measure_group_id"] for row in measures}) == 33
    assert structure["cross_cutting_project_theme_count"] == 3
    assert [row["name"] for row in structure["cross_cutting_project_themes"]] == [
        "循環型都市への移行",
        "観光・経済活性化",
        "未来を創るまちづくり",
    ]


def test_yokohama_policy_and_measure_indicator_semantics_remain_separate():
    structure = load(STRUCTURE)
    semantics = structure["indicator_semantics"]

    assert semantics["policy_indicator"]["role"] == (
        "citizen_experience_monitoring_indicator"
    )
    assert semantics["measure_indicator"]["role"] == (
        "plan_progress_outcome_indicator"
    )
    assert semantics["policy_indicator"]["role"] != semantics["measure_indicator"]["role"]


def test_yokohama_policy_monitoring_snapshot_is_explicitly_pre_final():
    snapshot = load(POLICY_SNAPSHOT)
    records = snapshot["records"]

    assert snapshot["policy_indicator_identity_count"] == len(records) == 15
    assert snapshot["policy_group_coverage_count"] == 14
    assert {row["policy_group_code"] for row in records} == {
        f"{i:02d}" for i in range(1, 15)
    }
    assert sum(row["policy_group_code"] == "01" for row in records) == 2
    assert all(row["unit"] == "percent" for row in records)
    assert all(row["value_status"] == "official_proposal_snapshot" for row in records)
    assert all(
        row["final_booklet_confirmation"]
        == "deferred_not_required_for_v1_completion"
        for row in records
    )
    assert "最終冊子の確定値と自動同一視しない" in snapshot["quality_boundary"]


def test_yokohama_historical_final_review_remains_source_reported_and_versioned():
    historical = load(HISTORICAL)

    assert historical["historical_plan_period"] == "2022年度～2025年度"
    assert historical["source_reported_aggregate"] == {
        "indicators_above_starting_value_percent": 90,
        "target_achievement_excluding_external_environment_effects_percent": 79,
        "evidence_location": "最終振り返り PDF p.3（PDF index p.3）",
    }
    assert "横浜市自身" in historical["quality_boundary"]
    assert "現行2026～2029計画の実績" in historical["quality_boundary"]
    assert "因果効果" in historical["quality_boundary"]


def test_yokohama_fiscal_top_lines_are_exact_and_state_separated():
    records = {row["id"]: row for row in load(FISCAL)}
    budget = records["jp-local-141003-fiscal-2026-total-revenue"]
    revenue = records["jp-local-141003-fiscal-2024-total-revenue"]
    expenditure = records["jp-local-141003-fiscal-2024-total-expenditure"]

    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 2_093_300_000_000
    assert revenue["stage"] == expenditure["stage"] == "settlement"
    assert revenue["amount_yen"] == 2_033_145_000_000
    assert expenditure["amount_yen"] == 2_009_287_000_000


def test_yokohama_completion_contract_matches_schema_and_declared_paths_exist():
    completion = load(COMPLETION)
    validator = Draft202012Validator(
        load(COMPLETION_SCHEMA), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(completion)) == []

    for key, value in completion["review_package"].items():
        if key.endswith("_path"):
            assert (ROOT / value).is_file(), (key, value)


def test_yokohama_completion_counts_are_derived_from_reviewed_layers():
    completion = load(COMPLETION)
    counts = completion["review_package"]["counts"]
    structure = load(STRUCTURE)
    snapshot = load(POLICY_SNAPSHOT)
    historical = load(HISTORICAL)
    fiscal = load(FISCAL)

    assert counts["current_policy_groups"] == structure["policy_group_count"] == 14
    assert counts["current_measure_groups"] == structure["measure_group_count"] == 33
    assert (
        counts["cross_cutting_project_themes"]
        == structure["cross_cutting_project_theme_count"]
        == 3
    )
    assert (
        counts["policy_monitoring_indicator_identities"]
        == snapshot["policy_indicator_identity_count"]
        == 15
    )
    assert counts["policy_monitoring_proposal_values"] == len(snapshot["records"]) == 15
    assert counts["policy_monitoring_final_values_deferred"] == 15
    assert (
        counts["historical_source_reported_improvement_percent"]
        == historical["source_reported_aggregate"][
            "indicators_above_starting_value_percent"
        ]
        == 90
    )
    assert (
        counts["historical_source_reported_adjusted_target_achievement_percent"]
        == historical["source_reported_aggregate"][
            "target_achievement_excluding_external_environment_effects_percent"
        ]
        == 79
    )
    assert counts["fiscal_top_line_records"] == len(fiscal) == 3


def test_yokohama_completion_deferred_depth_is_explicit_and_conservative():
    completion = load(COMPLETION)
    deferred = {row["id"]: row for row in completion["deferred_depth"]}

    final_detail = deferred["final-booklet-detailed-indicator-review"]
    assert final_detail["policy_indicator_count"] == 15
    assert final_detail["measure_group_count"] == 33
    assert "原案から最終値を推測しない" in final_detail["boundary"]

    linkage = deferred["historical-current-policy-versioned-linkage"]
    assert linkage["historical_policy_count"] == 38
    assert linkage["current_policy_group_count"] == 14
    assert linkage["current_measure_group_count"] == 33
    assert "名称類似だけ" in linkage["boundary"]

    annual = deferred["current-plan-annual-progress"]
    assert "流用しない" in annual["boundary"]

    assert all(
        row["status"] == "deferred_not_required_for_v1_completion"
        for row in deferred.values()
    )

    boundary = completion["completion_boundary"]
    for token in ("14", "33", "15", "90", "79"):
        assert token in boundary
    assert "政策達成度" in boundary
    assert "因果効果" in boundary
    assert "他都市比較可能性" in boundary


def test_yokohama_policy_manifest_keeps_all_non_inference_boundaries():
    manifest = load(MANIFEST)

    assert manifest["status"] == "review_in_progress"
    assert len(manifest["reviewed_facts"]) == 8
    assert len(manifest["remaining_work"]) == 4
    assert "Proposal detail is not silently promoted" in manifest["quality_boundary"]
    assert "No independent policy-achievement judgment" in manifest["quality_boundary"]
    assert "causal attribution" in manifest["quality_boundary"]
    assert "cross-city comparability" in manifest["quality_boundary"]


def test_yokohama_completion_advances_queue_to_kawasaki():
    queue = load(QUEUE)
    completion = load(COMPLETION)
    by_code = {row["official_code"]: row for row in queue["execution_queue"]}
    statuses = [row["status"] for row in queue["execution_queue"]]

    assert completion["status"] == "reviewed_complete"
    assert by_code["141003"]["status"] == "reviewed_complete"
    assert by_code["141305"]["status"] == "review_in_progress"
    assert queue["summary"]["reviewed_complete_count"] == statuses.count(
        "reviewed_complete"
    ) == 5
    assert queue["summary"]["review_in_progress_count"] == statuses.count(
        "review_in_progress"
    ) == 1
    assert queue["summary"]["pending_record_review_count"] == statuses.count(
        "pending_record_review"
    ) == 12
    assert queue["summary"]["next_official_code"] == "141305"


def test_yokohama_completion_quality_gates_are_all_true():
    completion = load(COMPLETION)
    assert completion["quality_gate"]
    assert all(value is True for value in completion["quality_gate"].values())
    assert completion["completion_depth"] == "declared_review_package_v1"
