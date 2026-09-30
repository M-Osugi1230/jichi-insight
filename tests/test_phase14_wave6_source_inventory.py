from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
INVENTORY_SCHEMA = ROOT / "schemas/phase14_municipality_source_inventory.schema.json"
REGISTRY = ROOT / "data/catalog/phase14_core_capital_target_registry.json"

WAVE6 = {
    "312010": "data/indexed/tottori-city/source_inventory.json",
    "322016": "data/indexed/matsue-city/source_inventory.json",
    "332020": "data/indexed/kurashiki-city/source_inventory.json",
    "342025": "data/indexed/kure-city/source_inventory.json",
    "342076": "data/indexed/fukuyama-city/source_inventory.json",
    "352012": "data/indexed/shimonoseki-city/source_inventory.json",
    "352039": "data/indexed/yamaguchi-city/source_inventory.json",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_phase14_wave6_has_seven_schema_valid_source_inventories():
    schema = load(INVENTORY_SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    assert len(WAVE6) == 7
    for relative_path in WAVE6.values():
        inventory = load(ROOT / relative_path)
        assert list(validator.iter_errors(inventory)) == []
        assert inventory["phase"] == 14
        assert inventory["status"] == "source_inventory_complete"
        assert inventory["review_status"] == "indexed_not_reviewed"
        assert len(inventory["sources"]) >= 4


def test_phase14_wave6_identity_and_roles_match_target_registry():
    registry = load(REGISTRY)
    targets = {
        row["official_code"]: row
        for row in registry["targets"]
        if row["wave"] == 6
    }

    assert set(targets) == set(WAVE6)
    for official_code, relative_path in WAVE6.items():
        inventory = load(ROOT / relative_path)
        target = targets[official_code]

        assert target["status"] == "source_inventory_complete"
        assert inventory["official_code"] == official_code
        assert inventory["standard_area_code"] == target["standard_area_code"]
        assert inventory["name_ja"] == target["name_ja"]
        assert inventory["prefecture_name_ja"] == target["prefecture_name_ja"]

        expected_roles = set()
        if target["core_city"]:
            expected_roles.add("core_city")
        if target["prefectural_capital"]:
            expected_roles.add("prefectural_capital")
        assert set(inventory["roles"]) == expected_roles


def test_phase14_wave6_sources_preserve_required_evidence_layers():
    for relative_path in WAVE6.values():
        inventory = load(ROOT / relative_path)
        layers = {source["layer"] for source in inventory["sources"]}

        assert any("plan" in layer for layer in layers)
        assert any(
            "implementation" in layer
            or "progress" in layer
            or "evaluation" in layer
            or "governance" in layer
            for layer in layers
        )
        assert "budget" in layers
        assert any("settlement" in layer for layer in layers)


def test_phase14_wave6_uses_only_official_municipal_sources():
    allowed_hosts = {
        "www.city.tottori.lg.jp",
        "www.city.matsue.lg.jp",
        "www.city.kurashiki.okayama.jp",
        "www.city.kure.lg.jp",
        "www.city.fukuyama.hiroshima.jp",
        "www.city.shimonoseki.lg.jp",
        "www.city.yamaguchi.lg.jp",
    }

    for relative_path in WAVE6.values():
        inventory = load(ROOT / relative_path)
        for source in inventory["sources"]:
            url = source["official_url"]
            assert url.startswith("https://")
            assert any(url.startswith(f"https://{host}/") for host in allowed_hosts)


def test_phase14_wave6_preserves_plan_transition_and_budget_boundaries():
    tottori = load(ROOT / WAVE6["312010"])
    kure = load(ROOT / WAVE6["342025"])
    fukuyama = load(ROOT / WAVE6["342076"])
    shimonoseki = load(ROOT / WAVE6["352012"])
    yamaguchi = load(ROOT / WAVE6["352039"])

    assert tottori["plan_period"]["start_fiscal_year"] == 2026
    assert "proposal" in tottori["quality_boundary"]

    assert kure["plan_period"]["start_fiscal_year"] == 2026
    assert "FY2024" in kure["availability_boundary"]

    assert fukuyama["plan_period"]["start_fiscal_year"] == 2026
    assert "第2期" in fukuyama["availability_boundary"]

    assert shimonoseki["plan_period"]["start_fiscal_year"] == 2025
    assert "2回改定" in shimonoseki["availability_boundary"]

    assert yamaguchi["roles"] == ["prefectural_capital"]
    assert yamaguchi["plan_period"]["period_status"] == "transition_or_unresolved"
    assert "2028年度" in yamaguchi["availability_boundary"]


def test_phase14_wave6_keeps_source_reported_evaluation_non_evaluative():
    matsue = load(ROOT / WAVE6["322016"])
    kurashiki = load(ROOT / WAVE6["332020"])
    yamaguchi = load(ROOT / WAVE6["352039"])

    assert "独自" in matsue["sources"][1]["review_boundary"]
    assert "独自" in kurashiki["sources"][1]["review_boundary"]
    assert "独自" in yamaguchi["sources"][2]["review_boundary"]


def test_phase14_wave6_does_not_claim_record_level_review():
    forbidden_statuses = {"reviewed", "reviewed_complete", "linked", "published"}

    for relative_path in WAVE6.values():
        inventory = load(ROOT / relative_path)
        assert inventory["review_status"] == "indexed_not_reviewed"
        assert inventory["status"] not in forbidden_statuses
        assert "Phase 15" in inventory["next_action"]
