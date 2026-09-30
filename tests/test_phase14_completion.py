from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/phase14_completion.json"
COMPLETION_SCHEMA = ROOT / "schemas/phase14_completion.schema.json"
REGISTRY = ROOT / "data/catalog/phase14_core_capital_target_registry.json"
QUEUE = ROOT / "data/catalog/phase14_core_capital_execution_queue.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_phase14_completion_manifest_validates():
    completion = load(COMPLETION)
    validator = Draft202012Validator(
        load(COMPLETION_SCHEMA), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(completion)) == []


def test_phase14_completion_matches_canonical_registry_and_queue():
    completion = load(COMPLETION)
    registry = load(REGISTRY)
    queue = load(QUEUE)

    assert completion["status"] == queue["status"] == "complete"
    assert len(registry["targets"]) == 67
    assert all(
        row["status"] == "source_inventory_complete"
        for row in registry["targets"]
    )
    assert queue["summary"]["source_inventory_complete_count"] == 67
    assert queue["summary"]["source_inventory_in_progress_count"] == 0
    assert queue["summary"]["pending_source_inventory_count"] == 0
    assert queue["summary"]["next_official_code"] is None

    assert completion["coverage"] == {
        "unique_target_count": 67,
        "core_city_count": 62,
        "remaining_prefectural_capital_count": 32,
        "core_city_and_prefectural_capital_overlap": 27,
        "prefectural_capital_only_count": 5,
        "source_inventory_complete_count": 67,
        "source_inventory_in_progress_count": 0,
        "pending_source_inventory_count": 0,
        "reviewed_promotion_count": 0,
        "phase13_overlap_count": 0,
    }


def test_phase14_all_eight_waves_are_complete_and_cover_67_targets():
    completion = load(COMPLETION)
    queue = load(QUEUE)

    assert [row["target_count"] for row in completion["wave_completions"]] == [
        10,
        12,
        6,
        6,
        14,
        7,
        4,
        8,
    ]
    assert sum(row["target_count"] for row in completion["wave_completions"]) == 67
    assert all(row["status"] == "complete" for row in completion["wave_completions"])

    assert len(queue["waves"]) == 8
    assert all(row["status"] == "complete" for row in queue["waves"])
    assert all(row["pending_count"] == 0 for row in queue["waves"])
    assert all(
        row["source_inventory_in_progress_count"] == 0 for row in queue["waves"]
    )
    assert sum(row["source_inventory_complete_count"] for row in queue["waves"]) == 67


def test_phase14_wave_regression_files_exist():
    completion = load(COMPLETION)
    wave_tests = {row["test_path"] for row in completion["wave_completions"]}

    assert len(wave_tests) == 8
    for path in wave_tests:
        assert (ROOT / path).is_file(), path


def test_phase14_completion_keeps_source_inventory_out_of_reviewed_state():
    completion = load(COMPLETION)
    registry = load(REGISTRY)
    quality = completion["quality_summary"]

    assert quality == {
        "policy_achievement_assessment_count": 0,
        "causal_attribution_count": 0,
        "cross_city_ranking_count": 0,
        "inferred_missing_evidence_count": 0,
        "reviewed_promotion_count": 0,
    }
    assert all(
        row["status"] == "source_inventory_complete"
        for row in registry["targets"]
    )

    boundary = completion["completion_boundary"]
    assert "indexed_not_reviewed" in boundary
    assert "does not mean that individual policies" in boundary
    assert "not-yet-published" in boundary
    assert "No independent Jichi Insight policy-achievement judgment" in boundary
    assert "causal attribution" in boundary
    assert "cross-city comparison" in boundary


def test_phase14_canonical_sources_exist():
    completion = load(COMPLETION)
    for path in completion["canonical_sources"]:
        assert (ROOT / path).exists(), path
