#!/usr/bin/env python3
"""Normalize all Fukuoka target-actual records without changing review judgments."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INDEX_RELATIVE_PATH = "data/catalog/fukuoka_annual_actual_linkage.json"
TARGET_CATALOG_TEMPLATE = (
    "data/entities/policy/"
    "fukuoka_prefecture_initiative_{initiative:02d}_targets.json"
)


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_linkage_records(
    root: Path = ROOT,
) -> tuple[dict[str, Any], list[tuple[str, dict[str, Any]]]]:
    index = load(root / INDEX_RELATIVE_PATH)
    records: list[tuple[str, dict[str, Any]]] = []
    for filename in index["part_files"]:
        relative_path = f"data/catalog/{filename}"
        part = load(root / relative_path)
        records.extend(
            (relative_path, record)
            for record in part["records"]
        )
    return index, records


def load_target_records(
    root: Path = ROOT,
) -> tuple[list[str], dict[str, tuple[dict[str, Any], dict[str, Any]]]]:
    paths: list[str] = []
    records: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
    for initiative in range(1, 27):
        relative_path = TARGET_CATALOG_TEMPLATE.format(initiative=initiative)
        catalog = load(root / relative_path)
        paths.append(relative_path)
        for record in catalog["items"]:
            assert record["id"] not in records
            records[record["id"]] = (catalog, record)
    return paths, records


def numeric_text(value: int | float | None) -> str:
    if value is None:
        return ""
    return str(value)


def canonical_components(
    target: dict[str, Any],
    role: str,
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for index, component in enumerate(target["components"], start=1):
        if role == "plan_current":
            value = component["baseline_value"]
            value_text = numeric_text(value)
            unit = component["baseline_unit"]
            scope = component["baseline_scope"]
            operator = None
            catalog_role = "baseline"
        else:
            value = component["target_value"]
            value_text = component.get("target_text") or numeric_text(value)
            unit = component["target_unit"]
            scope = component["target_scope"]
            operator = component.get("target_operator")
            catalog_role = "target"

        output.append(
            {
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
        )
    return output


def canonical_period(target: dict[str, Any], role: str) -> str:
    field = "baseline_period" if role == "plan_current" else "target_period"
    periods = list(dict.fromkeys(component[field] for component in target["components"]))
    return " / ".join(periods)


def joined_component_text(components: list[dict[str, Any]]) -> str:
    return " / ".join(component["value_text"] for component in components)


def source_measurement(
    role: str,
    status: str,
    value_text: str | None,
    period_text: str | None,
    page: int | None,
) -> dict[str, Any]:
    return {
        "role": role,
        "status": status,
        "period_text": period_text or "",
        "value_text": value_text or "",
        "components": [],
        "evidence": {
            "source_number": 2 if page is not None else None,
            "page": page,
        },
    }


def normalize_record(
    source_registry: str,
    index: dict[str, Any],
    linkage: dict[str, Any],
    target_catalog: dict[str, Any],
    target: dict[str, Any],
) -> dict[str, Any]:
    status = linkage["linkage_status"]
    source_page = linkage["source_pdf_page"]
    canonical_baseline = canonical_components(target, "plan_current")
    canonical_target = canonical_components(target, "final_target")

    if status == "linked":
        partial_reason = None
        actual_status = "available"
        source_status = "reported"
    elif status == "partial":
        partial_reason = linkage["target_version_status"]
        actual_status = "available_raw_only"
        source_status = "reported"
    else:
        partial_reason = linkage["target_version_status"]
        actual_status = "not_available"
        source_status = "not_available"

    locations = [
        {
            "source_number": 1,
            "page": target_catalog["source_page"],
            "is_reprint": False,
        }
    ]
    if source_page is not None:
        locations.append(
            {
                "source_number": 2,
                "page": source_page,
                "is_reprint": False,
            }
        )

    source_indicator_name = linkage.get("source_indicator_name")
    return {
        "id": f"phase11-record-fukuoka-{target['target_number']:03d}",
        "prefecture_code": "40",
        "source_registry": source_registry,
        "source_record_id": linkage["target_id"],
        "linkage_kind": "target_to_annual_actual",
        "linkage_status": status,
        "partial_reason": partial_reason,
        "subject": {
            "record_ref": target["id"],
            "sequence": target["target_number"],
            "name": target["indicator_name_original"],
            "source_name": source_indicator_name or target["indicator_name_original"],
            "definition": "",
            "hierarchy_refs": [target_catalog["policy_initiative_id"]],
        },
        "target_context": {
            "policy_initiative_ref": target_catalog["policy_initiative_id"],
            "submeasure_title": target["submeasure_title_original"],
            "match_basis": linkage["match_basis"],
            "target_version_status": linkage["target_version_status"],
            "source_indicator_name": source_indicator_name,
            "alias_review_note": linkage.get("alias_review_note"),
            "canonical_source_url": target_catalog["source_document_url"],
            "canonical_source_page": target_catalog["source_page"],
            "canonical_printed_page": target_catalog["printed_page"],
            "canonical_actual_linkage_status": target["actual_linkage_status"],
            "canonical_evaluation_status": target["evaluation_status"],
        },
        "measurements": [
            {
                "role": "plan_current",
                "status": "reported",
                "period_text": canonical_period(target, "plan_current"),
                "value_text": joined_component_text(canonical_baseline),
                "components": canonical_baseline,
                "evidence": {
                    "source_number": 1,
                    "page": target_catalog["source_page"],
                },
            },
            {
                "role": "final_target",
                "status": "reported",
                "period_text": canonical_period(target, "final_target"),
                "value_text": joined_component_text(canonical_target),
                "components": canonical_target,
                "evidence": {
                    "source_number": 1,
                    "page": target_catalog["source_page"],
                },
            },
            source_measurement(
                "source_initial",
                source_status,
                linkage["source_initial_value_text"],
                None,
                source_page,
            ),
            source_measurement(
                "source_target",
                source_status,
                linkage["source_target_value_text"],
                None,
                source_page,
            ),
            source_measurement(
                "annual_actual",
                actual_status,
                linkage["actual_value_text"],
                linkage["actual_period_text"],
                source_page,
            ),
        ],
        "evidence": {
            "primary_source_number": 1,
            "primary_page": target_catalog["source_page"],
            "locations": locations,
        },
        "boundary": index["boundaries"][status],
        "evaluation_status": index["evaluation_status"],
        "comparability_status": "excluded_until_verified",
    }


def build_catalog(root: Path = ROOT) -> dict[str, Any]:
    index, linkage_records = load_linkage_records(root)
    target_paths, target_records = load_target_records(root)
    records: list[dict[str, Any]] = []

    for source_registry, linkage in linkage_records:
        target_catalog, target = target_records[linkage["target_id"]]
        records.append(
            normalize_record(
                source_registry,
                index,
                linkage,
                target_catalog,
                target,
            )
        )

    statuses = Counter(record["linkage_status"] for record in records)
    match_basis_counts = Counter(
        record["target_context"]["match_basis"] for record in records
    )
    target_version_counts = Counter(
        record["target_context"]["target_version_status"]
        for record in records
    )

    return {
        "id": "phase11-fukuoka-normalized-records",
        "phase": 11,
        "status": "normalized",
        "prefecture_code": "40",
        "source_catalog": INDEX_RELATIVE_PATH,
        "source_files": [
            f"data/catalog/{filename}" for filename in index["part_files"]
        ],
        "target_catalog_files": target_paths,
        "sources": [
            {
                "source_number": 1,
                "role": "canonical_target_catalogs",
                "title": "福岡県総合計画 数値目標",
            },
            {
                "source_number": 2,
                "role": "annual_progress_report",
                "title": index["source"]["title"],
                "url": index["source"]["url"],
                "reporting_period": index["source"]["reporting_period"],
            },
        ],
        "records": records,
        "summary": {
            "record_count": len(records),
            "linked_record_count": statuses["linked"],
            "partial_record_count": statuses["partial"],
            "not_linked_record_count": statuses["not_linked"],
            "match_basis_counts": dict(sorted(match_basis_counts.items())),
            "target_version_counts": dict(sorted(target_version_counts.items())),
            "policy_achievement_assessment_count": 0,
        },
        "updated_at": index["updated_at"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    payload = build_catalog()
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
