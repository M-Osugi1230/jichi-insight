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
    "normalize_phase11_yamagata",
    SCRIPT_PATH,
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
        load(MANIFEST_SCHEMA_PATH),
        format_checker=FormatChecker(),
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
        for item in review_summary["prefectures"]
        if item["prefecture_code"] == "06"
    )

    assert source["prefecture_code"] == "06"
    assert source["reviewed_target_statement_count"] == 807
    assert source["evidence_packet_count"] == 807
    assert len(source["records"]) == 807
    assert summary_entry["reviewed_target_statement_count"] == 807
    assert summary_entry["evidence_packet_count"] == 807
    assert summary_entry["error_count"] == 0


def test_all_807_records_match_shared_phase11_schema():
    validator = Draft202012Validator(
        load(RECORD_SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    records = catalog()["records"]

    assert len(records) == 807
    for record in records:
        assert list(validator.iter_errors(record)) == []


def test_source_sequence_ids_and_evidence_are_complete_without_skips():
    source = load(SOURCE_PATH)
    source_records = source["records"]
    normalized = catalog()["records"]

    assert [record["display_order"] for record in source_records] == list(
        range(1, 808)
    )
    assert [record["subject"]["sequence"] for record in normalized] == list(
        range(1, 808)
    )
    assert [record["source_record_id"] for record in normalized] == [
        record["id"] for record in source_records
    ]
    assert len({record["id"] for record in normalized}) == 807
    assert len({record["source_record_id"] for record in normalized}) == 807
    assert all(
        isinstance(record["source_location"].get("page"), int)
        for record in source_records
    )


def test_every_reviewed_field_is_retained_exactly():
    source = load(SOURCE_PATH)
    source_by_id = {record["id"]: record for record in source["records"]}
    normalized_by_id = {
        record["source_record_id"]: record for record in catalog()["records"]
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
        assert measurements["plan_current"]["period_text"] == (
            " / ".join(source_record["period_tokens_original"])
        )
        assert measurements["plan_current"]["components"][0][
            "unit"
        ] == source_record["unit_original"]
        assert note["source_document_url"] == source_record[
            "source_document_url"
        ]
        assert note["source_document_sha256"] == source_record[
            "source_document_sha256"
        ]
        assert note["source_location"] == source_record["source_location"]
        assert note["numeric_tokens_original"] == source_record[
            "numeric_tokens_original"
        ]
        assert note["period_tokens_original"] == source_record[
            "period_tokens_original"
        ]
        assert note["matched_keywords"] == source_record["matched_keywords"]
        assert note["keyword_match_kind"] == source_record[
            "keyword_match_kind"
        ]
        assert note["unit_original"] == source_record["unit_original"]
        assert note["population_scope_original"] == source_record[
            "population_scope_original"
        ]
        assert note["aggregation_scope"] == source_record[
            "aggregation_scope"
        ]
        assert note["target_operator"] == source_record["target_operator"]
        assert note["comparability"] == source_record["comparability"]
        assert record["evidence"]["primary_page"] == page


def test_raw_statements_are_not_promoted_to_actual_or_structured_target():
    for record in catalog()["records"]:
        measurements = measurement_by_role(record)
        assert record["linkage_status"] == "partial"
        assert record["partial_reason"] == (
            "structured_actual_and_target_not_reviewed"
        )
        assert measurements["annual_actual"] == {
            "role": "annual_actual",
            "status": "not_available",
            "period_text": "",
            "value_text": "",
            "components": [],
            "evidence": {"source_number": None, "page": None},
        }
        assert measurements["final_target"] == {
            "role": "final_target",
            "status": "not_available",
            "period_text": "",
            "value_text": "",
            "components": [],
            "evidence": {"source_number": None, "page": None},
        }
        assert record["indicator_context"]["linked_current_series_count"] == 0
        assert record["indicator_context"]["target_series_count"] == 0


def test_documents_locations_missing_units_and_summary_are_dynamic_and_exact():
    source = load(SOURCE_PATH)
    source_records = source["records"]
    normalized = catalog()
    document_counts = Counter(
        record["source_document_title"] for record in source_records
    )
    location_counts = Counter(
        record["source_location"]["location_kind"]
        for record in source_records
    )
    missing_units = sum(
        record["unit_original"] is None for record in source_records
    )

    assert normalized["summary"] == {
        "record_count": 807,
        "linked_record_count": 0,
        "partial_record_count": 807,
        "not_linked_record_count": 0,
        "indicator_series_count": 807,
        "source_document_count": len(document_counts),
        "missing_unit_record_count": missing_units,
        "annual_actual_available_count": 0,
        "future_target_available_count": 0,
        "reviewed_maximum_depth_record_count": 807,
        "policy_achievement_assessment_count": 0,
    }
    assert normalized["document_record_counts"] == dict(
        sorted(document_counts.items())
    )
    assert normalized["source_location_counts"] == dict(
        sorted(location_counts.items())
    )
    assert sum(normalized["document_record_counts"].values()) == 807
    assert sum(normalized["source_location_counts"].values()) == 807


def test_all_records_remain_unassessed_and_noncomparable():
    for record in catalog()["records"]:
        assert record["evaluation_status"] == "not_assessed"
        assert record["comparability_status"] == "excluded_until_verified"
        assert "政策達成" in record["boundary"]


def test_normalization_is_deterministic():
    assert normalizer.build_catalog(ROOT) == normalizer.build_catalog(ROOT)
