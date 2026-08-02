#!/usr/bin/env python3
"""Reusable Phase 11 normalizer for large Phase 9 reviewed raw catalogs."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def source_page(record: dict[str, Any]) -> int:
    page = record["source_location"].get("page")
    if not isinstance(page, int) or page < 1:
        raise ValueError(f"Record {record['id']} has no reviewed PDF page")
    return page


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
        "catalog_role": "reviewed_phase9_statement",
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
            "source_document_sha256": record["source_document_sha256"],
            "source_location": record["source_location"],
            "numeric_tokens_original": record["numeric_tokens_original"],
            "period_tokens_original": record["period_tokens_original"],
            "matched_keywords": record["matched_keywords"],
            "keyword_match_kind": record["keyword_match_kind"],
            "unit_original": record["unit_original"],
            "population_scope_original": record[
                "population_scope_original"
            ],
            "aggregation_scope": record["aggregation_scope"],
            "target_operator": record["target_operator"],
            "comparability": record["comparability"],
            "maximum_depth": "reviewed_phase9_raw_statement",
        },
        ensure_ascii=False,
        sort_keys=True,
    )


def normalize_record(
    source: dict[str, Any],
    record: dict[str, Any],
    *,
    prefecture_code: str,
    slug: str,
    source_registry: str,
    boundary: str,
) -> dict[str, Any]:
    sequence = record["display_order"]
    page = source_page(record)
    period_text = " / ".join(record["period_tokens_original"])

    return {
        "id": f"phase11-record-{slug}-{sequence:04d}",
        "prefecture_code": prefecture_code,
        "source_registry": source_registry,
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
                f"{slug}-current-plan-reviewed-statements",
                f"{slug}-source-{record['source_document_sha256'][:12]}",
            ],
        },
        "indicator_context": {
            "policy_direction_code": "phase9-reviewed-statement",
            "policy_direction_name": record["source_document_title"],
            "source_page": page,
            "repost_of": None,
            "target_revision_status": "raw_reviewed_statement",
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
                        "Phase 9でReviewedされた原文行であり、複数の数値、"
                        "期間、注記、現状値、目標値が混在し得るため分解しない。"
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
        "boundary": boundary,
        "evaluation_status": record[
            "policy_achievement_assessment_status"
        ],
        "comparability_status": "excluded_until_verified",
    }


def build_raw_catalog(
    root: Path,
    *,
    prefecture_code: str,
    slug: str,
    source_registry: str,
    expected_record_count: int,
    boundary: str,
) -> dict[str, Any]:
    source = load(root / source_registry)
    if source["prefecture_code"] != prefecture_code:
        raise ValueError("Prefecture code mismatch")
    if len(source["records"]) != expected_record_count:
        raise ValueError("Reviewed record count mismatch")

    records = [
        normalize_record(
            source,
            record,
            prefecture_code=prefecture_code,
            slug=slug,
            source_registry=source_registry,
            boundary=boundary,
        )
        for record in source["records"]
    ]
    documents = Counter(
        record["source_document_title"] for record in source["records"]
    )
    locations = Counter(
        record["source_location"]["location_kind"]
        for record in source["records"]
    )
    missing_units = sum(
        record["unit_original"] is None for record in source["records"]
    )

    return {
        "id": f"phase11-{slug}-normalized-records",
        "phase": 11,
        "status": "reviewed_maximum_depth",
        "prefecture_code": prefecture_code,
        "source_catalog": source_registry,
        "sources": [
            {
                "source_number": 1,
                "role": "phase9_reviewed_statements",
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
            "missing_unit_record_count": missing_units,
            "annual_actual_available_count": 0,
            "future_target_available_count": 0,
            "reviewed_maximum_depth_record_count": len(records),
            "policy_achievement_assessment_count": 0,
        },
        "document_record_counts": dict(sorted(documents.items())),
        "source_location_counts": dict(sorted(locations.items())),
        "updated_at": source["updated_at"],
    }
