from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "data/catalog/phase13_designated_city_review_queue.json"
SCHEMA_PATH = ROOT / "schemas/phase13_designated_city_review_queue.schema.json"
PHASE12_QUEUE_PATH = ROOT / "data/catalog/phase12_designated_city_execution_queue.json"
SENDAI_COMPLETION_PATH = ROOT / "data/catalog/sendai_phase13_completion.json"

NEWLY_ELIGIBLE_CODES = {"221007", "271403", "281000", "331007", "341002"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_phase13_queue_matches_schema():
    validator = Draft202012Validator(
        load(SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(load(QUEUE_PATH))) == []


def test_phase13_queue_accepts_all_phase12_complete_cities():
    phase12 = load(PHASE12_QUEUE_PATH)
    phase13 = load(QUEUE_PATH)
    complete_codes = {
        item["official_code"]
        for item in phase12["execution_queue"]
        if item["status"] == "source_inventory_complete"
    }
    queued_codes = {item["official_code"] for item in phase13["execution_queue"]}
    assert queued_codes == complete_codes
    assert len(queued_codes) == 18
    assert [item["sequence"] for item in phase13["execution_queue"]] == list(range(1, 19))


def test_phase13_has_no_source_inventory_blocks_after_phase12_completion():
    phase12 = load(PHASE12_QUEUE_PATH)
    phase13 = load(QUEUE_PATH)
    partial_codes = {
        item["official_code"]
        for item in phase12["execution_queue"]
        if item["status"] == "source_inventory_partial"
    }
    assert partial_codes == set()
    assert phase13["blocked_source_inventories"] == []
    assert phase13["summary"]["blocked_source_inventory_count"] == 0


def test_phase13_newly_eligible_five_cities_enter_as_pending_record_review():
    phase13 = load(QUEUE_PATH)
    by_code = {item["official_code"]: item for item in phase13["execution_queue"]}
    assert set(by_code) >= NEWLY_ELIGIBLE_CODES
    assert all(by_code[code]["status"] == "pending_record_review" for code in NEWLY_ELIGIBLE_CODES)
    assert by_code["221007"]["sequence"] == 9
    assert by_code["271403"]["sequence"] == 14
    assert by_code["281000"]["sequence"] == 15
    assert by_code["331007"]["sequence"] == 16
    assert by_code["341002"]["sequence"] == 17


def test_phase13_summary_is_derived_from_queue_contents_after_sendai_completion():
    queue = load(QUEUE_PATH)
    statuses = [item["status"] for item in queue["execution_queue"]]
    summary = queue["summary"]
    assert summary["eligible_review_queue_count"] == len(queue["execution_queue"]) == 18
    assert summary["blocked_source_inventory_count"] == len(
        queue["blocked_source_inventories"]
    ) == 0
    assert summary["reviewed_complete_count"] == statuses.count(
        "reviewed_complete"
    ) == 1
    assert summary["review_in_progress_count"] == statuses.count(
        "review_in_progress"
    ) == 1
    assert summary["pending_record_review_count"] == statuses.count(
        "pending_record_review"
    ) == 16


def test_phase13_sendai_is_first_reviewed_complete_city_and_sapporo_remains_active():
    queue = load(QUEUE_PATH)
    first = queue["execution_queue"][0]
    sendai = next(
        item for item in queue["execution_queue"] if item["official_code"] == "041009"
    )
    completion = load(SENDAI_COMPLETION_PATH)

    assert first["sequence"] == 1
    assert first["official_code"] == "011002"
    assert first["status"] == "review_in_progress"
    assert sendai["sequence"] == 2
    assert sendai["status"] == "reviewed_complete"
    assert completion["official_code"] == sendai["official_code"]
    assert completion["status"] == sendai["status"]
    assert queue["summary"]["next_official_code"] == "011002"


def test_phase13_quality_gate_keeps_missing_records_explicit_without_downgrading_inventory():
    gate = " ".join(load(QUEUE_PATH)["quality_gate"]).lower()
    assert "source-reported evaluations" in gate
    assert "causal attribution" in gate
    assert "cross-city ranking" in gate
    assert "record-level evidence" in gate
    assert "not-yet-published evidence" in gate
    assert "without downgrading already verified source inventory coverage" in gate
    assert "declared review package" in gate
