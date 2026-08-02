from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts/normalize_phase11_tokyo.py"
SCHEMA_PATH = ROOT / "schemas/phase11_record_linkage.schema.json"
MANIFEST_PATH = ROOT / "data/catalog/phase11_tokyo_normalization.json"
MANIFEST_SCHEMA_PATH = ROOT / "schemas/phase11_tokyo_normalization.schema.json"
SOURCE_PATH = ROOT / "data/catalog/tokyo_children_annual_actual_linkage.json"

spec = importlib.util.spec_from_file_location(
    "normalize_phase11_tokyo",
    SCRIPT_PATH,
)
assert spec is not None
assert spec.loader is not None
normalizer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(normalizer)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def normalized_catalog() -> dict:
    return normalizer.build_catalog(ROOT)


def normalized_conflict(conflict: dict | None) -> dict | None:
    if conflict is None:
        return None
    return {
        "source_value": conflict.get("source_value"),
        "source_period": conflict.get("source_period"),
        "catalog_value": conflict.get("catalog_value"),
        "catalog_period": conflict.get("catalog_period"),
    }


def expected_components(source: dict) -> list[dict]:
    return [
        {
            "record_ref": series["series_id"],
            "catalog_role": series["catalog_role"],
            "label": series["series_label"],
            "unit": series["unit"],
            "value_text": series["actual_value_text"],
            "value": series["actual_value"],
            "value_status": series["value_status"],
        }
        for series in source["linked_series"]
    ]


def test_tokyo_normalization_manifest_matches_schema():
    validator = Draft202012Validator(
        load(MANIFEST_SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    manifest = load(MANIFEST_PATH)

    assert list(validator.iter_errors(manifest)) == []
    for path_field in (
        "source_catalog",
        "normalizer",
        "record_schema",
        "regression_test",
    ):
        assert (ROOT / manifest[path_field]).exists()


def test_all_eight_records_match_the_reusable_phase11_schema():
    validator = Draft202012Validator(load(SCHEMA_PATH))
    catalog = normalized_catalog()

    assert len(catalog["records"]) == 8
    for record in catalog["records"]:
        assert list(validator.iter_errors(record)) == []


def test_order_ids_statuses_and_series_counts_are_preserved():
    source = load(SOURCE_PATH)
    catalog = normalized_catalog()
    records = catalog["records"]

    assert [record["subject"]["sequence"] for record in records] == list(
        range(1, 9)
    )
    assert [record["source_record_id"] for record in records] == [
        record["id"] for record in source["records"]
    ]
    assert len({record["id"] for record in records}) == 8

    statuses = Counter(record["linkage_status"] for record in records)
    assert statuses == {"linked": 6, "partial": 2}
    assert sum(
        len(record["measurements"][0]["components"])
        for record in records
    ) == 7

    manifest = load(MANIFEST_PATH)
    assert catalog["summary"] == {
        "record_count": 8,
        "linked_record_count": 6,
        "partial_record_count": 2,
        "not_linked_record_count": 0,
        "linked_series_count": 7,
        "partial_reason_counts": manifest["partial_reason_counts"],
        "policy_achievement_assessment_count": 0,
    }


def test_every_source_field_is_mapped_or_retained():
    source = load(SOURCE_PATH)
    normalized_by_source_id = {
        record["source_record_id"]: record
        for record in normalized_catalog()["records"]
    }

    for source_record in source["records"]:
        record = normalized_by_source_id[source_record["id"]]
        actual = record["measurements"][0]
        linked = source_record["linkage_status"] == "linked"
        periods = list(
            dict.fromkeys(
                series["actual_period"]
                for series in source_record["linked_series"]
            )
        )

        assert record["partial_reason"] == source_record["partial_reason"]
        assert record["subject"] == {
            "record_ref": source_record["target_id"],
            "sequence": source_record["target_group_number"],
            "name": source_record["target_name"],
            "source_name": source_record["source_alias"],
            "definition": "",
            "hierarchy_refs": [
                f"tokyo-policy-area-{source['policy_area_code']}"
            ],
        }
        assert record["conflict"] == normalized_conflict(
            source_record["conflict"]
        )
        assert actual == {
            "role": "annual_actual",
            "status": "available" if linked else "not_promoted",
            "period_text": " / ".join(periods) if linked else "",
            "value_text": (
                " / ".join(
                    series["actual_value_text"]
                    for series in source_record["linked_series"]
                )
                if linked
                else ""
            ),
            "components": (
                expected_components(source_record) if linked else []
            ),
            "evidence": {
                "source_number": 2,
                "page": source_record["source_pdf_page"],
            },
        }
        assert record["evidence"] == {
            "primary_source_number": 2,
            "primary_page": source_record["source_pdf_page"],
            "locations": [
                {
                    "source_number": 2,
                    "page": source_record["source_pdf_page"],
                    "is_reprint": False,
                }
            ],
        }
        assert record["boundary"] == source_record["boundary"]
        assert record["evaluation_status"] == "not_assessed"
        assert record["comparability_status"] == "excluded_until_verified"


def test_linked_series_retain_identity_value_unit_and_period():
    source = load(SOURCE_PATH)
    source_by_id = {record["id"]: record for record in source["records"]}
    linked_records = [
        record
        for record in normalized_catalog()["records"]
        if record["linkage_status"] == "linked"
    ]

    assert len(linked_records) == 6
    for record in linked_records:
        source_record = source_by_id[record["source_record_id"]]
        actual = record["measurements"][0]
        assert record["partial_reason"] is None
        assert record["conflict"] is None
        assert actual["components"] == expected_components(source_record)
        assert actual["components"]


def test_partial_records_keep_both_official_source_conflicts():
    source = load(SOURCE_PATH)
    source_by_id = {record["id"]: record for record in source["records"]}
    partial_records = [
        record
        for record in normalized_catalog()["records"]
        if record["linkage_status"] == "partial"
    ]

    assert Counter(record["partial_reason"] for record in partial_records) == {
        "reporting_period_conflict": 1,
        "actual_value_and_period_conflict": 1,
    }
    for record in partial_records:
        source_record = source_by_id[record["source_record_id"]]
        assert record["conflict"] == normalized_conflict(
            source_record["conflict"]
        )
        assert record["conflict"] is not None
        assert record["measurements"] == [
            {
                "role": "annual_actual",
                "status": "not_promoted",
                "period_text": "",
                "value_text": "",
                "components": [],
                "evidence": {
                    "source_number": 2,
                    "page": source_record["source_pdf_page"],
                },
            }
        ]
        assert "上書きせず接続を保留" in record["boundary"]


def test_source_roles_and_versions_remain_separate():
    source = load(SOURCE_PATH)
    catalog = normalized_catalog()

    assert catalog["sources"] == [
        {
            "source_number": 1,
            "role": "target_catalog",
            "title": source["target_source_version"],
            "url": source["target_source_url"],
        },
        {
            "source_number": 2,
            "role": "annual_review",
            "title": source["review_source_version"],
            "url": source["review_source_url"],
        },
    ]


def test_normalization_is_deterministic():
    assert normalizer.build_catalog(ROOT) == normalizer.build_catalog(ROOT)
