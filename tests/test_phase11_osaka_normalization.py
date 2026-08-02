from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts/normalize_phase11_osaka.py"
SOURCE_PATH = ROOT / "data/reviewed/osaka_beyond_expo_indicators.json"
SOURCE_MANIFEST_PATH = (
    ROOT / "data/catalog/osaka_beyond_expo_indicator_review_manifest.json"
)
SCHEMA_PATH = ROOT / "schemas/phase11_record_linkage.schema.json"
MANIFEST_PATH = ROOT / "data/catalog/phase11_osaka_normalization.json"
MANIFEST_SCHEMA_PATH = ROOT / "schemas/phase11_osaka_normalization.schema.json"

spec = importlib.util.spec_from_file_location(
    "normalize_phase11_osaka",
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


def series_has_current(series: dict) -> bool:
    return any(
        value["role"] == "current" and value["status"] != "missing"
        for value in series["values"]
    )


def expected_partial_reasons(row: dict) -> list[str]:
    reasons: list[str] = []
    if row["indicator_layer"] == "strategy_target":
        reasons.append("target_without_current_observation")
    if (
        any(not series_has_current(series) for series in row["series"])
        and row["indicator_layer"] != "strategy_target"
    ):
        reasons.append("missing_current_series")
    return reasons


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
        "label": series["label_original"],
        "unit": series["unit_original"],
        "period_text": value["period"],
        "value_text": value["value_text_original"],
        "value": value["value"],
        "value_status": (
            "numeric" if value["status"] == "numeric" else "missing"
        ),
        "source_status": value["status"],
        "scope": value["aggregation_scope"],
        "aggregation_scope": value["aggregation_scope"],
        "preferred_direction": series["direction"],
        "operator": value["operator"],
    }


def expected_components(row: dict, role: str) -> list[dict]:
    output: list[dict] = []
    for series_index, series in enumerate(row["series"], start=1):
        role_values = [
            value for value in series["values"] if value["role"] == role
        ]
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


