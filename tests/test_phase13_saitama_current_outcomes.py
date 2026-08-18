from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/catalog/saitama_current_outcome_indicator_registry.json"
OUTCOME_PATHS = [
    ROOT / "data/catalog/saitama_current_outcomes_policy_chapters01_04.json",
    ROOT / "data/catalog/saitama_current_outcomes_policy_chapters05_08.json",
    ROOT / "data/catalog/saitama_current_outcomes_policy_chapters09_11.json",
    ROOT / "data/catalog/saitama_current_outcomes_quality_city_management.json",
]
PROJECT_PATHS = [
    ROOT / "data/catalog/saitama_current_project_identities_policy_chapters01_04.json",
    ROOT / "data/catalog/saitama_current_project_identities_policy_chapters05_08.json",
    ROOT / "data/catalog/saitama_current_project_identities_policy_chapters09_11.json",
    ROOT / "data/catalog/saitama_current_project_identities_quality_city_management.json",
]
EVIDENCE = ROOT / "data/evidence/saitama_current_outcome_indicator_evidence.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def outcome_records():
    return [row for path in OUTCOME_PATHS for row in load(path)["records"]]


def project_measure_codes():
    return {
        "-".join(row["project_code"].split("-")[:3])
        for path in PROJECT_PATHS
        for row in load(path)["records"]
    }


def test_saitama_current_outcome_universe_is_97_unique_records_across_64_measures():
    registry = load(REGISTRY)
    records = outcome_records()
    ids = [row["indicator_id"] for row in records]
    measures = {row["measure_code"] for row in records}

    assert registry["indicator_universe"]["indicator_count"] == 97
    assert registry["indicator_universe"]["identity_records_reviewed"] == 97
    assert registry["indicator_universe"]["identity_records_remaining"] == 0
    assert len(records) == len(ids) == len(set(ids)) == 97
    assert len(measures) == registry["measure_universe"]["measure_count"] == 64
    assert all(row["review_status"] == "reviewed_identity" for row in records)


def test_saitama_outcome_measure_codes_exactly_match_current_project_measure_prefixes():
    outcome_measures = {row["measure_code"] for row in outcome_records()}
    project_measures = project_measure_codes()

    assert len(project_measures) == 64
    assert outcome_measures == project_measures


def test_saitama_outcomes_reconcile_policy_and_quality_partitions():
    registry = load(REGISTRY)
    records = outcome_records()
    policy = [row for row in records if int(row["measure_code"][:2]) <= 11]
    quality = [
        row
        for row in records
        if row["measure_code"].startswith(("51-", "52-"))
    ]
    policy_measures = {row["measure_code"] for row in policy}
    quality_measures = {row["measure_code"] for row in quality}

    assert len(policy) == 78
    assert len(quality) == 19
    assert (
        len(policy_measures)
        == registry["measure_universe"]["policy_fields_measure_count"]
        == 50
    )
    assert (
        len(quality_measures)
        == registry["measure_universe"]["quality_city_management_measure_count"]
        == 14
    )
    assert len(policy) + len(quality) == 97


def test_saitama_semantic_measurement_lanes_partition_all_97_without_combining_scores():
    registry = load(REGISTRY)
    records = outcome_records()
    lanes = Counter(row["semantic_measurement_lane"] for row in records)

    assert lanes == {
        "self_report_or_perception": 62,
        "objective_or_administrative_statistical": 35,
    }
    assert registry["indicator_universe"]["self_report_or_perception_count"] == 62
    assert (
        registry["indicator_universe"][
            "objective_or_administrative_statistical_count"
        ]
        == 35
    )
    assert registry["measurement_boundary"]["no_combined_score"] is True
    assert registry["measurement_boundary"]["no_causal_attribution"] is True
    assert all(
        row["lane_decision_status"]
        == "semantic_separation_reviewed_exact_instrument_pending"
        for row in records
    )


def test_saitama_each_outcome_has_official_source_and_measure_level_locator():
    records = outcome_records()
    expected_sources = {
        "saitama-implementation-plan-2026-2030-policy-projects",
        "saitama-implementation-plan-2026-2030-quality-management-projects",
    }

    assert {row["source_id"] for row in records} == expected_sources
    assert all(
        row["source_location"] == f"施策 {row['measure_code']} 成果指標欄"
        for row in records
    )
    assert all(row["indicator_name"].strip() for row in records)


def test_saitama_outcome_evidence_preserves_semantic_vs_exact_method_boundary():
    evidence = load(EVIDENCE)

    assert evidence["review_status"] == (
        "reviewed_97_of_97_outcome_identities_semantic_lanes"
    )
    assert len(evidence["evidence"]) == 4
    assert all(row["decision"] == "accepted" for row in evidence["evidence"])
    assert "62件" in evidence["semantic_lane_boundary"]
    assert "35件" in evidence["semantic_lane_boundary"]
    assert "個票確認済みとするものではない" in evidence["semantic_lane_boundary"]
