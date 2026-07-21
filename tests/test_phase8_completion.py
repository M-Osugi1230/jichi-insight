import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data/catalog/phase8_completion.json"
SCHEMA_PATH = ROOT / "schemas/phase8_completion.schema.json"
ANCHOR_PATH = ROOT / "data/catalog/regional_anchor_source_registry.json"
PUBLISHED_PATH = ROOT / "data/catalog/published_prefecture_pages.json"
TOKYO_MANIFEST_PATH = ROOT / "data/catalog/tokyo_policy_target_review_manifest.json"
AICHI_MANIFEST_PATH = ROOT / "data/catalog/aichi_policy_indicator_review_manifest.json"
OSAKA_MANIFEST_PATH = ROOT / "data/catalog/osaka_beyond_expo_indicator_review_manifest.json"
HIROSHIMA_MANIFEST_PATH = (
    ROOT / "data/catalog/hiroshima_revised_vision_indicator_review_manifest.json"
)
KAGAWA_MANIFEST_PATH = (
    ROOT / "data/catalog/kagawa_extended_plan_indicator_review_manifest.json"
)
OKINAWA_MANIFEST_PATH = ROOT / "data/catalog/okinawa_midterm_indicator_review_manifest.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_phase8_manifest_matches_schema():
    validator = Draft202012Validator(load(SCHEMA_PATH), format_checker=FormatChecker())
    assert list(validator.iter_errors(load(MANIFEST_PATH))) == []


def test_phase8_counts_are_derived_from_canonical_registries():
    manifest = load(MANIFEST_PATH)
    anchors = load(ANCHOR_PATH)["records"]
    published_codes = {
        record["prefecture_code"] for record in load(PUBLISHED_PATH)["records"]
    }
    anchor_codes = {record["prefecture_code"] for record in anchors}
    reviewed_codes = {
        record["prefecture_code"]
        for record in anchors
        if record["numeric_target_status"] == "reviewed"
    }
    if load(TOKYO_MANIFEST_PATH)["reviewed_target_group_count"] > 0:
        reviewed_codes.add("13")
    if load(AICHI_MANIFEST_PATH)["status"] == "complete":
        reviewed_codes.add("23")
    if load(OSAKA_MANIFEST_PATH)["status"] == "complete":
        reviewed_codes.add("27")
    if load(HIROSHIMA_MANIFEST_PATH)["status"] == "complete":
        reviewed_codes.add("34")
    if load(KAGAWA_MANIFEST_PATH)["status"] == "complete":
        reviewed_codes.add("37")
    if load(OKINAWA_MANIFEST_PATH)["status"] == "complete":
        reviewed_codes.add("47")
    source_mapped = sum(len(record["sources"]) == 6 for record in anchors)
    published = len(anchor_codes & published_codes)
    assert manifest["counts"] == {
        "regional_anchors": 9,
        "anchors_with_plan_and_kpi_entrances": 9,
        "anchors_with_six_category_source_map": source_mapped,
        "anchors_with_reviewed_numeric_targets": len(reviewed_codes),
        "anchors_with_published_prefecture_pages": published,
        "anchors_pending_numeric_target_review": 9 - len(reviewed_codes),
    }


def test_phase8_is_complete_only_after_all_review_and_publication_gates_pass():
    manifest = load(MANIFEST_PATH)
    gates = {gate["id"]: gate["status"] for gate in manifest["gates"]}
    assert manifest["status"] == "complete"
    assert manifest["counts"] == {
        "regional_anchors": 9,
        "anchors_with_plan_and_kpi_entrances": 9,
        "anchors_with_six_category_source_map": 6,
        "anchors_with_reviewed_numeric_targets": 9,
        "anchors_with_published_prefecture_pages": 9,
        "anchors_pending_numeric_target_review": 0,
    }
    assert set(gates.values()) == {"passed"}
    assert manifest["next_review_order"] == []


def test_phase8_evidence_paths_are_real_files():
    for gate in load(MANIFEST_PATH)["gates"]:
        for path in gate["evidence_paths"]:
            assert (ROOT / path).is_file(), f"Missing Phase 8 evidence path: {path}"
