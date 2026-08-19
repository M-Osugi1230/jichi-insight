from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "data/catalog/phase13_designated_city_review_queue.json"
SCHEMA_PATH = ROOT / "schemas/phase13_designated_city_review_queue.schema.json"
PHASE12_QUEUE_PATH = ROOT / "data/catalog/phase12_designated_city_execution_queue.json"
SENDAI_COMPLETION_PATH = ROOT / "data/catalog/sendai_phase13_completion.json"
SAPPORO_COMPLETION_PATH = ROOT / "data/catalog/sapporo_phase13_completion.json"
SAITAMA_COMPLETION_PATH = ROOT / "data/catalog/saitama_phase13_completion.json"

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


def test_phase13_newly_eligible_five_cities_remain_queued():
    phase13 = load(QUEUE_PATH)
    by_code = {item["official_code"]: item for item in phase13["execution_queue"]}
    assert set(by_code) >= NEWLY_ELIGIBLE_CODES
    assert all(
        by_code[code]["status"] == "pending_record_review"
        for code in NEWLY_ELIGIBLE_CODES
    )
    assert by_code["221007"]["sequence"] == 9
    assert by_code["271403"]["sequence"] == 14
    assert by_code["281000"]["sequence"] == 15
    assert by_code["331007"]["sequence"] == 16
    assert by_code["341002"]["sequence"] == 17


def test_phase13_summary_is_derived_from_queue_contents():
    queue = load(QUEUE_PATH)
    statuses = [item["status"] for item in queue["execution_queue"]]
    summary = queue["summary"]
    assert summary["eligible_review_queue_count"] == len(queue["execution_queue"]) == 18
    assert summary["blocked_source_inventory_count"] == len(
        queue["blocked_source_inventories"]
    ) == 0
    assert summary["reviewed_complete_count"] == statuses.count("reviewed_complete")
    assert summary["review_in_progress_count"] == statuses.count("review_in_progress")
    assert summary["pending_record_review_count"] == statuses.count(
        "pending_record_review"
    )
    assert (
        summary["reviewed_complete_count"]
        + summary["review_in_progress_count"]
        + summary["pending_record_review_count"]
        == 18
    )


def test_phase13_three_cities_complete_and_chiba_in_progress():
    queue = load(QUEUE_PATH)
    by_code = {item["official_code"]: item for item in queue["execution_queue"]}
    completions = {
        "011002": load(SAPPORO_COMPLETION_PATH),
        "041009": load(SENDAI_COMPLETION_PATH),
        "111007": load(SAITAMA_COMPLETION_PATH),
    }

    for sequence, code in enumerate(("011002", "041009", "111007"), start=1):
        assert by_code[code]["sequence"] == sequence
        assert by_code[code]["status"] == "reviewed_complete"
        assert completions[code]["status"] == "reviewed_complete"

    assert by_code["121002"]["sequence"] == 4
    assert by_code["121002"]["status"] == "review_in_progress"
    assert queue["summary"]["reviewed_complete_count"] == 3
    assert queue["summary"]["review_in_progress_count"] == 1
    assert queue["summary"]["pending_record_review_count"] == 14
    assert queue["summary"]["next_official_code"] == "121002"


def test_phase13_quality_gate_keeps_missing_records_explicit_without_downgrading_inventory():
    gate = " ".join(load(QUEUE_PATH)["quality_gate"]).lower()
    assert "source-reported evaluations" in gate
    assert "causal attribution" in gate
    assert "cross-city ranking" in gate
    assert "record-level evidence" in gate
    assert "not-yet-published evidence" in gate
    assert "without downgrading already verified source inventory coverage" in gate
    assert "declared review package" in gate
