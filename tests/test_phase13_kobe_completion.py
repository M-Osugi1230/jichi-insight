from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_kobe_completion_contract():
    completion = load("data/catalog/kobe_phase13_completion.json")
    schema = load("schemas/kobe_phase13_completion.schema.json")
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    assert list(validator.iter_errors(completion)) == []
    assert completion["review_package"]["counts"] == {
        "basic_plan_directions": 3,
        "implementation_plan_directions": 3,
        "current_completed_annual_results": 0,
        "fiscal_top_line_records": 3,
    }
    assert all(completion["quality_gate"].values())


def test_kobe_fiscal_and_availability():
    fiscal = load("data/reviewed/kobe-city/fiscal_records.json")
    assert {record["amount_yen"] for record in fiscal} == {
        977_781_231_000,
        945_588_848_718,
        930_659_433_328,
    }

    progress = load("data/catalog/kobe_current_progress_availability.json")
    assert progress["current_plan_lane"]["annual_result_status"] == "not_yet_available"
    assert progress["governance"]["model"] == "annual_external_expert_progress_management"


def test_kobe_is_complete_in_final_phase13_queue():
    queue = load("data/catalog/phase13_designated_city_review_queue.json")
    by_code = {row["official_code"]: row["status"] for row in queue["execution_queue"]}

    assert by_code["281000"] == "reviewed_complete"
    assert queue["status"] == "complete"
    assert queue["summary"]["reviewed_complete_count"] == 18
    assert queue["summary"]["next_official_code"] is None
