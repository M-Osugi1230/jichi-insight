from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALUES_PATH = ROOT / "data/catalog/sapporo_outcome_indicator_2025_report_values.json"
EVIDENCE_PATH = ROOT / "data/evidence/sapporo_outcome_indicator_2025_report_values_evidence.json"
REGISTRY_PATH = ROOT / "data/catalog/sapporo_outcome_indicator_registry.json"
MANIFEST_PATH = ROOT / "data/catalog/sapporo_phase13_policy_review_manifest.json"
QUEUE_PATH = ROOT / "data/catalog/phase13_designated_city_review_queue.json"
COMPLETION_PATH = ROOT / "data/catalog/sapporo_phase13_completion.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sapporo_current_value_registry_covers_all_26_unique_indicators_in_order():
    values = load(VALUES_PATH)
    records = values["records"]
    registry = load(REGISTRY_PATH)["records"]

    assert values["official_code"] == "011002"
    assert values["reporting_year"] == 2025
    assert values["status"] == "reviewed_current_values_complete"
    assert len(records) == 26
    assert [record["sequence"] for record in records] == list(range(1, 27))
    assert [record["id"] for record in records] == [record["id"] for record in registry]
    assert [record["name_ja"] for record in records] == [
        record["name_ja"] for record in registry
    ]
    assert values["summary"]["reviewed_indicator_count"] == 26


def test_sapporo_current_trend_counts_match_official_2025_aggregate():
    values = load(VALUES_PATH)
    counts = Counter(record["source_trend_classification"] for record in values["records"])

    assert counts == {
        "source_reported_up": 17,
        "source_reported_down": 8,
        "source_reported_unaggregated": 1,
    }
    assert values["summary"]["source_reported_up_count"] == 17
    assert values["summary"]["source_reported_down_count"] == 8
    assert values["summary"]["source_reported_unaggregated_count"] == 1


def test_sapporo_current_values_preserve_exact_children_and_daily_life_rows():
    records = {record["id"]: record for record in load(VALUES_PATH)["records"]}

    fertility = records["total_fertility_rate"]
    assert fertility["current_actual"] == {
        "value": 0.96,
        "unit": "ratio",
        "fiscal_year": 2023,
    }
    assert fertility["source_trend_classification"] == "source_reported_down"

    outmigration = records["young_adult_outmigration_excess"]
    assert outmigration["current_actual"] == {
        "value": 2650,
        "unit": "people",
        "fiscal_year": 2024,
    }

    goals = records["children_with_personal_goals"]
    assert goals["current_actual"]["value"] == 76.1
    assert goals["current_actual"]["fiscal_year"] == 2024
    assert "2023年度からの新規項目" in goals["source_note"]

    health = records["healthy_life_expectancy"]
    dimensions = {item["dimension"]: item for item in health["dimensions"]}
    assert dimensions["male"]["current_actual"] == {
        "value": 72.28,
        "unit": "years",
        "fiscal_year": 2022,
    }
    assert dimensions["female"]["current_actual"] == {
        "value": 74.03,
        "unit": "years",
        "fiscal_year": 2022,
    }

    social = records["citizens_feeling_social_role"]
    social_dimensions = {item["dimension"]: item for item in social["dimensions"]}
    assert social_dimensions["age_18_64"]["current_actual"]["value"] == 47.1
    assert social_dimensions["age_65_plus"]["current_actual"]["value"] == 44.4


def test_sapporo_current_values_preserve_economy_and_unaggregated_boundary():
    records = {record["id"]: record for record in load(VALUES_PATH)["records"]}

    gdp = records["gdp_per_capita_nominal"]
    assert gdp["current_actual"] == {
        "value": 390,
        "unit": "10k_yen_per_person",
        "fiscal_year": 2022,
    }

    winter = records["winter_tourist_count"]
    assert winter["current_actual"] == {
        "value": 374,
        "unit": "10k_people",
        "fiscal_year": 2024,
    }

    tourism = records["total_tourism_consumption"]
    assert tourism["current_actual"] == {
        "value": 6941,
        "unit": "100m_yen",
        "fiscal_year": 2024,
    }

    employment = records["employment_rate"]
    assert employment["current_actual"] == {"status": "unaggregated"}
    assert employment["source_trend_classification"] == "source_reported_unaggregated"


