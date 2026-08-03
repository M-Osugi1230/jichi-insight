from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts/normalize_phase11_gifu.py"
SOURCE_PATH = ROOT / "data/reviewed/phase9/21.json"
SUMMARY_PATH = ROOT / "data/catalog/phase9_review_summary.json"
RECORD_SCHEMA_PATH = ROOT / "schemas/phase11_record_linkage.schema.json"
MANIFEST_PATH = ROOT / "data/catalog/phase11_gifu_normalization.json"
MANIFEST_SCHEMA_PATH = ROOT / "schemas/phase11_gifu_normalization.schema.json"

spec = importlib.util.spec_from_file_location(
    "normalize_phase11_gifu", SCRIPT_PATH
)
assert spec is not None
assert spec.loader is not None
normalizer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(normalizer)

EXPECTED_CANONICAL_COUNTS = {
    "令和5年度実施状況報告書 [PDFファイル／2.61MB]": 869,
    "令和7年度実施状況報告書 [PDFファイル／2.35MB]": 440,
    "施策編（令和8年3月改訂版） [PDFファイル／1.73MB]": 186,
    "本編 [PDFファイル／4.05MB]": 5,
}
EXPECTED_CANDIDATE_COUNTS = {
    "令和5年度実施状況報告書 [PDFファイル／2.61MB]": 869,
    "令和6年度報告書の修正について [PDFファイル／388KB]": 20,
    "令和6年度実施状況報告書（R8.6修正） [PDFファイル／2.66MB]": 1033,
    "令和7年度実施状況報告書 [PDFファイル／2.35MB]": 1119,
    "施策編（令和8年3月改訂版） [PDFファイル／1.73MB]": 186,
    "本編 [PDFファイル／4.05MB]": 5,
}
EXPECTED_UNUSED_DOCUMENTS = {
    "令和6年度報告書の修正について [PDFファイル／388KB]",
    "令和6年度実施状況報告書（R8.6修正） [PDFファイル／2.66MB]",
}


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
        if item["prefecture_code"] == "21"
    )

    assert source["prefecture_code"] == "21"
    assert source["name"] == "岐阜県"
    assert source["reviewed_target_statement_count"] == 1500
    assert source["evidence_packet_count"] == 1500
    assert len(source["records"]) == 1500
    assert summary_entry["reviewed_target_statement_count"] == 1500
    assert summary_entry["evidence_packet_count"] == 1500
    assert summary_entry["document_count"] == 6
    assert summary_entry["extraction_error_count"] == 0


def test_document_candidates_and_canonical_records_are_not_conflated():
    source = load(SOURCE_PATH)
    manifest = load(MANIFEST_PATH)
    candidate_counts = {
        item["title"]: item["reviewed_row_count"]
        for item in source["documents"]
    }
    canonical_counts = Counter(
        item["source_document_title"] for item in source["records"]
    )
    inventory_candidates = {
        item["title"]: item["reviewed_candidate_rows"]
        for item in manifest["source_document_inventory"]
    }
    inventory_canonical = {
        item["title"]: item["canonical_records"]
        for item in manifest["source_document_inventory"]
    }

    assert candidate_counts == EXPECTED_CANDIDATE_COUNTS
    assert dict(sorted(canonical_counts.items())) == EXPECTED_CANONICAL_COUNTS
    assert inventory_candidates == EXPECTED_CANDIDATE_COUNTS
    assert {
        title: count
        for title, count in inventory_canonical.items()
        if count > 0
    } == EXPECTED_CANONICAL_COUNTS
    assert sum(candidate_counts.values()) == 3232
    assert sum(canonical_counts.values()) == 1500
    assert sum(candidate_counts.values()) != len(source["records"])


def test_registered_overlap_documents_remain_explicit_without_records():
    source = load(SOURCE_PATH)
    manifest = load(MANIFEST_PATH)
    canonical_titles = {
        item["source_document_title"] for item in source["records"]
    }
    registered_titles = {item["title"] for item in source["documents"]}
    unused_titles = registered_titles - canonical_titles
    manifest_unused = {
        item["title"]
        for item in manifest["source_document_inventory"]
        if item["canonical_records"] == 0
    }

    assert unused_titles == EXPECTED_UNUSED_DOCUMENTS
    assert manifest_unused == EXPECTED_UNUSED_DOCUMENTS
    assert all(EXPECTED_CANDIDATE_COUNTS[title] > 0 for title in unused_titles)
    assert manifest["source_document_summary"] == {
        "registered_documents": 6,
        "documents_with_reviewed_candidates": 6,
        "documents_with_canonical_records": 4,
        "documents_without_canonical_records": 2,
        "reviewed_candidate_rows": 3232,
        "canonical_records": 1500,
        "unique_canonical_source_hashes": 4,
        "pdf_table_row_records": 1215,
        "pdf_text_line_records": 285,
    }


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
    assert len({item["id"] for item in source_records}) == 1500
    assert len({item["evidence_id"] for item in source_records}) == 1500
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
            "source_document_title",
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
        assert "候補行総数3,232行" in record["boundary"]


def test_dynamic_counts_locations_units_and_hashes_are_exact():
    source_records = load(SOURCE_PATH)["records"]
    normalized = catalog()
    documents = Counter(
        item["source_document_title"] for item in source_records
    )
    locations = Counter(
        item["source_location"]["location_kind"] for item in source_records
    )
    missing_units = sum(
        item["unit_original"] is None for item in source_records
    )
    hashes = {item["source_document_sha256"] for item in source_records}

    assert normalized["summary"] == {
        "record_count": 1500,
        "linked_record_count": 0,
        "partial_record_count": 1500,
        "not_linked_record_count": 0,
        "indicator_series_count": 1500,
        "source_document_count": 4,
        "missing_unit_record_count": 462,
        "annual_actual_available_count": 0,
        "future_target_available_count": 0,
        "reviewed_maximum_depth_record_count": 1500,
        "policy_achievement_assessment_count": 0,
    }
    assert normalized["document_record_counts"] == dict(sorted(documents.items()))
    assert normalized["document_record_counts"] == EXPECTED_CANONICAL_COUNTS
    assert normalized["source_location_counts"] == {
        "pdf_table_row": 1215,
        "pdf_text_line": 285,
    }
    assert dict(sorted(locations.items())) == normalized[
        "source_location_counts"
    ]
    assert missing_units == 462
    assert len(hashes) == 4


def test_normalization_is_deterministic():
    assert normalizer.build_catalog(ROOT) == normalizer.build_catalog(ROOT)
