#!/usr/bin/env python3
"""Extract and conservatively classify Miyagi project-money linkages.

The extractor links only exact project-name matches with the same normalized
responsible department and office. Multiple appearances, organization changes,
renamed projects, and new projects remain Partial or Not linked.
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


def normalize_organization(value: str) -> str:
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", value or ""))


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
                    number, name, description, department, office, period, amount = (
                        row[:7]
                    )
                    parsed_amount = parse_amount(amount)
                    if not name or parsed_amount is None:
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
                            "amount_thousand_yen": parsed_amount,
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
                    parsed_amount = parse_amount(amount)
                    if not name or parsed_amount is None:
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
                            "amount_thousand_yen": parsed_amount,
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
    for index, budget_record in enumerate(budget, start=1):
        name_matches = by_name.get(budget_record["project_name_normalized"], [])
        organization_matches = [
            match
            for match in name_matches
            if normalize_organization(budget_record["department"])
            == normalize_organization(match["department"])
            and normalize_organization(budget_record["office"])
            == normalize_organization(match["office"])
        ]

        if len(organization_matches) == 1:
            status = "linked"
            match_basis = "exact_project_name_department_office"
            selected = organization_matches[0]
            candidates_for_review = []
        elif len(name_matches) == 1:
            status = "partial"
            match_basis = "exact_project_name_organization_changed"
            selected = None
            candidates_for_review = name_matches
        elif len(name_matches) > 1:
            status = "partial"
            match_basis = "exact_project_name_multiple_measure_candidates"
            selected = None
            candidates_for_review = name_matches
        else:
            status = "not_linked"
            match_basis = "exact_project_name_not_found"
            selected = None
            candidates_for_review = []

        effective_measure = (
            selected["measure_number"] if selected is not None else None
        )
        candidates.append(
            {
                "id": f"miyagi-project-money-candidate-{index:04d}",
                "linkage_status": status,
                "match_basis": match_basis,
                "measure_id": (
                    f"miyagi-prefecture-policy-measure-{effective_measure:02d}"
                    if effective_measure is not None
                    else None
                ),
                "budget_record": budget_record,
                "settlement_record": selected,
                "settlement_candidates": candidates_for_review,
                "boundary": (
                    "同一事業名・部局・担当課を確認したが、令和8年度予算額と"
                    "令和6年度決算額は別年度の別金額として保持し、成果評価へ"
                    "自動変換しない。"
                    if status == "linked"
                    else "同一施策・同一事業として確定できないため、改称、組織変更、"
                    "複数施策への再掲、新規事業の可能性を追加確認する。"
                ),
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
        status: sum(item["linkage_status"] == status for item in candidates)
        for status in ("linked", "partial", "not_linked")
    }
    basis_counts = {
        basis: sum(item["match_basis"] == basis for item in candidates)
        for basis in (
            "exact_project_name_department_office",
            "exact_project_name_organization_changed",
            "exact_project_name_multiple_measure_candidates",
            "exact_project_name_not_found",
        )
    }
    summary = {
        "budget_source_url": (
            "https://www.pref.miyagi.jp/documents/59763/"
            "r7hanneijyoukyousetumeisyo.pdf"
        ),
        "settlement_source_url": (
            "https://www.pref.miyagi.jp/documents/59769/r7-seikatohyouka_1.pdf"
        ),
        "budget_record_count": len(budget),
        "settlement_record_count": len(settlement),
        "linkage_status_counts": status_counts,
        "match_basis_counts": basis_counts,
        "promotion_policy": "exact_name_department_office_only",
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
