#!/usr/bin/env python3
"""Extract conservative Fukuoka project, target, budget, and settlement linkages."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

import pdfplumber

ORGANIZATION_PREFIXES = (
    "総務部",
    "企画・地域振興部",
    "人づくり・県民生活部",
    "保健医療介護部",
    "福祉労働部",
    "環境部",
    "商工部",
    "農林水産部",
    "県土整備部",
    "建築都市部",
    "教育庁",
    "警察本部",
)


def clean(value: object) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "")
    return re.sub(r"[^0-9A-Za-z一-龠ぁ-んァ-ヶ]", "", value).lower()


def parse_int(value: str) -> int | None:
    digits = re.sub(r"[^0-9]", "", unicodedata.normalize("NFKC", value or ""))
    return int(digits) if digits else None


def split_project_and_organization(raw: object) -> tuple[str, str]:
    lines = [clean(line) for line in str(raw or "").splitlines() if clean(line)]
    organization_index = next(
        (
            index
            for index, line in enumerate(lines)
            if line.replace(" ", "").startswith(ORGANIZATION_PREFIXES)
        ),
        None,
    )
    if organization_index is None:
        return clean(raw), ""
    project_name = " ".join(lines[:organization_index])
    organization = " / ".join(lines[organization_index:])
    return project_name, organization


def project_aliases(project_name: str) -> list[str]:
    aliases = [project_name]
    outer = re.sub(r"[（(].*?[）)]", "", project_name).strip()
    if outer and outer != project_name:
        aliases.append(outer)
    for inner in re.findall(r"[（(]([^）)]+)[）)]", project_name):
        inner = clean(inner)
        if len(normalize(inner)) >= 8:
            aliases.append(inner)
    result = []
    for alias in aliases:
        if len(normalize(alias)) >= 6 and alias not in result:
            result.append(alias)
    return result


def extract_page_texts(path: Path) -> list[str]:
    with pdfplumber.open(path) as pdf:
        return [page.extract_text() or "" for page in pdf.pages]


def extract_evaluated_projects(path: Path) -> list[dict]:
    records: list[dict] = []
    with pdfplumber.open(path) as pdf:
        for page_number, page in enumerate(pdf.pages[1:44], start=2):
            for table in page.extract_tables() or []:
                for raw_row in (row for row in table if row):
                    if len(raw_row) < 7:
                        continue
                    row = [clean(cell) for cell in raw_row]
                    number = parse_int(row[0])
                    if number is None or not (1 <= number <= 266):
                        continue
                    cost = parse_int(row[2])
                    project_name, department_office = split_project_and_organization(
                        raw_row[1]
                    )
                    if not project_name or cost is None:
                        continue
                    records.append(
                        {
                            "evaluation_number": number,
                            "project_name": project_name,
                            "project_name_normalized": normalize(project_name),
                            "project_aliases": project_aliases(project_name),
                            "department_office": department_office,
                            "fy2025_project_cost_thousand_yen": cost,
                            "purpose": row[3],
                            "content": row[4],
                            "indicator_text": row[5],
                            "direction": row[6],
                            "evaluation_summary_pdf_page": page_number,
                        }
                    )
    by_number: dict[int, dict] = {}
    for record in records:
        current = by_number.get(record["evaluation_number"])
        if current is None or len(record["project_name"]) > len(current["project_name"]):
            by_number[record["evaluation_number"]] = record
    return [by_number[number] for number in sorted(by_number)]


def load_targets(root: Path) -> list[dict]:
    targets: list[dict] = []
    for path in sorted(root.glob("fukuoka_prefecture_initiative_*_targets.json")):
        catalog = json.loads(path.read_text(encoding="utf-8"))
        initiative_id = catalog["policy_initiative_id"]
        for target in catalog["items"]:
            targets.append(
                {
                    "target_id": target["id"],
                    "initiative_id": initiative_id,
                    "indicator_name": target["indicator_name_original"],
                    "indicator_normalized": normalize(target["indicator_name_original"]),
                }
            )
    return targets


def page_matches(aliases: list[str], page_texts: list[str]) -> list[dict]:
    normalized_pages = [normalize(text) for text in page_texts]
    matches: dict[int, str] = {}
    for alias in aliases:
        needle = normalize(alias)
        if not needle:
            continue
        for page_number, haystack in enumerate(normalized_pages, start=1):
            if needle in haystack:
                matches.setdefault(page_number, alias)
    return [
        {"pdf_page": page_number, "matched_alias": matches[page_number]}
        for page_number in sorted(matches)
    ]


def target_matches(indicator_text: str, targets: list[dict]) -> list[dict]:
    haystack = normalize(indicator_text)
    matches = []
    for target in targets:
        needle = target["indicator_normalized"]
        if len(needle) >= 8 and needle in haystack:
            matches.append(
                {
                    "target_id": target["target_id"],
                    "initiative_id": target["initiative_id"],
                    "indicator_name": target["indicator_name"],
                    "match_basis": "normalized_full_indicator_in_evaluation_summary",
                }
            )
    return matches


def classify(
    projects: list[dict],
    targets: list[dict],
    budget_pages: list[str],
    settlement_pages: list[str],
) -> list[dict]:
    records = []
    for project in projects:
        budget_matches = page_matches(project["project_aliases"], budget_pages)
        settlement_matches = page_matches(project["project_aliases"], settlement_pages)
        linked_targets = target_matches(project["indicator_text"], targets)
        exact_budget = [
            item
            for item in budget_matches
            if normalize(item["matched_alias"]) == project["project_name_normalized"]
        ]
        exact_settlement = [
            item
            for item in settlement_matches
            if normalize(item["matched_alias"]) == project["project_name_normalized"]
        ]
        if len(exact_budget) == 1 and len(exact_settlement) == 1:
            status = "linked"
            basis = "exact_full_project_name_unique_in_budget_and_settlement"
        elif budget_matches or settlement_matches or linked_targets:
            status = "partial"
            basis = "one_or_more_official_layers_require_review"
        else:
            status = "not_linked"
            basis = "project_alias_not_found_in_money_sources"
        records.append(
            {
                "id": f"fukuoka-project-linkage-{project['evaluation_number']:03d}",
                "linkage_status": status,
                "match_basis": basis,
                **project,
                "target_matches": linked_targets,
                "budget_matches": budget_matches,
                "settlement_matches": settlement_matches,
                "boundary": (
                    "完全な事業名が令和8年度予算と令和6年度決算の各1ページに存在する。"
                    "年度と金額は別レコードとして保持し、政策成果へ自動変換しない。"
                    if status == "linked"
                    else "名称・別称の一致だけでは同一事業系列を確定しない。担当課、事業再編、"
                    "計画上の取組、対象年度を追加確認する。"
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
    parser.add_argument("--evaluation-pdf", type=Path, required=True)
    parser.add_argument("--budget-pdf", type=Path, required=True)
    parser.add_argument("--settlement-pdf", type=Path, required=True)
    parser.add_argument("--target-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    projects = extract_evaluated_projects(args.evaluation_pdf)
    targets = load_targets(args.target_root)
    budget_pages = extract_page_texts(args.budget_pdf)
    settlement_pages = extract_page_texts(args.settlement_pdf)
    records = classify(projects, targets, budget_pages, settlement_pages)
    status_counts = Counter(record["linkage_status"] for record in records)
    target_ids = {
        match["target_id"]
        for record in records
        for match in record["target_matches"]
    }

    part_files = []
    for part_number, offset in enumerate(range(0, len(records), 100), start=1):
        filename = f"fukuoka_project_linkage_part_{part_number:02d}.json"
        part_files.append(filename)
        part_records = records[offset : offset + 100]
        write_json(
            args.output_dir / filename,
            {
                "id": f"fukuoka-project-linkage-part-{part_number:02d}",
                "record_number_from": offset + 1,
                "record_number_to": offset + len(part_records),
                "records": part_records,
            },
        )

    index = {
        "id": "fukuoka-prefecture-project-linkage",
        "prefecture_code": "40",
        "status": "candidate_review",
        "sources": {
            "evaluation": "https://www.pref.fukuoka.lg.jp/uploaded/life/810515_62838386_misc.pdf",
            "budget": "https://www.pref.fukuoka.lg.jp/uploaded/attachment/278132.pdf",
            "settlement": "https://www.pref.fukuoka.lg.jp/uploaded/attachment/272597.pdf",
        },
        "evaluated_project_count": len(projects),
        "target_catalog_count": len(targets),
        "target_candidate_count": len(target_ids),
        "record_count": len(records),
        "part_files": part_files,
        "summary": {
            "linked_record_count": status_counts["linked"],
            "partial_record_count": status_counts["partial"],
            "not_linked_record_count": status_counts["not_linked"],
        },
        "promotion_rule": "candidate-only until department, office, plan initiative, and fiscal-year identity are reviewed",
        "evaluation_status": "not_assessed",
        "updated_at": "2026-08-01",
    }
    write_json(args.output_dir / "fukuoka_project_linkage.json", index)
    print(json.dumps(index, ensure_ascii=False))


if __name__ == "__main__":
    main()
