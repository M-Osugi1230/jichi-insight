from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts/normalize_phase11_shizuoka.py"
SOURCE_PATH = ROOT / "data/reviewed/phase9/22.json"
SUMMARY_PATH = ROOT / "data/catalog/phase9_review_summary.json"
RECORD_SCHEMA_PATH = ROOT / "schemas/phase11_record_linkage.schema.json"
MANIFEST_PATH = ROOT / "data/catalog/phase11_shizuoka_normalization.json"
MANIFEST_SCHEMA_PATH = (
    ROOT / "schemas/phase11_shizuoka_normalization.schema.json"
)

spec = importlib.util.spec_from_file_location(
    "normalize_phase11_shizuoka", SCRIPT_PATH
)
assert spec is not None
assert spec.loader is not None
normalizer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(normalizer)

OVERVIEW_TITLE = (
    "静岡県総合計画～しずおか ウェルビーイングプラン～概要版 （PDF 9.3MB）"
)
FULL_TITLE = (
    "静岡県総合計画～しずおか ウェルビーイングプラン～全体版 （PDF 25.1MB）"
)
EXPECTED_DOCUMENT_COUNTS = {OVERVIEW_TITLE: 2, FULL_TITLE: 983}
EXPECTED_LOCATION_COUNTS = {"pdf_table_row": 660, "pdf_text_line": 325}
PLAN_HISTORY_BOUNDARY = (
    "2025～2028年度の新計画を現行正本とし、2022～2025年度後期アクションプランを"
    "過去計画として保持する。旧白書の進捗評価を新計画へ自動接続せず、"
    "現行計画の初回年次評価は未公表とする。"
)


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


def test_phase9_summary_and_source_reconcile_to_985():
    source = load(SOURCE_PATH)
    summary_entry = next(
        item
        for item in load(SUMMARY_PATH)["records"]
        if item["prefecture_code"] == "22"
    )

    assert source["prefecture_code"] == "22"
    assert source["name"] == "静岡県"
    assert source["plan_title"] == (
        "静岡県総合計画～しずおか ウェルビーイングプラン～"
    )
    assert source["plan_period"] == "2025年度～2028年度"
    assert source["reviewed_target_statement_count"] == 985
    assert source["evidence_packet_count"] == 985
    assert len(source["records"]) == 985
    assert summary_entry["reviewed_target_statement_count"] == 985
    assert summary_entry["evidence_packet_count"] == 985
    assert summary_entry["document_count"] == 2
    assert summary_entry["extraction_error_count"] == 0


def test_document_candidate_and_canonical_counts_are_exact():
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

    assert candidate_counts == EXPECTED_DOCUMENT_COUNTS
    assert dict(canonical_counts) == EXPECTED_DOCUMENT_COUNTS
    assert inventory_candidates == EXPECTED_DOCUMENT_COUNTS
    assert inventory_canonical == EXPECTED_DOCUMENT_COUNTS
    assert sum(candidate_counts.values()) == 985
    assert sum(canonical_counts.values()) == 985
    assert manifest["source_document_summary"] == {
        "registered_documents": 2,
        "documents_with_reviewed_candidates": 2,
        "documents_with_canonical_records": 2,
        "reviewed_candidate_rows": 985,
        "canonical_records": 985,
        "unique_canonical_source_hashes": 2,
        "pdf_table_row_records": 660,
        "pdf_text_line_records": 325,
    }


def test_all_985_records_validate_and_sequences_are_complete():
    source_records = load(SOURCE_PATH)["records"]
    records = catalog()["records"]
    validator = Draft202012Validator(
        load(RECORD_SCHEMA_PATH), format_checker=FormatChecker()
    )

    assert [item["display_order"] for item in source_records] == list(
        range(1, 986)
    )
    assert [item["subject"]["sequence"] for item in records] == list(
        range(1, 986)
    )
    assert [item["source_record_id"] for item in records] == [
        item["id"] for item in source_records
    ]
    assert len({item["id"] for item in source_records}) == 985
    assert len({item["evidence_id"] for item in source_records}) == 985
    assert len({item["id"] for item in records}) == 985
    assert len({item["source_record_id"] for item in records}) == 985
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
        assert note["plan_history_boundary"] == PLAN_HISTORY_BOUNDARY
        assert record["evidence"]["primary_page"] == page


def test_carbon_and_glossary_lines_remain_raw():
    source_records = load(SOURCE_PATH)["records"]
    records = catalog()["records"]
    first_source = source_records[0]
    last_source = source_records[-1]
    first = records[0]
    last = records[-1]

    assert first_source["id"] == "phase9-22-target-0001"
    assert first_source["source_document_title"] == OVERVIEW_TITLE
    assert first_source["source_location"] == {
        "location_kind": "pdf_text_line",
        "page": 2,
        "row": 10,
    }
    assert first_source["numeric_tokens_original"] == [
        "4,000",
        "3,792",
        "3,765",
        "3,700",
        "3,633",
        "3,511",
        "3,386",
        "2050",
    ]
    assert first_source["period_tokens_original"] == ["2050年"]
    assert first_source["unit_original"] == "年"
    assert measurements(first)["plan_current"]["value_text"] == (
        first_source["target_statement_original"]
    )
    assert len(measurements(first)["plan_current"]["components"]) == 1

    assert last_source["id"] == "phase9-22-target-0985"
    assert last_source["source_document_title"] == FULL_TITLE
    assert last_source["source_location"] == {
        "location_kind": "pdf_text_line",
        "page": 123,
        "row": 1,
    }
    assert last_source["numeric_tokens_original"] == ["50", "50", "＋２"]
    assert last_source["period_tokens_original"] == []
    assert last_source["unit_original"] is None
    assert "用語" in measurements(last)["plan_current"]["value_text"]
    assert len(measurements(last)["plan_current"]["components"]) == 1


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
        assert "概要版2行と全体版983行" in record["boundary"]
        assert "初回年次評価は未公表" in record["boundary"]


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
        "record_count": 985,
        "linked_record_count": 0,
        "partial_record_count": 985,
        "not_linked_record_count": 0,
        "indicator_series_count": 985,
        "source_document_count": 2,
        "missing_unit_record_count": 208,
        "annual_actual_available_count": 0,
        "future_target_available_count": 0,
        "reviewed_maximum_depth_record_count": 985,
        "policy_achievement_assessment_count": 0,
    }
    assert normalized["document_record_counts"] == dict(sorted(documents.items()))
    assert normalized["document_record_counts"] == EXPECTED_DOCUMENT_COUNTS
    assert normalized["source_location_counts"] == EXPECTED_LOCATION_COUNTS
    assert dict(sorted(locations.items())) == EXPECTED_LOCATION_COUNTS
    assert missing_units == 208
    assert len(hashes) == 2


def test_normalization_is_deterministic():
    assert normalizer.build_catalog(ROOT) == normalizer.build_catalog(ROOT)
