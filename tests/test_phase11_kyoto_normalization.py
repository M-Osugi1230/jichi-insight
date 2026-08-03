from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts/normalize_phase11_kyoto.py"
SOURCE_PATH = ROOT / "data/reviewed/phase9/26.json"
SUMMARY_PATH = ROOT / "data/catalog/phase9_review_summary.json"
RECORD_SCHEMA_PATH = ROOT / "schemas/phase11_record_linkage.schema.json"
MANIFEST_PATH = ROOT / "data/catalog/phase11_kyoto_normalization.json"
MANIFEST_SCHEMA_PATH = ROOT / "schemas/phase11_kyoto_normalization.schema.json"

spec = importlib.util.spec_from_file_location("normalize_phase11_kyoto", SCRIPT_PATH)
assert spec is not None and spec.loader is not None
normalizer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(normalizer)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def catalog() -> dict:
    return normalizer.build_catalog(ROOT)


def measurements(record: dict) -> dict[str, dict]:
    return {item["role"]: item for item in record["measurements"]}


def test_manifest_matches_schema_and_paths_exist():
    manifest = load(MANIFEST_PATH)
    validator = Draft202012Validator(load(MANIFEST_SCHEMA_PATH), format_checker=FormatChecker())
    assert list(validator.iter_errors(manifest)) == []
    for field in ("source_catalog", "normalizer", "shared_normalizer", "record_schema"):
        assert (ROOT / manifest[field]).exists()


def test_phase9_summary_and_source_reconcile_to_282():
    source = load(SOURCE_PATH)
    summary = next(item for item in load(SUMMARY_PATH)["records"] if item["prefecture_code"] == "26")
    assert source["name"] == "京都府"
    assert source["reviewed_target_statement_count"] == 282
    assert source["evidence_packet_count"] == 282
    assert len(source["records"]) == 282
    assert summary["reviewed_target_statement_count"] == 282
    assert summary["document_count"] == 6
    assert summary["extraction_error_count"] == 0


def test_registered_documents_and_canonical_counts_are_exact():
    source = load(SOURCE_PATH)
    manifest = load(MANIFEST_PATH)
    canonical = Counter(item["source_document_sha256"] for item in source["records"])
    inventory = {item["sha256"]: item for item in manifest["source_document_inventory"]}
    assert len(inventory) == 6
    assert sorted(canonical.values()) == [1, 7, 274]
    assert sum(canonical.values()) == 282
    assert sum(item["canonical_records"] for item in inventory.values()) == 282
    assert sum(item["reviewed_candidate_rows"] for item in inventory.values()) == 282
    assert sum(item["canonical_status"] == "used" for item in inventory.values()) == 3


def test_all_records_validate_and_preserve_source_fields():
    source_records = load(SOURCE_PATH)["records"]
    records = catalog()["records"]
    validator = Draft202012Validator(load(RECORD_SCHEMA_PATH), format_checker=FormatChecker())
    assert [item["display_order"] for item in source_records] == list(range(1, 283))
    assert [item["subject"]["sequence"] for item in records] == list(range(1, 283))
    assert [item["source_record_id"] for item in records] == [item["id"] for item in source_records]
    assert len({item["id"] for item in records}) == 282
    for source, record in zip(source_records, records, strict=True):
        assert list(validator.iter_errors(record)) == []
        note = json.loads(record["indicator_context"]["quality_note"])
        actual = measurements(record)
        assert record["subject"]["name"] == source["indicator_name_original"]
        assert actual["plan_current"]["value_text"] == source["target_statement_original"]
        assert record["indicator_context"]["source_page"] == source["source_location"]["page"]
        for field in ("source_document_title", "source_document_url", "source_document_sha256", "source_location", "numeric_tokens_original", "period_tokens_original", "matched_keywords", "keyword_match_kind", "unit_original", "population_scope_original", "aggregation_scope", "target_operator", "comparability"):
            assert note[field] == source[field]


def test_all_records_remain_partial_unassessed_and_noncomparable():
    for record in catalog()["records"]:
        actual = measurements(record)
        assert record["linkage_status"] == "partial"
        assert record["partial_reason"] == "structured_actual_and_target_not_reviewed"
        assert actual["annual_actual"]["status"] == "not_available"
        assert actual["final_target"]["status"] == "not_available"
        assert record["evaluation_status"] == "not_assessed"
        assert record["comparability_status"] == "excluded_until_verified"


def test_dynamic_counts_and_determinism():
    source = load(SOURCE_PATH)
    records = source["records"]
    manifest = load(MANIFEST_PATH)
    normalized = catalog()
    assert normalized["summary"] == manifest["expected_normalization"]
    assert Counter(item["source_location"]["location_kind"] for item in records) == {"pdf_table_row": 206, "pdf_text_line": 76}
    assert sum(item["unit_original"] is None for item in records) == 9
    assert len({item["source_document_sha256"] for item in records}) == 3
    assert normalizer.build_catalog(ROOT) == normalizer.build_catalog(ROOT)
