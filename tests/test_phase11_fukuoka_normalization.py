from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts/normalize_phase11_fukuoka.py"
SCHEMA_PATH = ROOT / "schemas/phase11_record_linkage.schema.json"
MANIFEST_PATH = ROOT / "data/catalog/phase11_fukuoka_normalization.json"
MANIFEST_SCHEMA_PATH = ROOT / "schemas/phase11_fukuoka_normalization.schema.json"

spec = importlib.util.spec_from_file_location(
    "normalize_phase11_fukuoka",
    SCRIPT_PATH,
)
assert spec is not None
assert spec.loader is not None
normalizer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(normalizer)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def normalized_catalog() -> dict:
    return normalizer.build_catalog(ROOT)


def measurement_by_role(record: dict) -> dict[str, dict]:
    return {
        measurement["role"]: measurement
        for measurement in record["measurements"]
    }


def target_sources() -> dict[str, tuple[dict, dict]]:
    _, records = normalizer.load_target_records(ROOT)
    return records


def linkage_sources() -> list[tuple[str, dict]]:
    _, records = normalizer.load_linkage_records(ROOT)
    return records


def expected_component(target: dict, component: dict, index: int, role: str) -> dict:
    if role == "plan_current":
        value = component["baseline_value"]
        value_text = "" if value is None else str(value)
        unit = component["baseline_unit"]
        scope = component["baseline_scope"]
        operator = None
        catalog_role = "baseline"
    else:
        value = component["target_value"]
        value_text = component.get("target_text") or (
            "" if value is None else str(value)
        )
        unit = component["target_unit"]
        scope = component["target_scope"]
        operator = component.get("target_operator")
        catalog_role = "target"

    return {
        "record_ref": f"{target['id']}-component-{index:02d}",
        "catalog_role": catalog_role,
        "label": component["label"],
        "unit": unit,
        "value_text": value_text,
        "value": value,
        "value_status": "numeric" if value is not None else "textual",
        "scope": scope,
        "preferred_direction": component["preferred_direction"],
        "operator": operator,
    }


