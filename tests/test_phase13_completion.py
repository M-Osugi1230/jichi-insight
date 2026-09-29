from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/phase13_completion.json"
COMPLETION_SCHEMA = ROOT / "schemas/phase13_completion.schema.json"
QUEUE = ROOT / "data/catalog/phase13_designated_city_review_queue.json"
QUEUE_SCHEMA = ROOT / "schemas/phase13_designated_city_review_queue.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_phase13_completion_and_queue_validate():
    completion = load(COMPLETION)
    queue = load(QUEUE)
    assert list(
        Draft202012Validator(
            load(COMPLETION_SCHEMA), format_checker=FormatChecker()
        ).iter_errors(completion)
    ) == []
    assert list(
        Draft202012Validator(
            load(QUEUE_SCHEMA), format_checker=FormatChecker()
        ).iter_errors(queue)
    ) == []


def test_phase13_has_full_designated_city_coverage():
    completion = load(COMPLETION)
    queue = load(QUEUE)

    assert completion["status"] == queue["status"] == "complete"
    assert completion["coverage"] == {
        "designated_city_count": 20,
        "reviewed_reference_count": 2,
        "execution_reviewed_complete_count": 18,
        "review_in_progress_count": 0,
        "pending_record_review_count": 0,
        "blocked_source_inventory_count": 0,
    }
    assert all(row["status"] == "reviewed_complete" for row in queue["execution_queue"])
    assert queue["summary"]["reviewed_complete_count"] == 18
    assert queue["summary"]["review_in_progress_count"] == 0
    assert queue["summary"]["pending_record_review_count"] == 0
    assert queue["summary"]["next_official_code"] is None


def test_phase13_reference_and_completion_codes_cover_twenty_unique_cities():
    completion = load(COMPLETION)
    reference_codes = {
        row["official_code"] for row in completion["reference_implementations"]
    }
    completion_codes = {
        row["official_code"] for row in completion["reviewed_completion_contracts"]
    }

    assert reference_codes == {"401005", "401307"}
    assert len(completion_codes) == 18
    assert reference_codes.isdisjoint(completion_codes)
    assert len(reference_codes | completion_codes) == 20


def test_all_eighteen_completion_contracts_exist_and_are_complete():
    completion = load(COMPLETION)
    queue = load(QUEUE)
    queued_codes = {row["official_code"] for row in queue["execution_queue"]}

    manifest_codes = set()
    for row in completion["reviewed_completion_contracts"]:
        path = ROOT / row["completion_path"]
        assert path.is_file(), row
        city_completion = load(path)
        assert city_completion["phase"] == 13
        assert city_completion["status"] == "reviewed_complete"
        assert city_completion["official_code"] == row["official_code"]
        assert city_completion["name_ja"] == row["name_ja"]
        assert city_completion["completion_depth"] == "declared_review_package_v1"
        assert city_completion["quality_gate"]
        assert all(value is True for value in city_completion["quality_gate"].values())
        manifest_codes.add(row["official_code"])

    assert manifest_codes == queued_codes


def test_phase13_completion_keeps_non_inference_boundaries():
    completion = load(COMPLETION)
    quality = completion["quality_summary"]

    assert quality["policy_achievement_assessment_count"] == 0
    assert quality["causal_attribution_count"] == 0
    assert quality["cross_city_ranking_count"] == 0
    assert quality["inferred_missing_evidence_count"] == 0

    boundary = completion["completion_boundary"]
    assert "does not mean that every policy" in boundary
    assert "not-yet-published" in boundary
    assert "No independent Jichi Insight policy-achievement judgment" in boundary
    assert "causal attribution" in boundary
    assert "cross-city comparison" in boundary


def test_phase13_canonical_sources_exist():
    completion = load(COMPLETION)
    for path in completion["canonical_sources"]:
        assert (ROOT / path).exists(), path
