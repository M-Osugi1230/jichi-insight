#!/usr/bin/env python3
"""Normalize all Tokyo children-policy records without resolving source conflicts."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INDEX_RELATIVE_PATH = "data/catalog/tokyo_children_annual_actual_linkage.json"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def normalized_conflict(source: dict[str, Any]) -> dict[str, Any] | None:
    conflict = source["conflict"]
    if conflict is None:
        return None
    return {
        "source_value": conflict.get("source_value"),
        "source_period": conflict.get("source_period"),
        "catalog_value": conflict.get("catalog_value"),
        "catalog_period": conflict.get("catalog_period"),
    }


def actual_components(source: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "record_ref": series["series_id"],
            "catalog_role": series["catalog_role"],
            "label": series["series_label"],
            "unit": series["unit"],
            "value_text": series["actual_value_text"],
            "value": series["actual_value"],
            "value_status": series["value_status"],
        }
        for series in source["linked_series"]
    ]


def actual_period(source: dict[str, Any]) -> str:
    periods = list(
        dict.fromkeys(
            series["actual_period"]
            for series in source["linked_series"]
        )
    )
    return " / ".join(periods)


def actual_value_text(source: dict[str, Any]) -> str:
    return " / ".join(
        series["actual_value_text"]
        for series in source["linked_series"]
    )


def normalize_record(
    source_registry: str,
    policy_area_code: str,
    source: dict[str, Any],
) -> dict[str, Any]:
    linked = source["linkage_status"] == "linked"
    components = actual_components(source) if linked else []

    return {
        "id": (
            "phase11-record-tokyo-children-"
            f"{source['target_group_number']:03d}"
        ),
        "prefecture_code": "13",
        "source_registry": source_registry,
        "source_record_id": source["id"],
        "linkage_kind": "target_to_annual_actual",
        "linkage_status": source["linkage_status"],
        "partial_reason": source["partial_reason"],
        "subject": {
            "record_ref": source["target_id"],
            "sequence": source["target_group_number"],
            "name": source["target_name"],
            "source_name": source["source_alias"],
            "definition": "",
            "hierarchy_refs": [f"tokyo-policy-area-{policy_area_code}"],
        },
        "conflict": normalized_conflict(source),
        "measurements": [
            {
                "role": "annual_actual",
                "status": "available" if linked else "not_promoted",
                "period_text": actual_period(source) if linked else "",
                "value_text": actual_value_text(source) if linked else "",
                "components": components,
                "evidence": {
                    "source_number": 2,
                    "page": source["source_pdf_page"],
                },
            }
        ],
        "evidence": {
            "primary_source_number": 2,
            "primary_page": source["source_pdf_page"],
            "locations": [
                {
                    "source_number": 2,
                    "page": source["source_pdf_page"],
                    "is_reprint": False,
                }
            ],
        },
        "boundary": source["boundary"],
        "evaluation_status": source["evaluation_status"],
        "comparability_status": "excluded_until_verified",
    }


def build_catalog(root: Path = ROOT) -> dict[str, Any]:
    source = load(root / INDEX_RELATIVE_PATH)
    records = [
        normalize_record(
            INDEX_RELATIVE_PATH,
            source["policy_area_code"],
            record,
        )
        for record in source["records"]
    ]
    statuses = Counter(record["linkage_status"] for record in records)
    partial_reasons = Counter(
        record["partial_reason"]
        for record in records
        if record["linkage_status"] == "partial"
    )

    return {
        "id": "phase11-tokyo-normalized-records",
        "phase": 11,
        "status": "normalized",
        "prefecture_code": "13",
        "source_catalog": INDEX_RELATIVE_PATH,
        "sources": [
            {
                "source_number": 1,
                "role": "target_catalog",
                "title": source["target_source_version"],
                "url": source["target_source_url"],
            },
            {
                "source_number": 2,
                "role": "annual_review",
                "title": source["review_source_version"],
                "url": source["review_source_url"],
            },
        ],
        "records": records,
        "summary": {
            "record_count": len(records),
            "linked_record_count": statuses["linked"],
            "partial_record_count": statuses["partial"],
            "not_linked_record_count": statuses["not_linked"],
            "linked_series_count": sum(
                len(record["measurements"][0]["components"])
                for record in records
            ),
            "partial_reason_counts": dict(sorted(partial_reasons.items())),
            "policy_achievement_assessment_count": 0,
        },
        "updated_at": source["updated_at"],
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
