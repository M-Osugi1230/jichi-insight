#!/usr/bin/env python3
"""Normalize reviewed Iwate change-booklet statements at maximum depth."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/phase9/03.json"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def unavailable_measurement(role: str) -> dict[str, Any]:
    return {
        "role": role,
        "status": "not_available",
        "period_text": "",
        "value_text": "",
        "components": [],
        "evidence": {"source_number": None, "page": None},
    }


def raw_component(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "record_ref": f"{record['id']}-reviewed-raw-statement",
        "catalog_role": "reviewed_change_booklet_statement",
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


def quality_note(source: dict[str, Any], record: dict[str, Any]) -> str:
    return json.dumps(
        {
            "plan_title": source["plan_title"],
            "plan_period": source["plan_period"],
            "source_id": source["source_id"],
            "evidence_id": record["evidence_id"],
            "source_document_title": record["source_document_title"],
            "source_document_url": record["source_document_url"],
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
            "matched_keywords": record["matched_keywords"],
            "keyword_match_kind": record["keyword_match_kind"],
            "unit_original": record["unit_original"],
            "population_scope_original": record[
                "population_scope_original"
            ],
            "comparability": record["comparability"],
            "maximum_depth": "reviewed_change_booklet_raw_statement",
        },
        ensure_ascii=False,
        sort_keys=True,
    )


def normalize_record(
    source: dict[str, Any],
    record: dict[str, Any],
) -> dict[str, Any]:
    sequence = record["display_order"]
    page = record["source_location"]["page"]
    period_text = " / ".join(record["period_tokens_original"])

    return {
        "id": f"phase11-record-iwate-{sequence:03d}",
        "prefecture_code": "03",
        "source_registry": SOURCE_RELATIVE_PATH,
        "source_record_id": record["id"],
        "linkage_kind": "target_to_annual_actual",
        "linkage_status": "partial",
        "partial_reason": "structured_actual_and_target_not_reviewed",
        "subject": {
            "record_ref": record["id"],
            "sequence": sequence,
            "name": record["indicator_name_original"],
            "source_name": record["indicator_name_original"],
            "definition": record["plan_history_boundary"],
            "hierarchy_refs": [
                "iwate-current-action-plan-2023-2026",
                f"iwate-source-{record['source_document_sha256'][:12]}",
            ],
        },
        "indicator_context": {
            "policy_direction_code": "change-booklet-reviewed-line",
            "policy_direction_name": record["source_document_title"],
            "source_page": page,
            "repost_of": None,
            "target_revision_status": "raw_change_booklet_statement",
            "linked_current_series_count": 0,
            "target_series_count": 0,
            "review_status": record["review_status"],
            "quality_note": quality_note(source, record),
            "series": [
                {
                    "series_ref": f"{record['id']}-raw-series-01",
                    "label": record["indicator_name_original"],
                    "unit": record["unit_original"] or "未記載",
                    "direction": "not_inferred",
                    "comparability_note": (
                        "変更別冊からReviewedされた原文行であり、現状値、"
                        "目標値、注記、複数系列が同じ行へ混在し得る。"
                    ),
                    "value_count": 1,
                }
            ],
        },
        "measurements": [
            {
                "role": "plan_current",
                "status": "reported",
                "period_text": period_text,
                "value_text": record["target_statement_original"],
                "components": [raw_component(record)],
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
            "令和6年12月の指標変更別冊からReviewedされた原文行を、"
            "資料、ページ、表行、ハッシュ、数値・期間トークン付きで保持した。"
            "表行には現状値、目標値、変更注記、複数系列が混在し得るため、"
            "構造化されたannual actualまたはfuture targetへ推測昇格せず"
            "Partialとする。政策推進、復興推進、4地域振興圏の別冊を混合せず、"
            "政策達成・因果・全国比較は判定しない。"
        ),
        "evaluation_status": record[
            "policy_achievement_assessment_status"
        ],
        "comparability_status": "excluded_until_verified",
    }


def build_catalog(root: Path = ROOT) -> dict[str, Any]:
    source = load(root / SOURCE_RELATIVE_PATH)
    records = [normalize_record(source, record) for record in source["records"]]
    documents = Counter(
        record["source_document_title"] for record in source["records"]
    )

    return {
        "id": "phase11-iwate-normalized-records",
        "phase": 11,
        "status": "reviewed_maximum_depth",
        "prefecture_code": "03",
        "source_catalog": SOURCE_RELATIVE_PATH,
        "sources": [
            {
                "source_number": 1,
                "role": "current_action_plan_change_booklets",
                "title": source["source_title"],
                "url": source["source_url"],
                "plan_title": source["plan_title"],
                "plan_period": source["plan_period"],
                "document_count": len(source["documents"]),
            }
        ],
        "records": records,
        "summary": {
            "record_count": len(records),
            "linked_record_count": 0,
            "partial_record_count": len(records),
            "not_linked_record_count": 0,
            "indicator_series_count": len(records),
            "source_document_count": len(documents),
            "annual_actual_available_count": 0,
            "future_target_available_count": 0,
            "reviewed_maximum_depth_record_count": len(records),
            "policy_achievement_assessment_count": 0,
        },
        "document_record_counts": dict(sorted(documents.items())),
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
