from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
INVENTORY_SCHEMA = ROOT / "schemas/phase14_municipality_source_inventory.schema.json"
REGISTRY = ROOT / "data/catalog/phase14_core_capital_target_registry.json"

WAVE1 = {
    "012025": "data/indexed/hakodate-city/source_inventory.json",
    "012041": "data/indexed/asahikawa-city/source_inventory.json",
    "022012": "data/indexed/aomori-city/source_inventory.json",
    "022039": "data/indexed/hachinohe-city/source_inventory.json",
    "032018": "data/indexed/morioka-city/source_inventory.json",
    "052019": "data/indexed/akita-city/source_inventory.json",
    "062014": "data/indexed/yamagata-city/source_inventory.json",
    "072010": "data/indexed/fukushima-city/source_inventory.json",
    "072036": "data/indexed/koriyama-city/source_inventory.json",
    "072044": "data/indexed/iwaki-city/source_inventory.json",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_phase14_wave1_has_ten_schema_valid_source_inventories():
    schema = load(INVENTORY_SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    assert len(WAVE1) == 10
    for relative_path in WAVE1.values():
        inventory = load(ROOT / relative_path)
        assert list(validator.iter_errors(inventory)) == []
        assert inventory["phase"] == 14
        assert inventory["status"] == "source_inventory_complete"
        assert inventory["review_status"] == "indexed_not_reviewed"
        assert len(inventory["sources"]) >= 4


def test_phase14_wave1_identity_matches_target_registry():
    registry = load(REGISTRY)
    targets = {
        row["official_code"]: row
        for row in registry["targets"]
        if row["wave"] == 1
    }

    assert set(targets) == set(WAVE1)
    for official_code, relative_path in WAVE1.items():
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


def test_phase14_wave1_sources_preserve_required_evidence_layers():
    for relative_path in WAVE1.values():
        inventory = load(ROOT / relative_path)
        layers = {source["layer"] for source in inventory["sources"]}

        assert any("plan" in layer or "policy" in layer for layer in layers)
        assert any(
            "implementation" in layer
            or "progress" in layer
            or "annual" in layer
            for layer in layers
        )
        assert "budget" in layers or "budget_document" in layers
        assert any("settlement" in layer for layer in layers)


def test_phase14_wave1_uses_only_official_municipal_sources():
    allowed_hosts = {
        "www.city.hakodate.hokkaido.jp",
        "www.city.asahikawa.hokkaido.jp",
        "www.city.aomori.aomori.jp",
        "www.city.hachinohe.aomori.jp",
        "www.city.morioka.iwate.jp",
        "www.city.akita.lg.jp",
        "www.city.yamagata-yamagata.lg.jp",
        "www.city.fukushima.fukushima.jp",
        "www.city.koriyama.lg.jp",
        "www.city.iwaki.lg.jp",
    }

    for relative_path in WAVE1.values():
        inventory = load(ROOT / relative_path)
        for source in inventory["sources"]:
            url = source["official_url"]
            assert url.startswith("https://")
            assert any(url.startswith(f"https://{host}/") for host in allowed_hosts)


def test_phase14_wave1_preserves_nonstandard_and_transition_boundaries():
    hakodate = load(ROOT / WAVE1["012025"])
    hachinohe = load(ROOT / WAVE1["022039"])
    fukushima = load(ROOT / WAVE1["072010"])
    iwaki = load(ROOT / WAVE1["072044"])

    for inventory in (hakodate, hachinohe, fukushima):
        assert inventory["plan_period"]["period_status"] == "transition_or_unresolved"
        assert "推測" in inventory["quality_boundary"] or "infer" in (
            inventory["quality_boundary"].lower()
        )

    assert iwaki["plan_period"]["period_status"] == "verified_no_fixed_end"
    assert iwaki["plan_period"]["start_fiscal_year"] is None
    assert iwaki["plan_period"]["end_fiscal_year"] is None
    assert "固定終期" in iwaki["availability_boundary"]


def test_phase14_wave1_does_not_claim_record_level_review():
    forbidden_statuses = {"reviewed", "reviewed_complete", "linked", "published"}

    for relative_path in WAVE1.values():
        inventory = load(ROOT / relative_path)
        assert inventory["review_status"] == "indexed_not_reviewed"
        assert inventory["status"] not in forbidden_statuses
        assert "Phase 15" in inventory["next_action"]
