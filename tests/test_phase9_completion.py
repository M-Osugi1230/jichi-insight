import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data/catalog/phase9_completion.json"
SCHEMA_PATH = ROOT / "schemas/phase9_completion.schema.json"
COVERAGE_PATH = ROOT / "data/catalog/prefecture_coverage.json"
ANCHOR_PATH = ROOT / "data/catalog/regional_anchor_source_registry.json"
QUEUE_PATH = ROOT / "data/catalog/phase9_execution_queue.json"
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


def test_phase9_manifest_matches_schema():
    validator = Draft202012Validator(load(SCHEMA_PATH), format_checker=FormatChecker())
    assert list(validator.iter_errors(load(MANIFEST_PATH))) == []


def test_phase9_counts_are_derived_from_current_registries():
    manifest = load(MANIFEST_PATH)
    coverage = load(COVERAGE_PATH)
    anchors = load(ANCHOR_PATH)["records"]
    queue = load(QUEUE_PATH)["items"]
    anchor_numeric_indexed = sum(
        record["numeric_target_status"] in {"indexed", "reviewed"}
        for record in anchors
    )
    anchor_reviewed_codes = {
        record["prefecture_code"]
        for record in anchors
        if record["numeric_target_status"] == "reviewed"
    }
    if load(TOKYO_MANIFEST_PATH)["reviewed_target_group_count"] > 0:
        anchor_reviewed_codes.add("13")
    if load(AICHI_MANIFEST_PATH)["status"] == "complete":
        anchor_reviewed_codes.add("23")
    if load(OSAKA_MANIFEST_PATH)["status"] == "complete":
        anchor_reviewed_codes.add("27")
    if load(HIROSHIMA_MANIFEST_PATH)["status"] == "complete":
        anchor_reviewed_codes.add("34")
    if load(KAGAWA_MANIFEST_PATH)["status"] == "complete":
        anchor_reviewed_codes.add("37")
    if load(OKINAWA_MANIFEST_PATH)["status"] == "complete":
        anchor_reviewed_codes.add("47")
    phase9_indexed = sum(
        item["numeric_target_status"] in {"indexed", "reviewed"} for item in queue
    )
    phase9_reviewed = sum(
        item["numeric_target_status"] == "reviewed" for item in queue
    )
    assert manifest["counts"] == {
        "total_prefectures": len(coverage["records"]),
        "major_policy_plans_indexed": len(coverage["plan_entry_indexed_codes"]),
        "numeric_target_entrances_indexed_or_reviewed": anchor_numeric_indexed
        + phase9_indexed,
        "evidence_backed_reviewed_prefectures": len(anchor_reviewed_codes)
        + phase9_reviewed,
        "remaining_phase9_prefectures": len(queue),
        "phase9_prefectures_with_numeric_targets_indexed": phase9_indexed,
        "phase9_prefectures_with_reviewed_numeric_targets": phase9_reviewed,
    }


def test_phase9_stays_in_progress_until_nationwide_evidence_gates_pass():
    manifest = load(MANIFEST_PATH)
    gates = {gate["id"]: gate["status"] for gate in manifest["gates"]}
    assert manifest["status"] == "in_progress"
    assert manifest["counts"]["major_policy_plans_indexed"] == 47
    assert manifest["counts"]["numeric_target_entrances_indexed_or_reviewed"] == 47
    assert manifest["counts"]["evidence_backed_reviewed_prefectures"] == 9
    assert manifest["counts"]["phase9_prefectures_with_numeric_targets_indexed"] == 38
    assert manifest["counts"]["phase9_prefectures_with_reviewed_numeric_targets"] == 0
    assert gates["all_major_policy_plans_indexed"] == "passed"
    assert gates["all_major_numeric_targets_indexed"] == "passed"
    assert gates["published_numeric_evidence_coverage"] == "in_progress"
    assert gates["incomparable_ranking_exclusion"] == "passed"
    assert not all(status == "passed" for status in gates.values())


def test_phase9_manifest_evidence_paths_exist():
    for gate in load(MANIFEST_PATH)["gates"]:
        for path in gate["evidence_paths"]:
            assert (ROOT / path).is_file(), f"Missing Phase 9 evidence path: {path}"
