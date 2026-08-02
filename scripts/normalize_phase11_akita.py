#!/usr/bin/env python3
"""Normalize the reviewed Akita digital-book indicator row at maximum depth."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/phase9/05.json"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def digital_book_page(url: str) -> int:
    filename = Path(urlparse(url).path).name
    if not filename.startswith("index") or not filename.endswith(".html"):
        raise ValueError(f"Unsupported digital-book page URL: {url}")
    return int(filename.removeprefix("index").removesuffix(".html"))


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
    page = digital_book_page(record["source_document_url"])
    return {
        "id": "phase11-record-akita-001",
        "prefecture_code": "05",
        "source_registry": SOURCE_RELATIVE_PATH,
        "source_record_id": record["id"],
        "linkage_kind": "target_to_annual_actual",
        "linkage_status": "partial",
        "partial_reason": "compound_plan_row_not_structured_and_annual_actual_unavailable",
        "subject": {
            "record_ref": record["id"],
            "sequence": record["display_order"],
            "name": "秋田県総合計画2026-2029 主要な指標",
            "source_name": record["indicator_name_original"],
            "definition": record["plan_history_boundary"],
            "hierarchy_refs": [
                "akita-comprehensive-plan-2026-2029",
                "akita-digital-book-major-indicators",
            ],
        },
        "indicator_context": {
            "policy_direction_code": "major-indicators-compound-row",
            "policy_direction_name": "秋田県総合計画2026-2029 主要な指標",
            "source_page": page,
            "repost_of": None,
            "target_revision_status": "new_plan_initial_version",
            "linked_current_series_count": 0,
            "target_series_count": 0,
            "review_status": record["review_status"],
            "quality_note": json.dumps(
                {
                    "plan_title": source["plan_title"],
                    "plan_period": source["plan_period"],
                    "source_id": source["source_id"],
                    "source_document_title": record[
                        "source_document_title"
                    ],
                    "source_document_url": record[
                        "source_document_url"
                    ],
                    "source_document_sha256": record[
                        "source_document_sha256"
                    ],
                    "source_row": record["source_location"]["row"],
                    "evidence_page": page,
                    "evidence_page_basis": "digital_book_index24_url",
                    "numeric_tokens_original": record[
                        "numeric_tokens_original"
                    ],
                    "period_tokens_original": record[
                        "period_tokens_original"
                    ],
                    "unit_original": record["unit_original"],
                    "population_scope_original": record[
                        "population_scope_original"
                    ],
                    "comparability": record["comparability"],
                    "maximum_depth": "compound_plan_indicator_row",
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
            "series": [
                {
                    "series_ref": f"{record['id']}-raw-series-01",
                    "label": "主要な指標の複合原文行",
                    "unit": record["unit_original"],
                    "direction": "not_inferred",
                    "comparability_note": (
                        "産業、農林水産、観光、人口、所得、企業等の複数指標が"
                        "一つのデジタルブック行へ混在しているため分解しない。"
                    ),
                    "value_count": 1,
                }
            ],
        },
        "measurements": [
            {
                "role": "plan_current",
                "status": "reported",
                "period_text": "",
                "value_text": record["target_statement_original"],
                "components": [
                    {
                        "record_ref": f"{record['id']}-compound-plan-row",
                        "catalog_role": "compound_plan_indicator_row",
                        "label": "主要な指標の複合原文行",
                        "unit": record["unit_original"],
                        "period_text": "",
                        "value_text": record["target_statement_original"],
                        "value": record["target_statement_original"],
                        "value_status": "textual",
                        "source_status": "reported_raw",
                        "scope": record["aggregation_scope"],
                        "aggregation_scope": record["aggregation_scope"],
                        "preferred_direction": None,
                        "operator": record["target_operator"],
                    }
                ],
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
            "2026年度開始の現行計画デジタルブック24ページに掲載された"
            "主要指標の複合原文行を、数値トークン、単位、対象、HTML行、"
            "ハッシュ付きで保持した。複数の現状値・目標値・推計値が一行へ"
            "混在するため構造を推測せずPartialとし、初年度年次評価は未公表"
            "としてannual actualを接続しない。旧計画の目標・実績を自動継承"
            "せず、政策達成・因果・全国比較は判定しない。"
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
        "id": "phase11-akita-normalized-records",
        "phase": 11,
        "status": "reviewed_maximum_depth",
        "prefecture_code": "05",
        "source_catalog": SOURCE_RELATIVE_PATH,
        "sources": [
            {
                "source_number": 1,
                "role": "current_plan_compound_indicator_row",
                "title": source["source_title"],
                "url": source["source_url"],
                "plan_title": source["plan_title"],
                "plan_period": source["plan_period"],
                "digital_book_page": 24,
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
            "structured_future_target_available_count": 0,
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
