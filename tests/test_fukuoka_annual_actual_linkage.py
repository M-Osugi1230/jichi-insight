import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/catalog"
ENTITY_ROOT = ROOT / "data/entities/policy"
INDEX_PATH = CATALOG / "fukuoka_annual_actual_linkage.json"
INDEX_SCHEMA_PATH = ROOT / "schemas/fukuoka_annual_actual_linkage.schema.json"
PART_SCHEMA_PATH = ROOT / "schemas/fukuoka_annual_actual_linkage_part.schema.json"

EXPECTED_PARTIAL_IDS = {
    "policy-target-fukuoka-prefecture-initiative-02-15",
    "policy-target-fukuoka-prefecture-initiative-03-18",
    "policy-target-fukuoka-prefecture-initiative-04-20",
    "policy-target-fukuoka-prefecture-initiative-09-39",
    "policy-target-fukuoka-prefecture-initiative-10-42",
    "policy-target-fukuoka-prefecture-initiative-10-47",
    "policy-target-fukuoka-prefecture-initiative-11-50",
    "policy-target-fukuoka-prefecture-initiative-11-55",
    "policy-target-fukuoka-prefecture-initiative-11-59",
    "policy-target-fukuoka-prefecture-initiative-11-60",
    "policy-target-fukuoka-prefecture-initiative-11-62",
    "policy-target-fukuoka-prefecture-initiative-19-90",
}
EXPECTED_ALIAS_IDS = {
    "policy-target-fukuoka-prefecture-initiative-01-03",
    "policy-target-fukuoka-prefecture-initiative-02-15",
    "policy-target-fukuoka-prefecture-initiative-07-26",
    "policy-target-fukuoka-prefecture-initiative-10-48",
    "policy-target-fukuoka-prefecture-initiative-11-53",
    "policy-target-fukuoka-prefecture-initiative-11-57",
    "policy-target-fukuoka-prefecture-initiative-14-73",
    "policy-target-fukuoka-prefecture-initiative-16-83",
    "policy-target-fukuoka-prefecture-initiative-17-87",
    "policy-target-fukuoka-prefecture-initiative-17-88",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def linkage_records():
    index = load(INDEX_PATH)
    parts = [load(CATALOG / filename) for filename in index["part_files"]]
    return index, parts, [record for part in parts for record in part["records"]]


def target_catalog_records():
    records = []
    for path in sorted(
        ENTITY_ROOT.glob("fukuoka_prefecture_initiative_*_targets.json")
    ):
        catalog = load(path)
        records.extend(catalog["items"])
    return records


def test_fukuoka_linkage_index_and_parts_match_schema():
    index_validator = Draft202012Validator(
        load(INDEX_SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    part_validator = Draft202012Validator(
        load(PART_SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    index, parts, _ = linkage_records()

    assert list(index_validator.iter_errors(index)) == []
    assert len(parts) == 4
    assert all(list(part_validator.iter_errors(part)) == [] for part in parts)
    assert [(part["target_number_from"], part["target_number_to"]) for part in parts] == [
        (1, 30),
        (31, 60),
        (61, 90),
        (91, 118),
    ]


def test_all_118_targets_are_covered_once_without_mutating_source_catalogs():
    index, _, records = linkage_records()
    targets = target_catalog_records()
    target_ids = [target["id"] for target in targets]
    record_ids = [record["target_id"] for record in records]

    assert index["target_count"] == 118
    assert len(target_ids) == len(set(target_ids)) == 118
    assert len(record_ids) == len(set(record_ids)) == 118
    assert set(record_ids) == set(target_ids)
    assert all(target["actual_linkage_status"] == "not_linked" for target in targets)
    assert all(target["evaluation_status"] == "not_assessed" for target in targets)


def test_linkage_summary_matches_reviewed_classification():
    index, _, records = linkage_records()
    statuses = Counter(record["linkage_status"] for record in records)
    match_basis = Counter(record["match_basis"] for record in records)
    versions = Counter(record["target_version_status"] for record in records)

    assert statuses == {"linked": 86, "partial": 12, "not_linked": 20}
    assert match_basis == {
        "normalized_indicator_exact": 88,
        "reviewed_alias": 10,
        "not_present_in_fy2024_progress_report": 20,
    }
    assert versions == {
        "same_target_definition": 86,
        "revised_target_detected": 12,
        "source_row_not_found": 20,
    }
    assert index["summary"] == {
        "linked_target_count": 86,
        "partial_target_count": 12,
        "not_linked_target_count": 20,
        "normalized_exact_match_count": 88,
        "reviewed_alias_match_count": 10,
        "revised_target_detected_count": 12,
        "source_row_not_found_count": 20,
    }
    assert index["evaluation_status"] == "not_assessed"


def test_linked_partial_and_unresolved_records_keep_distinct_boundaries():
    _, _, records = linkage_records()

    for record in records:
        if record["linkage_status"] in {"linked", "partial"}:
            assert isinstance(record["source_pdf_page"], int)
            assert record["source_initial_value_text"] is not None
            assert record["source_target_value_text"] is not None
            assert record["actual_value_text"] is not None
            assert record["actual_period_text"] is not None
        else:
            assert record["source_pdf_page"] is None
            assert record["source_initial_value_text"] is None
            assert record["source_target_value_text"] is None
            assert record["actual_value_text"] is None
            assert record["actual_period_text"] is None

    partial_ids = {
        record["target_id"]
        for record in records
        if record["linkage_status"] == "partial"
    }
    alias_ids = {
        record["target_id"]
        for record in records
        if record["match_basis"] == "reviewed_alias"
    }
    assert partial_ids == EXPECTED_PARTIAL_IDS
    assert alias_ids == EXPECTED_ALIAS_IDS


def test_partial_records_preserve_revised_target_versions():
    _, _, records = linkage_records()
    partial_records = [
        record for record in records if record["linkage_status"] == "partial"
    ]

    assert len(partial_records) == 12
    assert all(
        record["target_version_status"] == "revised_target_detected"
        for record in partial_records
    )
    assert all(record["source_target_value_text"] for record in partial_records)
    assert all(record["actual_value_text"] for record in partial_records)


def test_official_source_and_page_boundaries_are_fixed():
    index, _, records = linkage_records()

    assert index["source"] == {
        "title": "令和6年度 福岡県総合計画の実施状況",
        "url": "https://www.pref.fukuoka.lg.jp/uploaded/attachment/269803.pdf",
        "official_owner": "福岡県企画・地域振興部総合政策課",
        "reporting_period": "令和6年度",
        "pdf_page_count": 61,
        "observed_at": "2026-08-01",
    }
    assert all(
        record["source_pdf_page"] is None
        or 1 <= record["source_pdf_page"] <= 61
        for record in records
    )
    assert "達成・未達を判定しない" in index["boundaries"]["linked"]
    assert "目標版を分離" in index["boundaries"]["partial"]
    assert "別の公式実績資料" in index["boundaries"]["not_linked"]
