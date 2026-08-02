#!/usr/bin/env python3
"""Normalize all Miyagi project-money records without changing review judgments."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INDEX_RELATIVE_PATH = "data/catalog/miyagi_project_money_linkage.json"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_source_records(
    root: Path = ROOT,
) -> tuple[dict[str, Any], list[tuple[str, dict[str, Any]]]]:
    index = load(root / INDEX_RELATIVE_PATH)
    records: list[tuple[str, dict[str, Any]]] = []

    for filename in index["part_files"]:
        relative_path = f"data/catalog/{filename}"
        part = load(root / relative_path)
        records.extend(
            (relative_path, record)
            for record in part["records"]
        )

    return index, records


def numeric_component(value_text: str, value: int) -> dict[str, Any]:
    return {
        "label": None,
        "unit": "千円",
        "value_text": value_text,
        "value": value,
        "value_status": "numeric",
    }


def measurement(
    role: str,
    status: str,
    period_text: str,
    value_text: str,
    components: list[dict[str, Any]],
    source_number: int | None,
    page: int | None,
) -> dict[str, Any]:
    return {
        "role": role,
        "status": status,
        "period_text": period_text,
        "value_text": value_text,
        "components": components,
        "evidence": {
            "source_number": source_number,
            "page": page,
        },
    }


def normalized_candidates(source: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "policy_ref": candidate["policy_id"],
            "measure_ref": candidate["measure_id"],
            "name": candidate["project_name"],
            "department": candidate["department"],
            "office": candidate["office"],
            "amount_thousand_yen": candidate[
                "settlement_amount_thousand_yen"
            ],
            "page": candidate["settlement_pdf_page"],
        }
        for candidate in source["settlement_candidates"]
    ]


def evidence_locations(source: dict[str, Any]) -> list[dict[str, Any]]:
    locations = [
        {
            "source_number": 1,
            "page": source["budget_pdf_page"],
            "is_reprint": False,
        }
    ]

    if source["settlement_pdf_page"] is not None:
        locations.append(
            {
                "source_number": 2,
                "page": source["settlement_pdf_page"],
                "is_reprint": False,
            }
        )

    locations.extend(
        {
            "source_number": 2,
            "page": candidate["settlement_pdf_page"],
            "is_reprint": False,
        }
        for candidate in source["settlement_candidates"]
    )

    deduplicated: list[dict[str, Any]] = []
    seen: set[tuple[int, int]] = set()
    for location in locations:
        key = (location["source_number"], location["page"])
        if key not in seen:
            seen.add(key)
            deduplicated.append(location)
    return deduplicated


def settlement_measurement(source: dict[str, Any]) -> dict[str, Any]:
    status = source["linkage_status"]
    if status == "linked":
        return measurement(
            "settlement",
            "available",
            source["settlement_period"],
            source["settlement_amount_text"],
            [
                numeric_component(
                    source["settlement_amount_text"],
                    source["settlement_amount_thousand_yen"],
                )
            ],
            2,
            source["settlement_pdf_page"],
        )

    if status == "partial":
        return measurement(
            "settlement",
            "not_promoted",
            "",
            "",
            [],
            None,
            None,
        )

    return measurement(
        "settlement",
        "not_available",
        "",
        "",
        [],
        None,
        None,
    )


def normalize_record(
    source_registry: str,
    source: dict[str, Any],
) -> dict[str, Any]:
    sequence = int(source["id"].rsplit("-", maxsplit=1)[-1])
    hierarchy_refs = [
        value
        for value in (source["policy_id"], source["measure_id"])
        if value is not None
    ]
    partial_reason = (
        None
        if source["linkage_status"] == "linked"
        else source["match_basis"]
    )

    return {
        "id": f"phase11-record-miyagi-{sequence:04d}",
        "prefecture_code": "04",
        "source_registry": source_registry,
        "source_record_id": source["id"],
        "linkage_kind": "policy_measure_to_project_money",
        "linkage_status": source["linkage_status"],
        "partial_reason": partial_reason,
        "subject": {
            "record_ref": source["id"],
            "sequence": sequence,
            "name": source["project_name"],
            "source_name": source["project_name"],
            "definition": "",
            "hierarchy_refs": hierarchy_refs,
        },
        "context": {
            "policy_ref": source["policy_id"],
            "measure_ref": source["measure_id"],
            "normalized_name": source["project_name_normalized"],
            "department": source["department"],
            "office": source["office"],
            "implementation_period": source["implementation_period"],
            "match_basis": source["match_basis"],
            "settlement_project_number_text": source[
                "settlement_project_number_text"
            ],
            "settlement_candidates": normalized_candidates(source),
        },
        "measurements": [
            measurement(
                "budget",
                "reported",
                source["budget_period"],
                source["budget_amount_text"],
                [
                    numeric_component(
                        source["budget_amount_text"],
                        source["budget_amount_thousand_yen"],
                    )
                ],
                1,
                source["budget_pdf_page"],
            ),
            settlement_measurement(source),
        ],
        "evidence": {
            "primary_source_number": 1,
            "primary_page": source["budget_pdf_page"],
            "locations": evidence_locations(source),
        },
        "boundary": source["boundary"],
        "evaluation_status": "not_assessed",
        "comparability_status": "excluded_until_verified",
    }


def build_catalog(root: Path = ROOT) -> dict[str, Any]:
    index, source_records = load_source_records(root)
    records = [
        normalize_record(source_registry, source)
        for source_registry, source in source_records
    ]
    statuses = Counter(record["linkage_status"] for record in records)
    match_basis_counts = Counter(
        record["context"]["match_basis"] for record in records
    )

    return {
        "id": "phase11-miyagi-normalized-records",
        "phase": 11,
        "status": "normalized",
        "prefecture_code": "04",
        "source_catalog": INDEX_RELATIVE_PATH,
        "source_files": [
            f"data/catalog/{filename}"
            for filename in index["part_files"]
        ],
        "records": records,
        "summary": {
            "record_count": len(records),
            "linked_record_count": statuses["linked"],
            "partial_record_count": statuses["partial"],
            "not_linked_record_count": statuses["not_linked"],
            "policy_achievement_assessment_count": 0,
            "match_basis_counts": dict(sorted(match_basis_counts.items())),
        },
        "updated_at": index["updated_at"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    payload = build_catalog()
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
