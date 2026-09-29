from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
INVENTORY_SCHEMA = ROOT / "schemas/phase14_municipality_source_inventory.schema.json"
REGISTRY = ROOT / "data/catalog/phase14_core_capital_target_registry.json"

WAVE2 = {
    "082015": "data/indexed/mito-city/source_inventory.json",
    "092010": "data/indexed/utsunomiya-city/source_inventory.json",
    "102016": "data/indexed/maebashi-city/source_inventory.json",
    "102024": "data/indexed/takasaki-city/source_inventory.json",
    "112011": "data/indexed/kawagoe-city/source_inventory.json",
    "112038": "data/indexed/kawaguchi-city/source_inventory.json",
    "112224": "data/indexed/koshigaya-city/source_inventory.json",
    "122041": "data/indexed/funabashi-city/source_inventory.json",
    "122173": "data/indexed/kashiwa-city/source_inventory.json",
    "131040": "data/indexed/shinjuku-city/source_inventory.json",
    "132012": "data/indexed/hachioji-city/source_inventory.json",
    "142018": "data/indexed/yokosuka-city/source_inventory.json",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_phase14_wave2_has_twelve_schema_valid_source_inventories():
    schema = load(INVENTORY_SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    assert len(WAVE2) == 12
    for relative_path in WAVE2.values():
        inventory = load(ROOT / relative_path)
        assert list(validator.iter_errors(inventory)) == []
        assert inventory["phase"] == 14
        assert inventory["status"] == "source_inventory_complete"
        assert inventory["review_status"] == "indexed_not_reviewed"
        assert len(inventory["sources"]) >= 4


def test_phase14_wave2_identity_and_roles_match_target_registry():
    registry = load(REGISTRY)
    targets = {
        row["official_code"]: row
        for row in registry["targets"]
        if row["wave"] == 2
    }

    assert set(targets) == set(WAVE2)
    for official_code, relative_path in WAVE2.items():
        inventory = load(ROOT / relative_path)
        target = targets[official_code]

        assert target["status"] == "source_inventory_complete"
        assert inventory["official_code"] == official_code
        assert inventory["standard_area_code"] == target["standard_area_code"]
        assert inventory["name_ja"] == target["name_ja"]
        assert inventory["prefecture_name_ja"] == target["prefecture_name_ja"]
        assert inventory["municipality_type"] == target["municipality_type"]

        expected_roles = set()
        if target["core_city"]:
            expected_roles.add("core_city")
        if target["prefectural_capital"]:
            expected_roles.add("prefectural_capital")
        assert set(inventory["roles"]) == expected_roles


def test_phase14_wave2_sources_preserve_required_evidence_layers():
    for relative_path in WAVE2.values():
        inventory = load(ROOT / relative_path)
        layers = {source["layer"] for source in inventory["sources"]}

        assert any("plan" in layer or "framework" in layer for layer in layers)
        assert any(
            "implementation" in layer
            or "progress" in layer
            or "annual" in layer
            for layer in layers
        )
        assert "budget" in layers
        assert any("settlement" in layer for layer in layers)


def test_phase14_wave2_uses_only_official_municipal_sources():
    allowed_hosts = {
        "www.city.mito.lg.jp",
        "www.city.utsunomiya.lg.jp",
        "www.city.maebashi.gunma.jp",
        "www.city.takasaki.gunma.jp",
        "www.city.kawagoe.saitama.jp",
        "www.city.kawaguchi.lg.jp",
        "www.city.koshigaya.saitama.jp",
        "www.city.funabashi.lg.jp",
        "www.city.kashiwa.lg.jp",
        "www.city.shinjuku.lg.jp",
        "www.city.hachioji.tokyo.jp",
        "www.city.yokosuka.kanagawa.jp",
    }

    for relative_path in WAVE2.values():
        inventory = load(ROOT / relative_path)
        for source in inventory["sources"]:
            url = source["official_url"]
            assert url.startswith("https://")
            assert any(url.startswith(f"https://{host}/") for host in allowed_hosts)


def test_phase14_wave2_preserves_special_and_transition_boundaries():
    takasaki = load(ROOT / WAVE2["102024"])
    shinjuku = load(ROOT / WAVE2["131040"])
    kawagoe = load(ROOT / WAVE2["112011"])
    kawaguchi = load(ROOT / WAVE2["112038"])
    koshigaya = load(ROOT / WAVE2["112224"])
    kashiwa = load(ROOT / WAVE2["122173"])

    assert takasaki["plan_period"]["period_status"] == "transition_or_unresolved"
    assert takasaki["plan_period"]["end_fiscal_year"] is None
    assert "推測" in takasaki["sources"][0]["review_boundary"]

    assert shinjuku["municipality_type"] == "special_ward"
    assert shinjuku["roles"] == ["prefectural_capital"]
    assert "特別区" in shinjuku["availability_boundary"]

    for inventory in (kawagoe, kawaguchi, koshigaya, kashiwa):
        assert "FY2024" in inventory["availability_boundary"]
        assert (
            "旧計画" in inventory["availability_boundary"]
            or "前期計画" in inventory["availability_boundary"]
        )


def test_phase14_wave2_does_not_claim_record_level_review():
    forbidden_statuses = {"reviewed", "reviewed_complete", "linked", "published"}

    for relative_path in WAVE2.values():
        inventory = load(ROOT / relative_path)
        assert inventory["review_status"] == "indexed_not_reviewed"
        assert inventory["status"] not in forbidden_statuses
        assert "Phase 15" in inventory["next_action"]
