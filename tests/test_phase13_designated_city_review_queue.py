from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "data/catalog/phase13_designated_city_review_queue.json"
SCHEMA_PATH = ROOT / "schemas/phase13_designated_city_review_queue.schema.json"
PHASE12_QUEUE_PATH = ROOT / "data/catalog/phase12_designated_city_execution_queue.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_phase13_queue_matches_schema():
    validator = Draft202012Validator(
        load(SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(load(QUEUE_PATH))) == []


def test_phase13_queue_only_accepts_phase12_complete_cities():
    phase12 = load(PHASE12_QUEUE_PATH)
    phase13 = load(QUEUE_PATH)
    complete_codes = {
        item["official_code"]
        for item in phase12["execution_queue"]
        if item["status"] == "source_inventory_complete"
    }
    queued_codes = {item["official_code"] for item in phase13["execution_queue"]}
    assert queued_codes == complete_codes
    assert len(queued_codes) == 13


def test_phase13_blocked_cities_match_phase12_partial_inventory():
    phase12 = load(PHASE12_QUEUE_PATH)
    phase13 = load(QUEUE_PATH)
    partial_codes = {
        item["official_code"]
        for item in phase12["execution_queue"]
        if item["status"] == "source_inventory_partial"
    }
    blocked_codes = {
        item["official_code"] for item in phase13["blocked_source_inventories"]
    }
    assert blocked_codes == partial_codes
    assert len(blocked_codes) == 5


def test_phase13_summary_is_derived_from_queue_contents():
    queue = load(QUEUE_PATH)
    statuses = [item["status"] for item in queue["execution_queue"]]
    summary = queue["summary"]
    assert summary["eligible_review_queue_count"] == len(queue["execution_queue"])
    assert summary["blocked_source_inventory_count"] == len(
        queue["blocked_source_inventories"]
    )
    assert summary["reviewed_complete_count"] == statuses.count("reviewed_complete")
    assert summary["review_in_progress_count"] == statuses.count(
        "review_in_progress"
    )
    assert summary["pending_record_review_count"] == statuses.count(
        "pending_record_review"
    )


def test_phase13_first_review_target_remains_sapporo_while_sendai_has_started():
    queue = load(QUEUE_PATH)
    first = queue["execution_queue"][0]
    sendai = next(
        item for item in queue["execution_queue"] if item["official_code"] == "041009"
    )

    assert first["sequence"] == 1
    assert first["official_code"] == "011002"
    assert first["status"] == "review_in_progress"
    assert sendai["sequence"] == 2
    assert sendai["status"] == "review_in_progress"
    assert queue["summary"]["review_in_progress_count"] >= 2
    assert queue["summary"]["next_official_code"] == "011002"


def test_phase13_quality_gate_blocks_unsupported_assessment_and_comparison():
    gate = " ".join(load(QUEUE_PATH)["quality_gate"]).lower()
    assert "source-reported evaluations" in gate
    assert "causal attribution" in gate
    assert "cross-city ranking" in gate
    assert "record-level evidence" in gate
