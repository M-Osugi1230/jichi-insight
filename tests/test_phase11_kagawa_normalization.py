from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts/normalize_phase11_kagawa.py"
SCHEMA_PATH = ROOT / "schemas/phase11_record_linkage.schema.json"
MANIFEST_PATH = ROOT / "data/catalog/phase11_kagawa_normalization.json"
MANIFEST_SCHEMA_PATH = ROOT / "schemas/phase11_kagawa_normalization.schema.json"
SOURCE_MANIFEST_PATH = (
    ROOT / "data/catalog/kagawa_extended_plan_indicator_review_manifest.json"
)

spec = importlib.util.spec_from_file_location(
    "normalize_phase11_kagawa",
    SCRIPT_PATH,
)
assert spec is not None
assert spec.loader is not None
normalizer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(normalizer)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def source_records() -> list[tuple[str, dict]]:
    return normalizer.load_records(ROOT)


def occurrences() -> dict[int, list[dict]]:
    return normalizer.occurrence_index(ROOT)


def normalized_catalog() -> dict:
    return normalizer.build_catalog(ROOT)


def measurement_by_role(record: dict) -> dict[str, dict]:
    return {
        measurement["role"]: measurement
        for measurement in record["measurements"]
    }


def test_kagawa_manifest_matches_schema_and_paths_exist():
    validator = Draft202012Validator(
        load(MANIFEST_SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    manifest = load(MANIFEST_PATH)

    assert list(validator.iter_errors(manifest)) == []
    for path in manifest["source_catalogs"]:
        assert (ROOT / path).exists()
    for field in (
        "occurrence_catalog",
        "source_review_manifest",
        "normalizer",
        "record_schema",
    ):
        assert (ROOT / manifest[field]).exists()


def test_all_135_records_match_the_shared_phase11_schema():
    validator = Draft202012Validator(
        load(SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    records = normalized_catalog()["records"]

    assert len(records) == 135
    for record in records:
        assert list(validator.iter_errors(record)) == []


def test_three_parts_form_one_complete_sequence_without_skips():
    source = source_records()
    records = normalized_catalog()["records"]

    assert len(source) == 135
    assert [record["indicator_number"] for _, record in source] == list(
        range(1, 136)
    )
    assert [record["indicator_id"] for _, record in source] == [
        f"kagawa-plan-indicator-{number:03d}"
        for number in range(1, 136)
    ]
    assert [record["subject"]["sequence"] for record in records] == list(
        range(1, 136)
    )
    assert [record["source_record_id"] for record in records] == [
        f"kagawa-plan-indicator-{number:03d}"
        for number in range(1, 136)
    ]
    assert len({record["id"] for record in records}) == 135
    assert len({record["source_record_id"] for record in records}) == 135


def test_every_source_field_and_target_version_is_retained():
    source_by_id = {
        record["indicator_id"]: (source_registry, record)
        for source_registry, record in source_records()
    }
    normalized_by_id = {
        record["source_record_id"]: record
        for record in normalized_catalog()["records"]
    }
    occurrence_map = occurrences()

    for source_id, (source_registry, source) in source_by_id.items():
        record = normalized_by_id[source_id]
        measurements = measurement_by_role(record)
        note = json.loads(record["indicator_context"]["quality_note"])
        revised = source["target_r7_original"] != source["target_r8_original"]

        assert record["source_registry"] == source_registry
        assert record["subject"] == {
            "record_ref": source["indicator_id"],
            "sequence": source["indicator_number"],
            "name": source["indicator_name_original"],
            "source_name": source["indicator_name_original"],
            "definition": source["indicator_overview_original"],
            "hierarchy_refs": [
                f"kagawa-plan-{source['plan_heading_original']}",
                f"kagawa-section-{source['section_heading_original']}",
                f"kagawa-policy-{source['policy_number_original']}",
            ],
        }
        assert record["indicator_context"]["policy_direction_code"] == (
            f"policy-{source['policy_number_original']}"
        )
        assert record["indicator_context"]["policy_direction_name"] == source[
            "section_heading_original"
        ]
        assert record["indicator_context"]["source_page"] == source[
            "source_pdf_page"
        ]
        assert record["indicator_context"]["target_revision_status"] == (
            "revised_for_r8_extension" if revised else "unchanged_for_r8"
        )
        assert record["indicator_context"]["linked_current_series_count"] == 1
        assert record["indicator_context"]["target_series_count"] == 1
        assert record["indicator_context"]["review_status"] == source[
            "review_status"
        ]
        assert note == {
            "evidence_id": source["evidence_id"],
            "plan_heading_original": source["plan_heading_original"],
            "section_heading_original": source[
                "section_heading_original"
            ],
            "policy_number_original": source["policy_number_original"],
            "indicator_overview_original": source[
                "indicator_overview_original"
            ],
            "target_rationale_original": source[
                "target_rationale_original"
            ],
            "display_occurrence_count": source[
                "display_occurrence_count"
            ],
            "has_repost_occurrence": source[
                "has_repost_occurrence"
            ],
            "occurrences": occurrence_map[source["indicator_number"]],
        }
        assert measurements["annual_actual"]["value_text"] == source[
            "current_value_original"
        ]
        assert measurements["intermediate_target"]["value_text"] == source[
            "target_r7_original"
        ]
        assert measurements["final_target"]["value_text"] == source[
            "target_r8_original"
        ]
        assert record["linkage_status"] == "linked"
        assert record["partial_reason"] is None


def test_all_141_occurrences_are_retained_without_duplicate_records():
    occurrence_map = occurrences()
    records = normalized_catalog()["records"]
    normalized_by_number = {
        record["subject"]["sequence"]: record for record in records
    }

    assert sum(len(items) for items in occurrence_map.values()) == 141
    assert len(occurrence_map) == 135
    reposted_numbers = {
        number for number, items in occurrence_map.items() if len(items) > 1
    }
    assert reposted_numbers == {7, 14, 50, 66, 67, 96}

    for number, items in occurrence_map.items():
        locations = normalized_by_number[number]["evidence"]["locations"]
        assert locations == [
            {
                "source_number": 1,
                "page": item["source_pdf_page"],
                "is_reprint": index > 0,
            }
            for index, item in enumerate(items)
        ]
        assert len(locations) == len(items)


def test_revision_counts_match_manifest_and_keep_both_versions():
    source = [record for _, record in source_records()]
    review_manifest = load(SOURCE_MANIFEST_PATH)
    catalog = normalized_catalog()
    revised = [
        record
        for record in source
        if record["target_r7_original"] != record["target_r8_original"]
    ]
    unchanged = [
        record
        for record in source
        if record["target_r7_original"] == record["target_r8_original"]
    ]

    assert len(revised) == 87
    assert len(unchanged) == 48
    assert catalog["summary"]["target_revision_count"] == 87
    assert catalog["summary"]["unchanged_target_count"] == 48
    assert review_manifest["target_revision_count"] == 87

    normalized_by_id = {
        record["source_record_id"]: record for record in catalog["records"]
    }
    for source in revised:
        measurements = measurement_by_role(
            normalized_by_id[source["indicator_id"]]
        )
        assert measurements["intermediate_target"]["value_text"] == source[
            "target_r7_original"
        ]
        assert measurements["final_target"]["value_text"] == source[
            "target_r8_original"
        ]
        assert measurements["intermediate_target"]["value_text"] != (
            measurements["final_target"]["value_text"]
        )


def test_corrections_compound_values_and_reference_targets_remain_raw():
    source_by_number = {
        record["indicator_number"]: record for _, record in source_records()
    }
    normalized_by_number = {
        record["subject"]["sequence"]: record
        for record in normalized_catalog()["records"]
    }

    special_numbers = {2, 8, 9, 17, 66, 96, 135}
    for number in special_numbers:
        source = source_by_number[number]
        measurements = measurement_by_role(normalized_by_number[number])
        assert measurements["annual_actual"]["value_text"] == source[
            "current_value_original"
        ]
        assert measurements["intermediate_target"]["value_text"] == source[
            "target_r7_original"
        ]
        assert measurements["final_target"]["value_text"] == source[
            "target_r8_original"
        ]
        assert all(
            len(measurement["components"]) == 1
            for measurement in measurements.values()
        )

    technology = source_by_number[66]
    assert "160件" in technology["current_value_original"]
    assert "168件" in technology["current_value_original"]
    international = source_by_number[96]
    assert "R3～7年度" in international["target_r7_original"]
    assert "R3～8年度" in international["target_r8_original"]
    population = source_by_number[135]
    assert population["target_r7_original"] == "925千人 （R7年）"
    assert population["target_r8_original"] == "901千人 （R12年）"


def test_summary_and_non_assessment_boundaries_are_exact():
    catalog = normalized_catalog()
    statuses = Counter(
        record["linkage_status"] for record in catalog["records"]
    )
    review_manifest = load(SOURCE_MANIFEST_PATH)

    assert statuses == Counter({"linked": 135})
    assert catalog["summary"] == {
        "record_count": 135,
        "linked_record_count": 135,
        "partial_record_count": 0,
        "not_linked_record_count": 0,
        "indicator_series_count": 135,
        "display_occurrence_count": 141,
        "reposted_indicator_count": 6,
        "target_revision_count": 87,
        "unchanged_target_count": 48,
        "policy_achievement_assessment_count": 0,
    }
    assert review_manifest["reviewed_indicator_count"] == 135
    assert review_manifest["display_occurrence_count"] == 141
    assert review_manifest["indicators_with_current_value_count"] == 135
    for record in catalog["records"]:
        assert record["evaluation_status"] == "not_assessed"
        assert record["comparability_status"] == "excluded_until_verified"
        assert "政策達成" in record["boundary"]


def test_normalization_is_deterministic():
    assert normalizer.build_catalog(ROOT) == normalizer.build_catalog(ROOT)
