from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
INVENTORY_SCHEMA = ROOT / "schemas/phase14_municipality_source_inventory.schema.json"
REGISTRY = ROOT / "data/catalog/phase14_core_capital_target_registry.json"

WAVE8 = {
    "402036": "data/indexed/kurume-city/source_inventory.json",
    "412015": "data/indexed/saga-city/source_inventory.json",
    "422010": "data/indexed/nagasaki-city/source_inventory.json",
    "422029": "data/indexed/sasebo-city/source_inventory.json",
    "442011": "data/indexed/oita-city/source_inventory.json",
    "452017": "data/indexed/miyazaki-city/source_inventory.json",
    "462012": "data/indexed/kagoshima-city/source_inventory.json",
    "472018": "data/indexed/naha-city/source_inventory.json",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_phase14_wave8_has_eight_schema_valid_source_inventories():
    schema = load(INVENTORY_SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    assert len(WAVE8) == 8
    for relative_path in WAVE8.values():
        inventory = load(ROOT / relative_path)
        assert list(validator.iter_errors(inventory)) == []
        assert inventory["phase"] == 14
        assert inventory["status"] == "source_inventory_complete"
        assert inventory["review_status"] == "indexed_not_reviewed"
        assert len(inventory["sources"]) >= 4


def test_phase14_wave8_identity_and_roles_match_target_registry():
    registry = load(REGISTRY)
    targets = {
        row["official_code"]: row
        for row in registry["targets"]
        if row["wave"] == 8
    }

    assert set(targets) == set(WAVE8)
    for official_code, relative_path in WAVE8.items():
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


def test_phase14_wave8_sources_preserve_required_evidence_layers():
    for relative_path in WAVE8.values():
        inventory = load(ROOT / relative_path)
        layers = {source["layer"] for source in inventory["sources"]}

        assert any("plan" in layer for layer in layers)
        assert any(
            "implementation" in layer
            or "progress" in layer
            or "evaluation" in layer
            or "governance" in layer
            or "transition" in layer
            for layer in layers
        )
        assert "budget" in layers
        assert any("settlement" in layer for layer in layers)


def test_phase14_wave8_uses_only_official_municipal_sources():
    allowed_hosts = {
        "www.city.kurume.fukuoka.jp",
        "www.city.saga.lg.jp",
        "www.city.nagasaki.lg.jp",
        "www.city.sasebo.lg.jp",
        "www.city.oita.oita.jp",
        "www.city.miyazaki.miyazaki.jp",
        "www.city.kagoshima.lg.jp",
        "www.city.naha.okinawa.jp",
    }

    for relative_path in WAVE8.values():
        inventory = load(ROOT / relative_path)
        for source in inventory["sources"]:
            url = source["official_url"]
            assert url.startswith("https://")
            assert any(url.startswith(f"https://{host}/") for host in allowed_hosts)


def test_phase14_wave8_preserves_transition_and_prior_plan_boundaries():
    kurume = load(ROOT / WAVE8["402036"])
    saga = load(ROOT / WAVE8["412015"])
    nagasaki = load(ROOT / WAVE8["422010"])
    miyazaki = load(ROOT / WAVE8["452017"])
    kagoshima = load(ROOT / WAVE8["462012"])
    naha = load(ROOT / WAVE8["472018"])

    assert kurume["plan_period"]["start_fiscal_year"] == 2026
    assert "FY2024" in kurume["availability_boundary"]

    assert saga["roles"] == ["prefectural_capital"]
    assert saga["plan_period"]["end_fiscal_year"] == 2040

    assert nagasaki["plan_period"]["start_fiscal_year"] == 2026
    assert "未公表" in nagasaki["availability_boundary"]

    assert miyazaki["plan_period"]["start_fiscal_year"] == 2025
    assert "FY2024" in miyazaki["availability_boundary"]

    assert kagoshima["plan_period"]["period_status"] == "transition_or_unresolved"
    assert "FY2027" in kagoshima["availability_boundary"]

    assert naha["plan_period"]["period_status"] == "transition_or_unresolved"
    assert "2028年度" in naha["availability_boundary"]
    assert "第6次" in naha["availability_boundary"]


def test_phase14_wave8_keeps_source_reported_evaluation_non_evaluative():
    saga = load(ROOT / WAVE8["412015"])
    oita = load(ROOT / WAVE8["442011"])
    miyazaki = load(ROOT / WAVE8["452017"])

    assert "独自" in saga["sources"][2]["review_boundary"]
    assert "独自" in oita["sources"][1]["review_boundary"]
    assert "独自" in miyazaki["sources"][1]["review_boundary"]


def test_phase14_wave8_does_not_claim_record_level_review():
    forbidden_statuses = {"reviewed", "reviewed_complete", "linked", "published"}

    for relative_path in WAVE8.values():
        inventory = load(ROOT / relative_path)
        assert inventory["review_status"] == "indexed_not_reviewed"
        assert inventory["status"] not in forbidden_statuses
        assert "Phase 15" in inventory["next_action"]
