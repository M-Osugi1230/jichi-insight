from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
INVENTORY_SCHEMA = ROOT / "schemas/phase14_municipality_source_inventory.schema.json"
REGISTRY = ROOT / "data/catalog/phase14_core_capital_target_registry.json"

WAVE3 = {
    "162019": "data/indexed/toyama-city/source_inventory.json",
    "172014": "data/indexed/kanazawa-city/source_inventory.json",
    "182010": "data/indexed/fukui-city/source_inventory.json",
    "192015": "data/indexed/kofu-city/source_inventory.json",
    "202010": "data/indexed/nagano-city/source_inventory.json",
    "202029": "data/indexed/matsumoto-city/source_inventory.json",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_phase14_wave3_has_six_schema_valid_source_inventories():
    schema = load(INVENTORY_SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    assert len(WAVE3) == 6
    for relative_path in WAVE3.values():
        inventory = load(ROOT / relative_path)
        assert list(validator.iter_errors(inventory)) == []
        assert inventory["phase"] == 14
        assert inventory["status"] == "source_inventory_complete"
        assert inventory["review_status"] == "indexed_not_reviewed"
        assert len(inventory["sources"]) >= 4


def test_phase14_wave3_identity_and_roles_match_target_registry():
    registry = load(REGISTRY)
    targets = {
        row["official_code"]: row
        for row in registry["targets"]
        if row["wave"] == 3
    }

    assert set(targets) == set(WAVE3)
    for official_code, relative_path in WAVE3.items():
        inventory = load(ROOT / relative_path)
        target = targets[official_code]

        assert target["status"] == "source_inventory_complete"
        assert inventory["official_code"] == official_code
        assert inventory["standard_area_code"] == target["standard_area_code"]
        assert inventory["name_ja"] == target["name_ja"]
        assert inventory["prefecture_name_ja"] == target["prefecture_name_ja"]

        expected_roles = {"core_city"}
        if target["prefectural_capital"]:
            expected_roles.add("prefectural_capital")
        assert set(inventory["roles"]) == expected_roles


def test_phase14_wave3_sources_preserve_required_evidence_layers():
    for relative_path in WAVE3.values():
        inventory = load(ROOT / relative_path)
        layers = {source["layer"] for source in inventory["sources"]}

        assert any("plan" in layer for layer in layers)
        assert any(
            "implementation" in layer
            or "progress" in layer
            or "annual" in layer
            for layer in layers
        )
        assert "budget" in layers
        assert any("settlement" in layer for layer in layers)


def test_phase14_wave3_uses_only_official_municipal_sources():
    allowed_hosts = {
        "www.city.toyama.lg.jp",
        "www4.city.kanazawa.lg.jp",
        "www.city.fukui.lg.jp",
        "www.city.kofu.yamanashi.jp",
        "www.city.nagano.nagano.jp",
        "www.city.matsumoto.nagano.jp",
    }

    for relative_path in WAVE3.values():
        inventory = load(ROOT / relative_path)
        for source in inventory["sources"]:
            url = source["official_url"]
            assert url.startswith("https://")
            assert any(url.startswith(f"https://{host}/") for host in allowed_hosts)


def test_phase14_wave3_preserves_transition_and_new_plan_boundaries():
    toyama = load(ROOT / WAVE3["162019"])
    fukui = load(ROOT / WAVE3["182010"])
    kofu = load(ROOT / WAVE3["192015"])
    nagano = load(ROOT / WAVE3["202010"])
    matsumoto = load(ROOT / WAVE3["202029"])

    for inventory in (toyama, fukui, nagano):
        assert inventory["plan_period"]["period_status"] == "transition_or_unresolved"
        assert inventory["plan_period"]["end_fiscal_year"] == 2026

    assert kofu["plan_period"] == {
        "current_plan_name": "第七次甲府市総合計画",
        "start_fiscal_year": 2026,
        "end_fiscal_year": 2035,
        "period_status": "verified_fixed_period",
    }
    assert matsumoto["plan_period"]["start_fiscal_year"] == 2026
    assert matsumoto["plan_period"]["end_fiscal_year"] == 2030
    assert "FY2024" in kofu["availability_boundary"]
    assert "FY2024" in matsumoto["availability_boundary"]


def test_phase14_wave3_keeps_source_reported_progress_non_evaluative():
    kanazawa = load(ROOT / WAVE3["172014"])
    fukui = load(ROOT / WAVE3["182010"])
    nagano = load(ROOT / WAVE3["202010"])

    assert "独自政策達成" in kanazawa["sources"][1]["review_boundary"]
    assert "独自評価" in fukui["sources"][2]["review_boundary"]
    assert "独自評価" in nagano["sources"][1]["review_boundary"]


def test_phase14_wave3_does_not_claim_record_level_review():
    forbidden_statuses = {"reviewed", "reviewed_complete", "linked", "published"}

    for relative_path in WAVE3.values():
        inventory = load(ROOT / relative_path)
        assert inventory["review_status"] == "indexed_not_reviewed"
        assert inventory["status"] not in forbidden_statuses
        assert "Phase 15" in inventory["next_action"]
