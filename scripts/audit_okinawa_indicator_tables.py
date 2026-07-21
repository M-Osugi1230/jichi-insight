#!/usr/bin/env python3
"""Audit the official Okinawa mid-term implementation-plan appendix tables."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

import pdfplumber


def clean(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.replace("\u3000", " ").replace("\n", " ")
    value = re.sub(r"\s+", " ", value).strip()
    return value or None


def audit(pdf_path: Path) -> dict:
    pages: list[dict] = []
    all_rows: list[dict] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, 1):
            tables = page.extract_tables()
            page_record = {
                "page": page_number,
                "width": page.width,
                "height": page.height,
                "table_count": len(tables),
                "tables": [],
            }
            for table_index, table in enumerate(tables):
                cleaned_rows = [[clean(cell) for cell in row] for row in table if row]
                page_record["tables"].append(
                    {
                        "table_index": table_index,
                        "row_count": len(cleaned_rows),
                        "column_counts": sorted({len(row) for row in cleaned_rows}),
                        "sample_rows": cleaned_rows[:6],
                    }
                )
                for row_index, row in enumerate(cleaned_rows, 1):
                    all_rows.append(
                        {
                            "page": page_number,
                            "table_index": table_index,
                            "row_index": row_index,
                            "cells": row,
                        }
                    )
            pages.append(page_record)

    code_pattern = re.compile(r"^[１-５1-5][－-]（?[０-９0-9]+）?(?:[－-][ァ-ヶA-Za-z0-9①-⑳]+)*")
    candidate_rows = [
        row
        for row in all_rows
        if any(cell and code_pattern.match(cell) for cell in row["cells"])
    ]
    return {
        "page_count": len(pages),
        "pages_with_tables": sum(bool(page["table_count"]) for page in pages),
        "table_count": sum(page["table_count"] for page in pages),
        "row_count": len(all_rows),
        "candidate_code_row_count": len(candidate_rows),
        "pages": pages,
        "candidate_rows": candidate_rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = audit(args.pdf)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {key: result[key] for key in result if key not in {"pages", "candidate_rows"}},
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
