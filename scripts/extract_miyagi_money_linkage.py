#!/usr/bin/env python3
"""Extract Miyagi measure/project money candidates from two official PDFs.

The output is candidate-only. It does not mark any budget or settlement record as
linked until measure, project name, department, office, and period are reviewed.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path

import pdfplumber


def clean(value) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value)
    return re.sub(r"[\s・･()（）\[\]［］「」『』,，.。:：/／-]", "", value)


def parse_amount(value: str) -> int | None:
    digits = re.sub(r"[^0-9]", "", value)
    return int(digits) if digits else None


def page_measure(text: str, previous: tuple[int | None, int | None]):
    policy, measure = previous
    policy_match = re.search(r"政策番号\s*([0-9]+)", text)
    measure_match = re.search(r"施策番号\s*([0-9]+)", text)
    if policy_match:
        policy = int(policy_match.group(1))
    if measure_match:
        measure = int(measure_match.group(1))
    return policy, measure


def extract_budget(path: Path) -> list[dict]:
    records: list[dict] = []
    context: tuple[int | None, int | None] = (None, None)
    with pdfplumber.open(path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            context = page_measure(text, context)
            for table_index, table in enumerate(page.extract_tables() or []):
                rows = [[clean(cell) for cell in row] for row in table if row]
                if not rows:
                    continue
                header = " | ".join(rows[0])
                if "事業名" not in header or "R8事業費" not in header:
                    continue
                for row_index, row in enumerate(rows[1:], start=1):
                    if len(row) < 7:
                        continue
                    number, name, description, department, office, period, amount = row[:7]
                    if not name or not parse_amount(amount):
                        continue
                    records.append(
                        {
                            "source": "r8_budget_reflection",
                            "pdf_page": page_number,
                            "table_index": table_index,
                            "row_index": row_index,
                            "policy_number": context[0],
                            "measure_number": context[1],
                            "project_number_text": number,
                            "project_name": name,
                            "project_name_normalized": normalize(name),
                            "description": description,
                            "department": department,
                            "office": office,
                            "implementation_period": period,
                            "amount_thousand_yen": parse_amount(amount),
                            "amount_text": amount,
                        }
                    )
    return records


def extract_settlement(path: Path) -> list[dict]:
    records: list[dict] = []
    context: tuple[int | None, int | None] = (None, None)
    with pdfplumber.open(path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            context = page_measure(text, context)
            for table_index, table in enumerate(page.extract_tables() or []):
                rows = [[clean(cell) for cell in row] for row in table if row]
                if not rows:
                    continue
                header = " | ".join(rows[0])
                if "推進事業名" not in header or "決算額" not in header:
                    continue
                for row_index, row in enumerate(rows[1:], start=1):
                    if len(row) < 6:
                        continue
                    number, name, department, office, amount, evidence = row[:6]
                    if not name or not parse_amount(amount):
                        continue
                    records.append(
                        {
                            "source": "r6_settlement_results",
                            "pdf_page": page_number,
                            "table_index": table_index,
                            "row_index": row_index,
                            "policy_number": context[0],
                            "measure_number": context[1],
                            "project_number_text": number,
                            "project_name": name,
                            "project_name_normalized": normalize(name),
                            "department": department,
                            "office": office,
                            "amount_thousand_yen": parse_amount(amount),
                            "amount_text": amount,
                            "result_evidence": evidence,
                        }
                    )
    return records


def match_candidates(budget: list[dict], settlement: list[dict]) -> list[dict]:
    by_name: dict[str, list[dict]] = {}
    for record in settlement:
        by_name.setdefault(record["project_name_normalized"], []).append(record)

    candidates = []
    for record in budget:
        matches = by_name.get(record["project_name_normalized"], [])
        reviewed_candidates = [
            match
            for match in matches
            if record["measure_number"] == match["measure_number"]
            and (not record["department"] or record["department"] == match["department"])
        ]
        candidates.append(
            {
                "budget_record": record,
                "candidate_status": (
                    "single_candidate"
                    if len(reviewed_candidates) == 1
                    else "multiple_candidates"
                    if reviewed_candidates
                    else "not_found"
                ),
                "settlement_candidates": reviewed_candidates,
            }
        )
    return candidates


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--budget-pdf", type=Path, required=True)
    parser.add_argument("--settlement-pdf", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    budget = extract_budget(args.budget_pdf)
    settlement = extract_settlement(args.settlement_pdf)
    candidates = match_candidates(budget, settlement)
    status_counts = {
        status: sum(item["candidate_status"] == status for item in candidates)
        for status in ("single_candidate", "multiple_candidates", "not_found")
    }
    summary = {
        "budget_source_url": "https://www.pref.miyagi.jp/documents/59763/r7hanneijyoukyousetumeisyo.pdf",
        "settlement_source_url": "https://www.pref.miyagi.jp/documents/59769/r7-seikatohyouka_1.pdf",
        "budget_record_count": len(budget),
        "settlement_record_count": len(settlement),
        "candidate_status_counts": status_counts,
        "promotion_policy": "candidate_only_no_automatic_linkage",
    }

    for filename, value in (
        ("budget-records.json", budget),
        ("settlement-records.json", settlement),
        ("money-linkage-candidates.json", candidates),
        ("summary.json", summary),
    ):
        (args.output_dir / filename).write_text(
            json.dumps(value, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