def test_fukuoka_normalization_manifest_matches_schema():
    validator = Draft202012Validator(
        load(MANIFEST_SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    manifest = load(MANIFEST_PATH)

    assert list(validator.iter_errors(manifest)) == []
    for path_field in (
        "source_catalog",
        "normalizer",
        "record_schema",
        "regression_test",
    ):
        assert (ROOT / manifest[path_field]).exists()
    assert all((ROOT / path).exists() for path in manifest["source_files"])


def test_all_118_records_match_the_reusable_phase11_schema():
    validator = Draft202012Validator(
        load(SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    catalog = normalized_catalog()

    assert len(catalog["records"]) == 118
    for record in catalog["records"]:
        assert list(validator.iter_errors(record)) == []


def test_linkage_and_canonical_target_sets_match_without_skips():
    linkage = linkage_sources()
    targets = target_sources()
    catalog = normalized_catalog()
    records = catalog["records"]

    linkage_ids = [record["target_id"] for _, record in linkage]
    assert len(linkage_ids) == 118
    assert len(set(linkage_ids)) == 118
    assert set(linkage_ids) == set(targets)
    assert [record["subject"]["sequence"] for record in records] == list(
        range(1, 119)
    )
    assert [record["source_record_id"] for record in records] == linkage_ids
    assert len({record["id"] for record in records}) == 118
    assert len(catalog["target_catalog_files"]) == 26
    assert all((ROOT / path).exists() for path in catalog["target_catalog_files"])


def test_status_match_basis_and_version_counts_are_exact():
    catalog = normalized_catalog()
    records = catalog["records"]
    manifest = load(MANIFEST_PATH)

    statuses = Counter(record["linkage_status"] for record in records)
    match_basis = Counter(
        record["target_context"]["match_basis"] for record in records
    )
    versions = Counter(
        record["target_context"]["target_version_status"]
        for record in records
    )

    assert statuses == {"linked": 86, "partial": 12, "not_linked": 20}
    assert dict(match_basis) == manifest["match_basis_counts"]
    assert dict(versions) == manifest["target_version_counts"]
    assert catalog["summary"]["record_count"] == 118
    assert catalog["summary"]["linked_record_count"] == 86
    assert catalog["summary"]["partial_record_count"] == 12
    assert catalog["summary"]["not_linked_record_count"] == 20


def test_every_canonical_target_field_is_retained():
    targets = target_sources()
    linkage_by_id = {
        record["target_id"]: (source_registry, record)
        for source_registry, record in linkage_sources()
    }
    normalized_by_id = {
        record["source_record_id"]: record
        for record in normalized_catalog()["records"]
    }

    for target_id, (target_catalog, target) in targets.items():
        source_registry, linkage = linkage_by_id[target_id]
        record = normalized_by_id[target_id]
        measurements = measurement_by_role(record)

        assert record["source_registry"] == source_registry
        assert record["subject"] == {
            "record_ref": target["id"],
            "sequence": target["target_number"],
            "name": target["indicator_name_original"],
            "source_name": linkage.get("source_indicator_name")
            or target["indicator_name_original"],
            "definition": "",
            "hierarchy_refs": [target_catalog["policy_initiative_id"]],
        }
        assert record["target_context"] == {
            "policy_initiative_ref": target_catalog["policy_initiative_id"],
            "submeasure_title": target["submeasure_title_original"],
            "match_basis": linkage["match_basis"],
            "target_version_status": linkage["target_version_status"],
            "source_indicator_name": linkage.get("source_indicator_name"),
            "alias_review_note": linkage.get("alias_review_note"),
            "canonical_source_url": target_catalog["source_document_url"],
            "canonical_source_page": target_catalog["source_page"],
            "canonical_printed_page": target_catalog["printed_page"],
            "canonical_actual_linkage_status": target[
                "actual_linkage_status"
            ],
            "canonical_evaluation_status": target["evaluation_status"],
        }

        baseline_components = measurements["plan_current"]["components"]
        target_components = measurements["final_target"]["components"]
        assert len(baseline_components) == len(target["components"])
        assert len(target_components) == len(target["components"])
        for index, component in enumerate(target["components"], start=1):
            assert baseline_components[index - 1] == expected_component(
                target,
                component,
                index,
                "plan_current",
            )
            assert target_components[index - 1] == expected_component(
                target,
                component,
                index,
                "final_target",
            )

        expected_baseline_periods = list(
            dict.fromkeys(
                (component["baseline_period"] or "")
                for component in target["components"]
            )
        )
        expected_target_periods = list(
            dict.fromkeys(
                component["target_period"]
                for component in target["components"]
            )
        )
        assert measurements["plan_current"]["period_text"] == " / ".join(
            expected_baseline_periods
        )
        assert measurements["final_target"]["period_text"] == " / ".join(
            expected_target_periods
        )


def test_report_values_and_evidence_are_retained_by_status():
    targets = target_sources()
    normalized_by_id = {
        record["source_record_id"]: record
        for record in normalized_catalog()["records"]
    }

    for _, linkage in linkage_sources():
        target_catalog, _ = targets[linkage["target_id"]]
        record = normalized_by_id[linkage["target_id"]]
        measurements = measurement_by_role(record)
        source_page = linkage["source_pdf_page"]
        source_status = (
            "not_available"
            if linkage["linkage_status"] == "not_linked"
            else "reported"
        )
        actual_status = {
            "linked": "available",
            "partial": "available_raw_only",
            "not_linked": "not_available",
        }[linkage["linkage_status"]]

        assert measurements["source_initial"] == {
            "role": "source_initial",
            "status": source_status,
            "period_text": "",
            "value_text": linkage["source_initial_value_text"] or "",
            "components": [],
            "evidence": {
                "source_number": 2 if source_page is not None else None,
                "page": source_page,
            },
        }
        assert measurements["source_target"] == {
            "role": "source_target",
            "status": source_status,
            "period_text": "",
            "value_text": linkage["source_target_value_text"] or "",
            "components": [],
            "evidence": {
                "source_number": 2 if source_page is not None else None,
                "page": source_page,
            },
        }
        assert measurements["annual_actual"] == {
            "role": "annual_actual",
            "status": actual_status,
            "period_text": linkage["actual_period_text"] or "",
            "value_text": linkage["actual_value_text"] or "",
            "components": [],
            "evidence": {
                "source_number": 2 if source_page is not None else None,
                "page": source_page,
            },
        }

        expected_locations = [
            {
                "source_number": 1,
                "page": target_catalog["source_page"],
                "is_reprint": False,
            }
        ]
        if source_page is not None:
            expected_locations.append(
                {
                    "source_number": 2,
                    "page": source_page,
                    "is_reprint": False,
                }
            )
        assert record["evidence"] == {
            "primary_source_number": 1,
            "primary_page": target_catalog["source_page"],
            "locations": expected_locations,
        }


def test_partial_records_keep_revised_targets_without_promotion():
    partial = [
        record
        for record in normalized_catalog()["records"]
        if record["linkage_status"] == "partial"
    ]

    assert len(partial) == 12
    for record in partial:
        measurements = measurement_by_role(record)
        assert record["partial_reason"] == "revised_target_detected"
        assert record["target_context"]["target_version_status"] == (
            "revised_target_detected"
        )
        assert measurements["source_target"]["value_text"]
        assert measurements["annual_actual"]["status"] == "available_raw_only"
        assert measurements["annual_actual"]["value_text"]


def test_not_linked_records_keep_missing_progress_rows_explicit():
    not_linked = [
        record
        for record in normalized_catalog()["records"]
        if record["linkage_status"] == "not_linked"
    ]

    assert len(not_linked) == 20
    for record in not_linked:
        measurements = measurement_by_role(record)
        assert record["partial_reason"] == "source_row_not_found"
        assert record["target_context"]["match_basis"] == (
            "not_present_in_fy2024_progress_report"
        )
        assert len(record["evidence"]["locations"]) == 1
        for role in ("source_initial", "source_target", "annual_actual"):
            assert measurements[role]["status"] == "not_available"
            assert measurements[role]["value_text"] == ""
            assert measurements[role]["evidence"] == {
                "source_number": None,
                "page": None,
            }


def test_alias_reviews_are_retained_exactly():
    aliases = [
        record
        for record in normalized_catalog()["records"]
        if record["target_context"]["match_basis"] == "reviewed_alias"
    ]

    assert len(aliases) == 10
    for record in aliases:
        assert record["target_context"]["source_indicator_name"]
        assert record["target_context"]["alias_review_note"]


def test_no_record_gains_assessment_or_comparability():
    for record in normalized_catalog()["records"]:
        assert record["evaluation_status"] == "not_assessed"
        assert record["comparability_status"] == "excluded_until_verified"


def test_normalization_is_deterministic():
    assert normalizer.build_catalog(ROOT) == normalizer.build_catalog(ROOT)
