from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts/normalize_phase11_yamagata.py"
SOURCE_PATH = ROOT / "data/reviewed/phase9/06.json"
PHASE9_SUMMARY_PATH = ROOT / "data/catalog/phase9_review_summary.json"
RECORD_SCHEMA_PATH = ROOT / "schemas/phase11_record_linkage.schema.json"
MANIFEST_PATH = ROOT / "data/catalog/phase11_yamagata_normalization.json"
MANIFEST_SCHEMA_PATH = ROOT / "schemas/phase11_yamagata_normalization.schema.json"

spec = importlib.util.spec_from_file_location(
    "normalize_phase11_yamagata", SCRIPT_PATH
)
assert spec is not None
assert spec.loader is not None
normalizer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(normalizer)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def catalog() -> dict:
    return normalizer.build_catalog(ROOT)


def measurement_by_role(record: dict) -> dict[str, dict]:
    return {
        measurement["role"]: measurement
        for measurement in record["measurements"]
    }


def test_yamagata_manifest_matches_schema_and_paths_exist():
    validator = Draft202012Validator(
        load(MANIFEST_SCHEMA_PATH), format_checker=FormatChecker()
    )
    manifest = load(MANIFEST_PATH)
    assert list(validator.iter_errors(manifest)) == []
    for field in ("source_catalog", "normalizer", "record_schema"):
        assert (ROOT / manifest[field]).exists()


def test_phase9_summary_and_large_source_reconcile_to_807():
    source = load(SOURCE_PATH)
    review_summary = load(PHASE9_SUMMARY_PATH)
    summary_entry = next(
        item
        for item in review_summary["records"]
        if item["prefecture_code"] == "06"
    )

    assert source["prefecture_code"] == "06"
    assert source["reviewed_target_statement_count"] == 807
    assert source["evidence_packet_count"] == 807
    assert len(source["records"]) == 807
    assert summary_entry["reviewed_target_statement_count"] == 807
    assert summary_entry["evidence_packet_count"] == 807
    assert summary_entry["document_count"] == 4
    assert summary_entry["extraction_error_count"] == 0


def test_all_records_validate_and_sequences_are_complete():
    source = load(SOURCE_PATH)
    source_records = source["records"]
    records = catalog()["records"]
    validator = Draft202012Validator(
        load(RECORD_SCHEMA_PATH), format_checker=FormatChecker()
    )

    assert len(records) == 807
    assert [item["display_order"] for item in source_records] == list(
        range(1, 808)
    )
    assert [item["subject"]["sequence"] for item in records] == list(
        range(1, 808)
    )
    assert [item["source_record_id"] for item in records] == [
        item["id"] for item in source_records
    ]
    assert len({item["id"] for item in records}) == 807
    assert len({item["source_record_id"] for item in records}) == 807
    assert all(
        isinstance(item["source_location"].get("page"), int)
        for item in source_records
    )
    for record in records:
        assert list(validator.iter_errors(record)) == []


def test_every_reviewed_field_is_retained_exactly():
    source_by_id = {
        item["id"]: item for item in load(SOURCE_PATH)["records"]
    }
    normalized_by_id = {
        item["source_record_id"]: item for item in catalog()["records"]
    }

    for source_id, source_record in source_by_id.items():
        record = normalized_by_id[source_id]
        measurements = measurement_by_role(record)
        note = json.loads(record["indicator_context"]["quality_note"])
        page = source_record["source_location"]["page"]

        assert record["subject"]["name"] == source_record[
            "indicator_name_original"
        ]
        assert record["subject"]["definition"] == source_record[
            "plan_history_boundary"
        ]
        assert record["indicator_context"]["source_page"] == page
        assert record["indicator_context"]["policy_direction_name"] == (
            source_record["source_document_title"]
        )
        assert measurements["plan_current"]["value_text"] == source_record[
            "target_statement_original"
        ]
        assert measurements["plan_current"]["period_text"] == " / ".join(
            source_record["period_tokens_original"]
        )
        assert measurements["plan_current"]["components"][0][
            "unit"
        ] == source_record["unit_original"]
        for field in (
            "source_document_url",
            "source_document_sha256",
            "source_location",
            "numeric_tokens_original",
            "period_tokens_original",
            "matched_keywords",
            "keyword_match_kind",
            "unit_original",
            "population_scope_original",
            "aggregation_scope",
            "target_operator",
            "comparability",
        ):
            assert note[field] == source_record[field]
        assert record["evidence"]["primary_page"] == page


def test_raw_statements_remain_partial_without_inferred_values():
    for record in catalog()["records"]:
        measurements = measurement_by_role(record)
        assert record["linkage_status"] == "partial"
        assert record["partial_reason"] == (
            "structured_actual_and_target_not_reviewed"
        )
        for role in ("annual_actual", "final_target"):
            assert measurements[role] == {
                "role": role,
                "status": "not_available",
                "period_text": "",
                "value_text": "",
                "components": [],
                "evidence": {"source_number": None, "page": None},
            }
        assert record["indicator_context"]["linked_current_series_count"] == 0
        assert record["indicator_context"]["target_series_count"] == 0
        assert record["evaluation_status"] == "not_assessed"
        assert record["comparability_status"] == "excluded_until_verified"


def test_dynamic_source_counts_and_summary_are_exact():
    source_records = load(SOURCE_PATH)["records"]
    normalized = catalog()
    documents = Counter(
        item["source_document_title"] for item in source_records
    )
    locations = Counter(
        item["source_location"]["location_kind"] for item in source_records
    )
    missing_units = sum(item["unit_original"] is None for item in source_records)

    assert normalized["summary"] == {
        "record_count": 807,
        "linked_record_count": 0,
        "partial_record_count": 807,
        "not_linked_record_count": 0,
        "indicator_series_count": 807,
        "source_document_count": len(documents),
        "missing_unit_record_count": missing_units,
        "annual_actual_available_count": 0,
        "future_target_available_count": 0,
        "reviewed_maximum_depth_record_count": 807,
        "policy_achievement_assessment_count": 0,
    }
    assert normalized["document_record_counts"] == dict(sorted(documents.items()))
    assert normalized["source_location_counts"] == dict(sorted(locations.items()))
    assert sum(normalized["document_record_counts"].values()) == 807
    assert sum(normalized["source_location_counts"].values()) == 807


def test_normalization_is_deterministic():
    assert normalizer.build_catalog(ROOT) == normalizer.build_catalog(ROOT)
