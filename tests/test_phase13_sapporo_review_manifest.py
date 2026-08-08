from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data/catalog/phase13_sapporo_review_manifest.json"
SCHEMA_PATH = ROOT / "schemas/phase13_sapporo_review_manifest.schema.json"
SOURCE_INVENTORY_PATH = ROOT / "data/indexed/sapporo-city/source_inventory.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sapporo_phase13_manifest_matches_schema():
    validator = Draft202012Validator(
        load(SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(load(MANIFEST_PATH))) == []


def test_sapporo_review_packages_cover_phase12_source_roles_conservatively():
    manifest = load(MANIFEST_PATH)
    inventory = load(SOURCE_INVENTORY_PATH)
    source_ids = {source["id"] for source in inventory["sources"]}
    package_source_ids = {package["source_id"] for package in manifest["review_packages"]}
    assert package_source_ids <= source_ids
    assert {package["layer"] for package in manifest["review_packages"]} == {
        "comprehensive_plan",
        "implementation_plan",
        "annual_progress",
        "budget",
        "settlement",
    }


def test_sapporo_manifest_keeps_unverified_sources_blocked():
    manifest = load(MANIFEST_PATH)
    packages = {package["layer"]: package for package in manifest["review_packages"]}
    assert packages["implementation_plan"]["status"] == "blocked_source_verification"
    assert packages["settlement"]["status"] == "blocked_source_verification"
    assert manifest["summary"]["blocked_source_verification_count"] == 2
    assert manifest["summary"]["promotion_ready"] is False
    assert manifest["summary"]["reviewed_record_count"] == 0


def test_sapporo_manifest_does_not_infer_policy_achievement():
    manifest = load(MANIFEST_PATH)
    boundary = manifest["quality_boundary"].lower()
    assert "promotes no sapporo records to reviewed" in boundary
    assert "citizen-survey progress" in boundary
    assert "causal claim" in boundary
    assert "cross-city comparison" in boundary
    assert "policy-achievement judgment" in boundary
