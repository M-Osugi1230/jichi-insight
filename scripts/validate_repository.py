#!/usr/bin/env python3
"""Validate the Jichi Insight repository structure and JSON contracts."""

from __future__ import annotations

import json
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

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
    "schemas/README.md",
    "schemas/registry.json",
    "data/catalog/pilot_scope.json",
    "data/catalog/official_sources.json",
]


def load_json(relative_path: str) -> Any:
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


def registry_entries() -> list[dict[str, str]]:
    registry = load_json("schemas/registry.json")
    return registry["entries"]


def validate_schema_registry() -> list[str]:
    errors: list[str] = []
    entries = registry_entries()
    names = [entry["name"] for entry in entries]

    if len(names) != len(set(names)):
        errors.append("Schema registry contains duplicate names.")

    checker = FormatChecker()
    for entry in entries:
        schema_path = entry["schema"]
        fixture_path = entry["fixture"]
        if not (ROOT / schema_path).is_file():
            errors.append(f"Missing schema registered as {entry['name']}: {schema_path}")
            continue
        if not (ROOT / fixture_path).is_file():
            errors.append(f"Missing fixture registered as {entry['name']}: {fixture_path}")
            continue

        schema = load_json(schema_path)
        fixture = load_json(fixture_path)
        validator = Draft202012Validator(schema, format_checker=checker)
        for error in sorted(validator.iter_errors(fixture), key=lambda item: list(item.path)):
            location = ".".join(str(item) for item in error.path) or "<root>"
            errors.append(f"{fixture_path}:{location}: {error.message}")

    return errors


def validate_fixture_markers() -> list[str]:
    errors: list[str] = []
    for entry in registry_entries():
        if entry["name"] == "source_catalog":
            continue
        fixture_path = entry["fixture"]
        serialized = json.dumps(load_json(fixture_path), ensure_ascii=False)
        if "架空" not in serialized and "000000" not in serialized:
            errors.append(f"{fixture_path} must be clearly identifiable as fictional.")
    return errors


def iter_source_references(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"sources", "source_ids", "manifesto_source_ids"} and isinstance(
                child, list
            ):
                yield from (item for item in child if isinstance(item, str))
            yield from iter_source_references(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_source_references(child)


def validate_reference_integrity() -> list[str]:
    errors: list[str] = []
    fixtures = {
        entry["name"]: load_json(entry["fixture"])
        for entry in registry_entries()
        if entry["name"] != "source_catalog"
    }
    catalog = load_json("data/catalog/official_sources.json")
    source_ids = {fixtures["source"]["id"]}
    source_ids.update(record["id"] for record in catalog["records"])

    entity_ids = {
        name: fixture.get("id")
        for name, fixture in fixtures.items()
        if isinstance(fixture, dict) and fixture.get("id")
    }

    expected_references = [
        ("fiscal_record", "municipality_id", entity_ids["municipality"]),
        ("project", "municipality_id", entity_ids["municipality"]),
        ("contract", "municipality_id", entity_ids["municipality"]),
        ("contract", "project_id", entity_ids["project"]),
        ("kpi", "project_id", entity_ids["project"]),
        ("executive_term", "municipality_id", entity_ids["municipality"]),
        ("promise", "municipality_id", entity_ids["municipality"]),
        ("promise", "executive_term_id", entity_ids["executive_term"]),
        ("assembly", "municipality_id", entity_ids["municipality"]),
        ("proposal", "assembly_id", entity_ids["assembly"]),
        ("vote", "proposal_id", entity_ids["proposal"]),
        ("inspection_trip", "assembly_id", entity_ids["assembly"]),
    ]
    for entity, field, expected in expected_references:
        actual = fixtures[entity].get(field)
        if actual != expected:
            errors.append(f"{entity}.{field} must reference {expected}, got {actual}.")

    if entity_ids["project"] not in fixtures["promise"].get("related_project_ids", []):
        errors.append("Promise fixture must reference the project fixture.")
    if entity_ids["project"] not in fixtures["proposal"].get("related_project_ids", []):
        errors.append("Proposal fixture must reference the project fixture.")

    evidence = fixtures["evidence_packet"]
    subject_type = evidence["subject_type"]
    if evidence["subject_id"] != entity_ids.get(subject_type):
        errors.append("Evidence packet fixture must reference its registered subject fixture.")

    for name, fixture in fixtures.items():
        missing_sources = set(iter_source_references(fixture)) - source_ids
        if missing_sources:
            errors.append(
                f"{name} fixture references unknown sources: {sorted(missing_sources)}"
            )

    return errors


def validate_source_catalog() -> list[str]:
    catalog = load_json("data/catalog/official_sources.json")
    records = catalog.get("records", [])
    errors: list[str] = []

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
            "Official source catalog municipality keys must match the pilot municipalities."
        )

    for record in records:
        record_id = record.get("id", "<unknown>")
        url = str(record.get("url", ""))
        if not url.startswith("https://"):
            errors.append(f"{record_id}: official source URL must use HTTPS.")
        if record.get("review_status") not in {"reviewed", "verified"}:
            errors.append(f"{record_id}: catalog records must be reviewed or verified.")

    return errors


def validate_north_star_links() -> list[str]:
    errors: list[str] = []
    for relative_path in ["README.md", "GOVERNANCE.md"]:
        content = (ROOT / relative_path).read_text(encoding="utf-8")
        if "docs/NORTH_STAR.md" not in content:
            errors.append(f"{relative_path} must reference docs/NORTH_STAR.md.")
        if "docs/PROJECT_MEMORY.md" not in content:
            errors.append(f"{relative_path} must reference docs/PROJECT_MEMORY.md.")
    return errors


def main() -> int:
    failures: list[str] = []
    failures.extend(f"Missing required file: {path}" for path in validate_required_files())
    failures.extend(validate_all_json())
    failures.extend(validate_schema_registry())
    failures.extend(validate_fixture_markers())
    failures.extend(validate_reference_integrity())
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
