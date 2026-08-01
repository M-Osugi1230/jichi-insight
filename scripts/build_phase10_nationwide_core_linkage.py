from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALL_CODES = [f"{value:02d}" for value in range(1, 48)]
CORE_DIMENSIONS = (
    "annual_actuals",
    "budget",
    "settlement",
    "priority_projects",
    "audit",
)

REVIEW_FILES = [
    "data/catalog/phase10_reference_depth_reviews.json",
    "data/catalog/phase10_anchor_depth_reviews.json",
    "data/catalog/phase10_tohoku_depth_reviews.json",
    "data/catalog/phase10_kanto_depth_reviews.json",
    "data/catalog/phase10_chubu_depth_reviews.json",
    "data/catalog/phase10_kinki_depth_reviews.json",
    "data/catalog/phase10_chugoku_depth_reviews.json",
    "data/catalog/phase10_shikoku_depth_reviews.json",
    "data/catalog/phase10_kyushu_depth_reviews.json",
]

DEEPER_EVIDENCE = {
    "01": [
        "data/catalog/hokkaido_annual_actual_linkage.json",
        "tests/test_hokkaido_annual_actual_linkage.py",
    ],
    "04": [
        "data/catalog/miyagi_policy_review_manifest.json",
        "data/catalog/miyagi_project_money_linkage_index.json",
        "tests/test_miyagi_project_money_linkage.py",
    ],
    "13": [
        "data/catalog/tokyo_children_annual_actual_linkage.json",
        "tests/test_tokyo_children_annual_actual_linkage.py",
    ],
    "40": [
        "data/catalog/fukuoka_annual_actual_linkage_index.json",
        "data/catalog/fukuoka_project_linkage_index.json",
        "tests/test_fukuoka_annual_actual_linkage.py",
        "tests/test_fukuoka_project_linkage.py",
    ],
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def registry_coverage(registry_path: str) -> dict[str, set[str]]:
    payload = load(ROOT / registry_path)
    coverage: dict[str, set[str]] = {}
    for record in payload["records"]:
        code = record["prefecture_code"]
        dimensions = record.get("sources", {}).keys()
        if not dimensions and record.get("dimension"):
            dimensions = [record["dimension"]]
        coverage.setdefault(code, set()).update(
            dimension for dimension in dimensions if dimension in CORE_DIMENSIONS
        )
    return coverage


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    groups = []
    expanded: dict[str, set[str]] = {code: set() for code in ALL_CODES}
    for registry_path in REVIEW_FILES:
        coverage = registry_coverage(registry_path)
        by_dimensions: dict[tuple[str, ...], list[str]] = {}
        for code, dimensions in coverage.items():
            key = tuple(dimension for dimension in CORE_DIMENSIONS if dimension in dimensions)
            if key:
                by_dimensions.setdefault(key, []).append(code)
                expanded[code].update(key)
        for dimensions, codes in sorted(by_dimensions.items()):
            groups.append(
                {
                    "source_registry": registry_path,
                    "prefecture_codes": sorted(codes),
                    "dimensions": list(dimensions),
                    "selector": "prefecture_code_and_dimension",
                    "linkage_status": "linked",
                    "linkage_level": "document_scope",
                }
            )

    groups.append(
        {
            "source_registry": "data/catalog/miyagi_policy_review_manifest.json",
            "prefecture_codes": ["04"],
            "dimensions": ["annual_actuals"],
            "selector": "prefecture_code_and_work_package:evaluation_linkage",
            "linkage_status": "linked",
            "linkage_level": "record_and_document_scope",
        }
    )
    expanded["04"].add("annual_actuals")

    missing = {
        code: sorted(set(CORE_DIMENSIONS) - dimensions)
        for code, dimensions in expanded.items()
        if set(CORE_DIMENSIONS) - dimensions
    }
    if missing:
        raise SystemExit(f"Missing core linkage coverage: {missing}")

    counts = Counter(
        dimension for dimensions in expanded.values() for dimension in dimensions
    )
    payload = {
        "id": "phase10-nationwide-core-linkage",
        "phase": 10,
        "status": "complete",
        "scope_version": "2026-08-01",
        "linkage_definition": (
            "Document-scope linkage verifies the correct prefecture, official source role, "
            "plan or fiscal period, and publication scope. It does not assert that every target, "
            "budget line, project, payment, or audit finding has a one-to-one record-level link."
        ),
        "record_level_boundary": (
            "Unresolved one-to-one relationships remain explicit in the referenced Reviewed "
            "registries and are not used for policy-achievement assessment or ranking."
        ),
        "dimensions": list(CORE_DIMENSIONS),
        "link_groups": groups,
        "deeper_record_level_evidence": DEEPER_EVIDENCE,
        "summary": {
            "prefecture_count": len(expanded),
            "linked_prefecture_count": sum(
                dimensions == set(CORE_DIMENSIONS) for dimensions in expanded.values()
            ),
            "linked_dimension_counts": {
                dimension: counts[dimension] for dimension in CORE_DIMENSIONS
            },
            "policy_achievement_assessment_count": 0,
        },
        "policy_achievement_assessment_status": "not_assessed",
        "updated_at": "2026-08-01",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
