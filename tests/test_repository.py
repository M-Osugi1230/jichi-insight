from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]


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
    with (ROOT / "schemas/project.schema.json").open(encoding="utf-8") as handle:
        schema = json.load(handle)
    with (ROOT / "data/examples/project.example.json").open(encoding="utf-8") as handle:
        instance = json.load(handle)

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = list(validator.iter_errors(instance))
    assert errors == [], "\n".join(error.message for error in errors)


def test_pilot_scope_has_three_targets() -> None:
    with (ROOT / "data/catalog/pilot_scope.json").open(encoding="utf-8") as handle:
        scope = json.load(handle)
    assert [item["name_ja"] for item in scope["municipalities"]] == [
        "福岡県",
        "福岡市",
        "北九州市",
    ]
