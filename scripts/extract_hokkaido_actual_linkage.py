#!/usr/bin/env python3
"""Create reviewed Hokkaido annual-actual linkage records.

The official indicator number is the primary key. Indicators with a revised name,
target version, or component structure remain Partial and are never promoted by
position alone.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import pdfplumber

PARTIAL_NUMBERS = {6, 10, 21, *range(31, 40), 65, 107, 108}


def clean(value: object) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "")
    return re.sub(r"[^0-9A-Za-z一-龠ぁ-んァ-ヶ]", "", value).lower()


def parse_number(value: str) -> int | float | None:
    text = unicodedata.normalize("NFKC", value or "")
    text = text.replace(",", "").replace("以上", "").replace("以下", "").strip()
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    if re.fullmatch(r"-?\d+\.\d+", text):
        return float(text)
    return None


def split_values(value: str) -> list[str]:
    text = unicodedata.normalize("NFKC", value or "").replace("、", " ").strip()
    return [token for token in re.split(r"\s+", text) if token]


def load_indicators(root: Path) -> list[dict]:
    indicators = []
    for path in sorted(root.glob("hokkaido_indicator_catalog_*.json")):
        catalog = json.loads(path.read_text(encoding="utf-8"))
        for item in catalog["items"]:
            indicators.append(
                {
                    "indicator_id": item["id"],
                    "indicator_number": item["indicator_number"],
                    "indicator_name": item["indicator_name_original"],
                    "policy_direction_id": item["policy_direction_id"],
                    "policy_field_ids": item["policy_field_ids"],
                    "series": item["series"],
                }
            )
    return sorted(indicators, key=lambda item: item["indicator_number"])


def extract_rows(paths: list[Path]) -> dict[int, list[dict]]:
    by_number: dict[int, list[dict]] = defaultdict(list)
    for source_number, path in enumerate(paths, start=1):
        with pdfplumber.open(path) as pdf:
            for pdf_page, page in enumerate(pdf.pages, start=1):
                for table_index, table in enumerate(page.extract_tables() or []):
                    for row_index, raw_row in enumerate(table):
                        row = [clean(cell) for cell in raw_row] if raw_row else []
                        if len(row) < 15 or not row[2].isdigit():
                            continue
                        number = int(row[2])
                        if not 1 <= number <= 108:
                            continue
                        if not row[3].startswith(("●", "○")):
                            continue
                        by_number[number].append(
                            {
                                "source_number": source_number,
                                "pdf_page": pdf_page,
                                "table_index": table_index,
                                "row_index": row_index,
                                "indicator_name_text": row[3],
                                "plan_current_value_text": row[4],
                                "plan_current_period_text": row[5],
                                "reference_value_text": row[6],
                                "reference_period_text": row[7],
                                "actual_value_text": row[8],
                                "actual_period_text": row[9],
                                "intermediate_target_text": row[10],
                                "intermediate_target_period_text": row[11],
                                "final_target_text": row[12],
                                "final_target_period_text": row[13],
                                "definition_text": row[14],
                            }
                        )
    return by_number


def primary_row(rows: list[dict]) -> dict:
    non_reprint = [row for row in rows if "再掲" not in row["indicator_name_text"]]
    return (non_reprint or rows)[0]


def actual_components(indicator: dict, row: dict) -> list[dict]:
    tokens = split_values(row["actual_value_text"])
    series = indicator["series"]
    if len(tokens) != len(series):
        return []
    components = []
    for series_item, token in zip(series, tokens, strict=True):
        components.append(
            {
                "label": series_item.get("label"),
                "unit": series_item.get("unit_original"),
                "value_text": token,
                "value": parse_number(token),
                "value_status": (
                    "numeric" if parse_number(token) is not None else "textual"
                ),
            }
        )
    return components


def partial_reason(number: int) -> str:
    if number in {6, 10, 21}:
        return "target_version_changed"
    if 31 <= number <= 39 or number == 65:
        return "indicator_definition_or_numbering_changed"
    if number in {107, 108}:
        return "component_structure_changed"
    raise ValueError(number)


def build_records(indicators: list[dict], rows: dict[int, list[dict]]) -> list[dict]:
    records = []
    for indicator in indicators:
        number = indicator["indicator_number"]
        source_rows = rows[number]
        row = primary_row(source_rows)
        status = "partial" if number in PARTIAL_NUMBERS else "linked"
        components = actual_components(indicator, row) if status == "linked" else []
        if status == "linked" and not row["actual_value_text"]:
            actual_status = "not_available"
        elif status == "linked" and components:
            actual_status = "available"
        elif status == "linked":
            actual_status = "available_raw_only"
        else:
            actual_status = "not_promoted"
        records.append(
            {
                "id": f"hokkaido-annual-actual-linkage-{number:03d}",
                "indicator_id": indicator["indicator_id"],
                "indicator_number": number,
                "indicator_name": indicator["indicator_name"],
                "policy_direction_id": indicator["policy_direction_id"],
                "policy_field_ids": indicator["policy_field_ids"],
                "linkage_status": status,
                "partial_reason": partial_reason(number) if status == "partial" else None,
                "source_indicator_name_text": row["indicator_name_text"],
                "actual_status": actual_status,
                "actual_value_text": row["actual_value_text"],
                "actual_period_text": row["actual_period_text"],
                "actual_components": components,
                "definition_text": row["definition_text"],
                "source_number": row["source_number"],
                "pdf_page": row["pdf_page"],
                "related_source_locations": [
                    {
                        "source_number": source_row["source_number"],
                        "pdf_page": source_row["pdf_page"],
                        "is_reprint": "再掲" in source_row["indicator_name_text"],
                    }
                    for source_row in source_rows
                ],
                "plan_current_value_text": row["plan_current_value_text"],
                "plan_current_period_text": row["plan_current_period_text"],
                "intermediate_target_text": row["intermediate_target_text"],
                "intermediate_target_period_text": row[
                    "intermediate_target_period_text"
                ],
                "final_target_text": row["final_target_text"],
                "final_target_period_text": row["final_target_period_text"],
                "evaluation_status": "not_assessed",
                "boundary": (
                    "公式指標番号、指標名、単位、構成系列を確認し、年度実績を接続した。"
                    "実績値から政策の達成・未達は判定しない。"
                    if status == "linked"
                    else "公式指標番号は存在するが、指標定義、目標版、または構成系列が"
                    "現行Reviewedカタログと一致しないため実績を接続しない。"
                ),
            }
        )
    return records


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", action="append", type=Path, required=True)
    parser.add_argument("--catalog-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    indicators = load_indicators(args.catalog_root)
    rows = extract_rows(args.pdf)
    if set(rows) != set(range(1, 109)):
        raise SystemExit("Official indicator rows 1-108 were not extracted exactly")
    records = build_records(indicators, rows)
    counts = Counter(record["linkage_status"] for record in records)

    part_files = []
    for part_number, offset in enumerate(range(0, len(records), 54), start=1):
        filename = f"hokkaido_annual_actual_linkage_part_{part_number:02d}.json"
        part_files.append(filename)
        part_records = records[offset : offset + 54]
        write_json(
            args.output_dir / filename,
            {
                "id": f"hokkaido-annual-actual-linkage-part-{part_number:02d}",
                "record_number_from": offset + 1,
                "record_number_to": offset + len(part_records),
                "records": part_records,
            },
        )

    index = {
        "id": "hokkaido-prefecture-annual-actual-linkage",
        "prefecture_code": "01",
        "status": "reviewed",
        "source_urls": [
            "https://www.pref.hokkaido.lg.jp/fs/1/2/2/1/7/9/6/5/_/%E5%9F%BA%E6%9C%AC%E6%96%B9%E5%90%911.pdf",
            "https://www.pref.hokkaido.lg.jp/fs/1/2/2/1/7/9/6/6/_/%E5%9F%BA%E6%9C%AC%E6%96%B9%E5%90%912.pdf",
            "https://www.pref.hokkaido.lg.jp/fs/1/2/2/1/7/9/6/7/_/%E5%9F%BA%E6%9C%AC%E6%96%B9%E5%90%913.pdf",
        ],
        "reporting_period": "令和6年度推進状況・資料内最新実績",
        "indicator_count": len(records),
        "series_count": sum(len(item["series"]) for item in indicators),
        "part_files": part_files,
        "summary": {
            "linked_record_count": counts["linked"],
            "partial_record_count": counts["partial"],
            "not_linked_record_count": counts["not_linked"],
        },
        "evaluation_status": "not_assessed",
        "updated_at": "2026-08-01",
    }
    write_json(args.output_dir / "hokkaido_annual_actual_linkage.json", index)
    print(json.dumps(index, ensure_ascii=False))


if __name__ == "__main__":
    main()
