#!/usr/bin/env python3
"""Create reviewed Miyagi budget-to-settlement linkage candidates.

Only a single exact project-name match in the same measure, department, and office
is promoted to Linked. Organization changes, measure changes, duplicated projects,
and missing prior-year projects remain Partial or Not linked.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

import extract_miyagi_money_linkage as base


def page_measure(
    text: str,
    previous: tuple[int | None, int | None],
) -> tuple[int | None, int | None]:
    normalized = unicodedata.normalize("NFKC", text)
    policy, measure = previous
    policy_match = re.search(r"政策番号\s*([0-9]+)", normalized)
    measure_match = re.search(r"施策番号\s*([0-9]+)", normalized)
    if policy_match:
        policy = int(policy_match.group(1))
    if measure_match:
        measure = int(measure_match.group(1))
    return policy, measure


def measure_id(number: int | None) -> str | None:
    return f"policy-measure-miyagi-{number}" if number is not None else None


def policy_id(number: int | None) -> str | None:
    return f"policy-miyagi-{number}" if number is not None else None


def compact_candidate(record: dict) -> dict:
    return {
        "measure_id": measure_id(record.get("measure_number")),
        "policy_id": policy_id(record.get("policy_number")),
        "project_name": record["project_name"],
        "department": record["department"],
        "office": record["office"],
        "settlement_amount_thousand_yen": record["amount_thousand_yen"],
        "settlement_pdf_page": record["pdf_page"],
    }


def classify(budget: list[dict], settlement: list[dict]) -> list[dict]:
    by_name: dict[str, list[dict]] = {}
    for record in settlement:
        by_name.setdefault(record["project_name_normalized"], []).append(record)

    rows: list[dict] = []
    for index, budget_record in enumerate(budget, start=1):
        name_matches = by_name.get(budget_record["project_name_normalized"], [])
        same_measure = [
            item
            for item in name_matches
            if budget_record["measure_number"] is not None
            and budget_record["measure_number"] == item["measure_number"]
        ]
        same_measure_org = [
            item
            for item in same_measure
            if base.normalize_organization(budget_record["department"])
            == base.normalize_organization(item["department"])
            and base.normalize_organization(budget_record["office"])
            == base.normalize_organization(item["office"])
        ]

        selected: dict | None = None
        review_candidates: list[dict] = []
        if len(same_measure_org) == 1:
            linkage_status = "linked"
            match_basis = "exact_name_measure_department_office"
            selected = same_measure_org[0]
        elif len(same_measure_org) > 1:
            linkage_status = "partial"
            match_basis = "duplicate_within_same_measure"
            review_candidates = same_measure_org
        elif len(same_measure) == 1:
            linkage_status = "partial"
            match_basis = "same_measure_organization_changed"
            review_candidates = same_measure
        elif len(same_measure) > 1:
            linkage_status = "partial"
            match_basis = "multiple_candidates_within_same_measure"
            review_candidates = same_measure
        elif name_matches:
            linkage_status = "partial"
            match_basis = "exact_name_measure_changed_or_relisted"
            review_candidates = name_matches
        else:
            linkage_status = "not_linked"
            match_basis = "exact_name_not_found_in_fy2024_settlement"

        rows.append(
            {
                "id": f"miyagi-project-money-linkage-{index:04d}",
                "linkage_status": linkage_status,
                "match_basis": match_basis,
                "policy_id": policy_id(budget_record["policy_number"]),
                "measure_id": measure_id(budget_record["measure_number"]),
                "project_name": budget_record["project_name"],
                "project_name_normalized": budget_record["project_name_normalized"],
                "department": budget_record["department"],
                "office": budget_record["office"],
                "implementation_period": budget_record["implementation_period"],
                "budget_period": "令和8年度",
                "budget_amount_thousand_yen": budget_record["amount_thousand_yen"],
                "budget_amount_text": budget_record["amount_text"],
                "budget_pdf_page": budget_record["pdf_page"],
                "settlement_period": "令和6年度" if selected else None,
                "settlement_amount_thousand_yen": (
                    selected["amount_thousand_yen"] if selected else None
                ),
                "settlement_amount_text": selected["amount_text"] if selected else None,
                "settlement_pdf_page": selected["pdf_page"] if selected else None,
                "settlement_project_number_text": (
                    selected["project_number_text"] if selected else None
                ),
                "settlement_candidates": [
                    compact_candidate(item) for item in review_candidates
                ],
                "boundary": (
                    "同一施策、同一事業名、同一部局、同一担当課を確認した。"
                    "令和8年度予算額と令和6年度決算額は別年度の別金額として保持し、"
                    "増減を政策成果へ自動変換しない。"
                    if linkage_status == "linked"
                    else "同一事業系列を確定できないため、改称、組織変更、施策変更、"
                    "複数施策への再掲、新規事業の可能性を追加確認する。"
                ),
            }
        )
    return rows


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--budget-pdf", type=Path, required=True)
    parser.add_argument("--settlement-pdf", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    base.page_measure = page_measure
    budget = base.extract_budget(args.budget_pdf)
    settlement = base.extract_settlement(args.settlement_pdf)
    records = classify(budget, settlement)
    status_counts = Counter(record["linkage_status"] for record in records)
    basis_counts = Counter(record["match_basis"] for record in records)

    part_size = 160
    part_files: list[str] = []
    for part_number, offset in enumerate(range(0, len(records), part_size), start=1):
        filename = f"miyagi_project_money_linkage_part_{part_number:02d}.json"
        part_files.append(filename)
        part_records = records[offset : offset + part_size]
        write_json(
            args.output_dir / filename,
            {
                "id": f"miyagi-project-money-linkage-part-{part_number:02d}",
                "record_number_from": offset + 1,
                "record_number_to": offset + len(part_records),
                "records": part_records,
            },
        )

    index = {
        "id": "miyagi-prefecture-project-money-linkage",
        "prefecture_code": "04",
        "status": "reviewed",
        "sources": {
            "budget": {
                "title": "令和7年度行政活動の評価の結果の反映状況説明書",
                "url": "https://www.pref.miyagi.jp/documents/59763/r7hanneijyoukyousetumeisyo.pdf",
                "period": "令和8年度予算",
            },
            "settlement": {
                "title": "新・宮城の将来ビジョン 成果と評価",
                "url": "https://www.pref.miyagi.jp/documents/59769/r7-seikatohyouka_1.pdf",
                "period": "令和6年度決算・実績",
            },
        },
        "budget_record_count": len(budget),
        "settlement_record_count": len(settlement),
        "record_count": len(records),
        "part_files": part_files,
        "summary": {
            "linked_record_count": status_counts["linked"],
            "partial_record_count": status_counts["partial"],
            "not_linked_record_count": status_counts["not_linked"],
            "match_basis_counts": dict(sorted(basis_counts.items())),
        },
        "promotion_rule": (
            "single exact normalized project-name match in the same official measure, "
            "department, and office"
        ),
        "evaluation_status": "not_assessed",
        "updated_at": "2026-08-01",
    }
    write_json(args.output_dir / "miyagi_project_money_linkage.json", index)
    write_json(args.output_dir / "budget-records.json", budget)
    write_json(args.output_dir / "settlement-records.json", settlement)
    print(json.dumps(index, ensure_ascii=False))


if __name__ == "__main__":
    main()
