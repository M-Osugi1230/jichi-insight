from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
INVENTORY_SCHEMA = ROOT / "schemas/phase14_municipality_source_inventory.schema.json"
REGISTRY = ROOT / "data/catalog/phase14_core_capital_target_registry.json"

WAVE7 = {
    "362018": "data/indexed/tokushima-city/source_inventory.json",
    "372013": "data/indexed/takamatsu-city/source_inventory.json",
    "382019": "data/indexed/matsuyama-city/source_inventory.json",
    "392014": "data/indexed/kochi-city/source_inventory.json",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_phase14_wave7_has_four_schema_valid_source_inventories():
    schema = load(INVENTORY_SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    assert len(WAVE7) == 4
    for relative_path in WAVE7.values():
        inventory = load(ROOT / relative_path)
        assert list(validator.iter_errors(inventory)) == []
        assert inventory["phase"] == 14
        assert inventory["status"] == "source_inventory_complete"
        assert inventory["review_status"] == "indexed_not_reviewed"
        assert len(inventory["sources"]) >= 4


def test_phase14_wave7_identity_and_roles_match_target_registry():
    registry = load(REGISTRY)
    targets = {
        row["official_code"]: row
        for row in registry["targets"]
        if row["wave"] == 7
    }

    assert set(targets) == set(WAVE7)
    for official_code, relative_path in WAVE7.items():
        inventory = load(ROOT / relative_path)
        target = targets[official_code]

        assert target["status"] == "source_inventory_complete"
        assert inventory["official_code"] == official_code
        assert inventory["standard_area_code"] == target["standard_area_code"]
        assert inventory["name_ja"] == target["name_ja"]

        expected_roles = set()
        if target["core_city"]:
            expected_roles.add("core_city")
        if target["prefectural_capital"]:
            expected_roles.add("prefectural_capital")
        assert set(inventory["roles"]) == expected_roles


def test_phase14_wave7_sources_preserve_required_evidence_layers():
    for relative_path in WAVE7.values():
        inventory = load(ROOT / relative_path)
        layers = {source["layer"] for source in inventory["sources"]}

        assert any("plan" in layer for layer in layers)
        assert any(
            "implementation" in layer
            or "progress" in layer
            or "transition" in layer
            for layer in layers
        )
        assert "budget" in layers
        assert any("settlement" in layer for layer in layers)


def test_phase14_wave7_uses_only_official_municipal_sources():
    allowed_hosts = {
        "www.city.tokushima.tokushima.jp",
        "www.city.takamatsu.kagawa.jp",
        "www.city.matsuyama.ehime.jp",
        "www.city.kochi.kochi.jp",
    }

    for relative_path in WAVE7.values():
        inventory = load(ROOT / relative_path)
        for source in inventory["sources"]:
            url = source["official_url"]
            assert url.startswith("https://")
            assert any(url.startswith(f"https://{host}/") for host in allowed_hosts)


def test_phase14_wave7_preserves_special_version_boundaries():
    tokushima = load(ROOT / WAVE7["362018"])
    takamatsu = load(ROOT / WAVE7["372013"])
    matsuyama = load(ROOT / WAVE7["382019"])
    kochi = load(ROOT / WAVE7["392014"])

    assert tokushima["roles"] == ["prefectural_capital"]
    assert "FY2024" in tokushima["availability_boundary"]

    assert "重複" in takamatsu["availability_boundary"]
    assert takamatsu["plan_period"]["end_fiscal_year"] == 2031

    assert matsuyama["plan_period"]["start_fiscal_year"] == 2025
    assert "旧第6次" in matsuyama["availability_boundary"]

    assert kochi["plan_period"]["period_status"] == "transition_or_unresolved"
    assert kochi["plan_period"]["end_fiscal_year"] == 2030
    assert "FY2026末" in kochi["availability_boundary"]
    assert "FY2027" in kochi["availability_boundary"]


def test_phase14_wave7_does_not_claim_record_level_review():
    forbidden_statuses = {"reviewed", "reviewed_complete", "linked", "published"}

    for relative_path in WAVE7.values():
        inventory = load(ROOT / relative_path)
        assert inventory["review_status"] == "indexed_not_reviewed"
        assert inventory["status"] not in forbidden_statuses
        assert "Phase 15" in inventory["next_action"]
