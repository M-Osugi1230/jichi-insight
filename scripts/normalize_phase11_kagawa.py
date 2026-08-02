#!/usr/bin/env python3
"""Normalize all reviewed Kagawa extended-plan indicators."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATHS = [
    "data/reviewed/kagawa_extended_plan_indicators_part1.json",
    "data/reviewed/kagawa_extended_plan_indicators_part2.json",
    "data/reviewed/kagawa_extended_plan_indicators_part3.json",
]
OCCURRENCES_RELATIVE_PATH = (
    "data/reviewed/kagawa_extended_plan_indicator_occurrences.json"
)


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_records(
    root: Path = ROOT,
) -> list[tuple[str, dict[str, Any]]]:
    records: list[tuple[str, dict[str, Any]]] = []
    for relative_path in SOURCE_RELATIVE_PATHS:
        part = load(root / relative_path)
        records.extend(
            (relative_path, record)
            for record in part["records"]
        )
    return records


def occurrence_index(
    root: Path = ROOT,
) -> dict[int, list[dict[str, Any]]]:
    document = load(root / OCCURRENCES_RELATIVE_PATH)
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for occurrence in document["occurrences"]:
        grouped[occurrence["indicator_number"]].append(occurrence)
    return dict(grouped)


def component(
    record: dict[str, Any],
    role: str,
    value_text: str,
) -> dict[str, Any]:
    return {
        "record_ref": f"{record['indicator_id']}-{role}",
        "catalog_role": role,
        "label": None,
        "unit": None,
        "period_text": value_text,
        "value_text": value_text,
        "value": value_text,
        "value_status": "textual",
        "source_status": "reported_raw",
        "scope": None,
        "aggregation_scope": None,
        "preferred_direction": None,
        "operator": None,
    }


def measurement(
    record: dict[str, Any],
    normalized_role: str,
    source_role: str,
    value_text: str,
) -> dict[str, Any]:
    return {
        "role": normalized_role,
        "status": "available" if normalized_role == "annual_actual" else "reported",
        "period_text": value_text,
        "value_text": value_text,
        "components": [component(record, source_role, value_text)],
        "evidence": {
            "source_number": 1,
            "page": record["source_pdf_page"],
        },
    }


def evidence_locations(
    occurrences: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {
            "source_number": 1,
            "page": occurrence["source_pdf_page"],
            "is_reprint": index > 0,
        }
        for index, occurrence in enumerate(occurrences)
    ]


def quality_note(
    record: dict[str, Any],
    occurrences: list[dict[str, Any]],
) -> str:
    return json.dumps(
        {
            "evidence_id": record["evidence_id"],
            "plan_heading_original": record["plan_heading_original"],
            "section_heading_original": record["section_heading_original"],
            "policy_number_original": record["policy_number_original"],
            "indicator_overview_original": record[
                "indicator_overview_original"
            ],
            "target_rationale_original": record[
                "target_rationale_original"
            ],
            "display_occurrence_count": record[
                "display_occurrence_count"
            ],
            "has_repost_occurrence": record["has_repost_occurrence"],
            "occurrences": occurrences,
        },
        ensure_ascii=False,
        sort_keys=True,
    )


def boundary(record: dict[str, Any]) -> str:
    revised = record["target_r7_original"] != record["target_r8_original"]
    revision_note = (
        "R7目標と延長後R8目標を別Measurementとして保持した。"
        if revised
        else "R7目標と延長後R8目標は同値だが別版として保持した。"
    )
    return (
        "延長計画の固有指標について、指標名、現状値、R7目標、R8目標、"
        "概要、目標設定理由、政策番号、全表示位置を原文のまま保持した。"
        f"{revision_note}訂正矢印、複数系列、累積期間、参考目標を推測で"
        "分解・補正せず、再掲を別指標へ重複計上せず、政策達成・因果・"
        "全国比較は判定しない。"
    )


def normalize_record(
    source_registry: str,
    record: dict[str, Any],
    occurrences: list[dict[str, Any]],
) -> dict[str, Any]:
    revised = record["target_r7_original"] != record["target_r8_original"]
    number = record["indicator_number"]

    return {
        "id": f"phase11-record-kagawa-{number:03d}",
        "prefecture_code": "37",
        "source_registry": source_registry,
        "source_record_id": record["indicator_id"],
        "linkage_kind": "target_to_annual_actual",
        "linkage_status": "linked",
        "partial_reason": None,
        "subject": {
            "record_ref": record["indicator_id"],
            "sequence": number,
            "name": record["indicator_name_original"],
            "source_name": record["indicator_name_original"],
            "definition": record["indicator_overview_original"],
            "hierarchy_refs": [
                f"kagawa-plan-{record['plan_heading_original']}",
                f"kagawa-section-{record['section_heading_original']}",
                f"kagawa-policy-{record['policy_number_original']}",
            ],
        },
        "indicator_context": {
            "policy_direction_code": (
                f"policy-{record['policy_number_original']}"
            ),
            "policy_direction_name": record["section_heading_original"],
            "source_page": record["source_pdf_page"],
            "repost_of": None,
            "target_revision_status": (
                "revised_for_r8_extension" if revised else "unchanged_for_r8"
            ),
            "linked_current_series_count": 1,
            "target_series_count": 1,
            "review_status": record["review_status"],
            "quality_note": quality_note(record, occurrences),
            "series": [
                {
                    "series_ref": (
                        f"{record['indicator_id']}-raw-series-01"
                    ),
                    "label": None,
                    "unit": "原文",
                    "direction": "not_inferred",
                    "comparability_note": (
                        "訂正値、複数系列、累積期間、参考目標を含み得る"
                        "原文を一つのReviewed系列として保持する。"
                    ),
                    "value_count": 3,
                }
            ],
        },
        "measurements": [
            measurement(
                record,
                "annual_actual",
                "current",
                record["current_value_original"],
            ),
            measurement(
                record,
                "intermediate_target",
                "target_r7",
                record["target_r7_original"],
            ),
            measurement(
                record,
                "final_target",
                "target_r8",
                record["target_r8_original"],
            ),
        ],
        "evidence": {
            "primary_source_number": 1,
            "primary_page": record["source_pdf_page"],
            "locations": evidence_locations(occurrences),
        },
        "boundary": boundary(record),
        "evaluation_status": record[
            "policy_achievement_assessment_status"
        ],
        "comparability_status": "excluded_until_verified",
    }


def build_catalog(root: Path = ROOT) -> dict[str, Any]:
    source_records = load_records(root)
    occurrences_by_number = occurrence_index(root)
    records = [
        normalize_record(
            source_registry,
            record,
            occurrences_by_number[record["indicator_number"]],
        )
        for source_registry, record in source_records
    ]
    revised_count = sum(
        record["target_r7_original"] != record["target_r8_original"]
        for _, record in source_records
    )
    repost_count = sum(
        len(occurrences_by_number[number]) > 1
        for number in occurrences_by_number
    )

    return {
        "id": "phase11-kagawa-normalized-records",
        "phase": 11,
        "status": "normalized",
        "prefecture_code": "37",
        "source_catalogs": SOURCE_RELATIVE_PATHS,
        "occurrence_catalog": OCCURRENCES_RELATIVE_PATH,
        "sources": [
            {
                "source_number": 1,
                "role": "extended_plan_indicator_catalog",
                "title": "計画期間の延長及び指標の目標値等の見直しについて",
                "url": "https://www.pref.kagawa.lg.jp/documents/36520/shiryou3_shihyouminaoshi.pdf",
                "indicator_pages": list(range(3, 18)),
            }
        ],
        "records": records,
        "summary": {
            "record_count": len(records),
            "linked_record_count": len(records),
            "partial_record_count": 0,
            "not_linked_record_count": 0,
            "indicator_series_count": len(records),
            "display_occurrence_count": sum(
                len(items) for items in occurrences_by_number.values()
            ),
            "reposted_indicator_count": repost_count,
            "target_revision_count": revised_count,
            "unchanged_target_count": len(records) - revised_count,
            "policy_achievement_assessment_count": 0,
        },
        "updated_at": "2026-08-02",
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
