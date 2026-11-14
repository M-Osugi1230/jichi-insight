#!/usr/bin/env python3
"""Validate Phase 15 candidate staging packages for schema and evidence boundary compliance."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES_DIR = ROOT / "data/candidates"
SCHEMA_PATH = ROOT / "schemas/phase15_review_candidate.schema.json"


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def validate_schema(instance: Any) -> list[str]:
    schema = load_json(SCHEMA_PATH)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors: list[str] = []
    validation_errors = sorted(
        validator.iter_errors(instance),
        key=lambda item: list(item.path),
    )
    for error in validation_errors:
        location = ".".join(str(item) for item in error.path) or "<root>"
        errors.append(f"schema:{location}: {error.message}")
    return errors


def validate_evidence_boundaries(candidate: dict[str, Any], path: Path) -> list[str]:
    errors: list[str] = []
    label = str(path.relative_to(ROOT))

    # Validate source inventory file existence
    inv_path_str = candidate.get("source_inventory_path", "")
    if not inv_path_str.startswith("data/indexed/"):
        errors.append(f"{label}: source_inventory_path must start with data/indexed/")
    inv_path = ROOT / inv_path_str
    if not inv_path.is_file():
        errors.append(f"{label}: source_inventory_path file does not exist ({inv_path_str})")

    # Validate human review boundaries
    human_review = candidate.get("human_review", {})
    if human_review.get("required") is not True:
        errors.append(f"{label}: human_review.required must be true")
    if human_review.get("status") != "pending":
        errors.append(f"{label}: human_review.status must be pending")
    if human_review.get("reviewed_at") is not None:
        errors.append(f"{label}: human_review.reviewed_at must be null")
    if human_review.get("reviewer_note") is not None:
        errors.append(f"{label}: human_review.reviewer_note must be null")

    # Validate publication eligibility
    pub = candidate.get("publication", {})
    if pub.get("eligible") is not False:
        errors.append(f"{label}: publication.eligible must be false")

    # Validate quality boundaries
    quality = candidate.get("quality_boundaries", [])
    text = " ".join(quality).lower()
    for keyword in ("score", "causal", "ranking"):
        if keyword not in text:
            errors.append(f"{label}: quality_boundaries must prohibit {keyword}")
    if not any("human" in b.lower() or "person checks" in b.lower() for b in quality):
        errors.append(f"{label}: quality_boundaries must require human check before promotion")

    # Validate package state and candidate package
    pkg_state = candidate.get("package_state")
    if pkg_state not in {"scaffold", "prepared"}:
        errors.append(f"{label}: package_state must be scaffold or prepared")

    if pkg_state == "prepared":
        pkg = candidate.get("candidate_package", {})
        code = candidate.get("official_code")
        name_ja = candidate.get("name_ja")

        # Source catalog
        sc = pkg.get("source_catalog", {})
        if sc.get("phase") != 15:
            errors.append(f"{label}: source_catalog.phase must be 15")
        if sc.get("official_code") != code:
            errors.append(f"{label}: source_catalog.official_code mismatch")
        if sc.get("name_ja") != name_ja:
            errors.append(f"{label}: source_catalog.name_ja mismatch")
        sources = sc.get("sources", [])
        if len(sources) < 4:
            errors.append(f"{label}: source_catalog must contain at least 4 sources")
        for src in sources:
            if not src.get("official_url", "").startswith("https://"):
                errors.append(
                    f"{label}: source {src.get('id')} official_url must use https://"
                )

        # Plan review
        pr = pkg.get("plan_review", {})
        if pr.get("official_code") != code:
            errors.append(f"{label}: plan_review.official_code mismatch")
        if pr.get("name_ja") != name_ja:
            errors.append(f"{label}: plan_review.name_ja mismatch")
        records = pr.get("records", [])
        if len(records) < 3:
            errors.append(f"{label}: plan_review must contain at least 3 records")
        for rec in records:
            if rec.get("decision") not in {"needs_review", "not_assessable", "accepted"}:
                errors.append(f"{label}: plan_review record {rec.get('id')} invalid decision")

        # Policy structure
        ps = pkg.get("policy_structure", {})
        if ps.get("phase") != 15 or ps.get("official_code") != code:
            errors.append(f"{label}: policy_structure identity mismatch")

        # Fiscal records and evidence packets
        fiscals = pkg.get("fiscal_records", [])
        evidences = pkg.get("evidence_packets", [])
        expected_mun_id = f"jp-local-{code}"

        fiscal_ids = {f.get("id") for f in fiscals}
        for f in fiscals:
            if f.get("municipality_id") != expected_mun_id:
                errors.append(f"{label}: fiscal record {f.get('id')} municipality_id mismatch")
            if f.get("account_type") != "general":
                errors.append(f"{label}: fiscal record {f.get('id')} must use general account")
            if f.get("review_status") != "needs_review":
                errors.append(
                    f"{label}: fiscal record {f.get('id')} review_status must be needs_review"
                )

        evidence_sub_ids = {e.get("subject_id") for e in evidences}
        if fiscal_ids != evidence_sub_ids:
            errors.append(f"{label}: evidence packet subject_ids do not match fiscal_record ids")

        for e in evidences:
            if e.get("subject_type") != "fiscal_record":
                errors.append(
                    f"{label}: evidence packet {e.get('id')} subject_type must be fiscal_record"
                )
            if e.get("review_status") != "needs_review":
                errors.append(
                    f"{label}: evidence packet {e.get('id')} review_status must be needs_review"
                )
            for claim in e.get("claims", []):
                if claim.get("decision") != "needs_review":
                    errors.append(
                        f"{label}: evidence claim in {e.get('id')} decision must be needs_review"
                    )

    return errors


def main() -> int:
    candidate_paths = sorted(CANDIDATES_DIR.glob("*/review_candidate.json"))
    if not candidate_paths:
        print("No Phase 15 candidate staging files found.")
        return 1

    total_failures: list[str] = []

    for path in candidate_paths:
        try:
            data = load_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            total_failures.append(f"{path.relative_to(ROOT)}: {exc}")
            continue

        schema_errors = validate_schema(data)
        boundary_errors = validate_evidence_boundaries(data, path)

        for err in schema_errors:
            total_failures.append(f"{path.relative_to(ROOT)}:{err}")
        for err in boundary_errors:
            total_failures.append(err)

    if total_failures:
        print("Phase 15 candidate validation failed:")
        for failure in total_failures:
            print(f"- {failure}")
        return 1

    print(f"Phase 15 candidate validation passed for {len(candidate_paths)} packages.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
