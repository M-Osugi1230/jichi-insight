#!/usr/bin/env python3
"""Normalize Okinawa plan indicators without inventing annual actuals."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATHS = [
    "data/reviewed/okinawa_midterm_major_indicators.json",
    "data/reviewed/okinawa_midterm_outcome_indicators_part1.json",
    "data/reviewed/okinawa_midterm_outcome_indicators_part2.json",
    "data/reviewed/okinawa_midterm_outcome_indicators_part3.json",
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


def raw_component(
    record: dict[str, Any],
    role: str,
    value_text: str,
) -> dict[str, Any]:
    return {
        "record_ref": f"{record['id']}-{role}",
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


def reported_measurement(
    record: dict[str, Any],
    role: str,
    source_role: str,
    value_text: str,
) -> dict[str, Any]:
    return {
        "role": role,
        "status": "reported",
        "period_text": value_text,
        "value_text": value_text,
        "components": [raw_component(record, source_role, value_text)],
        "evidence": {
            "source_number": 1,
            "page": record["source_pdf_page"],
        },
    }


def unavailable_actual() -> dict[str, Any]:
    return {
        "role": "annual_actual",
        "status": "not_available",
        "period_text": "",
        "value_text": "",
        "components": [],
        "evidence": {"source_number": None, "page": None},
    }


def context_note(record: dict[str, Any]) -> str:
    return json.dumps(
        {
            "evidence_id": record["evidence_id"],
            "indicator_level": record["indicator_level"],
            "policy_code_original": record["policy_code_original"],
            "rationale_source_original": record[
                "rationale_source_original"
            ],
            "national_current_original": record[
                "national_current_original"
            ],
            "national_comparison_status": record[
                "national_comparison_status"
            ],
            "island_indicator_original": record[
                "island_indicator_original"
            ],
            "sdgs_priority_original": record[
                "sdgs_priority_original"
            ],
            "is_island_indicator": record["is_island_indicator"],
            "has_sdgs_priority": record["has_sdgs_priority"],
            "target_value_kind": record["target_value_kind"],
            "source_value_note": record["source_value_note"],
            "source_table_row": record["source_table_row"],
            "maximum_depth": "plan_baseline_to_r9_target",
        },
        ensure_ascii=False,
        sort_keys=True,
    )


def boundary(record: dict[str, Any]) -> str:
    anomaly = (
        " 公式資料内の値・単位の不整合はsource_value_noteとして保持し、"
        "訂正しない。"
        if record["source_value_note"]
        else ""
    )
    return (
        "中期実施計画附属資料の指標名、計画基準値、R9目標、全国参考値、"
        "設定理由・出典、島しょ指標、SDGs優先課題、ページ・表行を原文の"
        "まま保持した。Reviewed年度実績が未接続のためPartialとし、計画"
        "基準値をannual actualへ昇格せず、政策達成・因果・全国比較は"
        f"判定しない。{anomaly}"
    )


def normalized_id(record: dict[str, Any]) -> str:
    level = record["indicator_level"]
    return f"phase11-record-okinawa-{level}-{record['sequence']:03d}"


def normalize_record(
    source_registry: str,
    record: dict[str, Any],
) -> dict[str, Any]:
    level = record["indicator_level"]
    return {
        "id": normalized_id(record),
        "prefecture_code": "47",
        "source_registry": source_registry,
        "source_record_id": record["id"],
        "linkage_kind": "target_to_annual_actual",
        "linkage_status": "partial",
        "partial_reason": "annual_actual_not_reviewed",
        "subject": {
            "record_ref": record["id"],
            "sequence": record["sequence"],
            "name": record["indicator_name_original"],
            "source_name": record["indicator_name_original"],
            "definition": record["rationale_source_original"],
            "hierarchy_refs": [
                f"okinawa-level-{level}",
                f"okinawa-policy-{record['policy_code_original']}",
            ],
        },
        "indicator_context": {
            "policy_direction_code": record["policy_code_original"],
            "policy_direction_name": record["policy_title_original"],
            "source_page": record["source_pdf_page"],
            "repost_of": None,
            "target_revision_status": "current_midterm_plan_target",
            "linked_current_series_count": 0,
            "target_series_count": 1,
            "review_status": record["review_status"],
            "quality_note": context_note(record),
            "series": [
                {
                    "series_ref": f"{record['id']}-raw-series-01",
                    "label": level,
                    "unit": "原文",
                    "direction": "not_inferred",
                    "comparability_note": (
                        "計画基準値とR9目標を保持する最大到達深度。"
                        "全国値は参考値であり年度実績や比較評価へ昇格しない。"
                    ),
                    "value_count": 2,
                }
            ],
        },
        "measurements": [
            reported_measurement(
                record,
                "plan_current",
                "baseline",
                record["baseline_original"],
            ),
            unavailable_actual(),
            reported_measurement(
                record,
                "final_target",
                "target_r9",
                record["target_r9_original"],
            ),
        ],
        "evidence": {
            "primary_source_number": 1,
            "primary_page": record["source_pdf_page"],
            "locations": [
                {
                    "source_number": 1,
                    "page": record["source_pdf_page"],
                    "is_reprint": False,
                }
            ],
        },
        "boundary": boundary(record),
        "evaluation_status": record[
            "policy_achievement_assessment_status"
        ],
        "comparability_status": "excluded_until_verified",
    }


def build_catalog(root: Path = ROOT) -> dict[str, Any]:
    source_records = load_records(root)
    records = [
        normalize_record(source_registry, record)
        for source_registry, record in source_records
    ]
    level_counts = Counter(record["indicator_level"] for _, record in source_records)
    national_counts = Counter(
        record["national_comparison_status"] for _, record in source_records
    )
    target_kind_counts = Counter(
        record["target_value_kind"] for _, record in source_records
    )

    return {
        "id": "phase11-okinawa-normalized-records",
        "phase": 11,
        "status": "reviewed_maximum_depth",
        "prefecture_code": "47",
        "source_catalogs": SOURCE_RELATIVE_PATHS,
        "sources": [
            {
                "source_number": 1,
                "role": "midterm_plan_indicator_catalog",
                "title": "新・沖縄21世紀ビジョン実施計画（中期：令和7年度～令和9年度）附属資料",
                "url": "https://www.pref.okinawa.jp/_res/projects/default_project/_page_/001/034/436/7_tyukijisshikeikaku_r2.pdf",
            }
        ],
        "records": records,
        "summary": {
            "record_count": len(records),
            "linked_record_count": 0,
            "partial_record_count": len(records),
            "not_linked_record_count": 0,
            "major_indicator_count": level_counts["major"],
            "outcome_indicator_count": level_counts["outcome"],
            "indicator_series_count": len(records),
            "annual_actual_available_count": 0,
            "annual_actual_unavailable_count": len(records),
            "island_indicator_count": sum(
                record["is_island_indicator"] for _, record in source_records
            ),
            "sdgs_priority_indicator_count": sum(
                record["has_sdgs_priority"] for _, record in source_records
            ),
            "qualitative_target_count": target_kind_counts["qualitative"],
            "national_comparison_provided_count": national_counts["provided"],
            "national_comparison_unavailable_count": national_counts[
                "unavailable"
            ],
            "source_value_note_count": sum(
                record["source_value_note"] is not None
                for _, record in source_records
            ),
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
