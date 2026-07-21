#!/usr/bin/env python3
"""Build Okinawa midterm major/outcome indicator data from the official annex."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

import pdfplumber

SOURCE_URL = (
    "https://www.pref.okinawa.jp/_res/projects/default_project/_page_/"
    "001/034/436/7_tyukijisshikeikaku_r2.pdf"
)


def clean(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.replace("\u3000", " ").replace("\n", " ")
    value = re.sub(r"\s+", " ", value).strip()
    return value or None


def is_data_row(row: list[str | None]) -> bool:
    if len(row) < 8:
        return False
    indicator_name = row[1]
    baseline = row[2]
    target = row[3]
    if not indicator_name or not baseline or not target:
        return False
    if indicator_name in {"指標名", "標一覧"}:
        return False
    return True


def extract(pdf_path: Path) -> list[dict]:
    records: list[dict] = []
    current_policy: dict[str, str | None] = {"major": None, "outcome": None}

    with pdfplumber.open(pdf_path) as pdf:
        for page_index in range(4, len(pdf.pages)):
            layer = "major" if page_index <= 10 else "outcome"
            tables = pdf.pages[page_index].extract_tables()
            if not tables:
                continue
            for row_index, raw_row in enumerate(tables[0]):
                row = [clean(value) for value in raw_row]
                if not is_data_row(row):
                    continue
                if row[0]:
                    current_policy[layer] = row[0]
                policy = current_policy[layer]
                assert policy
                order = len(records) + 1
                records.append(
                    {
                        "display_order": order,
                        "indicator_id": f"okinawa-midterm-indicator-{order:03d}",
                        "evidence_id": f"okinawa-midterm-evidence-{order:03d}",
                        "indicator_layer": layer,
                        "policy_original": policy,
                        "indicator_name_original": row[1],
                        "baseline_original": row[2],
                        "target_r9_original": row[3],
                        "national_current_original": row[4],
                        "rationale_and_source_original": row[5],
                        "remote_island_marker_original": row[6],
                        "sdgs_priority_original": row[7],
                        "source_pdf_page": page_index + 1,
                        "source_table_row": row_index + 1,
                        "review_status": "reviewed",
                        "policy_achievement_assessment_status": "not_assessed",
                    }
                )

    major = [record for record in records if record["indicator_layer"] == "major"]
    outcome = [record for record in records if record["indicator_layer"] == "outcome"]
    assert len(major) == 37
    assert len(outcome) == 339
    assert len(records) == 376
    return records


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )


def has_numeric_text(value: str) -> bool:
    return bool(re.search(r"[0-9０-９]", value))


def build(pdf_path: Path, root: Path) -> None:
    records = extract(pdf_path)
    reviewed_root = root / "data/reviewed"
    evidence_root = root / "data/evidence"
    catalog_root = root / "data/catalog"

    ranges = [(0, 94), (94, 188), (188, 282), (282, 376)]
    for part, (start, end) in enumerate(ranges, 1):
        current = records[start:end]
        write_json(
            reviewed_root / f"okinawa_midterm_indicators_part{part}.json",
            {
                "id": f"okinawa-midterm-indicators-part-{part}",
                "prefecture_code": "47",
                "source_url": SOURCE_URL,
                "record_count": len(current),
                "records": current,
                "updated_at": "2026-07-22",
            },
        )
        packets = []
        for record in current:
            packets.append(
                {
                    "id": record["evidence_id"],
                    "subject_id": record["indicator_id"],
                    "source_url": SOURCE_URL,
                    "source_pdf_page": record["source_pdf_page"],
                    "source_table_row": record["source_table_row"],
                    "claims": [
                        {
                            "field": "policy",
                            "value_original": record["policy_original"],
                        },
                        {
                            "field": "indicator_name",
                            "value_original": record["indicator_name_original"],
                        },
                        {
                            "field": "baseline",
                            "value_original": record["baseline_original"],
                        },
                        {
                            "field": "target_r9",
                            "value_original": record["target_r9_original"],
                        },
                        {
                            "field": "national_current",
                            "value_original": record["national_current_original"],
                        },
                    ],
                    "review_status": "reviewed",
                }
            )
        write_json(
            evidence_root / f"okinawa_midterm_indicator_evidence_part{part}.json",
            {
                "id": f"okinawa-midterm-indicator-evidence-part-{part}",
                "prefecture_code": "47",
                "packet_count": len(packets),
                "packets": packets,
                "updated_at": "2026-07-22",
            },
        )

    names = [record["indicator_name_original"] for record in records]
    duplicate_names = {
        name: count for name, count in Counter(names).items() if count > 1
    }
    major_count = sum(record["indicator_layer"] == "major" for record in records)
    outcome_count = sum(record["indicator_layer"] == "outcome" for record in records)
    national_count = sum(
        record["national_current_original"] not in {None, "－", "-"}
        for record in records
    )
    island_count = sum(bool(record["remote_island_marker_original"]) for record in records)
    sdgs_count = sum(bool(record["sdgs_priority_original"]) for record in records)
    qualitative_count = sum(
        not has_numeric_text(record["target_r9_original"]) for record in records
    )
    manifest = {
        "id": "okinawa-midterm-indicator-review-manifest",
        "prefecture_code": "47",
        "municipality_key": "okinawa-prefecture",
        "plan_title": "新・沖縄21世紀ビジョン実施計画（中期）",
        "plan_period": "令和7年度～令和9年度",
        "source_url": SOURCE_URL,
        "source_document_title": "新・沖縄21世紀ビジョン実施計画（中期）附属資料",
        "reviewed_indicator_count": len(records),
        "major_indicator_count": major_count,
        "outcome_indicator_count": outcome_count,
        "evidence_packet_count": len(records),
        "national_comparator_present_count": national_count,
        "remote_island_indicator_count": island_count,
        "sdgs_linked_indicator_count": sdgs_count,
        "qualitative_target_count": qualitative_count,
        "duplicate_indicator_name_count": len(duplicate_names),
        "duplicate_indicator_names": duplicate_names,
        "activity_indicator_included_count": 0,
        "policy_achievement_assessed_indicator_count": 0,
        "status": "complete",
        "updated_at": "2026-07-22",
        "next_review_scope": (
            "PDCA実施結果と基本計画評価検証報告書を、主要指標・成果指標へ"
            "定義照合して年度実績として接続する。"
        ),
        "quality_note": (
            "主要指標37件と成果指標339件を別レイヤーで保持し、活動指標は"
            "年度事業量として除外する。全国値、離島指標、SDGs優先課題、"
            "定性目標、複数系列を単一スコアへ変換しない。"
        ),
    }
    write_json(
        catalog_root / "okinawa_midterm_indicator_review_manifest.json",
        manifest,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    build(args.pdf, args.root)


if __name__ == "__main__":
    main()