def test_sapporo_current_values_preserve_direction_and_target_boundaries():
    values = load(VALUES_PATH)
    records = {record["id"]: record for record in values["records"]}

    walking = records["daily_walking_minutes"]
    assert walking["current_actual"]["value"] == 67
    assert walking["target"]["value"] == 65
    assert walking["source_trend_classification"] == "source_reported_up"

    citywide_ghg = records["citywide_ghg_emissions"]
    assert citywide_ghg["current_actual"] == {
        "value": 1022,
        "unit": "10k_t_co2",
        "fiscal_year": 2022,
    }
    assert citywide_ghg["target"]["value"] == 690
    assert citywide_ghg["source_trend_classification"] == "source_reported_up"

    municipal_ghg = records["municipal_facility_ghg_emissions"]
    assert municipal_ghg["current_actual"] == {
        "value": 63.5,
        "unit": "10k_t_co2",
        "fiscal_year": 2023,
    }
    assert municipal_ghg["source_trend_classification"] == "source_reported_up"

    waste = records["waste_resource_collection_satisfaction"]
    assert waste["current_actual"]["value"] == 77.1
    assert waste["target"]["value"] == 77

    boundary = values["quality_boundary"]
    assert "not recomputed by Jichi Insight" in boundary
    assert "does not become an independent achievement judgment" in boundary
    assert "Decrease-oriented indicators" in boundary


def test_sapporo_current_values_keep_measurement_years_distinct_from_reporting_year():
    records = load(VALUES_PATH)["records"]
    fiscal_years: set[int] = set()
    for record in records:
        if "current_actual" in record and "fiscal_year" in record["current_actual"]:
            fiscal_years.add(record["current_actual"]["fiscal_year"])
        for dimension in record.get("dimensions", []):
            fiscal_years.add(dimension["current_actual"]["fiscal_year"])

    assert {2022, 2023, 2024}.issubset(fiscal_years)
    assert load(VALUES_PATH)["reporting_year"] == 2025
    assert "fiscal years" in load(VALUES_PATH)["quality_boundary"]


def test_sapporo_current_value_page_evidence_covers_exactly_26_non_repost_ids():
    evidence = load(EVIDENCE_PATH)
    records = load(VALUES_PATH)["records"]
    pages = evidence["page_evidence"]
    evidence_ids = [
        indicator_id
        for page in pages
        for indicator_id in page["indicator_ids"]
    ]

    assert evidence["reviewed_indicator_count"] == 26
    assert [page["source_page"] for page in pages] == [1, 2, 3]
    assert [len(page["indicator_ids"]) for page in pages] == [11, 7, 8]
    assert len(evidence_ids) == len(set(evidence_ids)) == 26
    assert set(evidence_ids) == {record["id"] for record in records}
    repost = evidence["repost_boundary"]
    assert repost["displayed_occurrence_count"] == 33
    assert repost["unique_indicator_count"] == 26
    assert repost["reposted_occurrence_count"] == 7
    assert len(repost["reposted_indicator_ids"]) == 7


def test_sapporo_current_outcome_layer_remains_distinct_inside_declared_v1_completion():
    manifest = load(MANIFEST_PATH)
    facts = {fact["id"]: fact for fact in manifest["reviewed_facts"]}
    current = facts["outcome-indicator-current-values-2025-report"]
    queue = load(QUEUE_PATH)
    completion = load(COMPLETION_PATH)
    sapporo = next(
        item for item in queue["execution_queue"] if item["official_code"] == "011002"
    )

    assert current["value"] == 26
    assert current["registry_path"] == (
        "data/catalog/sapporo_outcome_indicator_2025_report_values.json"
    )
    assert current["evidence_path"] == (
        "data/evidence/sapporo_outcome_indicator_2025_report_values_evidence.json"
    )
    assert manifest["status"] == "reviewed_at_declared_depth"
    assert sapporo["status"] == "reviewed_complete"
    assert completion["status"] == "reviewed_complete"
    assert completion["completion_depth"] == "declared_review_package_v1"
    assert any("395件" in item for item in manifest["deferred_extension_work"])
