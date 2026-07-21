#!/usr/bin/env python3
"""Build the reviewed Okinawa mid-term indicator catalog from the official appendix."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pdfplumber

SOURCE_URL = (
    "https://www.pref.okinawa.jp/_res/projects/default_project/_page_/001/034/436/"
    "7_tyukijisshikeikaku_r2.pdf"
)
SOURCE_TITLE = "新・沖縄21世紀ビジョン実施計画（中期：令和7年度～令和9年度）附属資料"
UPDATED_AT = "2026-07-22"


def clean(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.replace("\u3000", " ").replace("\n", " ")
    value = re.sub(r"\s+", " ", value).strip()
    return value or None


def target_value_kind(value: str) -> str:
    return "numeric_or_mixed" if re.search(r"[0-9０-９]", value) else "qualitative"


def extract(pdf_path: Path) -> list[dict]:
    records: list[dict] = []
    counters = {"major": 0, "outcome": 0}
    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, 1):
            if page_number < 5:
                continue
            for table in page.extract_tables():
                for row_number, raw_row in enumerate(table, 1):
                    if not raw_row:
                        continue
                    row = [clean(cell) for cell in raw_row]
                    if len(row) != 8 or not row[0] or not row[1]:
                        continue
                    if not re.match(r"^[１-５1-5][－-]", row[0]):
                        continue
                    first = row[0].split(" ", 1)
                    if len(first) != 2:
                        continue
                    indicator_level = "major" if page_number <= 11 else "outcome"
                    counters[indicator_level] += 1
                    sequence = counters[indicator_level]
                    prefix = f"okinawa-midterm-{indicator_level}-{sequence:03d}"
                    source_note = None
                    if first[0] == "１－（１）－ア－①":
                        source_note = (
                            "R9年度目標値欄は、指標名・基準値と単位が異なるが、"
                            "公式附属資料の記載を訂正せず保持する。"
                        )
                    record = {
                        "id": prefix,
                        "evidence_id": f"{prefix}-evidence",
                        "indicator_level": indicator_level,
                        "sequence": sequence,
                        "policy_code_original": first[0],
                        "policy_title_original": first[1],
                        "indicator_name_original": row[1],
                        "baseline_original": row[2],
                        "target_r9_original": row[3],
                        "national_current_original": row[4],
                        "rationale_source_original": row[5],
                        "island_indicator_original": row[6],
                        "sdgs_priority_original": row[7],
                        "is_island_indicator": row[6] is not None,
                        "has_sdgs_priority": row[7] is not None,
                        "target_value_kind": target_value_kind(row[3]),
                        "national_comparison_status": (
                            "unavailable" if row[4] == "－" else "provided"
                        ),
                        "source_value_note": source_note,
                        "source_pdf_page": page_number,
                        "source_table_row": row_number,
                        "review_status": "reviewed",
                        "policy_achievement_assessment_status": "not_assessed",
                    }
                    records.append(record)
    assert counters == {"major": 36, "outcome": 339}, counters
    assert len(records) == 375
    assert len({record["policy_code_original"] for record in records}) == 375
    return records


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )


def indicator_document(identifier: str, records: list[dict]) -> dict:
    return {
        "id": identifier,
        "prefecture_code": "47",
        "source_url": SOURCE_URL,
        "source_document_title": SOURCE_TITLE,
        "record_count": len(records),
        "records": records,
        "updated_at": UPDATED_AT,
    }


def evidence_document(identifier: str, records: list[dict]) -> dict:
    packets = []
    for record in records:
        packets.append(
            {
                "id": record["evidence_id"],
                "subject_id": record["id"],
                "source_url": SOURCE_URL,
                "source_document_title": SOURCE_TITLE,
                "source_pdf_page": record["source_pdf_page"],
                "source_table_row": record["source_table_row"],
                "claims": [
                    {
                        "field": "policy_code",
                        "value_original": record["policy_code_original"],
                    },
                    {
                        "field": "policy_title",
                        "value_original": record["policy_title_original"],
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
                    {
                        "field": "rationale_source",
                        "value_original": record["rationale_source_original"],
                    },
                    {
                        "field": "island_indicator",
                        "value_original": record["island_indicator_original"],
                    },
                    {
                        "field": "sdgs_priority",
                        "value_original": record["sdgs_priority_original"],
                    },
                ],
                "source_value_note": record["source_value_note"],
                "review_status": "reviewed",
            }
        )
    return {
        "id": identifier,
        "prefecture_code": "47",
        "packet_count": len(packets),
        "packets": packets,
        "updated_at": UPDATED_AT,
    }


def build(pdf_path: Path, root: Path) -> None:
    records = extract(pdf_path)
    major = [record for record in records if record["indicator_level"] == "major"]
    outcome = [record for record in records if record["indicator_level"] == "outcome"]
    outcome_parts = [outcome[0:113], outcome[113:226], outcome[226:339]]

    reviewed_root = root / "data/reviewed"
    evidence_root = root / "data/evidence"
    catalog_root = root / "data/catalog"

    write_json(
        reviewed_root / "okinawa_midterm_major_indicators.json",
        indicator_document("okinawa-midterm-major-indicators", major),
    )
    write_json(
        evidence_root / "okinawa_midterm_major_indicator_evidence.json",
        evidence_document("okinawa-midterm-major-indicator-evidence", major),
    )
    for part_number, part in enumerate(outcome_parts, 1):
        write_json(
            reviewed_root / f"okinawa_midterm_outcome_indicators_part{part_number}.json",
            indicator_document(
                f"okinawa-midterm-outcome-indicators-part-{part_number}", part
            ),
        )
        write_json(
            evidence_root
            / f"okinawa_midterm_outcome_indicator_evidence_part{part_number}.json",
            evidence_document(
                f"okinawa-midterm-outcome-indicator-evidence-part-{part_number}",
                part,
            ),
        )

    manifest = {
        "id": "okinawa-midterm-indicator-review-manifest",
        "prefecture_code": "47",
        "municipality_key": "okinawa-prefecture",
        "plan_title": "新・沖縄21世紀ビジョン実施計画（中期：令和7年度～令和9年度）",
        "plan_period": "令和7年度～令和9年度",
        "source_url": SOURCE_URL,
        "source_document_title": SOURCE_TITLE,
        "reviewed_indicator_count": len(records),
        "major_indicator_count": len(major),
        "outcome_indicator_count": len(outcome),
        "evidence_packet_count": len(records),
        "island_indicator_count": sum(record["is_island_indicator"] for record in records),
        "sdgs_priority_indicator_count": sum(
            record["has_sdgs_priority"] for record in records
        ),
        "qualitative_target_count": sum(
            record["target_value_kind"] == "qualitative" for record in records
        ),
        "national_comparison_provided_count": sum(
            record["national_comparison_status"] == "provided" for record in records
        ),
        "source_value_note_count": sum(
            record["source_value_note"] is not None for record in records
        ),
        "policy_achievement_assessed_indicator_count": 0,
        "status": "complete",
        "updated_at": UPDATED_AT,
        "next_review_scope": (
            "令和4～6年度PDCA実施結果を、現行中期計画のR9年度目標へ"
            "定義・期間を照合した上で別レイヤー接続する。"
        ),
        "quality_note": (
            "主要指標36件と成果指標339件を分離し、基準値、R9年度目標、"
            "全国値、設定根拠、離島指標、SDGs優先課題を原文のまま保持する。"
            "活動指標と過年度PDCA実績は現行目標カタログへ混入しない。"
        ),
    }
    assert manifest["island_indicator_count"] == 32
    assert manifest["sdgs_priority_indicator_count"] == 43
    assert manifest["qualitative_target_count"] == 9
    assert manifest["national_comparison_provided_count"] == 174
    assert manifest["source_value_note_count"] == 1
    write_json(
        catalog_root / "okinawa_midterm_indicator_review_manifest.json", manifest
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    build(args.pdf, args.root)


if __name__ == "__main__":
    main()
