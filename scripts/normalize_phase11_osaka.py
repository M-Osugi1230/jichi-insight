#!/usr/bin/env python3
"""Normalize every reviewed Osaka Beyond EXPO indicator row."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/osaka_beyond_expo_indicators.json"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def series_ref(row_id: str, series_index: int) -> str:
    return f"{row_id}-series-{series_index:02d}"


def value_status(source_status: str) -> str:
    return "numeric" if source_status == "numeric" else "missing"


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
        "label": series["label_original"],
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


def series_has_current(series: dict[str, Any]) -> bool:
    return any(
        value["role"] == "current" and value["status"] != "missing"
        for value in series["values"]
    )


def partial_reasons(row: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if row["indicator_layer"] == "strategy_target":
        reasons.append("target_without_current_observation")
    missing_current = sum(
        not series_has_current(series) for series in row["series"]
    )
    if missing_current and row["indicator_layer"] != "strategy_target":
        reasons.append("missing_current_series")
    return reasons


def measurement_status(
    normalized_role: str,
    linkage_status: str,
    components: list[dict[str, Any]],
) -> str:
    if not components:
        return "not_available"
    if all(component["value_status"] == "missing" for component in components):
        return "not_available"
    if normalized_role == "annual_actual":
        return "available_raw_only" if linkage_status == "partial" else "available"
    return "reported"


def measurement(
    source_page: int,
    normalized_role: str,
    linkage_status: str,
    components: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "role": normalized_role,
        "status": measurement_status(
            normalized_role,
            linkage_status,
            components,
        ),
        "period_text": joined_unique(components, "period_text"),
        "value_text": joined_unique(components, "value_text"),
        "components": components,
        "evidence": {"source_number": 1, "page": source_page},
    }


def context_quality_note(row: dict[str, Any]) -> str:
    metadata = {
        "category_original": row["category_original"],
        "response_scale": row["response_scale"],
        "legacy_vision_linkage_status": row[
            "legacy_vision_linkage_status"
        ],
        "business_list_linkage_status": row[
            "business_list_linkage_status"
        ],
        "confidence": row["confidence"],
        "comparability_note_original": row[
            "comparability_note_original"
        ],
    }
    return json.dumps(metadata, ensure_ascii=False, sort_keys=True)


def boundary(row: dict[str, Any], reasons: list[str]) -> str:
    if not reasons:
        return (
            "Beyond EXPO 2025の同一指標行に記載されたcurrent値を、系列、"
            "単位、期間、方向、集計範囲とともに保持した。個別数値目標がない"
            "KPIを目標達成とみなさず、政策達成・因果・全国比較は判定しない。"
        )
    return (
        "Beyond EXPO 2025の指標行と全系列は保持したが、"
        f"{', '.join(reasons)}のため個票はPartialとする。"
        "初回調査前の欠損値や将来目標を実績として補完せず、政策達成・因果・"
        "全国比較は判定しない。"
    )


def normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    reasons = partial_reasons(row)
    linkage_status = "partial" if reasons else "linked"
    baseline = components_for_role(row, "baseline")
    current = components_for_role(row, "current")
    target = components_for_role(row, "target")
    current_series_count = sum(
        series_has_current(series) for series in row["series"]
    )
    target_series_count = sum(
        any(value["role"] == "target" for value in series["values"])
        for series in row["series"]
    )

    return {
        "id": f"phase11-record-osaka-{row['display_order']:03d}",
        "prefecture_code": "27",
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
            "definition": row["comparability_note_original"],
            "hierarchy_refs": [
                f"osaka-layer-{row['indicator_layer']}",
                f"osaka-pillar-{row['pillar_original']}",
                f"osaka-category-{row['category_original']}",
            ],
        },
        "indicator_context": {
            "policy_direction_code": row["indicator_layer"],
            "policy_direction_name": row["pillar_original"],
            "source_page": row["source_page"],
            "repost_of": None,
            "target_revision_status": "not_applicable",
            "linked_current_series_count": current_series_count,
            "target_series_count": target_series_count,
            "review_status": row["review_status"],
            "quality_note": context_quality_note(row),
            "series": [
                {
                    "series_ref": series_ref(row["id"], index),
                    "label": series["label_original"],
                    "unit": series["unit_original"],
                    "direction": series["direction"],
                    "comparability_note": row[
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
                "plan_current",
                linkage_status,
                baseline,
            ),
            measurement(
                row["source_page"],
                "annual_actual",
                linkage_status,
                current,
            ),
            measurement(
                row["source_page"],
                "final_target",
                linkage_status,
                target,
            ),
        ],
        "evidence": {
            "primary_source_number": 1,
            "primary_page": row["source_page"],
            "locations": [
                {
                    "source_number": 1,
                    "page": row["source_page"],
                    "is_reprint": False,
                }
            ],
        },
        "boundary": boundary(row, reasons),
        "evaluation_status": row[
            "policy_achievement_assessment_status"
        ],
        "comparability_status": "excluded_until_verified",
    }


def build_catalog(root: Path = ROOT) -> dict[str, Any]:
    source = load(root / SOURCE_RELATIVE_PATH)
    records = [normalize_row(row) for row in source["items"]]
    statuses = Counter(record["linkage_status"] for record in records)
    layers = Counter(row["indicator_layer"] for row in source["items"])
    current_series = sum(
        series_has_current(series)
        for row in source["items"]
        for series in row["series"]
    )
    target_series = sum(
        any(value["role"] == "target" for value in series["values"])
        for row in source["items"]
        for series in row["series"]
    )
    rows_with_current = sum(
        all(series_has_current(series) for series in row["series"])
        for row in source["items"]
    )

    return {
        "id": "phase11-osaka-normalized-records",
        "phase": 11,
        "status": "normalized",
        "prefecture_code": "27",
        "source_catalog": SOURCE_RELATIVE_PATH,
        "sources": [
            {
                "source_number": 1,
                "role": "current_strategy_indicator_catalog",
                "title": source["source_title"],
                "url": source["source_document_url"],
                "adopted_at": source["adopted_at"],
            }
        ],
        "records": records,
        "summary": {
            "record_count": len(records),
            "linked_record_count": statuses["linked"],
            "partial_record_count": statuses["partial"],
            "not_linked_record_count": statuses["not_linked"],
            "indicator_series_count": sum(
                len(row["series"]) for row in source["items"]
            ),
            "series_with_current_value": current_series,
            "series_without_current_value": (
                source["indicator_series_count"] - current_series
            ),
            "rows_with_current_observation": rows_with_current,
            "rows_without_current_observation": len(records) - rows_with_current,
            "target_series_count": target_series,
            "strategy_target_count": layers["strategy_target"],
            "objective_kpi_count": layers["objective_kpi"],
            "subjective_indicator_count": layers[
                "subjective_wellbeing"
            ],
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
