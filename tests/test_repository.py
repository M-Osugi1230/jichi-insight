from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: str) -> object:
    with (ROOT / path).open(encoding="utf-8") as handle:
        return json.load(handle)


def schema_errors(schema_path: str, instance_path: str) -> list[str]:
    schema = load_json(schema_path)
    instance = load_json(instance_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [error.message for error in validator.iter_errors(instance)]


def test_all_json_files_are_parseable() -> None:
    json_files = [
        path
        for path in ROOT.rglob("*.json")
        if "node_modules" not in path.parts and ".next" not in path.parts
    ]
    assert json_files, "No JSON files were found."
    for path in json_files:
        with path.open(encoding="utf-8") as handle:
            json.load(handle)


def test_project_example_matches_schema() -> None:
    assert schema_errors(
        "schemas/project.schema.json",
        "data/examples/project.example.json",
    ) == []


def test_source_catalog_matches_schema() -> None:
    assert schema_errors(
        "schemas/source_catalog.schema.json",
        "data/catalog/official_sources.json",
    ) == []


def test_pilot_scope_has_three_targets() -> None:
    scope = load_json("data/catalog/pilot_scope.json")
    assert [item["name_ja"] for item in scope["municipalities"]] == [
        "福岡県",
        "福岡市",
        "北九州市",
    ]


def test_source_catalog_has_expected_initial_coverage() -> None:
    catalog = load_json("data/catalog/official_sources.json")
    records = catalog["records"]
    assert len(records) >= 30
    assert {record["municipality_key"] for record in records} == {
        "fukuoka-prefecture",
        "fukuoka-city",
        "kitakyushu-city",
    }
    assert len({record["id"] for record in records}) == len(records)
    assert all(record["url"].startswith("https://") for record in records)
    assert all(record["review_status"] in {"reviewed", "verified"} for record in records)


def test_north_star_is_referenced_by_governance_documents() -> None:
    for path in ["README.md", "GOVERNANCE.md"]:
        content = (ROOT / path).read_text(encoding="utf-8")
        assert "docs/NORTH_STAR.md" in content
        assert "docs/PROJECT_MEMORY.md" in content
