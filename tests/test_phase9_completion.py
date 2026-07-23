import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data/catalog/phase9_completion.json"
SCHEMA_PATH = ROOT / "schemas/phase9_completion.schema.json"
COVERAGE_PATH = ROOT / "data/catalog/prefecture_coverage.json"
ANCHOR_PATH = ROOT / "data/catalog/regional_anchor_source_registry.json"
QUEUE_PATH = ROOT / "data/catalog/phase9_execution_queue.json"
SUMMARY_PATH = ROOT / "data/catalog/phase9_review_summary.json"


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
    summary = load(SUMMARY_PATH)
    anchor_numeric_indexed = sum(
        record["numeric_target_status"] in {"indexed", "reviewed"}
        for record in anchors
    )
    phase9_indexed = sum(
        item["numeric_target_status"] in {"indexed", "reviewed"} for item in queue
    )
    phase9_reviewed = sum(
        item["numeric_target_status"] == "reviewed" for item in queue
    )

    assert summary["prefecture_count"] == phase9_reviewed == 38
    assert manifest["counts"] == {
        "total_prefectures": len(coverage["records"]),
        "major_policy_plans_indexed": len(coverage["plan_entry_indexed_codes"]),
        "numeric_target_entrances_indexed_or_reviewed": anchor_numeric_indexed
        + phase9_indexed,
        "evidence_backed_reviewed_prefectures": len(coverage["reviewed_prefecture_codes"]),
        "remaining_phase9_prefectures": len(queue),
        "phase9_prefectures_with_numeric_targets_indexed": phase9_indexed,
        "phase9_prefectures_with_reviewed_numeric_targets": phase9_reviewed,
    }


def test_phase9_is_complete_only_after_all_evidence_and_publication_gates_pass():
    manifest = load(MANIFEST_PATH)
    gates = {gate["id"]: gate["status"] for gate in manifest["gates"]}
    assert manifest["status"] == "complete"
    assert manifest["counts"] == {
        "total_prefectures": 47,
        "major_policy_plans_indexed": 47,
        "numeric_target_entrances_indexed_or_reviewed": 47,
        "evidence_backed_reviewed_prefectures": 47,
        "remaining_phase9_prefectures": 38,
        "phase9_prefectures_with_numeric_targets_indexed": 38,
        "phase9_prefectures_with_reviewed_numeric_targets": 38,
    }
    assert set(gates.values()) == {"passed"}
    assert gates["all_major_policy_plans_indexed"] == "passed"
    assert gates["all_major_numeric_targets_indexed"] == "passed"
    assert gates["published_numeric_evidence_coverage"] == "passed"
    assert gates["semantic_quality_tests"] == "passed"
    assert gates["plan_revision_and_history_tracking"] == "passed"
    assert gates["incomparable_ranking_exclusion"] == "passed"
    assert gates["nationwide_publication_and_smoke"] == "passed"


def test_phase9_manifest_evidence_paths_exist():
    for gate in load(MANIFEST_PATH)["gates"]:
        for path in gate["evidence_paths"]:
            assert (ROOT / path).is_file(), f"Missing Phase 9 evidence path: {path}"
