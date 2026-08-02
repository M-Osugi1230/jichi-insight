from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts/normalize_phase11_fukushima.py"
SOURCE_PATH = ROOT / "data/reviewed/phase9/07.json"
SUMMARY_PATH = ROOT / "data/catalog/phase9_review_summary.json"
RECORD_SCHEMA_PATH = ROOT / "schemas/phase11_record_linkage.schema.json"
MANIFEST_PATH = ROOT / "data/catalog/phase11_fukushima_normalization.json"
MANIFEST_SCHEMA_PATH = ROOT / "schemas/phase11_fukushima_normalization.schema.json"

spec = importlib.util.spec_from_file_location(
    "normalize_phase11_fukushima", SCRIPT_PATH
)
assert spec is not None
assert spec.loader is not None
normalizer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(normalizer)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def catalog() -> dict:
    return normalizer.build_catalog(ROOT)


def measurements(record: dict) -> dict[str, dict]:
    return {item["role"]: item for item in record["measurements"]}


def test_manifest_matches_schema_and_all_paths_exist():
    manifest = load(MANIFEST_PATH)
    validator = Draft202012Validator(
        load(MANIFEST_SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(manifest)) == []
    for field in (
        "source_catalog",
        "normalizer",
        "shared_normalizer",
        "record_schema",
    ):
        assert (ROOT / manifest[field]).exists()


def test_phase9_summary_and_source_reconcile_to_1500():
    source = load(SOURCE_PATH)
    summary_entry = next(
        item
        for item in load(SUMMARY_PATH)["records"]
        if item["prefecture_code"] == "07"
    )

    assert source["prefecture_code"] == "07"
    assert source["reviewed_target_statement_count"] == 1500
    assert source["evidence_packet_count"] == 1500
    assert len(source["records"]) == 1500
    assert summary_entry["reviewed_target_statement_count"] == 1500
    assert summary_entry["evidence_packet_count"] == 1500
    assert summary_entry["document_count"] == 1
    assert summary_entry["extraction_error_count"] == 0


def test_all_1500_records_validate_and_sequences_are_complete():
    source_records = load(SOURCE_PATH)["records"]
    records = catalog()["records"]
    validator = Draft202012Validator(
        load(RECORD_SCHEMA_PATH), format_checker=FormatChecker()
    )

    assert [item["display_order"] for item in source_records] == list(
        range(1, 1501)
    )
    assert [item["subject"]["sequence"] for item in records] == list(
        range(1, 1501)
    )
    assert [item["source_record_id"] for item in records] == [
        item["id"] for item in source_records
    ]
    assert len({item["id"] for item in records}) == 1500
    assert len({item["source_record_id"] for item in records}) == 1500
    assert all(
        isinstance(item["source_location"].get("page"), int)
        for item in source_records
    )
    for record in records:
        assert list(validator.iter_errors(record)) == []


def test_every_reviewed_source_field_is_retained():
    source_by_id = {
        item["id"]: item for item in load(SOURCE_PATH)["records"]
    }
    normalized_by_id = {
        item["source_record_id"]: item for item in catalog()["records"]
    }

    for source_id, source_record in source_by_id.items():
        record = normalized_by_id[source_id]
        actual = measurements(record)
        note = json.loads(record["indicator_context"]["quality_note"])
        page = source_record["source_location"]["page"]

        assert record["subject"]["name"] == source_record[
            "indicator_name_original"
        ]
        assert record["indicator_context"]["source_page"] == page
        assert actual["plan_current"]["value_text"] == source_record[
            "target_statement_original"
        ]
        assert actual["plan_current"]["components"][0][
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


def test_all_records_remain_partial_unassessed_and_noncomparable():
    for record in catalog()["records"]:
        actual = measurements(record)
        assert record["linkage_status"] == "partial"
        assert record["partial_reason"] == (
            "structured_actual_and_target_not_reviewed"
        )
        for role in ("annual_actual", "final_target"):
            assert actual[role]["status"] == "not_available"
            assert actual[role]["components"] == []
            assert actual[role]["evidence"] == {
                "source_number": None,
                "page": None,
            }
        assert record["evaluation_status"] == "not_assessed"
        assert record["comparability_status"] == "excluded_until_verified"
        assert "復興" in record["boundary"]


def test_dynamic_counts_and_summary_are_exact():
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
        "record_count": 1500,
        "linked_record_count": 0,
        "partial_record_count": 1500,
        "not_linked_record_count": 0,
        "indicator_series_count": 1500,
        "source_document_count": len(documents),
        "missing_unit_record_count": missing_units,
        "annual_actual_available_count": 0,
        "future_target_available_count": 0,
        "reviewed_maximum_depth_record_count": 1500,
        "policy_achievement_assessment_count": 0,
    }
    assert normalized["document_record_counts"] == dict(sorted(documents.items()))
    assert normalized["source_location_counts"] == dict(sorted(locations.items()))
    assert sum(normalized["document_record_counts"].values()) == 1500


def test_normalization_is_deterministic():
    assert normalizer.build_catalog(ROOT) == normalizer.build_catalog(ROOT)
