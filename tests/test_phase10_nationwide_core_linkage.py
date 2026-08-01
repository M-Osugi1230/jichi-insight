from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data/catalog/phase10_nationwide_core_linkage.json"
SCHEMA_PATH = ROOT / "schemas/phase10_nationwide_core_linkage.schema.json"

ALL_CODES = [f"{value:02d}" for value in range(1, 48)]
CORE_DIMENSIONS = {
    "annual_actuals",
    "budget",
    "settlement",
    "priority_projects",
    "audit",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def expand_links(catalog: dict) -> dict[str, dict[str, dict]]:
    expanded: dict[str, dict[str, dict]] = defaultdict(dict)
    for group in catalog["link_groups"]:
        registry = ROOT / group["source_registry"]
        assert registry.exists()
        for code in group["prefecture_codes"]:
            for dimension in group["dimensions"]:
                assert dimension not in expanded[code]
                expanded[code][dimension] = group
    return expanded


def test_nationwide_core_linkage_matches_schema():
    validator = Draft202012Validator(
        load(SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(load(CATALOG_PATH))) == []


def test_all_prefectures_have_exactly_five_core_links():
    catalog = load(CATALOG_PATH)
    expanded = expand_links(catalog)

    assert sorted(expanded) == ALL_CODES
    assert all(set(links) == CORE_DIMENSIONS for links in expanded.values())
    assert sum(len(links) for links in expanded.values()) == 47 * 5
    assert catalog["summary"]["prefecture_count"] == 47
    assert catalog["summary"]["linked_prefecture_count"] == 47


def test_dimension_summary_is_derived_from_expanded_links():
    catalog = load(CATALOG_PATH)
    expanded = expand_links(catalog)
    counts = Counter(
        dimension
        for links in expanded.values()
        for dimension in links
    )

    assert catalog["summary"]["linked_dimension_counts"] == {
        dimension: counts[dimension]
        for dimension in (
            "annual_actuals",
            "budget",
            "settlement",
            "priority_projects",
            "audit",
        )
    }


def test_every_group_resolves_to_reviewed_source_role_and_period():
    catalog = load(CATALOG_PATH)

    for group in catalog["link_groups"]:
        registry = load(ROOT / group["source_registry"])
        if group["source_registry"].endswith("miyagi_policy_review_manifest.json"):
            packages = {item["id"]: item for item in registry["work_packages"]}
            assert registry["prefecture_code"] == "04"
            assert packages["evaluation_linkage"]["status"] == "completed"
            assert registry["actual_linked_indicator_series_count"] > 0
            continue

        records_by_code = {
            record["prefecture_code"]: record
            for record in registry["records"]
            if record["prefecture_code"] in group["prefecture_codes"]
        }
        assert set(records_by_code) == set(group["prefecture_codes"])

        for code, record in records_by_code.items():
            if "sources" in record:
                sources = record["sources"]
                for dimension in group["dimensions"]:
                    source = sources[dimension]
                    assert source["url"].startswith("https://")
                    assert len(source["official_owner"]) >= 4
                    assert len(source["reporting_period"]) >= 4
                    assert len(source["claim"]) >= 20
                    assert len(source["boundary"]) >= 20
            else:
                records = [
                    item
                    for item in registry["records"]
                    if item["prefecture_code"] == code
                    and item["dimension"] in group["dimensions"]
                ]
                assert {item["dimension"] for item in records} == set(
                    group["dimensions"]
                )
                for item in records:
                    assert item["url"].startswith("https://")
                    assert len(item["official_owner"]) >= 4
                    assert len(item["reporting_period"]) >= 4
                    assert len(item["claims"][0]) >= 20
                    assert len(item["boundary"]) >= 20


def test_document_scope_does_not_claim_record_level_completion():
    catalog = load(CATALOG_PATH)

    assert "does not assert" in catalog["linkage_definition"]
    assert "Unresolved one-to-one" in catalog["record_level_boundary"]
    assert catalog["policy_achievement_assessment_status"] == "not_assessed"
    assert catalog["summary"]["policy_achievement_assessment_count"] == 0
    assert all(
        group["linkage_level"] == "document_scope"
        or group["source_registry"].endswith("miyagi_policy_review_manifest.json")
        for group in catalog["link_groups"]
    )


def test_deeper_evidence_paths_exist_without_becoming_nationwide_requirement():
    catalog = load(CATALOG_PATH)
    deeper = catalog["deeper_record_level_evidence"]

    assert set(deeper) == {"01", "04", "13", "40"}
    for paths in deeper.values():
        assert paths
        assert all((ROOT / path).exists() for path in paths)
