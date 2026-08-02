from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts/normalize_phase11_aichi.py"
SOURCE_PATH = ROOT / "data/reviewed/aichi_policy_indicators.json"
SCHEMA_PATH = ROOT / "schemas/phase11_record_linkage.schema.json"
MANIFEST_PATH = ROOT / "data/catalog/phase11_aichi_normalization.json"
MANIFEST_SCHEMA_PATH = ROOT / "schemas/phase11_aichi_normalization.schema.json"

spec = importlib.util.spec_from_file_location(
    "normalize_phase11_aichi",
    SCRIPT_PATH,
)
assert spec is not None
assert spec.loader is not None
normalizer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(normalizer)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def source() -> dict:
    return load(SOURCE_PATH)


def normalized_catalog() -> dict:
    return normalizer.build_catalog(ROOT)


def measurement_by_role(record: dict) -> dict[str, dict]:
    return {
        measurement["role"]: measurement
        for measurement in record["measurements"]
    }


def expected_value_status(source_status: str) -> str:
    if source_status == "numeric":
        return "numeric"
    if source_status == "missing":
        return "missing"
    return "textual"


def expected_component(
    row: dict,
    series: dict,
    series_index: int,
    role: str,
    value: dict,
    value_index: int,
) -> dict:
    return {
        "record_ref": (
            f"{row['id']}-series-{series_index:02d}-"
            f"{role}-{value_index:02d}"
        ),
        "catalog_role": role,
        "label": series["label"],
        "unit": series["unit_original"],
        "period_text": value["period"],
        "value_text": value["value_text_original"],
        "value": value["value"],
        "value_status": expected_value_status(value["status"]),
        "source_status": value["status"],
        "scope": value["aggregation_scope"],
        "aggregation_scope": value["aggregation_scope"],
        "preferred_direction": series["direction"],
        "operator": value["operator"],
    }


def expected_components(row: dict, role: str) -> list[dict]:
    output: list[dict] = []
    for series_index, series in enumerate(row["series"], start=1):
        role_values = [value for value in series["values"] if value["role"] == role]
        for value_index, value in enumerate(role_values, start=1):
            output.append(
                expected_component(
                    row,
                    series,
                    series_index,
                    role,
                    value,
                    value_index,
                )
            )
    return output


def expected_partial_reasons(row: dict) -> list[str]:
    reasons: list[str] = []
    if row["linked_current_series_count"] < len(row["series"]):
        reasons.append("missing_current_series")
    if row["target_revision_status"] == "revised_in_2025_report":
        reasons.append("target_revised_in_2025_report")
    return reasons


