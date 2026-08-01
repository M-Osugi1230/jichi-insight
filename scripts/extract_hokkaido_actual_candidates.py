#!/usr/bin/env python3
"""Extract Hokkaido FY2024 actual candidates by official indicator number."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

import pdfplumber


def clean(value: object) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "")
    return re.sub(r"[^0-9A-Za-z一-龠ぁ-んァ-ヶ]", "", value).lower()


def load_catalogs(root: Path) -> list[dict]:
    indicators = []
    for path in sorted(root.glob("hokkaido_indicator_catalog_*.json")):
        catalog = json.loads(path.read_text(encoding="utf-8"))
        for item in catalog["items"]:
            indicators.append(
                {
                    "indicator_id": item["id"],
                    "indicator_number": item["indicator_number"],
                    "indicator_name": item["indicator_name_original"],
                    "indicator_name_normalized": normalize(
                        item["indicator_name_original"]
                    ),
                    "policy_direction_id": item["policy_direction_id"],
                    "policy_field_ids": item["policy_field_ids"],
                    "series": item["series"],
                    "catalog_path": str(path),
                }
            )
    return sorted(indicators, key=lambda item: item["indicator_number"])


def page_texts(paths: list[Path]) -> list[dict]:
    pages = []
    for source_number, path in enumerate(paths, start=1):
        with pdfplumber.open(path) as pdf:
            for pdf_page, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                tables = []
                for table_index, table in enumerate(page.extract_tables() or []):
                    rows = [
                        [clean(cell) for cell in row]
                        for row in table
                        if row and any(clean(cell) for cell in row)
                    ]
                    if rows:
                        tables.append(
                            {
                                "table_index": table_index,
                                "rows": rows,
                            }
                        )
                pages.append(
                    {
                        "source_number": source_number,
                        "pdf_page": pdf_page,
                        "text": text,
                        "normalized_text": normalize(text),
                        "tables": tables,
                    }
                )
    return pages


def number_row_candidates(number: int, page: dict) -> list[dict]:
    candidates = []
    number_pattern = re.compile(rf"(^|\D){number}(\D|$)")
    for table in page["tables"]:
        rows = table["rows"]
        for row_index, row in enumerate(rows):
            joined = " | ".join(row)
            first_cells = " ".join(row[:3])
            if not number_pattern.search(unicodedata.normalize("NFKC", first_cells)):
                continue
            context_rows = rows[max(0, row_index - 1) : min(len(rows), row_index + 3)]
            candidates.append(
                {
                    "source_number": page["source_number"],
                    "pdf_page": page["pdf_page"],
                    "table_index": table["table_index"],
                    "row_index": row_index,
                    "row": row,
                    "joined": joined,
                    "context_rows": context_rows,
                }
            )
    return candidates


def classify(indicators: list[dict], pages: list[dict]) -> list[dict]:
    records = []
    for indicator in indicators:
        name_pages = [
            {
                "source_number": page["source_number"],
                "pdf_page": page["pdf_page"],
            }
            for page in pages
            if indicator["indicator_name_normalized"] in page["normalized_text"]
        ]
        row_candidates = [
            candidate
            for page in pages
            for candidate in number_row_candidates(
                indicator["indicator_number"], page
            )
        ]
        candidate_pages = {
            (item["source_number"], item["pdf_page"]) for item in row_candidates
        }
        exact_page_overlap = [
            page
            for page in name_pages
            if (page["source_number"], page["pdf_page"]) in candidate_pages
        ]
        if len(exact_page_overlap) == 1:
            status = "single_page_candidate"
        elif exact_page_overlap:
            status = "multiple_page_candidates"
        elif name_pages:
            status = "name_only_candidate"
        else:
            status = "not_found"
        records.append(
            {
                **indicator,
                "candidate_status": status,
                "name_pages": name_pages,
                "row_candidates": row_candidates,
                "exact_page_overlap": exact_page_overlap,
            }
        )
    return records


def write_json(path: Path, value: object, *, pretty: bool = False) -> None:
    path.write_text(
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2 if pretty else None,
            separators=None if pretty else (",", ":"),
        ),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", action="append", type=Path, required=True)
    parser.add_argument("--catalog-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    indicators = load_catalogs(args.catalog_root)
    pages = page_texts(args.pdf)
    records = classify(indicators, pages)
    statuses = Counter(record["candidate_status"] for record in records)
    summary = {
        "indicator_count": len(indicators),
        "series_count": sum(len(indicator["series"]) for indicator in indicators),
        "pdf_count": len(args.pdf),
        "pdf_page_count": len(pages),
        "candidate_status_counts": dict(sorted(statuses.items())),
        "promotion_policy": (
            "candidate-only; indicator number, name, unit, actual value, "
            "measurement period, and source location must be reviewed"
        ),
    }
    write_json(args.output_dir / "summary.json", summary, pretty=True)
    write_json(args.output_dir / "indicator-candidates.json", records)
    write_json(args.output_dir / "page-tables.json", pages)
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
