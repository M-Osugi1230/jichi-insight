from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts/normalize_phase11_chiba.py"
SOURCE_PATH = ROOT / "data/reviewed/phase9/12.json"
SUMMARY_PATH = ROOT / "data/catalog/phase9_review_summary.json"
RECORD_SCHEMA_PATH = ROOT / "schemas/phase11_record_linkage.schema.json"
MANIFEST_PATH = ROOT / "data/catalog/phase11_chiba_normalization.json"
MANIFEST_SCHEMA_PATH = ROOT / "schemas/phase11_chiba_normalization.schema.json"

spec = importlib.util.spec_from_file_location("normalize_phase11_chiba", SCRIPT_PATH)
assert spec is not None and spec.loader is not None
normalizer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(normalizer)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def catalog() -> dict:
    return normalizer.build_catalog(ROOT)


def test_manifest_source_and_phase9_summary_reconcile():
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

    source = load(SOURCE_PATH)
    summary = next(
        item
        for item in load(SUMMARY_PATH)["records"]
        if item["prefecture_code"] == "12"
    )
    assert len(source["records"]) == 1
    assert source["reviewed_target_statement_count"] == 1
    assert source["evidence_packet_count"] == 1
    assert len(source["documents"]) == 1
    assert source["documents"][0]["reviewed_row_count"] == 1
    assert source["landing_audit"]["selected_document_count"] == 1
    assert summary["reviewed_target_statement_count"] == 1
    assert summary["evidence_packet_count"] == 1
    assert summary["document_count"] == 1
    assert summary["extraction_error_count"] == 0


def test_single_record_validates_and_preserves_every_source_field():
    source = load(SOURCE_PATH)["records"][0]
    record = catalog()["records"][0]
    validator = Draft202012Validator(
        load(RECORD_SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(record)) == []
    assert record["source_record_id"] == source["id"]
    assert record["subject"]["sequence"] == 1
    note = json.loads(record["indicator_context"]["quality_note"])
    plan = next(
        item for item in record["measurements"] if item["role"] == "plan_current"
    )
    assert plan["value_text"] == source["target_statement_original"]
    assert plan["components"][0]["unit"] == source["unit_original"]
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
        assert note[field] == source[field]
    assert record["evidence"]["primary_page"] == 1


def test_review_process_sentence_and_extraction_noise_remain_raw():
    source = load(SOURCE_PATH)["records"][0]
    assert source["source_location"] == {
        "location_kind": "pdf_text_line",
        "page": 1,
        "row": 32,
    }
    assert source["numeric_tokens_original"] == ["7743"]
    assert source["period_tokens_original"] == []
    assert source["unit_original"] == "年・点・分"
    assert "毎年度" in source["target_statement_original"]
    assert "点検・分析" in source["target_statement_original"]
    record = catalog()["records"][0]
    assert "89社会目標の個別指標値ではなく" in record["boundary"]
    assert "文字抽出ノイズ" in record["boundary"]


def test_record_remains_partial_unassessed_and_noncomparable():
    record = catalog()["records"][0]
    by_role = {item["role"]: item for item in record["measurements"]}
    assert record["linkage_status"] == "partial"
    assert record["partial_reason"] == "structured_actual_and_target_not_reviewed"
    assert by_role["annual_actual"]["status"] == "not_available"
    assert by_role["final_target"]["status"] == "not_available"
    assert record["evaluation_status"] == "not_assessed"
    assert record["comparability_status"] == "excluded_until_verified"
    assert "旧計画76" in record["boundary"]


def test_summary_and_determinism_are_exact():
    normalized = catalog()
    assert normalized["sources"][0]["document_count"] == 1
    assert normalized["summary"] == {
        "record_count": 1,
        "linked_record_count": 0,
        "partial_record_count": 1,
        "not_linked_record_count": 0,
        "indicator_series_count": 1,
        "source_document_count": 1,
        "missing_unit_record_count": 0,
        "annual_actual_available_count": 0,
        "future_target_available_count": 0,
        "reviewed_maximum_depth_record_count": 1,
        "policy_achievement_assessment_count": 0,
    }
    assert normalizer.build_catalog(ROOT) == normalizer.build_catalog(ROOT)
