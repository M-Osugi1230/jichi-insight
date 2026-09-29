from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
INVENTORY_SCHEMA = ROOT / "schemas/phase14_municipality_source_inventory.schema.json"
REGISTRY = ROOT / "data/catalog/phase14_core_capital_target_registry.json"

WAVE4 = {
    "212016": "data/indexed/gifu-city/source_inventory.json",
    "232017": "data/indexed/toyohashi-city/source_inventory.json",
    "232025": "data/indexed/okazaki-city/source_inventory.json",
    "232033": "data/indexed/ichinomiya-city/source_inventory.json",
    "232114": "data/indexed/toyota-city/source_inventory.json",
    "242012": "data/indexed/tsu-city/source_inventory.json",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_phase14_wave4_has_six_schema_valid_source_inventories():
    schema = load(INVENTORY_SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    assert len(WAVE4) == 6
    for relative_path in WAVE4.values():
        inventory = load(ROOT / relative_path)
        assert list(validator.iter_errors(inventory)) == []
        assert inventory["phase"] == 14
        assert inventory["status"] == "source_inventory_complete"
        assert inventory["review_status"] == "indexed_not_reviewed"
        assert len(inventory["sources"]) >= 4


def test_phase14_wave4_identity_and_roles_match_target_registry():
    registry = load(REGISTRY)
    targets = {
        row["official_code"]: row
        for row in registry["targets"]
        if row["wave"] == 4
    }

    assert set(targets) == set(WAVE4)
    for official_code, relative_path in WAVE4.items():
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


def test_phase14_wave4_sources_preserve_required_evidence_layers():
    for relative_path in WAVE4.values():
        inventory = load(ROOT / relative_path)
        layers = {source["layer"] for source in inventory["sources"]}

        assert any(
            "plan" in layer
            or "framework" in layer
            or "policy" in layer
            for layer in layers
        )
        assert any(
            "implementation" in layer
            or "progress" in layer
            or "annual" in layer
            for layer in layers
        )
        assert "budget" in layers
        assert any("settlement" in layer for layer in layers)


def test_phase14_wave4_uses_only_official_municipal_sources():
    allowed_hosts = {
        "www.city.gifu.lg.jp",
        "www.city.toyohashi.lg.jp",
        "www.city.okazaki.lg.jp",
        "www.city.ichinomiya.aichi.jp",
        "www.city.toyota.aichi.jp",
        "www.info.city.tsu.mie.jp",
    }

    for relative_path in WAVE4.values():
        inventory = load(ROOT / relative_path)
        for source in inventory["sources"]:
            url = source["official_url"]
            assert url.startswith("https://")
            assert any(url.startswith(f"https://{host}/") for host in allowed_hosts)


def test_phase14_wave4_preserves_nonstandard_and_transition_boundaries():
    gifu = load(ROOT / WAVE4["212016"])
    toyohashi = load(ROOT / WAVE4["232017"])
    okazaki = load(ROOT / WAVE4["232025"])
    ichinomiya = load(ROOT / WAVE4["232033"])
    tsu = load(ROOT / WAVE4["242012"])

    assert gifu["plan_period"]["end_fiscal_year"] is None
    assert gifu["plan_period"]["period_status"] == "transition_or_unresolved"
    assert "推測" in gifu["sources"][0]["review_boundary"]

    assert toyohashi["plan_period"]["start_fiscal_year"] == 2026
    assert toyohashi["plan_period"]["end_fiscal_year"] == 2030
    assert "FY2024" in toyohashi["availability_boundary"]

    assert okazaki["plan_period"]["start_fiscal_year"] == 2026
    assert "FY2024" in okazaki["availability_boundary"]

    assert ichinomiya["plan_period"]["period_status"] == "transition_or_unresolved"
    assert "第8次" in ichinomiya["availability_boundary"]

    assert tsu["roles"] == ["prefectural_capital"]
    assert "期間を定めない基本構想" in tsu["availability_boundary"]


def test_phase14_wave4_keeps_source_reported_evaluation_non_evaluative():
    ichinomiya = load(ROOT / WAVE4["232033"])
    toyota = load(ROOT / WAVE4["232114"])
    tsu = load(ROOT / WAVE4["242012"])

    assert "独自達成率" in ichinomiya["sources"][2]["review_boundary"]
    assert "独自達成評価" in toyota["sources"][1]["review_boundary"]
    assert "独自達成判定" in tsu["sources"][1]["review_boundary"]


def test_phase14_wave4_does_not_claim_record_level_review():
    forbidden_statuses = {"reviewed", "reviewed_complete", "linked", "published"}

    for relative_path in WAVE4.values():
        inventory = load(ROOT / relative_path)
        assert inventory["review_status"] == "indexed_not_reviewed"
        assert inventory["status"] not in forbidden_statuses
        assert "Phase 15" in inventory["next_action"]
