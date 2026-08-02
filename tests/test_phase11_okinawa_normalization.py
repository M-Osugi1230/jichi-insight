from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts/normalize_phase11_okinawa.py"
SCHEMA_PATH = ROOT / "schemas/phase11_record_linkage.schema.json"
MANIFEST_PATH = ROOT / "data/catalog/phase11_okinawa_normalization.json"
MANIFEST_SCHEMA_PATH = ROOT / "schemas/phase11_okinawa_normalization.schema.json"
SOURCE_MANIFEST_PATH = (
    ROOT / "data/catalog/okinawa_midterm_indicator_review_manifest.json"
)

spec = importlib.util.spec_from_file_location(
    "normalize_phase11_okinawa",
    SCRIPT_PATH,
)
assert spec is not None
assert spec.loader is not None
normalizer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(normalizer)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def source_records() -> list[tuple[str, dict]]:
    return normalizer.load_records(ROOT)


def normalized_catalog() -> dict:
    return normalizer.build_catalog(ROOT)


def measurement_by_role(record: dict) -> dict[str, dict]:
    return {
        measurement["role"]: measurement
        for measurement in record["measurements"]
    }


def test_okinawa_manifest_matches_schema_and_paths_exist():
    validator = Draft202012Validator(
        load(MANIFEST_SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    manifest = load(MANIFEST_PATH)

    assert list(validator.iter_errors(manifest)) == []
    for path in manifest["source_catalogs"]:
        assert (ROOT / path).exists()
    for field in ("source_review_manifest", "normalizer", "record_schema"):
        assert (ROOT / manifest[field]).exists()


def test_all_375_records_match_the_shared_phase11_schema():
    validator = Draft202012Validator(
        load(SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    records = normalized_catalog()["records"]

    assert len(records) == 375
    for record in records:
        assert list(validator.iter_errors(record)) == []


def test_four_source_files_are_complete_without_skips():
    source = [record for _, record in source_records()]
    major = [record for record in source if record["indicator_level"] == "major"]
    outcome = [record for record in source if record["indicator_level"] == "outcome"]
    normalized = normalized_catalog()["records"]

    assert len(major) == 36
    assert len(outcome) == 339
    assert [record["sequence"] for record in major] == list(range(1, 37))
    assert [record["sequence"] for record in outcome] == list(range(1, 340))
    assert [record["id"] for record in major] == [
        f"okinawa-midterm-major-{number:03d}" for number in range(1, 37)
    ]
    assert [record["id"] for record in outcome] == [
        f"okinawa-midterm-outcome-{number:03d}" for number in range(1, 340)
    ]
    assert len({record["id"] for record in normalized}) == 375
    assert len({record["source_record_id"] for record in normalized}) == 375


def test_every_source_field_is_retained_exactly():
    source_by_id = {
        record["id"]: (source_registry, record)
        for source_registry, record in source_records()
    }
    normalized_by_id = {
        record["source_record_id"]: record
        for record in normalized_catalog()["records"]
    }

    for source_id, (source_registry, source) in source_by_id.items():
        record = normalized_by_id[source_id]
        measurements = measurement_by_role(record)
        note = json.loads(record["indicator_context"]["quality_note"])

        assert record["source_registry"] == source_registry
        assert record["subject"] == {
            "record_ref": source["id"],
            "sequence": source["sequence"],
            "name": source["indicator_name_original"],
            "source_name": source["indicator_name_original"],
            "definition": source["rationale_source_original"],
            "hierarchy_refs": [
                f"okinawa-level-{source['indicator_level']}",
                f"okinawa-policy-{source['policy_code_original']}",
            ],
        }
        assert record["indicator_context"]["policy_direction_code"] == source[
            "policy_code_original"
        ]
        assert record["indicator_context"]["policy_direction_name"] == source[
            "policy_title_original"
        ]
        assert record["indicator_context"]["source_page"] == source[
            "source_pdf_page"
        ]
        assert record["indicator_context"]["linked_current_series_count"] == 0
        assert record["indicator_context"]["target_series_count"] == 1
        assert note == {
            "evidence_id": source["evidence_id"],
            "indicator_level": source["indicator_level"],
            "policy_code_original": source["policy_code_original"],
            "rationale_source_original": source[
                "rationale_source_original"
            ],
            "national_current_original": source[
                "national_current_original"
            ],
            "national_comparison_status": source[
                "national_comparison_status"
            ],
            "island_indicator_original": source[
                "island_indicator_original"
            ],
            "sdgs_priority_original": source[
                "sdgs_priority_original"
            ],
            "is_island_indicator": source["is_island_indicator"],
            "has_sdgs_priority": source["has_sdgs_priority"],
            "target_value_kind": source["target_value_kind"],
            "source_value_note": source["source_value_note"],
            "source_table_row": source["source_table_row"],
            "maximum_depth": "plan_baseline_to_r9_target",
        }
        assert measurements["plan_current"]["value_text"] == source[
            "baseline_original"
        ]
        assert measurements["final_target"]["value_text"] == source[
            "target_r9_original"
        ]
        assert record["evidence"]["primary_page"] == source["source_pdf_page"]


def test_plan_baselines_are_never_promoted_to_annual_actuals():
    source_by_id = {record["id"]: record for _, record in source_records()}
    for record in normalized_catalog()["records"]:
        source = source_by_id[record["source_record_id"]]
        measurements = measurement_by_role(record)
        baseline = measurements["plan_current"]
        actual = measurements["annual_actual"]

        assert baseline["value_text"] == source["baseline_original"]
        assert baseline["status"] == "reported"
        assert actual == {
            "role": "annual_actual",
            "status": "not_available",
            "period_text": "",
            "value_text": "",
            "components": [],
            "evidence": {"source_number": None, "page": None},
        }
        assert record["linkage_status"] == "partial"
        assert record["partial_reason"] == "annual_actual_not_reviewed"


def test_reference_attributes_and_summary_match_review_manifest():
    source = [record for _, record in source_records()]
    review_manifest = load(SOURCE_MANIFEST_PATH)
    catalog = normalized_catalog()
    summary = catalog["summary"]
    levels = Counter(record["indicator_level"] for record in source)
    comparisons = Counter(
        record["national_comparison_status"] for record in source
    )
    target_kinds = Counter(record["target_value_kind"] for record in source)

    assert levels == Counter({"outcome": 339, "major": 36})
    assert summary["major_indicator_count"] == 36
    assert summary["outcome_indicator_count"] == 339
    assert summary["island_indicator_count"] == 32
    assert summary["sdgs_priority_indicator_count"] == 43
    assert summary["qualitative_target_count"] == 9
    assert summary["national_comparison_provided_count"] == 174
    assert summary["national_comparison_unavailable_count"] == 201
    assert summary["source_value_note_count"] == 1
    assert comparisons == Counter({"unavailable": 201, "provided": 174})
    assert target_kinds["qualitative"] == 9
    assert review_manifest["reviewed_indicator_count"] == 375
    assert review_manifest["major_indicator_count"] == 36
    assert review_manifest["outcome_indicator_count"] == 339
    assert review_manifest["island_indicator_count"] == 32
    assert review_manifest["sdgs_priority_indicator_count"] == 43
    assert review_manifest["qualitative_target_count"] == 9
    assert review_manifest["national_comparison_provided_count"] == 174
    assert review_manifest["source_value_note_count"] == 1


def test_single_source_anomaly_is_preserved_without_correction():
    source_notes = [
        record for _, record in source_records() if record["source_value_note"]
    ]
    assert len(source_notes) == 1
    source = source_notes[0]
    assert source["id"] == "okinawa-midterm-outcome-001"

    normalized = next(
        record
        for record in normalized_catalog()["records"]
        if record["source_record_id"] == source["id"]
    )
    measurements = measurement_by_role(normalized)
    note = json.loads(normalized["indicator_context"]["quality_note"])

    assert measurements["final_target"]["value_text"] == source[
        "target_r9_original"
    ]
    assert note["source_value_note"] == source["source_value_note"]
    assert "不整合" in normalized["boundary"]


def test_all_records_remain_partial_unassessed_and_noncomparable():
    catalog = normalized_catalog()
    statuses = Counter(
        record["linkage_status"] for record in catalog["records"]
    )

    assert statuses == Counter({"partial": 375})
    assert catalog["summary"]["annual_actual_available_count"] == 0
    assert catalog["summary"]["annual_actual_unavailable_count"] == 375
    for record in catalog["records"]:
        assert record["evaluation_status"] == "not_assessed"
        assert record["comparability_status"] == "excluded_until_verified"
        assert "基準値をannual actualへ昇格せず" in record["boundary"]


def test_normalization_is_deterministic():
    assert normalizer.build_catalog(ROOT) == normalizer.build_catalog(ROOT)
