#!/usr/bin/env python3
"""Build the reviewed Kagawa extended-plan indicator catalog from the official PDF."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

import pdfplumber

SOURCE_URL = (
    "https://www.pref.kagawa.lg.jp/documents/36520/"
    "shiryou3_shihyouminaoshi.pdf"
)


def clean(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.replace("\u3000", " ").replace("\n", " ")
    value = re.sub(r"\s+", " ", value).strip()
    return value or None


def extract(pdf_path: Path) -> tuple[list[dict], list[dict]]:
    records: dict[int, dict] = {}
    occurrences: list[dict] = []
    current_plan: str | None = None
    current_section: str | None = None

    with pdfplumber.open(pdf_path) as pdf:
        for page_index in range(2, len(pdf.pages)):
            tables = pdf.pages[page_index].extract_tables()
            if not tables:
                continue
            for row_index, raw_row in enumerate(tables[0]):
                if not raw_row:
                    continue
                row = [clean(value) for value in raw_row]
                if len(row) == 8:
                    row = [None] + row
                if len(row) < 9:
                    row += [None] * (9 - len(row))
                number_cell = row[1]
                if number_cell in {"指標 番号", "番号", "指標番号"} or row[2] == "指標":
                    continue
                if not number_cell:
                    heading = row[0]
                    if heading and re.match(r"^[１-３]\s", heading):
                        current_plan = heading
                    elif heading and re.match(r"^（[０-９0-9]+）", heading):
                        current_section = heading
                    continue
                if re.match(r"^[１-３]\s", number_cell):
                    current_plan = number_cell
                    continue
                if re.match(r"^（[０-９0-9]+）", number_cell):
                    current_section = number_cell
                    continue
                match = re.match(r"^(\d{1,3})(?:\s*\*)?$", number_cell)
                if not match:
                    continue
                number = int(match.group(1))
                if not 1 <= number <= 135:
                    continue
                repost = "*" in number_cell
                record = {
                    "indicator_number": number,
                    "indicator_id": f"kagawa-plan-indicator-{number:03d}",
                    "evidence_id": f"kagawa-plan-evidence-{number:03d}",
                    "plan_heading_original": current_plan,
                    "section_heading_original": current_section,
                    "indicator_name_original": row[2],
                    "current_value_original": row[3],
                    "target_r7_original": row[4],
                    "target_r8_original": row[5],
                    "indicator_overview_original": row[6],
                    "target_rationale_original": row[7],
                    "policy_number_original": row[8],
                    "source_pdf_page": page_index + 1,
                    "source_table_row": row_index + 1,
                    "repost_marker": repost,
                    "review_status": "reviewed",
                    "policy_achievement_assessment_status": "not_assessed",
                }
                occurrences.append(
                    {
                        "indicator_number": number,
                        "source_pdf_page": page_index + 1,
                        "source_table_row": row_index + 1,
                        "repost_marker": repost,
                        "section_heading_original": current_section,
                    }
                )
                if number not in records:
                    records[number] = record
                else:
                    records[number]["repost_marker"] = (
                        records[number]["repost_marker"] or repost
                    )

    assert list(records) == list(range(1, 136))
    counts = Counter(item["indicator_number"] for item in occurrences)
    for number, record in records.items():
        record["display_occurrence_count"] = counts[number]
        record["has_repost_occurrence"] = (
            counts[number] > 1 or record["repost_marker"]
        )
    return [records[number] for number in range(1, 136)], occurrences


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )


def build(pdf_path: Path, root: Path) -> None:
    records, occurrences = extract(pdf_path)
    reviewed_root = root / "data/reviewed"
    evidence_root = root / "data/evidence"
    ranges = [(0, 45), (45, 90), (90, 135)]

    for part, (start, end) in enumerate(ranges, 1):
        write_json(
            reviewed_root / f"kagawa_extended_plan_indicators_part{part}.json",
            {
                "id": f"kagawa-extended-plan-indicators-part-{part}",
                "prefecture_code": "37",
                "source_url": SOURCE_URL,
                "record_count": end - start,
                "records": records[start:end],
                "updated_at": "2026-07-22",
            },
        )
        packets = []
        for record in records[start:end]:
            packets.append(
                {
                    "id": record["evidence_id"],
                    "subject_id": record["indicator_id"],
                    "source_url": SOURCE_URL,
                    "source_pdf_page": record["source_pdf_page"],
                    "source_table_row": record["source_table_row"],
                    "claims": [
                        {
                            "field": "indicator_name",
                            "value_original": record["indicator_name_original"],
                        },
                        {
                            "field": "current_value",
                            "value_original": record["current_value_original"],
                        },
                        {
                            "field": "target_r7",
                            "value_original": record["target_r7_original"],
                        },
                        {
                            "field": "target_r8",
                            "value_original": record["target_r8_original"],
                        },
                    ],
                    "review_status": "reviewed",
                }
            )
        write_json(
            evidence_root
            / f"kagawa_extended_plan_indicator_evidence_part{part}.json",
            {
                "id": f"kagawa-extended-plan-evidence-part-{part}",
                "prefecture_code": "37",
                "packet_count": len(packets),
                "packets": packets,
                "updated_at": "2026-07-22",
            },
        )

    write_json(
        reviewed_root / "kagawa_extended_plan_indicator_occurrences.json",
        {
            "id": "kagawa-extended-plan-indicator-occurrences",
            "prefecture_code": "37",
            "occurrence_count": len(occurrences),
            "occurrences": occurrences,
            "updated_at": "2026-07-22",
        },
    )
    target_revisions = sum(
        record["target_r7_original"] != record["target_r8_original"]
        for record in records
    )
    manifest = {
        "id": "kagawa-extended-plan-indicator-review-manifest",
        "prefecture_code": "37",
        "municipality_key": "kagawa-prefecture",
        "plan_title": "「人生100年時代のフロンティア県・香川」実現計画",
        "plan_period": "令和3年度～令和8年度",
        "source_url": SOURCE_URL,
        "source_document_title": "計画期間の延長及び指標の目標値等の見直しについて",
        "reviewed_indicator_count": 135,
        "display_occurrence_count": len(occurrences),
        "evidence_packet_count": 135,
        "reposted_indicator_count": 6,
        "reposted_indicator_numbers": [7, 14, 50, 66, 67, 96],
        "indicators_with_current_value_count": 135,
        "target_revision_count": target_revisions,
        "policy_achievement_assessed_indicator_count": 0,
        "status": "complete",
        "updated_at": "2026-07-22",
        "next_review_scope": (
            "行政評価報告書と年度実績を、延長後の令和8年度目標へ"
            "定義照合して接続する。"
        ),
        "quality_note": (
            "令和7年度目標と令和8年度目標を分離し、再掲6指標は表示位置を"
            "保持しつつ固有指標数へ重複計上しない。135番の県人口は"
            "令和12年目標として保持する。"
        ),
    }
    write_json(
        root / "data/catalog/kagawa_extended_plan_indicator_review_manifest.json",
        manifest,
    )
    assert len(records) == 135
    assert len(occurrences) == 141
    assert target_revisions == 87


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    build(args.pdf, args.root)


if __name__ == "__main__":
    main()
