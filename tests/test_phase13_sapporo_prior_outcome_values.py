from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALUES_PATH = ROOT / "data/catalog/sapporo_outcome_indicator_2024_report_values.json"
EVIDENCE_PATH = ROOT / "data/evidence/sapporo_outcome_indicator_2024_report_values_evidence.json"
REGISTRY_PATH = ROOT / "data/catalog/sapporo_outcome_indicator_registry.json"
MANIFEST_PATH = ROOT / "data/catalog/sapporo_phase13_policy_review_manifest.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sapporo_prior_value_registry_covers_all_26_unique_indicators_in_official_order():
    values = load(VALUES_PATH)
    records = values["records"]
    registry = load(REGISTRY_PATH)["records"]

    assert values["official_code"] == "011002"
    assert values["status"] == "reviewed_prior_values_complete"
    assert len(records) == 26
    assert [record["sequence"] for record in records] == list(range(1, 27))
    assert [record["id"] for record in records] == [record["id"] for record in registry]
    assert [record["name_ja"] for record in records] == [
        record["name_ja"] for record in registry
    ]
    assert values["summary"]["reviewed_indicator_count"] == 26
    assert values["summary"]["latest_2025_values_reviewed_count"] == 26


def test_sapporo_prior_value_source_trend_counts_match_official_2024_report():
    values = load(VALUES_PATH)
    counts = Counter(record["source_trend_classification"] for record in values["records"])

    assert counts == {
        "source_reported_up": 13,
        "source_reported_down": 11,
        "source_reported_not_evaluated": 1,
        "source_reported_unaggregated": 1,
    }
    assert values["summary"]["source_reported_up_count"] == 13
    assert values["summary"]["source_reported_down_count"] == 11
    assert values["summary"]["source_reported_not_evaluated_count"] == 1
    assert values["summary"]["source_reported_unaggregated_count"] == 1


def test_sapporo_prior_values_preserve_exact_children_and_community_rows():
    records = {record["id"]: record for record in load(VALUES_PATH)["records"]}

    fertility = records["total_fertility_rate"]
    assert fertility["baseline"] == {"value": 1.08, "unit": "ratio", "fiscal_year": 2021}
    assert fertility["prior_actual"] == {
        "value": 1.02,
        "unit": "ratio",
        "fiscal_year": 2022,
    }
    assert fertility["target"] == {"value": 1.3, "unit": "ratio", "fiscal_year": 2027}

    goals = records["children_with_personal_goals"]
    assert goals["baseline"] == {"value": 71.6, "unit": "percent", "fiscal_year": 2023}
    assert goals["prior_actual"] == {
        "value": 71.6,
        "unit": "percent",
        "fiscal_year": 2023,
    }
    assert goals["source_trend_classification"] == "source_reported_not_evaluated"

    social_role = records["citizens_feeling_social_role"]
    assert social_role["value_type"] == "composite"
    dimensions = {item["dimension"]: item for item in social_role["dimensions"]}
    assert dimensions["age_18_64"]["prior_actual"]["value"] == 44.5
    assert dimensions["age_65_plus"]["prior_actual"]["value"] == 45.3

    participation = records["citizen_machizukuri_participation"]
    assert participation["baseline"]["value"] == 86.3
    assert participation["prior_actual"]["value"] == 84.9
    assert participation["source_trend_classification"] == "source_reported_down"


def test_sapporo_prior_values_preserve_composite_health_and_unaggregated_employment():
    records = {record["id"]: record for record in load(VALUES_PATH)["records"]}

    health = records["healthy_life_expectancy"]
    dimensions = {item["dimension"]: item for item in health["dimensions"]}
    assert dimensions["male"]["baseline"]["value"] == 71.34
    assert dimensions["male"]["prior_actual"]["value"] == 72.08
    assert dimensions["male"]["target"]["value"] == 72.72
    assert dimensions["female"]["baseline"]["value"] == 72.89
    assert dimensions["female"]["prior_actual"]["value"] == 74.69
    assert dimensions["female"]["target"]["value"] == 74.27

    employment = records["employment_rate"]
    assert employment["baseline"] == {
        "value": 49,
        "unit": "percent",
        "fiscal_year": 2020,
    }
    assert employment["prior_actual"] == {"status": "unaggregated"}
    assert employment["target"] == {
        "value": 52,
        "unit": "percent",
        "fiscal_year": 2027,
    }
    assert employment["source_trend_classification"] == "source_reported_unaggregated"


def test_sapporo_prior_values_keep_measurement_years_and_source_trends_separate():
    records = {record["id"]: record for record in load(VALUES_PATH)["records"]}

    gdp = records["gdp_per_capita_nominal"]
    assert gdp["baseline"]["fiscal_year"] == 2019
    assert gdp["prior_actual"]["fiscal_year"] == 2021

    municipal_ghg = records["municipal_facility_ghg_emissions"]
    assert municipal_ghg["baseline"]["value"] == 66.0
    assert municipal_ghg["prior_actual"]["value"] == 65.4
    assert municipal_ghg["source_trend_classification"] == "source_reported_up"

    citywide_ghg = records["citywide_ghg_emissions"]
    assert citywide_ghg["baseline"]["value"] == 1150
    assert citywide_ghg["prior_actual"]["value"] == 1025
    assert citywide_ghg["target"]["value"] == 690
    assert citywide_ghg["source_trend_classification"] == "source_reported_up"

    boundary = load(VALUES_PATH)["quality_boundary"]
    assert "fiscal year printed in each row" in boundary
    assert "source-reported classification" in boundary
    assert "must not be presented as the latest" in boundary


def test_sapporo_prior_value_evidence_covers_exactly_the_26_unique_ids():
    evidence = load(EVIDENCE_PATH)
    values = load(VALUES_PATH)["records"]
    page_evidence = evidence["page_evidence"]
    evidence_ids = [
        indicator_id
        for page in page_evidence
        for indicator_id in page["indicator_ids"]
    ]

    assert evidence["reviewed_indicator_count"] == 26
    assert [page["source_page"] for page in page_evidence] == [1, 2]
    assert all(page["evidence_status"] == "reviewed" for page in page_evidence)
    assert len(evidence_ids) == 26
    assert len(set(evidence_ids)) == 26
    assert set(evidence_ids) == {record["id"] for record in values}


def test_sapporo_manifest_preserves_prior_layer_after_declared_v1_completion():
    manifest = load(MANIFEST_PATH)
    facts = {fact["id"]: fact for fact in manifest["reviewed_facts"]}
    prior = facts["outcome-indicator-prior-values-2024-report"]
    current = facts["outcome-indicator-current-values-2025-report"]

    assert prior["value"] == 26
    assert prior["reporting_year"] == 2024
    assert prior["review_status"] == "reviewed"
    assert prior["registry_path"] == (
        "data/catalog/sapporo_outcome_indicator_2024_report_values.json"
    )
    assert "最新値として表示・比較しない" in prior["interpretation_boundary"]
    assert current["value"] == 26
    assert current["reporting_year"] == 2025
    assert current["registry_path"] == (
        "data/catalog/sapporo_outcome_indicator_2025_report_values.json"
    )
    assert current["evidence_path"] == (
        "data/evidence/sapporo_outcome_indicator_2025_report_values_evidence.json"
    )
    assert "成果指標26件" in manifest["quality_boundary"]
    assert "測定レイヤー12客観系/14自己申告系" in manifest["quality_boundary"]
    assert manifest["status"] == "reviewed_at_declared_depth"
