from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: str) -> Any:
    with (ROOT / path).open(encoding="utf-8") as handle:
        return json.load(handle)


def registry_entries() -> list[dict[str, str]]:
    return load_json("schemas/registry.json")["entries"]


def test_all_json_files_are_parseable() -> None:
    json_files = [
        path
        for path in ROOT.rglob("*.json")
        if "node_modules" not in path.parts and ".next" not in path.parts
    ]
    assert json_files
    for path in json_files:
        with path.open(encoding="utf-8") as handle:
            json.load(handle)


def test_all_registered_fixtures_match_their_schemas() -> None:
    checker = FormatChecker()
    for entry in registry_entries():
        schema = load_json(entry["schema"])
        fixture = load_json(entry["fixture"])
        validator = Draft202012Validator(schema, format_checker=checker)
        errors = list(validator.iter_errors(fixture))
        assert errors == [], (
            f"{entry['name']} fixture failed: "
            + "; ".join(error.message for error in errors)
        )


def test_schema_registry_names_and_paths_are_unique() -> None:
    entries = registry_entries()
    assert len({entry["name"] for entry in entries}) == len(entries)
    assert len({entry["schema"] for entry in entries}) == len(entries)
    assert len({entry["fixture"] for entry in entries}) == len(entries)


def test_pilot_scope_has_three_targets() -> None:
    scope = load_json("data/catalog/pilot_scope.json")
    assert [item["name_ja"] for item in scope["municipalities"]] == [
        "福岡県",
        "福岡市",
        "北九州市",
    ]


def test_source_catalog_has_expected_initial_coverage() -> None:
    records = load_json("data/catalog/official_sources.json")["records"]
    assert len(records) >= 30
    assert {record["municipality_key"] for record in records} == {
        "fukuoka-prefecture",
        "fukuoka-city",
        "kitakyushu-city",
    }
    assert len({record["id"] for record in records}) == len(records)
    assert all(record["url"].startswith("https://") for record in records)


def test_fixture_reference_spine_is_consistent() -> None:
    fixtures = {
        entry["name"]: load_json(entry["fixture"])
        for entry in registry_entries()
        if entry["name"] != "source_catalog"
    }
    municipality_id = fixtures["municipality"]["id"]
    project_id = fixtures["project"]["id"]
    executive_term_id = fixtures["executive_term"]["id"]
    assembly_id = fixtures["assembly"]["id"]
    proposal_id = fixtures["proposal"]["id"]

    assert fixtures["fiscal_record"]["municipality_id"] == municipality_id
    assert fixtures["project"]["municipality_id"] == municipality_id
    assert fixtures["contract"]["project_id"] == project_id
    assert fixtures["kpi"]["project_id"] == project_id
    assert fixtures["promise"]["executive_term_id"] == executive_term_id
    assert project_id in fixtures["promise"]["related_project_ids"]
    assert fixtures["proposal"]["assembly_id"] == assembly_id
    assert fixtures["vote"]["proposal_id"] == proposal_id
    assert fixtures["inspection_trip"]["assembly_id"] == assembly_id
    assert fixtures["evidence_packet"]["subject_id"] == project_id


def test_north_star_is_referenced_by_governance_documents() -> None:
    for path in ["README.md", "GOVERNANCE.md"]:
        content = (ROOT / path).read_text(encoding="utf-8")
        assert "docs/NORTH_STAR.md" in content
        assert "docs/PROJECT_MEMORY.md" in content
