from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path
from types import ModuleType

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
COMPLETION_PATH = ROOT / "data/catalog/phase11_wave1_completion.json"
COMPLETION_SCHEMA_PATH = ROOT / "schemas/phase11_wave1_completion.schema.json"
RECORD_SCHEMA_PATH = ROOT / "schemas/phase11_record_linkage.schema.json"
MIGRATION_PATH = ROOT / "data/catalog/phase11_wave1_migration.json"
QUEUE_PATH = ROOT / "data/catalog/phase11_execution_queue.json"

NORMALIZER_PATHS = {
    "01": ROOT / "scripts/normalize_phase11_hokkaido.py",
    "04": ROOT / "scripts/normalize_phase11_miyagi.py",
    "13": ROOT / "scripts/normalize_phase11_tokyo.py",
    "40": ROOT / "scripts/normalize_phase11_fukuoka.py",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def import_module(code: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        f"phase11_normalizer_{code}",
        path,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalized_catalogs() -> dict[str, dict]:
    return {
        code: import_module(code, path).build_catalog(ROOT)
        for code, path in NORMALIZER_PATHS.items()
    }


def all_records() -> list[dict]:
    return [
        record
        for catalog in normalized_catalogs().values()
        for record in catalog["records"]
    ]


def test_wave1_completion_manifest_matches_schema_and_paths_exist():
    validator = Draft202012Validator(
        load(COMPLETION_SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    completion = load(COMPLETION_PATH)

    assert list(validator.iter_errors(completion)) == []
    for path in completion["normalizers"]:
        assert (ROOT / path).exists()
    for path in completion["completion_manifests"]:
        assert (ROOT / path).exists()
    assert (ROOT / completion["record_schema"]).exists()
    assert (ROOT / completion["integration_test"]).exists()
    for gate in completion["gates"]:
        assert gate["status"] == "passed"
        assert (ROOT / gate["evidence_path"]).exists()


def test_all_861_records_validate_against_one_shared_schema():
    validator = Draft202012Validator(
        load(RECORD_SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    records = all_records()

    assert len(records) == 861
    for record in records:
        assert list(validator.iter_errors(record)) == []


def test_prefecture_and_status_totals_match_the_exhaustive_inventory():
    catalogs = normalized_catalogs()
    migration = load(MIGRATION_PATH)
    expected_by_code = {
        source["prefecture_code"]: source["expected_counts"]
        for source in migration["sources"]
    }

    assert set(catalogs) == set(expected_by_code) == {"01", "04", "13", "40"}
    for code, catalog in catalogs.items():
        statuses = Counter(
            record["linkage_status"] for record in catalog["records"]
        )
        actual = {
            "total": len(catalog["records"]),
            "linked": statuses["linked"],
            "partial": statuses["partial"],
            "not_linked": statuses["not_linked"],
        }
        assert actual == expected_by_code[code]

    records = all_records()
    aggregate = Counter(record["linkage_status"] for record in records)
    completion = load(COMPLETION_PATH)["summary"]
    assert aggregate == {
        "linked": 420,
        "partial": 58,
        "not_linked": 383,
    }
    assert completion["record_count"] == len(records)
    assert completion["linked_record_count"] == aggregate["linked"]
    assert completion["partial_record_count"] == aggregate["partial"]
    assert completion["not_linked_record_count"] == aggregate["not_linked"]


def test_global_normalized_and_source_record_ids_are_unique():
    records = all_records()
    normalized_ids = [record["id"] for record in records]
    source_keys = [
        (
            record["prefecture_code"],
            record["source_registry"],
            record["source_record_id"],
        )
        for record in records
    ]

    assert len(normalized_ids) == len(set(normalized_ids)) == 861
    assert len(source_keys) == len(set(source_keys)) == 861
    assert all((ROOT / record["source_registry"]).exists() for record in records)


def test_every_record_preserves_non_assessment_and_comparison_exclusion():
    records = all_records()

    assert all(record["evaluation_status"] == "not_assessed" for record in records)
    assert all(
        record["comparability_status"] == "excluded_until_verified"
        for record in records
    )
    completion = load(COMPLETION_PATH)["summary"]
    assert completion["policy_achievement_assessment_count"] == 0
    assert completion["ranking_eligible_record_count"] == 0


def test_wave1_queue_stays_complete_after_later_waves_advance():
    queue = load(QUEUE_PATH)
    waves = {wave["id"]: wave for wave in queue["waves"]}

    assert queue["active_wave"] == "wave3-nationwide-minimum-record-depth"
    assert waves["wave1-reference-implementations"]["status"] == "complete"
    assert waves["wave2-remaining-regional-anchors"]["status"] == "complete"
    assert waves["wave3-nationwide-minimum-record-depth"]["status"] == (
        "in_progress"
    )
    assert queue["summary"]["wave1_normalization"] == {
        "prefectures_complete": 4,
        "records_complete": 861,
        "linked_complete": 420,
        "partial_complete": 58,
        "not_linked_complete": 383,
    }


def test_all_normalizers_are_deterministic_together():
    first = normalized_catalogs()
    second = normalized_catalogs()
    assert first == second
