from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MIGRATION_PATH = ROOT / "data/catalog/phase11_wave1_migration.json"
MIGRATION_SCHEMA_PATH = ROOT / "schemas/phase11_wave1_migration.schema.json"
REFERENCE_PATH = ROOT / "data/catalog/phase11_reference_records.json"

SUMMARY_FIELDS = {
    "01": {
        "total": "indicator_count",
        "linked": "linked_record_count",
        "partial": "partial_record_count",
        "not_linked": "not_linked_record_count",
    },
    "04": {
        "total": "record_count",
        "linked": "linked_record_count",
        "partial": "partial_record_count",
        "not_linked": "not_linked_record_count",
    },
    "13": {
        "total": "target_group_count",
        "linked": "linked_target_group_count",
        "partial": "partial_target_group_count",
        "not_linked": "not_linked_target_group_count",
    },
    "40": {
        "total": "target_count",
        "linked": "linked_target_count",
        "partial": "partial_target_count",
        "not_linked": "not_linked_target_count",
    },
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def records_for_source(source: dict) -> list[dict]:
    records: list[dict] = []
    for relative_path in source["record_files"]:
        payload = load(ROOT / relative_path)
        assert "records" in payload
        records.extend(payload["records"])
    return records


def catalog_counts(source: dict) -> dict[str, int]:
    catalog = load(ROOT / source["catalog_path"])
    fields = SUMMARY_FIELDS[source["prefecture_code"]]
    summary = catalog.get("summary", {})
    return {
        "total": catalog[fields["total"]],
        "linked": summary[fields["linked"]],
        "partial": summary[fields["partial"]],
        "not_linked": summary[fields["not_linked"]],
    }


def test_wave1_migration_matches_schema():
    validator = Draft202012Validator(
        load(MIGRATION_SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(load(MIGRATION_PATH))) == []


def test_all_catalog_part_files_are_included_without_skips():
    migration = load(MIGRATION_PATH)

    for source in migration["sources"]:
        catalog = load(ROOT / source["catalog_path"])
        record_files = source["record_files"]
        assert all((ROOT / path).is_file() for path in record_files)

        if "part_files" in catalog:
            expected = catalog["part_files"]
            actual = [Path(path).name for path in record_files]
            assert actual == expected
        else:
            assert record_files == [source["catalog_path"]]


def test_every_wave1_record_is_counted_once_with_its_original_status():
    migration = load(MIGRATION_PATH)
    aggregate = Counter()

    for source in migration["sources"]:
        records = records_for_source(source)
        id_field = source["record_id_field"]
        status_field = source["status_field"]
        record_ids = [record[id_field] for record in records]
        statuses = Counter(record[status_field] for record in records)

        assert len(record_ids) == len(set(record_ids))
        assert set(statuses) <= {"linked", "partial", "not_linked"}

        actual = {
            "total": len(records),
            "linked": statuses["linked"],
            "partial": statuses["partial"],
            "not_linked": statuses["not_linked"],
        }
        assert actual == source["expected_counts"]
        assert actual == catalog_counts(source)
        aggregate.update(actual)

    summary = migration["summary"]
    assert aggregate["total"] == summary["record_count"]
    assert aggregate["linked"] == summary["linked_record_count"]
    assert aggregate["partial"] == summary["partial_record_count"]
    assert aggregate["not_linked"] == summary["not_linked_record_count"]
    assert aggregate["total"] == (
        aggregate["linked"]
        + aggregate["partial"]
        + aggregate["not_linked"]
    )


def test_wave1_inventory_has_exact_declared_coverage():
    migration = load(MIGRATION_PATH)
    sources = migration["sources"]

    assert [source["prefecture_code"] for source in sources] == [
        "01",
        "04",
        "13",
        "40",
    ]
    assert sum(len(source["record_files"]) for source in sources) == 11
    assert sum(source["expected_counts"]["total"] for source in sources) == 861
    assert sum(source["expected_counts"]["linked"] for source in sources) == 420
    assert sum(source["expected_counts"]["partial"] for source in sources) == 58
    assert (
        sum(source["expected_counts"]["not_linked"] for source in sources)
        == 383
    )


def test_initial_reference_records_are_members_of_the_full_inventory():
    migration = load(MIGRATION_PATH)
    references = load(REFERENCE_PATH)["records"]
    sources_by_code = {
        source["prefecture_code"]: source for source in migration["sources"]
    }

    assert len(references) == 4
    for reference in references:
        source = sources_by_code[reference["prefecture_code"]]
        records = records_for_source(source)
        record_ids = {
            record[source["record_id_field"]]
            for record in records
        }
        assert reference["source_registry"] in source["record_files"]
        assert reference["source_record_id"] in record_ids


def test_wave1_migration_preserves_non_assessment_boundary():
    migration = load(MIGRATION_PATH)

    assert migration["summary"]["policy_achievement_assessment_count"] == 0
    assert "does not promote unresolved records" in migration[
        "migration_definition"
    ]
    for source in migration["sources"]:
        catalog = load(ROOT / source["catalog_path"])
        assert catalog["evaluation_status"] == "not_assessed"
        assert len(source["migration_boundary"]) >= 100
