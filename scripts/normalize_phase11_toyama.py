#!/usr/bin/env python3
"""Normalize the single reviewed Toyama HTML statement without fake pages."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/phase9/16.json"
BOUNDARY = (
    "富山県総合計画のPhase 9 Reviewed正本1行を、公式HTML、ハッシュ、"
    "html_text_lineの行79、原文、数値・期間トークン、単位、対象範囲、"
    "演算子、比較不能理由付きで保持した。HTML行位置をPDFページへ偽装せず、"
    "source_pageとprimary_pageはnull、source_locationは行79として記録する。"
    "この行は2022年9月の県民意識調査を踏まえ2023年1月に県独自の"
    "ウェルビーイング指標を策定したという説明であり、2025〜2029年度新計画"
    "の政策指標値や実績値そのものではない。新計画の12政策分野と"
    "ウェルビーイング指標を分離し、旧元気とやま創造計画の100政策評価を"
    "自動継承せず、初回政策評価は未公表として扱う。構造化annual actual、"
    "future target、政策達成、因果、全国比較へ推測昇格しない。"
)


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


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
            "population_scope_original": record["population_scope_original"],
            "aggregation_scope": record["aggregation_scope"],
            "target_operator": record["target_operator"],
            "comparability": record["comparability"],
            "maximum_depth": "reviewed_phase9_html_statement",
        },
        ensure_ascii=False,
        sort_keys=True,
    )


def unavailable_measurement(role: str) -> dict[str, Any]:
    return {
        "role": role,
        "status": "not_available",
        "period_text": "",
        "value_text": "",
        "components": [],
        "evidence": {
            "source_number": None,
            "page": None,
            "source_location": None,
        },
    }


def normalize_record(source: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    location = record["source_location"]
    if location != {"location_kind": "html_text_line", "row": 79}:
        raise ValueError("Toyama reviewed HTML location changed")
    period_text = " / ".join(record["period_tokens_original"])
    component = {
        "record_ref": f"{record['id']}-reviewed-raw-statement",
        "catalog_role": "reviewed_phase9_statement",
        "label": record["indicator_name_original"],
        "unit": record["unit_original"],
        "period_text": period_text,
        "value_text": record["target_statement_original"],
        "value": record["target_statement_original"],
        "value_status": "textual",
        "source_status": "reported_raw",
        "scope": record["aggregation_scope"],
        "aggregation_scope": record["aggregation_scope"],
        "preferred_direction": None,
        "operator": record["target_operator"],
    }
    return {
        "id": "phase11-record-toyama-0001",
        "prefecture_code": "16",
        "source_registry": SOURCE_RELATIVE_PATH,
        "source_record_id": record["id"],
        "linkage_kind": "target_to_annual_actual",
        "linkage_status": "partial",
        "partial_reason": "html_explanation_not_structured_indicator_value",
        "subject": {
            "record_ref": record["id"],
            "sequence": 1,
            "name": record["indicator_name_original"],
            "source_name": record["indicator_name_original"],
            "definition": record["plan_history_boundary"],
            "hierarchy_refs": [
                "toyama-current-plan-reviewed-statements",
                f"toyama-source-{record['source_document_sha256'][:12]}",
            ],
        },
        "indicator_context": {
            "policy_direction_code": "phase9-reviewed-html-statement",
            "policy_direction_name": record["source_document_title"],
            "source_page": None,
            "source_location": location,
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
                        "HTML説明文であり、政策指標値、実績値、目標値として"
                        "構造化しない。"
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
                "components": [component],
                "evidence": {
                    "source_number": 1,
                    "page": None,
                    "source_location": location,
                },
            },
            unavailable_measurement("annual_actual"),
            unavailable_measurement("final_target"),
        ],
        "evidence": {
            "primary_source_number": 1,
            "primary_page": None,
            "primary_location": location,
            "locations": [
                {
                    "source_number": 1,
                    "page": None,
                    "source_location": location,
                    "is_reprint": False,
                }
            ],
        },
        "boundary": BOUNDARY,
        "evaluation_status": "not_assessed",
        "comparability_status": "excluded_until_verified",
    }


def build_catalog(root: Path = ROOT) -> dict[str, Any]:
    source = load(root / SOURCE_RELATIVE_PATH)
    if source["prefecture_code"] != "16" or len(source["records"]) != 1:
        raise ValueError("Toyama source identity or record count mismatch")
    record = normalize_record(source, source["records"][0])
    return {
        "id": "phase11-toyama-normalized-records",
        "phase": 11,
        "status": "reviewed_maximum_depth",
        "prefecture_code": "16",
        "source_catalog": SOURCE_RELATIVE_PATH,
        "record_schema": "schemas/phase11_record_linkage_source_location.schema.json",
        "sources": [
            {
                "source_number": 1,
                "role": "phase9_reviewed_html_statement",
                "title": source["source_title"],
                "url": source["source_url"],
                "plan_title": source["plan_title"],
                "plan_period": source["plan_period"],
                "document_count": len(source["documents"]),
            }
        ],
        "records": [record],
        "summary": {
            "record_count": 1,
            "linked_record_count": 0,
            "partial_record_count": 1,
            "not_linked_record_count": 0,
            "indicator_series_count": 1,
            "source_document_count": 1,
            "missing_unit_record_count": 0,
            "annual_actual_available_count": 0,
            "future_target_available_count": 0,
            "reviewed_maximum_depth_record_count": 1,
            "policy_achievement_assessment_count": 0,
        },
        "document_record_counts": {source["records"][0]["source_document_title"]: 1},
        "source_location_counts": {"html_text_line": 1},
        "updated_at": source["updated_at"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rendered = json.dumps(build_catalog(), ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
