from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
COMPLETION_PATH = ROOT / "data/catalog/phase11_wave2_completion.json"
COMPLETION_SCHEMA_PATH = ROOT / "schemas/phase11_wave2_completion.schema.json"
RECORD_SCHEMA_PATH = ROOT / "schemas/phase11_record_linkage.schema.json"

NORMALIZER_PATHS = {
    "23": ROOT / "scripts/normalize_phase11_aichi.py",
    "27": ROOT / "scripts/normalize_phase11_osaka.py",
    "34": ROOT / "scripts/normalize_phase11_hiroshima.py",
    "37": ROOT / "scripts/normalize_phase11_kagawa.py",
    "47": ROOT / "scripts/normalize_phase11_okinawa.py",
}
EXPECTED_RECORD_COUNTS = {
    "23": 56,
    "27": 83,
    "34": 62,
    "37": 135,
    "47": 375,
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_normalizer(prefecture_code: str):
    path = NORMALIZER_PATHS[prefecture_code]
    spec = importlib.util.spec_from_file_location(
        f"phase11_wave2_{prefecture_code}",
        path,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def catalogs() -> dict[str, dict]:
    return {
        prefecture_code: load_normalizer(prefecture_code).build_catalog(ROOT)
        for prefecture_code in NORMALIZER_PATHS
    }


def all_records() -> list[dict]:
    return [
        record
        for catalog in catalogs().values()
        for record in catalog["records"]
    ]


def measurement_by_role(record: dict) -> dict[str, dict]:
    return {
        measurement["role"]: measurement
        for measurement in record["measurements"]
    }


def test_wave2_completion_manifest_matches_schema_and_paths_exist():
    validator = Draft202012Validator(
        load(COMPLETION_SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    completion = load(COMPLETION_PATH)

    assert list(validator.iter_errors(completion)) == []
    assert (ROOT / completion["record_schema"]).exists()
    for path in completion["normalizers"]:
        assert (ROOT / path).exists()
    for path in completion["completion_manifests"]:
        assert (ROOT / path).exists()


def test_all_five_normalizers_execute_and_record_counts_reconcile():
    built = catalogs()

    assert set(built) == {"23", "27", "34", "37", "47"}
    for prefecture_code, expected_count in EXPECTED_RECORD_COUNTS.items():
        catalog = built[prefecture_code]
        assert catalog["prefecture_code"] == prefecture_code
        assert len(catalog["records"]) == expected_count
    assert sum(len(catalog["records"]) for catalog in built.values()) == 711


def test_all_711_records_validate_against_one_shared_schema():
    validator = Draft202012Validator(
        load(RECORD_SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    records = all_records()

    assert len(records) == 711
    for record in records:
        assert list(validator.iter_errors(record)) == []


def test_global_ids_source_keys_and_source_registries_are_complete():
    records = all_records()
    normalized_ids = [record["id"] for record in records]
    source_keys = [
        (record["prefecture_code"], record["source_record_id"])
        for record in records
    ]

    assert len(set(normalized_ids)) == 711
    assert len(set(source_keys)) == 711
    for record in records:
        assert (ROOT / record["source_registry"]).exists()


def test_wave2_series_current_and_target_totals_are_exact():
    records = all_records()
    indicator_series = sum(
        len(record["indicator_context"]["series"])
        for record in records
    )
    current_available = sum(
        record["indicator_context"]["linked_current_series_count"]
        for record in records
    )
    target_series = sum(
        record["indicator_context"]["target_series_count"]
        for record in records
    )

    assert indicator_series == 725
    assert current_available == 340
    assert indicator_series - current_available == 385
    assert target_series == 602

    completion_summary = load(COMPLETION_PATH)["summary"]
    assert completion_summary["records"] == 711
    assert completion_summary["indicator_series"] == 725
    assert completion_summary["current_value_series_available"] == 340
    assert completion_summary[
        "current_value_series_missing_or_unavailable"
    ] == 385
    assert completion_summary["progress_or_explicit_target_series"] == 602


def test_missing_and_partial_states_are_preserved_per_anchor():
    built = catalogs()
    statuses = {
        code: Counter(
            record["linkage_status"] for record in catalog["records"]
        )
        for code, catalog in built.items()
    }

    assert statuses["27"] == Counter({"linked": 77, "partial": 6})
    assert statuses["34"] == Counter({"linked": 59, "partial": 3})
    assert statuses["37"] == Counter({"linked": 135})
    assert statuses["47"] == Counter({"partial": 375})
    assert statuses["23"]["linked"] + statuses["23"]["partial"] == 56
    assert statuses["23"]["partial"] >= 1

    for record in built["47"]["records"]:
        actual = measurement_by_role(record)["annual_actual"]
        assert record["partial_reason"] == "annual_actual_not_reviewed"
        assert actual["status"] == "not_available"
        assert actual["components"] == []


def test_every_wave2_record_remains_unassessed_and_noncomparable():
    for record in all_records():
        assert record["evaluation_status"] == "not_assessed"
        assert record["comparability_status"] == "excluded_until_verified"


def test_wave2_normalization_is_deterministic():
    first = catalogs()
    second = catalogs()
    assert first == second
