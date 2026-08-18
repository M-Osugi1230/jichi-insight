from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "data/catalog/sapporo_outcome_indicator_registry.json"
MANIFEST_PATH = ROOT / "data/catalog/sapporo_phase13_policy_review_manifest.json"
CURRENT_VALUES_PATH = ROOT / "data/catalog/sapporo_outcome_indicator_2025_report_values.json"
CURRENT_EVIDENCE_PATH = (
    ROOT / "data/evidence/sapporo_outcome_indicator_2025_report_values_evidence.json"
)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sapporo_outcome_indicator_registry_covers_all_unique_indicators_once():
    registry = load(REGISTRY_PATH)
    records = registry["records"]

    assert registry["official_code"] == "011002"
    assert registry["status"] == "identity_prior_and_current_value_review_complete"
    assert len(records) == 26
    assert [record["sequence"] for record in records] == list(range(1, 27))
    assert len({record["id"] for record in records}) == 26
    assert len({record["name_ja"] for record in records}) == 26
    assert all(record["identity_review_status"] == "reviewed" for record in records)
    assert registry["summary"]["prior_value_reviewed_count"] == 26
    assert registry["summary"]["current_value_reviewed_count"] == 26
    assert all(record["current_value_review_status"] == "reviewed" for record in records)


def test_sapporo_registry_preserves_33_to_26_repost_boundary():
    registry = load(REGISTRY_PATH)
    records = registry["records"]
    summary = registry["summary"]

    assert summary["field_occurrence_count"] == 33
    assert summary["unique_indicator_count"] == 26
    assert summary["reposted_occurrence_count"] == 7
    assert sum(record["reposted_elsewhere"] for record in records) == 7
    assert summary["field_occurrence_count"] - summary["reposted_occurrence_count"] == 26


def test_sapporo_registry_keeps_reported_2024_and_2025_aggregates_separate():
    summary = load(REGISTRY_PATH)["summary"]

    assert (
        summary["reported_2024_up_count"],
        summary["reported_2024_down_count"],
        summary["reported_2024_flat_count"],
        summary["reported_2024_unaggregated_or_unevaluated_count"],
    ) == (13, 11, 0, 2)
    assert (
        summary["reported_2025_up_count"],
        summary["reported_2025_down_count"],
        summary["reported_2025_flat_count"],
        summary["reported_2025_unaggregated_count"],
    ) == (17, 8, 0, 1)
    assert sum(
        [
            summary["reported_2025_up_count"],
            summary["reported_2025_down_count"],
            summary["reported_2025_flat_count"],
            summary["reported_2025_unaggregated_count"],
        ]
    ) == 26


def test_sapporo_registry_has_exact_reviewed_identity_anchors():
    records = {record["id"]: record for record in load(REGISTRY_PATH)["records"]}

    assert records["total_fertility_rate"] == {
        "sequence": 1,
        "id": "total_fertility_rate",
        "field": "children_youth",
        "name_ja": "合計特殊出生率",
        "source_page": 1,
        "reposted_elsewhere": False,
        "identity_review_status": "reviewed",
        "current_value_review_status": "reviewed",
    }
    assert records["young_adult_outmigration_excess"]["name_ja"] == (
        "20～29歳の道外への転出超過数（日本人のみ）"
    )
    assert records["perceived_barrier_free_progress"]["sequence"] == 6
    assert records["understanding_elderly_disabled"]["sequence"] == 7
    assert records["healthy_life_expectancy"]["sequence"] == 8
    assert records["lifelong_learning_participation"]["sequence"] == 9
    assert records["citizens_feeling_social_role"]["sequence"] == 12
    assert records["citizen_machizukuri_participation"]["sequence"] == 13
    assert records["understanding_elderly_disabled"]["reposted_elsewhere"] is True
    assert records["citizens_prepared_for_disasters"]["source_page"] == 2
    assert records["regional_hub_effective_far"]["sequence"] == 26


def test_sapporo_prior_and_current_value_layers_are_both_complete_but_separate():
    registry = load(REGISTRY_PATH)
    prior = registry["prior_value_review"]
    current = registry["current_value_review"]

    assert prior["status"] == "reviewed"
    assert prior["reviewed_count"] == 26
    assert prior["record_path"] == (
        "data/catalog/sapporo_outcome_indicator_2024_report_values.json"
    )
    assert current["status"] == "reviewed"
    assert current["reviewed_count"] == 26
    assert current["record_path"] == (
        "data/catalog/sapporo_outcome_indicator_2025_report_values.json"
    )
    assert current["evidence_path"] == (
        "data/evidence/sapporo_outcome_indicator_2025_report_values_evidence.json"
    )
    assert CURRENT_VALUES_PATH.is_file()
    assert CURRENT_EVIDENCE_PATH.is_file()
    assert "fiscal year printed" in current["boundary"]
    assert "not Jichi Insight achievement judgments" in registry["quality_boundary"]


def test_sapporo_manifest_records_both_outcome_value_layers_inside_declared_v1():
    manifest = load(MANIFEST_PATH)
    facts = {fact["id"]: fact for fact in manifest["reviewed_facts"]}
    identity = facts["outcome-indicator-identity-registry"]
    prior_values = facts["outcome-indicator-prior-values-2024-report"]
    current_values = facts["outcome-indicator-current-values-2025-report"]

    assert manifest["status"] == "reviewed_at_declared_depth"
    assert identity["value"] == 26
    assert identity["displayed_field_occurrences"] == 33
    assert identity["reposted_occurrences"] == 7
    assert prior_values["value"] == 26
    assert prior_values["reporting_year"] == 2024
    assert current_values["value"] == 26
    assert current_values["reporting_year"] == 2025
    assert current_values["review_status"] == "reviewed"
    assert "すべてを2024年度値とは扱わない" in current_values["interpretation_boundary"]
    assert any("成果指標" in item for item in manifest["deferred_extension_work"])
