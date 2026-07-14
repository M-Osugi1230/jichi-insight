#!/usr/bin/env python3
"""Validate the Jichi Insight repository structure and JSON contracts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "DATA_POLICY.md",
    "GOVERNANCE.md",
    "docs/NORTH_STAR.md",
    "docs/PROJECT_MEMORY.md",
    "docs/PROJECT_CHARTER.md",
    "docs/METHODOLOGY.md",
    "docs/ROADMAP.md",
    "schemas/source.schema.json",
    "schemas/source_catalog.schema.json",
    "schemas/municipality.schema.json",
    "schemas/project.schema.json",
    "schemas/promise.schema.json",
    "data/catalog/pilot_scope.json",
    "data/catalog/official_sources.json",
]


def load_json(relative_path: str) -> object:
    path = ROOT / relative_path
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def validate_required_files() -> list[str]:
    return [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]


def validate_all_json() -> list[str]:
    errors: list[str] = []
    for path in sorted(ROOT.rglob("*.json")):
        if any(part in {"node_modules", ".next"} for part in path.parts):
            continue
        try:
            with path.open(encoding="utf-8") as handle:
                json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")
    return errors


def validate_schema_pairs() -> list[str]:
    errors: list[str] = []
    pairs = [
        ("schemas/project.schema.json", "data/examples/project.example.json"),
        ("schemas/source_catalog.schema.json", "data/catalog/official_sources.json"),
    ]
    checker = FormatChecker()
    for schema_path, instance_path in pairs:
        schema = load_json(schema_path)
        instance = load_json(instance_path)
        validator = Draft202012Validator(schema, format_checker=checker)
        for error in sorted(validator.iter_errors(instance), key=lambda item: list(item.path)):
            location = ".".join(str(item) for item in error.path) or "<root>"
            errors.append(f"{instance_path}:{location}: {error.message}")
    return errors


def validate_example_markers() -> list[str]:
    project = load_json("data/examples/project.example.json")
    errors: list[str] = []
    if not str(project.get("official_title", "")).startswith("【架空例】"):
        errors.append("Example project must clearly state that it is fictional.")
    if project.get("municipality_id") != "jp-local-000000":
        errors.append("Example project must use the reserved fictional municipality ID.")
    return errors


def validate_source_catalog() -> list[str]:
    catalog = load_json("data/catalog/official_sources.json")
    errors: list[str] = []
    records = catalog.get("records", [])

    if len(records) < 30:
        errors.append("Official source catalog must contain at least 30 initial records.")

    ids = [record.get("id") for record in records]
    if len(ids) != len(set(ids)):
        errors.append("Official source catalog contains duplicate record IDs.")

    expected_municipalities = {
        "fukuoka-prefecture",
        "fukuoka-city",
        "kitakyushu-city",
    }
    actual_municipalities = {record.get("municipality_key") for record in records}
    if actual_municipalities != expected_municipalities:
        errors.append(
            "Official source catalog municipality keys must match the three pilot municipalities."
        )

    for record in records:
        record_id = record.get("id", "<unknown>")
        url = str(record.get("url", ""))
        if not url.startswith("https://"):
            errors.append(f"{record_id}: official source URL must use HTTPS.")
        if record.get("review_status") not in {"reviewed", "verified"}:
            errors.append(f"{record_id}: initial catalog records must be reviewed or verified.")
        if record.get("source_kind") != "landing_page":
            errors.append(f"{record_id}: initial catalog must contain landing-page records only.")

    return errors


def validate_north_star_links() -> list[str]:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    governance = (ROOT / "GOVERNANCE.md").read_text(encoding="utf-8")
    errors: list[str] = []
    for document, name in [(readme, "README.md"), (governance, "GOVERNANCE.md")]:
        if "docs/NORTH_STAR.md" not in document:
            errors.append(f"{name} must reference docs/NORTH_STAR.md.")
        if "docs/PROJECT_MEMORY.md" not in document:
            errors.append(f"{name} must reference docs/PROJECT_MEMORY.md.")
    return errors


def main() -> int:
    failures: list[str] = []

    missing = validate_required_files()
    failures.extend(f"Missing required file: {path}" for path in missing)
    failures.extend(validate_all_json())
    failures.extend(validate_schema_pairs())
    failures.extend(validate_example_markers())
    failures.extend(validate_source_catalog())
    failures.extend(validate_north_star_links())

    if failures:
        print("Repository validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Repository validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
