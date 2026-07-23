#!/usr/bin/env python3
"""Finalize canonical nationwide registries after all Phase 9 reviews are generated."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
UPDATED_AT = "2026-07-22"
ALL_CODES = [f"{value:02d}" for value in range(1, 48)]
PHASE9_NEXT_ACTION = (
    "主要数値目標とEvidenceをReviewed化済み。"
    "次に年度実績、重点事業、予算、契約を定義照合して接続する。"
)


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def rebuild_inventory_summary(inventory: dict[str, Any]) -> None:
    statuses = inventory["status_order"]
    summary: dict[str, Any] = {"prefecture_count": len(inventory["records"])}
    for category in inventory["categories"]:
        counts = Counter(
            record["sources"][category] for record in inventory["records"]
        )
        summary[category] = {status: counts[status] for status in statuses}
    inventory["summary"] = summary


def finalize(root: Path) -> None:
    summary_path = root / "data/catalog/phase9_review_summary.json"
    summary = load(summary_path)
    if summary["status"] != "reviewed_complete" or summary["prefecture_count"] != 38:
        raise ValueError("Phase 9 review summary is not complete")
    if summary["evidence_coverage_percent"] != 100:
        raise ValueError("Phase 9 Evidence coverage must be 100%")
    if summary["policy_achievement_assessed_count"] != 0:
        raise ValueError("Phase 9 must not introduce independent achievement assessments")
    if summary["ranking_eligible_record_count"] != 0:
        raise ValueError("Unverified Phase 9 records must remain excluded from ranking")

    coverage_path = root / "data/catalog/prefecture_coverage.json"
    coverage = load(coverage_path)
    coverage["updated_at"] = UPDATED_AT
    coverage["reviewed_prefecture_codes"] = ALL_CODES
    for source in coverage["plan_sources"]:
        source["review_status"] = "reviewed"
    write(coverage_path, coverage)

    publication_path = root / "data/catalog/published_prefecture_pages.json"
    publication = load(publication_path)
    by_code = {record["prefecture_code"]: record for record in publication["records"]}
    for record in summary["records"]:
        by_code[record["prefecture_code"]] = {
            "prefecture_code": record["prefecture_code"],
            "route": record["route"],
            "publication_status": "published",
        }
    publication["updated_at"] = UPDATED_AT
    publication["records"] = [by_code[code] for code in ALL_CODES]
    if len(publication["records"]) != 47:
        raise ValueError("Published prefecture registry must contain all 47 prefectures")
    write(publication_path, publication)

    inventory_path = root / "data/catalog/nationwide_source_inventory.json"
    inventory = load(inventory_path)
    phase9_codes = {record["prefecture_code"] for record in summary["records"]}
    reviewed_codes = set(coverage["reviewed_prefecture_codes"])
    for record in inventory["records"]:
        code = record["prefecture_code"]
        if code in reviewed_codes:
            record["sources"]["policy_plan"] = "reviewed"
            record["sources"]["kpi_source"] = "reviewed"
        if code not in phase9_codes:
            continue

        # Phase 9 reviewed current-plan target statements. It did not review or
        # link annual results, so never infer annual-evaluation depth from the
        # existence of a target source. Repair the earlier auto-promotion only
        # while this Phase 9 next-action boundary is still active.
        if record["next_action"] == PHASE9_NEXT_ACTION:
            record["sources"]["annual_evaluation"] = "not_indexed"
        record["next_action"] = PHASE9_NEXT_ACTION

    inventory["updated_at"] = UPDATED_AT
    rebuild_inventory_summary(inventory)
    write(inventory_path, inventory)

    phase7_path = root / "data/catalog/phase7_completion.json"
    phase7 = load(phase7_path)
    phase7["scope_version"] = UPDATED_AT
    phase7["counts"]["published_prefecture_pages"] = 47
    phase7["scope_note"] = (
        "Phase 7 completed the nationwide registry and publication-state model. "
        "Phase 8 and Phase 9 have now expanded Reviewed public pages to all 47 prefectures; "
        "publication count remains independently derived from the canonical page registry."
    )
    write(phase7_path, phase7)

    completion_path = root / "data/catalog/phase9_completion.json"
    completion = load(completion_path)
    completion["scope_version"] = UPDATED_AT
    completion["updated_at"] = UPDATED_AT
    completion["status"] = "complete"
    for gate in completion["gates"]:
        gate["status"] = "passed"
        if gate["id"] == "nationwide_publication_and_smoke":
            for evidence_path in (
                "data/catalog/published_prefecture_pages.json",
                "apps/web/app/municipalities/phase9/page.tsx",
                "apps/web/app/municipalities/phase9/[slug]/page.tsx",
                "scripts/validate_static_export.py",
                ".github/workflows/production-smoke.yml",
            ):
                if evidence_path not in gate["evidence_paths"]:
                    gate["evidence_paths"].append(evidence_path)
    completion["scope_note"] = (
        "Phase 9 is complete. All 38 remaining prefectures have Evidence-backed Reviewed "
        "target statements, explicit plan-history and comparability metadata, published static "
        "pages, and nationwide production verification. Together with the nine Phase 8 anchors, "
        "all 47 prefectures now have Reviewed numeric-target coverage."
    )
    write(completion_path, completion)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    finalize(args.root)


if __name__ == "__main__":
    main()
