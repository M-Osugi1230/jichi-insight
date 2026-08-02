#!/usr/bin/env python3
"""Normalize every reviewed Hiroshima revised-vision indicator."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATHS = [
    "data/reviewed/hiroshima_revised_vision_indicators_part1.json",
    "data/reviewed/hiroshima_revised_vision_indicators_part2.json",
    "data/reviewed/hiroshima_revised_vision_indicators_part3.json",
]


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


def is_missing_current(raw: str) -> bool:
    return raw == "―" or "新たに調査" in raw


def component(
    record: dict[str, Any],
    role: str,
    raw: str,
    period_text: str,
) -> dict[str, Any]:
    missing = raw == "―" or (role == "current" and is_missing_current(raw))
    return {
        "record_ref": f"{record['id']}-{role}",
        "catalog_role": role,
        "label": None,
        "unit": None,
        "period_text": period_text,
        "value_text": raw,
        "value": None if missing else raw,
        "value_status": "missing" if missing else "textual",
        "source_status": (
            "pending_measurement"
            if role == "current" and "新たに調査" in raw
            else "missing" if missing else "reported_raw"
        ),
        "scope": None,
        "aggregation_scope": None,
        "preferred_direction": None,
        "operator": None,
    }


def measurement(
    record: dict[str, Any],
    source_page: int,
    source_role: str,
    normalized_role: str,
    raw: str,
    period_text: str,
    linkage_status: str,
) -> dict[str, Any]:
    item = component(record, source_role, raw, period_text)
    if item["value_status"] == "missing":
        status = "not_available"
    elif normalized_role == "annual_actual":
        status = "available_raw_only" if linkage_status == "partial" else "available"
    else:
        status = "reported"
    return {
        "role": normalized_role,
        "status": status,
        "period_text": period_text,
        "value_text": raw,
        "components": [item],
        "evidence": {"source_number": 1, "page": source_page},
    }


def quality_note(record: dict[str, Any]) -> str:
    return json.dumps(
        {
            "evidence_id": record["evidence_id"],
            "change": record["change"],
            "source_original": record["source"],
            "target_period": record["target_period"],
            "raw_values_are_not_split": True,
        },
        ensure_ascii=False,
        sort_keys=True,
    )


def boundary(record: dict[str, Any], linkage_status: str) -> str:
    if linkage_status == "partial":
        return (
            "改定版ビジョンの指標名、基準値、現状値、目標値、目標年度、"
            "定義変更状態、出典を原文のまま保持したが、現状値が未測定または"
            "測定予定のためPartialとする。値を推測せず、政策達成・因果・"
            "全国比較は判定しない。"
        )
    return (
        "改定版ビジョンの同一指標行に記載された基準値、現状値、目標値、"
        "目標年度、定義変更状態、出典を原文のまま保持した。複数系列、"
        "比較値、平均期間、定性条件を分解・補正せず、政策達成・因果・"
        "全国比較は判定しない。"
    )


def normalize_record(
    source_registry: str,
    record: dict[str, Any],
) -> dict[str, Any]:
    partial = is_missing_current(record["current"])
    linkage_status = "partial" if partial else "linked"
    sequence = int(record["id"].rsplit("-", 1)[1])
    series_ref = f"{record['id']}-raw-series-01"

    return {
        "id": f"phase11-record-hiroshima-{sequence:03d}",
        "prefecture_code": "34",
        "source_registry": source_registry,
        "source_record_id": record["id"],
        "linkage_kind": "target_to_annual_actual",
        "linkage_status": linkage_status,
        "partial_reason": "pending_measurement" if partial else None,
        "subject": {
            "record_ref": record["id"],
            "sequence": sequence,
            "name": record["name"],
            "source_name": record["name"],
            "definition": record["change"],
            "hierarchy_refs": [f"hiroshima-policy-area-{record['area']}"],
        },
        "indicator_context": {
            "policy_direction_code": record["area"],
            "policy_direction_name": record["area"],
            "source_page": record["page"],
            "repost_of": None,
            "target_revision_status": record["change"],
            "linked_current_series_count": 0 if partial else 1,
            "target_series_count": 1,
            "review_status": record["review"],
            "quality_note": quality_note(record),
            "series": [
                {
                    "series_ref": series_ref,
                    "label": None,
                    "unit": "原文",
                    "direction": "not_inferred",
                    "comparability_note": (
                        "複数系列、全国比較値、平均期間、定性条件を含み得る"
                        "原文を一つのReviewed行として保持する。"
                    ),
                    "value_count": 3,
                }
            ],
        },
        "measurements": [
            measurement(
                record,
                record["page"],
                "baseline",
                "plan_current",
                record["baseline"],
                record["baseline"],
                linkage_status,
            ),
            measurement(
                record,
                record["page"],
                "current",
                "annual_actual",
                record["current"],
                record["current"],
                linkage_status,
            ),
            measurement(
                record,
                record["page"],
                "target",
                "final_target",
                record["target"],
                record["target_period"],
                linkage_status,
            ),
        ],
        "evidence": {
            "primary_source_number": 1,
            "primary_page": record["page"],
            "locations": [
                {
                    "source_number": 1,
                    "page": record["page"],
                    "is_reprint": False,
                }
            ],
        },
        "boundary": boundary(record, linkage_status),
        "evaluation_status": record["assessment"],
        "comparability_status": "excluded_until_verified",
    }


def build_catalog(root: Path = ROOT) -> dict[str, Any]:
    source_records = load_records(root)
    records = [
        normalize_record(source_registry, record)
        for source_registry, record in source_records
    ]
    statuses = Counter(record["linkage_status"] for record in records)
    areas = Counter(
        record["indicator_context"]["policy_direction_name"]
        for record in records
    )
    change_counts = Counter(
        json.loads(record["indicator_context"]["quality_note"])["change"]
        for record in records
    )

    return {
        "id": "phase11-hiroshima-normalized-records",
        "phase": 11,
        "status": "normalized",
        "prefecture_code": "34",
        "source_catalogs": SOURCE_RELATIVE_PATHS,
        "sources": [
            {
                "source_number": 1,
                "role": "revised_vision_indicator_catalog",
                "title": "安心・誇り・挑戦 ひろしまビジョン 改定版",
                "url": "https://www.pref.hiroshima.lg.jp/uploaded/attachment/674716.pdf",
                "indicator_pages": [109, 111, 113, 115, 117, 119, 121],
            }
        ],
        "records": records,
        "summary": {
            "record_count": len(records),
            "linked_record_count": statuses["linked"],
            "partial_record_count": statuses["partial"],
            "not_linked_record_count": statuses["not_linked"],
            "policy_area_count": len(areas),
            "pending_measurement_record_count": statuses["partial"],
            "qualitative_target_record_count": sum(
                record["target"]
                == "多国間枠組みに核兵器国を含む全ての国が参加"
                for _, record in source_records
            ),
            "change_counts": dict(sorted(change_counts.items())),
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