def test_osaka_manifest_matches_schema_and_paths_exist():
    validator = Draft202012Validator(
        load(MANIFEST_SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    manifest = load(MANIFEST_PATH)

    assert list(validator.iter_errors(manifest)) == []
    for field in (
        "source_catalog",
        "source_review_manifest",
        "normalizer",
        "record_schema",
    ):
        assert (ROOT / manifest[field]).exists()


def test_all_83_rows_match_the_shared_phase11_schema():
    validator = Draft202012Validator(
        load(SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    records = normalized_catalog()["records"]

    assert len(records) == 83
    for record in records:
        assert list(validator.iter_errors(record)) == []


def test_order_ids_layers_and_series_are_complete_without_skips():
    original = source()
    source_manifest = load(SOURCE_MANIFEST_PATH)
    catalog = normalized_catalog()
    records = catalog["records"]

    assert [row["display_order"] for row in original["items"]] == list(
        range(1, 84)
    )
    assert [record["subject"]["sequence"] for record in records] == list(
        range(1, 84)
    )
    assert [record["source_record_id"] for record in records] == [
        row["id"] for row in original["items"]
    ]
    assert len({record["id"] for record in records}) == 83
    assert sum(len(row["series"]) for row in original["items"]) == 91
    assert sum(len(record["indicator_context"]["series"]) for record in records) == 91
    assert catalog["summary"]["record_count"] == original["indicator_row_count"]
    assert catalog["summary"]["indicator_series_count"] == original[
        "indicator_series_count"
    ]
    assert source_manifest["reviewed_indicator_row_count"] == 83
    assert source_manifest["reviewed_indicator_series_count"] == 91


def test_every_source_value_is_mapped_field_for_field():
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
        assert record["partial_reason"] == (
            "+".join(reasons) if reasons else None
        )
        assert record["subject"]["record_ref"] == row["id"]
        assert record["subject"]["sequence"] == row["display_order"]
        assert record["subject"]["name"] == row["indicator_name_original"]
        assert record["subject"]["definition"] == row[
            "comparability_note_original"
        ]
        assert record["subject"]["hierarchy_refs"] == [
            f"osaka-layer-{row['indicator_layer']}",
            f"osaka-pillar-{row['pillar_original']}",
            f"osaka-category-{row['category_original']}",
        ]
        assert record["indicator_context"]["policy_direction_code"] == row[
            "indicator_layer"
        ]
        assert record["indicator_context"]["policy_direction_name"] == row[
            "pillar_original"
        ]
        assert record["indicator_context"]["source_page"] == row["source_page"]
        assert record["indicator_context"]["target_revision_status"] == (
            "not_applicable"
        )
        context_note = json.loads(record["indicator_context"]["quality_note"])
        assert context_note == {
            "category_original": row["category_original"],
            "response_scale": row["response_scale"],
            "legacy_vision_linkage_status": row[
                "legacy_vision_linkage_status"
            ],
            "business_list_linkage_status": row[
                "business_list_linkage_status"
            ],
            "confidence": row["confidence"],
            "comparability_note_original": row[
                "comparability_note_original"
            ],
        }

        expected_series = [
            {
                "series_ref": f"{row['id']}-series-{index:02d}",
                "label": series["label_original"],
                "unit": series["unit_original"],
                "direction": series["direction"],
                "comparability_note": row[
                    "comparability_note_original"
                ],
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


def test_all_values_appear_exactly_once():
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


def test_linked_and_partial_counts_match_reviewed_source_boundaries():
    original = source()
    source_manifest = load(SOURCE_MANIFEST_PATH)
    catalog = normalized_catalog()
    records = catalog["records"]
    statuses = Counter(record["linkage_status"] for record in records)
    layers = Counter(row["indicator_layer"] for row in original["items"])

    assert layers["strategy_target"] == 1
    assert layers["objective_kpi"] == 27
    assert layers["subjective_wellbeing"] == 55
    assert statuses == Counter({"linked": 77, "partial": 6})
    assert catalog["summary"]["linked_record_count"] == 77
    assert catalog["summary"]["partial_record_count"] == 6
    assert catalog["summary"]["not_linked_record_count"] == 0
    assert catalog["summary"]["rows_with_current_observation"] == 77
    assert catalog["summary"]["rows_without_current_observation"] == 6
    assert source_manifest["subjective_indicators_with_2024_value"] == 50
    assert source_manifest["subjective_indicators_pending_first_survey"] == 5


def test_partial_rows_are_only_target_or_missing_first_observation():
    original_by_id = {row["id"]: row for row in source()["items"]}
    partial_records = [
        record
        for record in normalized_catalog()["records"]
        if record["linkage_status"] == "partial"
    ]

    assert len(partial_records) == 6
    reasons = Counter(record["partial_reason"] for record in partial_records)
    assert reasons == Counter(
        {
            "target_without_current_observation": 1,
            "missing_current_series": 5,
        }
    )
    for record in partial_records:
        row = original_by_id[record["source_record_id"]]
        current = measurement_by_role(record)["annual_actual"]
        if row["indicator_layer"] == "strategy_target":
            assert current["status"] == "not_available"
        else:
            assert all(
                component["value_status"] == "missing"
                for component in current["components"]
            )
            assert current["status"] == "not_available"
        assert "Partial" in record["boundary"]


def test_lineage_business_and_assessment_boundaries_are_not_promoted():
    original = source()
    records = normalized_catalog()["records"]

    assert all(
        row["legacy_vision_linkage_status"] == "separate_lineage"
        for row in original["items"]
    )
    assert all(
        row["business_list_linkage_status"] == "not_linked"
        for row in original["items"]
    )
    for record in records:
        assert record["evaluation_status"] == "not_assessed"
        assert record["comparability_status"] == "excluded_until_verified"
        assert "政策達成" in record["boundary"]


def test_normalization_is_deterministic():
    assert normalizer.build_catalog(ROOT) == normalizer.build_catalog(ROOT)
