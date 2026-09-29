from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
INVENTORY_SCHEMA = ROOT / "schemas/phase14_municipality_source_inventory.schema.json"
REGISTRY = ROOT / "data/catalog/phase14_core_capital_target_registry.json"

WAVE5 = {
    "252018": "data/indexed/otsu-city/source_inventory.json",
    "272035": "data/indexed/toyonaka-city/source_inventory.json",
    "272051": "data/indexed/suita-city/source_inventory.json",
    "272078": "data/indexed/takatsuki-city/source_inventory.json",
    "272108": "data/indexed/hirakata-city/source_inventory.json",
    "272124": "data/indexed/yao-city/source_inventory.json",
    "272159": "data/indexed/neyagawa-city/source_inventory.json",
    "272272": "data/indexed/higashiosaka-city/source_inventory.json",
    "282014": "data/indexed/himeji-city/source_inventory.json",
    "282022": "data/indexed/amagasaki-city/source_inventory.json",
    "282030": "data/indexed/akashi-city/source_inventory.json",
    "282049": "data/indexed/nishinomiya-city/source_inventory.json",
    "292010": "data/indexed/nara-city/source_inventory.json",
    "302015": "data/indexed/wakayama-city/source_inventory.json",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_phase14_wave5_has_fourteen_schema_valid_source_inventories():
    schema = load(INVENTORY_SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    assert len(WAVE5) == 14
    for relative_path in WAVE5.values():
        inventory = load(ROOT / relative_path)
        assert list(validator.iter_errors(inventory)) == []
        assert inventory["phase"] == 14
        assert inventory["status"] == "source_inventory_complete"
        assert inventory["review_status"] == "indexed_not_reviewed"
        assert len(inventory["sources"]) >= 4


def test_phase14_wave5_identity_and_roles_match_target_registry():
    registry = load(REGISTRY)
    targets = {
        row["official_code"]: row
        for row in registry["targets"]
        if row["wave"] == 5
    }

    assert set(targets) == set(WAVE5)
    for official_code, relative_path in WAVE5.items():
        inventory = load(ROOT / relative_path)
        target = targets[official_code]

        assert target["status"] == "source_inventory_complete"
        assert inventory["official_code"] == official_code
        assert inventory["standard_area_code"] == target["standard_area_code"]
        assert inventory["name_ja"] == target["name_ja"]
        assert inventory["prefecture_name_ja"] == target["prefecture_name_ja"]
        assert inventory["municipality_type"] == target["municipality_type"]

        expected_roles = {"core_city"}
        if target["prefectural_capital"]:
            expected_roles.add("prefectural_capital")
        assert set(inventory["roles"]) == expected_roles


def test_phase14_wave5_sources_preserve_required_evidence_layers():
    for relative_path in WAVE5.values():
        inventory = load(ROOT / relative_path)
        layers = {source["layer"] for source in inventory["sources"]}

        assert any(
            "plan" in layer
            or "framework" in layer
            for layer in layers
        )
        assert any(
            "implementation" in layer
            or "progress" in layer
            or "evaluation" in layer
            or "transition" in layer
            for layer in layers
        )
        assert "budget" in layers
        assert any("settlement" in layer for layer in layers)


def test_phase14_wave5_uses_only_official_municipal_sources():
    allowed_hosts = {
        "www.city.otsu.lg.jp",
        "www.city.toyonaka.osaka.jp",
        "www.city.suita.osaka.jp",
        "www.city.takatsuki.osaka.jp",
        "www.city.hirakata.osaka.jp",
        "www.city.yao.osaka.jp",
        "www.city.neyagawa.osaka.jp",
        "www.city.higashiosaka.lg.jp",
        "www.city.himeji.lg.jp",
        "www.city.amagasaki.hyogo.jp",
        "www.city.akashi.lg.jp",
        "www.nishi.or.jp",
        "www.city.nara.lg.jp",
        "www.city.wakayama.wakayama.jp",
    }

    for relative_path in WAVE5.values():
        inventory = load(ROOT / relative_path)
        for source in inventory["sources"]:
            url = source["official_url"]
            assert url.startswith("https://")
            assert any(url.startswith(f"https://{host}/") for host in allowed_hosts)


def test_phase14_wave5_preserves_nonstandard_period_boundaries():
    suita = load(ROOT / WAVE5["272051"])
    hirakata = load(ROOT / WAVE5["272108"])
    nara = load(ROOT / WAVE5["292010"])
    wakayama = load(ROOT / WAVE5["302015"])

    assert suita["plan_period"]["end_fiscal_year"] == 2028
    assert "2030年度" in suita["availability_boundary"]

    assert hirakata["plan_period"]["period_status"] == "verified_no_fixed_end"
    assert hirakata["plan_period"]["end_fiscal_year"] is None
    assert "固定終期" in hirakata["availability_boundary"]

    assert nara["plan_period"]["start_fiscal_year"] == 2022
    assert nara["plan_period"]["end_fiscal_year"] == 2031
    assert "後期推進方針" in nara["availability_boundary"]

    assert wakayama["plan_period"]["period_status"] == "transition_or_unresolved"
    assert wakayama["plan_period"]["end_fiscal_year"] == 2026


def test_phase14_wave5_preserves_old_current_and_accountability_boundaries():
    yao = load(ROOT / WAVE5["272124"])
    amagasaki = load(ROOT / WAVE5["282022"])
    akashi = load(ROOT / WAVE5["282030"])

    assert "FY2024" in yao["availability_boundary"]
    assert "前期" in yao["availability_boundary"]

    assert "後期基本計画" in amagasaki["availability_boundary"]
    assert "version" in amagasaki["availability_boundary"]

    assert "前期戦略" in akashi["availability_boundary"]
    assert "後期戦略" in akashi["availability_boundary"]


def test_phase14_wave5_does_not_claim_record_level_review():
    forbidden_statuses = {"reviewed", "reviewed_complete", "linked", "published"}

    for relative_path in WAVE5.values():
        inventory = load(ROOT / relative_path)
        assert inventory["review_status"] == "indexed_not_reviewed"
        assert inventory["status"] not in forbidden_statuses
        assert "Phase 15" in inventory["next_action"]
