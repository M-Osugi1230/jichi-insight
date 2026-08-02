#!/usr/bin/env python3
"""Normalize reviewed Aomori Phase 9 records at maximum official-source depth."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/phase9/02.json"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def reported_component(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "record_ref": f"{record['id']}-reviewed-observation",
        "catalog_role": "reviewed_observation_statement",
        "label": record["indicator_name_original"],
        "unit": record["unit_original"],
        "period_text": " / ".join(record["period_tokens_original"]),
        "value_text": record["target_statement_original"],
        "value": record["target_statement_original"],
        "value_status": "textual",
        "source_status": "reported_raw",
        "scope": record["aggregation_scope"],
        "aggregation_scope": record["aggregation_scope"],
        "preferred_direction": None,
        "operator": record["target_operator"],
    }


def unavailable_measurement(role: str) -> dict[str, Any]:
    return {
        "role": role,
        "status": "not_available",
        "period_text": "",
        "value_text": "",
        "components": [],
        "evidence": {"source_number": None, "page": None},
    }


def normalize_record(
    source: dict[str, Any],
    record: dict[str, Any],
) -> dict[str, Any]:
    page = record["source_location"]["page"]
    return {
        "id": "phase11-record-aomori-001",
        "prefecture_code": "02",
        "source_registry": SOURCE_RELATIVE_PATH,
        "source_record_id": record["id"],
        "linkage_kind": "target_to_annual_actual",
        "linkage_status": "partial",
        "partial_reason": "annual_actual_and_future_target_not_reviewed",
        "subject": {
            "record_ref": record["id"],
            "sequence": record["display_order"],
            "name": record["indicator_name_original"],
            "source_name": record["indicator_name_original"],
            "definition": record["plan_history_boundary"],
            "hierarchy_refs": [
                "aomori-current-plan-2024-2028",
                "aomori-observation-indicator",
            ],
        },
        "indicator_context": {
            "policy_direction_code": "fiscal-and-economic-observation",
            "policy_direction_name": "現行基本計画の観察指標",
            "source_page": page,
            "repost_of": None,
            "target_revision_status": "future_target_not_reviewed",
            "linked_current_series_count": 0,
            "target_series_count": 0,
            "review_status": record["review_status"],
            "quality_note": json.dumps(
                {
                    "plan_title": source["plan_title"],
                    "plan_period": source["plan_period"],
                    "source_id": source["source_id"],
                    "source_title": source["source_title"],
                    "source_document_title": record[
                        "source_document_title"
                    ],
                    "source_document_sha256": record[
                        "source_document_sha256"
                    ],
                    "source_row": record["source_location"]["row"],
                    "numeric_tokens_original": record[
                        "numeric_tokens_original"
                    ],
                    "period_tokens_original": record[
                        "period_tokens_original"
                    ],
                    "comparability": record["comparability"],
                    "maximum_depth": "reviewed_observation_statement",
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
            "series": [
                {
                    "series_ref": f"{record['id']}-raw-series-01",
                    "label": record["indicator_name_original"],
                    "unit": record["unit_original"],
                    "direction": "not_inferred",
                    "comparability_note": (
                        "2011〜2021年度の推移を示す観察指標の原文であり、"
                        "将来目標またはReviewed年度実績ではない。"
                    ),
                    "value_count": 1,
                }
            ],
        },
        "measurements": [
            {
                "role": "plan_current",
                "status": "reported",
                "period_text": " / ".join(record["period_tokens_original"]),
                "value_text": record["target_statement_original"],
                "components": [reported_component(record)],
                "evidence": {"source_number": 1, "page": page},
            },
            unavailable_measurement("annual_actual"),
            unavailable_measurement("final_target"),
        ],
        "evidence": {
            "primary_source_number": 1,
            "primary_page": page,
            "locations": [
                {
                    "source_number": 1,
                    "page": page,
                    "is_reprint": False,
                }
            ],
        },
        "boundary": (
            "青森県の現行基本計画概要版でReviewedされた1人当たり県民所得の"
            "2011〜2021年度推移を、観察指標の原文として保持した。"
            "この記載は将来目標または年度実績の接続ではないためPartialとし、"
            "数値トークンを単一系列へ推測分解せず、旧計画KPIや政策点検結果を"
            "自動継承せず、政策達成・因果・全国比較は判定しない。"
        ),
        "evaluation_status": record[
            "policy_achievement_assessment_status"
        ],
        "comparability_status": "excluded_until_verified",
    }


def build_catalog(root: Path = ROOT) -> dict[str, Any]:
    source = load(root / SOURCE_RELATIVE_PATH)
    records = [normalize_record(source, record) for record in source["records"]]

    return {
        "id": "phase11-aomori-normalized-records",
        "phase": 11,
        "status": "reviewed_maximum_depth",
        "prefecture_code": "02",
        "source_catalog": SOURCE_RELATIVE_PATH,
        "sources": [
            {
                "source_number": 1,
                "role": "current_plan_reviewed_observation",
                "title": source["source_title"],
                "url": source["source_url"],
                "plan_title": source["plan_title"],
                "plan_period": source["plan_period"],
            }
        ],
        "records": records,
        "summary": {
            "record_count": len(records),
            "linked_record_count": 0,
            "partial_record_count": len(records),
            "not_linked_record_count": 0,
            "indicator_series_count": len(records),
            "annual_actual_available_count": 0,
            "future_target_available_count": 0,
            "reviewed_maximum_depth_record_count": len(records),
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
