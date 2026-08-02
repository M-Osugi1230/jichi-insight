#!/usr/bin/env python3
"""Normalize every reviewed Aichi indicator row without collapsing series history."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/aichi_policy_indicators.json"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def value_status(source_status: str) -> str:
    if source_status == "numeric":
        return "numeric"
    if source_status == "missing":
        return "missing"
    return "textual"


def series_ref(row_id: str, series_index: int) -> str:
    return f"{row_id}-series-{series_index:02d}"


def component(
    row_id: str,
    series_index: int,
    value_index: int,
    series: dict[str, Any],
    value: dict[str, Any],
) -> dict[str, Any]:
    return {
        "record_ref": (
            f"{series_ref(row_id, series_index)}-"
            f"{value['role']}-{value_index:02d}"
        ),
        "catalog_role": value["role"],
        "label": series["label"],
        "unit": series["unit_original"],
        "period_text": value["period"],
        "value_text": value["value_text_original"],
        "value": value["value"],
        "value_status": value_status(value["status"]),
        "source_status": value["status"],
        "scope": value["aggregation_scope"],
        "aggregation_scope": value["aggregation_scope"],
        "preferred_direction": series["direction"],
        "operator": value["operator"],
    }


def components_for_role(row: dict[str, Any], role: str) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for series_index, series in enumerate(row["series"], start=1):
        role_values = [value for value in series["values"] if value["role"] == role]
        for value_index, value in enumerate(role_values, start=1):
            output.append(
                component(
                    row["id"],
                    series_index,
                    value_index,
                    series,
                    value,
                )
            )
    return output


def joined_unique(components: list[dict[str, Any]], field: str) -> str:
    return " / ".join(
        dict.fromkeys(
            str(item[field])
            for item in components
            if str(item[field])
        )
    )


def measurement_status(
    role: str,
    linkage_status: str,
    components: list[dict[str, Any]],
) -> str:
    if not components:
        return "not_available"
    if role != "current":
        return "reported"
    if all(component["value_status"] == "missing" for component in components):
        return "not_available"
    if linkage_status == "partial":
        return "available_raw_only"
    return "available"


def measurement(
    source_page: int,
    role: str,
    normalized_role: str,
    linkage_status: str,
    components: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "role": normalized_role,
        "status": measurement_status(role, linkage_status, components),
        "period_text": joined_unique(components, "period_text"),
        "value_text": joined_unique(components, "value_text"),
        "components": components,
        "evidence": {"source_number": 1, "page": source_page},
    }


def partial_reasons(row: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if row["linked_current_series_count"] < len(row["series"]):
        reasons.append("missing_current_series")
    if row["target_revision_status"] == "revised_in_2025_report":
        reasons.append("target_revised_in_2025_report")
    return reasons


def evidence_locations(
    row: dict[str, Any],
    rows_by_id: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    if row["repost_of"] is None:
        return [
            {
                "source_number": 1,
                "page": row["source_page"],
                "is_reprint": False,
            }
        ]

    original = rows_by_id[row["repost_of"]]
    return [
        {
            "source_number": 1,
            "page": original["source_page"],
            "is_reprint": False,
        },
        {
            "source_number": 1,
            "page": row["source_page"],
            "is_reprint": True,
        },
    ]


def boundary(row: dict[str, Any], reasons: list[str]) -> str:
    if not reasons:
        base = (
            "年次レポートの全系列でcurrent値を確認し、baseline、current、"
            "targetを期間別に保持した。値から政策達成・未達は判定しない。"
        )
    else:
        base = (
            "年次レポートの系列と値を保持したが、"
            f"{', '.join(reasons)}のため個票はPartialとする。"
            "欠損値や改定目標を推測で補完せず、政策達成・未達は判定しない。"
        )
    if row["quality_note"]:
        return f"{base} {row['quality_note']}"
    return base


def normalize_row(
    source: dict[str, Any],
    row: dict[str, Any],
    rows_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    reasons = partial_reasons(row)
    linkage_status = "partial" if reasons else "linked"
    baseline = components_for_role(row, "baseline")
    current = components_for_role(row, "current")
    target = components_for_role(row, "target")

    return {
        "id": f"phase11-record-aichi-{row['display_order']:03d}",
        "prefecture_code": "23",
        "source_registry": SOURCE_RELATIVE_PATH,
        "source_record_id": row["id"],
        "linkage_kind": "target_to_annual_actual",
        "linkage_status": linkage_status,
        "partial_reason": "+".join(reasons) if reasons else None,
        "subject": {
            "record_ref": row["id"],
            "sequence": row["display_order"],
            "name": row["indicator_name_original"],
            "source_name": row["indicator_name_original"],
            "definition": "",
            "hierarchy_refs": [
                f"aichi-policy-direction-{row['policy_direction_code']}"
            ],
        },
        "indicator_context": {
            "policy_direction_code": row["policy_direction_code"],
            "policy_direction_name": row["policy_direction_name_original"],
            "source_page": row["source_page"],
            "repost_of": row["repost_of"],
            "target_revision_status": row["target_revision_status"],
            "linked_current_series_count": row["linked_current_series_count"],
            "target_series_count": row["target_series_count"],
            "review_status": row["review_status"],
            "quality_note": row["quality_note"],
            "series": [
                {
                    "series_ref": series_ref(row["id"], index),
                    "label": series["label"],
                    "unit": series["unit_original"],
                    "direction": series["direction"],
                    "comparability_note": series[
                        "comparability_note_original"
                    ],
                    "value_count": len(series["values"]),
                }
                for index, series in enumerate(row["series"], start=1)
            ],
        },
        "measurements": [
            measurement(
                row["source_page"],
                "baseline",
                "plan_current",
                linkage_status,
                baseline,
            ),
            measurement(
                row["source_page"],
                "current",
                "annual_actual",
                linkage_status,
                current,
            ),
            measurement(
                row["source_page"],
                "target",
                "final_target",
                linkage_status,
                target,
            ),
        ],
        "evidence": {
            "primary_source_number": 1,
            "primary_page": row["source_page"],
            "locations": evidence_locations(row, rows_by_id),
        },
        "boundary": boundary(row, reasons),
        "evaluation_status": row["evaluation_status"],
        "comparability_status": "excluded_until_verified",
    }


def build_catalog(root: Path = ROOT) -> dict[str, Any]:
    source = load(root / SOURCE_RELATIVE_PATH)
    rows_by_id = {row["id"]: row for row in source["items"]}
    records = [
        normalize_row(source, row, rows_by_id)
        for row in source["items"]
    ]
    statuses = Counter(record["linkage_status"] for record in records)
    partial_reason_counts = Counter(
        record["partial_reason"]
        for record in records
        if record["linkage_status"] == "partial"
    )

    return {
        "id": "phase11-aichi-normalized-records",
        "phase": 11,
        "status": "normalized",
        "prefecture_code": "23",
        "source_catalog": SOURCE_RELATIVE_PATH,
        "sources": [
            {
                "source_number": 1,
                "role": "annual_progress_report",
                "title": source["source_title"],
                "url": source["source_document_url"],
            },
            {
                "source_number": 2,
                "role": "target_plan",
                "title": "あいちビジョン2030 2024-2026実施計画 進捗目標",
                "url": source["target_source_document_url"],
            },
        ],
        "records": records,
        "summary": {
            "record_count": len(records),
            "linked_record_count": statuses["linked"],
            "partial_record_count": statuses["partial"],
            "indicator_series_count": sum(
                len(row["series"]) for row in source["items"]
            ),
            "linked_current_series_count": sum(
                row["linked_current_series_count"] for row in source["items"]
            ),
            "missing_current_series_count": (
                source["indicator_series_count"]
                - source["series_with_current_value"]
            ),
            "target_series_count": sum(
                row["target_series_count"] for row in source["items"]
            ),
            "repost_record_count": sum(
                row["repost_of"] is not None for row in source["items"]
            ),
            "target_revision_record_count": sum(
                row["target_revision_status"] == "revised_in_2025_report"
                for row in source["items"]
            ),
            "partial_reason_counts": dict(sorted(partial_reason_counts.items())),
            "policy_achievement_assessment_count": 0,
        },
        "updated_at": source["reviewed_at"],
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