def test_aichi_completion_manifest_matches_schema_and_paths_exist():
    validator = Draft202012Validator(
        load(MANIFEST_SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    manifest = load(MANIFEST_PATH)

    assert list(validator.iter_errors(manifest)) == []
    for field in ("source_catalog", "normalizer", "record_schema", "regression_test"):
        assert (ROOT / manifest[field]).exists()


def test_all_56_rows_match_the_shared_phase11_schema():
    validator = Draft202012Validator(
        load(SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    records = normalized_catalog()["records"]

    assert len(records) == 56
    for record in records:
        assert list(validator.iter_errors(record)) == []


def test_row_order_ids_and_series_inventory_are_complete_without_skips():
    original = source()
    catalog = normalized_catalog()
    records = catalog["records"]

    assert [row["display_order"] for row in original["items"]] == list(range(1, 57))
    assert [record["subject"]["sequence"] for record in records] == list(range(1, 57))
    assert [record["source_record_id"] for record in records] == [
        row["id"] for row in original["items"]
    ]
    assert len({record["id"] for record in records}) == 56
    assert sum(len(record["indicator_context"]["series"]) for record in records) == 62
    assert catalog["summary"]["record_count"] == original["indicator_row_count"]
    assert catalog["summary"]["indicator_series_count"] == original[
        "indicator_series_count"
    ]


def test_every_series_and_value_is_mapped_field_for_field():
    original = source()
    normalized_by_id = {
        record["source_record_id"]: record
        for record in normalized_catalog()["records"]
    }

    for row in original["items"]:
        record = normalized_by_id[row["id"]]
        measurements = measurement_by_role(record)
        reasons = expected_partial_reasons(row)
        expected_status = "partial" if reasons else "linked"

        assert record["linkage_status"] == expected_status
        assert record["partial_reason"] == ("+".join(reasons) if reasons else None)
        assert record["subject"] == {
            "record_ref": row["id"],
            "sequence": row["display_order"],
            "name": row["indicator_name_original"],
            "source_name": row["indicator_name_original"],
            "definition": "",
            "hierarchy_refs": [
                f"aichi-policy-direction-{row['policy_direction_code']}"
            ],
        }
        assert record["indicator_context"]["policy_direction_code"] == row[
            "policy_direction_code"
        ]
        assert record["indicator_context"]["policy_direction_name"] == row[
            "policy_direction_name_original"
        ]
        assert record["indicator_context"]["source_page"] == row["source_page"]
        assert record["indicator_context"]["repost_of"] == row["repost_of"]
        assert record["indicator_context"]["target_revision_status"] == row[
            "target_revision_status"
        ]
        assert record["indicator_context"]["linked_current_series_count"] == row[
            "linked_current_series_count"
        ]
        assert record["indicator_context"]["target_series_count"] == row[
            "target_series_count"
        ]
        assert record["indicator_context"]["quality_note"] == row["quality_note"]

        expected_series = [
            {
                "series_ref": f"{row['id']}-series-{index:02d}",
                "label": series["label"],
                "unit": series["unit_original"],
                "direction": series["direction"],
                "comparability_note": series["comparability_note_original"],
                "value_count": len(series["values"]),
            }
            for index, series in enumerate(row["series"], start=1)
        ]
        assert record["indicator_context"]["series"] == expected_series
        assert measurements["plan_current"]["components"] == expected_components(
            row,
            "baseline",
        )
        assert measurements["annual_actual"]["components"] == expected_components(
            row,
            "current",
        )
        assert measurements["final_target"]["components"] == expected_components(
            row,
            "target",
        )


def test_all_source_values_appear_exactly_once_in_normalized_components():
    original = source()
    expected_value_count = sum(
        len(series["values"])
        for row in original["items"]
        for series in row["series"]
    )
    normalized_components = [
        component
        for record in normalized_catalog()["records"]
        for measurement in record["measurements"]
        for component in measurement["components"]
    ]

    assert len(normalized_components) == expected_value_count
    assert len({component["record_ref"] for component in normalized_components}) == (
        expected_value_count
    )


def test_current_target_repost_and_revision_counts_match_source_summary():
    original = source()
    catalog = normalized_catalog()
    summary = catalog["summary"]

    current_values = [
        value
        for row in original["items"]
        for series in row["series"]
        for value in series["values"]
        if value["role"] == "current"
    ]
    target_series = [
        series
        for row in original["items"]
        for series in row["series"]
        if any(value["role"] == "target" for value in series["values"])
    ]

    assert sum(value["status"] != "missing" for value in current_values) == 61
    assert sum(value["status"] == "missing" for value in current_values) == 1
    assert len(target_series) == 29
    assert summary["linked_current_series_count"] == 61
    assert summary["missing_current_series_count"] == 1
    assert summary["target_series_count"] == 29
    assert summary["repost_record_count"] == 2
    assert summary["target_revision_record_count"] == 1


def test_partial_rows_keep_missing_current_and_revised_target_conditions():
    original_by_id = {row["id"]: row for row in source()["items"]}
    partial_records = [
        record
        for record in normalized_catalog()["records"]
        if record["linkage_status"] == "partial"
    ]

    assert partial_records
    for record in partial_records:
        row = original_by_id[record["source_record_id"]]
        reasons = expected_partial_reasons(row)
        assert reasons
        assert record["partial_reason"] == "+".join(reasons)
        current = measurement_by_role(record)["annual_actual"]
        if row["linked_current_series_count"] == 0:
            assert current["status"] == "not_available"
        else:
            assert current["status"] == "available_raw_only"
        assert "Partial" in record["boundary"]


def test_repost_rows_retain_original_and_repost_evidence_pages():
    original = source()
    rows_by_id = {row["id"]: row for row in original["items"]}
    normalized_by_id = {
        record["source_record_id"]: record
        for record in normalized_catalog()["records"]
    }
    reposts = [row for row in original["items"] if row["repost_of"] is not None]

    assert len(reposts) == 2
    for row in reposts:
        original_row = rows_by_id[row["repost_of"]]
        assert normalized_by_id[row["id"]]["evidence"]["locations"] == [
            {
                "source_number": 1,
                "page": original_row["source_page"],
                "is_reprint": False,
            },
            {
                "source_number": 1,
                "page": row["source_page"],
                "is_reprint": True,
            },
        ]


def test_no_record_gains_assessment_or_comparison_eligibility():
    records = normalized_catalog()["records"]
    statuses = Counter(record["linkage_status"] for record in records)

    assert statuses["linked"] + statuses["partial"] == 56
    for record in records:
        assert record["evaluation_status"] == "not_assessed"
        assert record["comparability_status"] == "excluded_until_verified"
        assert "達成・未達は判定しない" in record["boundary"]


def test_normalization_is_deterministic():
    assert normalizer.build_catalog(ROOT) == normalizer.build_catalog(ROOT)
