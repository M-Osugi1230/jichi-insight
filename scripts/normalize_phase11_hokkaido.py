#!/usr/bin/env python3
"""Normalize all Hokkaido Phase 11 records without changing source judgments."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INDEX_RELATIVE_PATH = "data/catalog/hokkaido_annual_actual_linkage.json"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def text_status(value_text: str) -> str:
    return "reported" if value_text.strip() else "not_available"


def measurement(
    role: str,
    value_text: str,
    period_text: str,
    *,
    status: str | None = None,
    components: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "role": role,
        "status": status or text_status(value_text),
        "period_text": period_text,
        "value_text": value_text,
        "components": components or [],
    }


def load_source_records(
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


def normalize_record(
    source_registry: str,
    source: dict[str, Any],
) -> dict[str, Any]:
    hierarchy_refs = [
        source["policy_direction_id"],
        *source["policy_field_ids"],
    ]
    locations = [
        {
            "source_number": location["source_number"],
            "page": location["pdf_page"],
            "is_reprint": location["is_reprint"],
        }
        for location in source["related_source_locations"]
    ]

    return {
        "id": (
            "phase11-record-hokkaido-"
            f"{source['indicator_number']:03d}"
        ),
        "prefecture_code": "01",
        "source_registry": source_registry,
        "source_record_id": source["id"],
        "linkage_kind": "target_to_annual_actual",
        "linkage_status": source["linkage_status"],
        "partial_reason": source["partial_reason"],
        "subject": {
            "record_ref": source["indicator_id"],
            "sequence": source["indicator_number"],
            "name": source["indicator_name"],
            "source_name": source["source_indicator_name_text"],
            "definition": source["definition_text"],
            "hierarchy_refs": hierarchy_refs,
        },
        "measurements": [
            measurement(
                "plan_current",
                source["plan_current_value_text"],
                source["plan_current_period_text"],
            ),
            measurement(
                "intermediate_target",
                source["intermediate_target_text"],
                source["intermediate_target_period_text"],
            ),
            measurement(
                "final_target",
                source["final_target_text"],
                source["final_target_period_text"],
            ),
            measurement(
                "annual_actual",
                source["actual_value_text"],
                source["actual_period_text"],
                status=source["actual_status"],
                components=source["actual_components"],
            ),
        ],
        "evidence": {
            "primary_source_number": source["source_number"],
            "primary_page": source["pdf_page"],
            "locations": locations,
        },
        "boundary": source["boundary"],
        "evaluation_status": source["evaluation_status"],
        "comparability_status": "excluded_until_verified",
    }


def build_catalog(root: Path = ROOT) -> dict[str, Any]:
    index, source_records = load_source_records(root)
    records = [
        normalize_record(source_registry, source)
        for source_registry, source in source_records
    ]
    statuses = Counter(record["linkage_status"] for record in records)

    return {
        "id": "phase11-hokkaido-normalized-records",
        "phase": 11,
        "status": "normalized",
        "prefecture_code": "01",
        "source_catalog": INDEX_RELATIVE_PATH,
        "source_files": [
            f"data/catalog/{filename}"
            for filename in index["part_files"]
        ],
        "records": records,
        "summary": {
            "record_count": len(records),
            "linked_record_count": statuses["linked"],
            "partial_record_count": statuses["partial"],
            "not_linked_record_count": statuses["not_linked"],
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
