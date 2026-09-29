from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_sakai_completion_contract():
    completion = load("data/catalog/sakai_phase13_completion.json")
    schema = load("schemas/sakai_phase13_completion.schema.json")
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    assert list(validator.iter_errors(completion)) == []
    assert completion["review_package"]["counts"] == {
        "kgi": 3,
        "priority_strategies": 5,
        "measures": 27,
        "current_completed_annual_results": 0,
        "fiscal_top_line_records": 3,
    }
    assert all(completion["quality_gate"].values())


def test_sakai_fiscal_and_availability():
    fiscal = load("data/reviewed/sakai-city/fiscal_records.json")
    amounts: dict[str, list[int]] = {}
    for record in fiscal:
        amounts.setdefault(record["metric"], []).append(record["amount_yen"])

    assert 521_700_000_000 in amounts["total_revenue"]
    assert 477_935_503_067 in amounts["total_revenue"]
    assert 470_108_227_969 in amounts["total_expenditure"]

    progress = load("data/catalog/sakai_current_progress_availability.json")
    assert progress["current_plan_lane"]["annual_progress_status"] == "not_yet_available"
    assert "流用しない" in progress["historical_lane"]["boundary"]


def test_sakai_is_complete_in_final_phase13_queue():
    queue = load("data/catalog/phase13_designated_city_review_queue.json")
    by_code = {row["official_code"]: row["status"] for row in queue["execution_queue"]}

    assert by_code["271403"] == "reviewed_complete"
    assert queue["status"] == "complete"
    assert queue["summary"]["reviewed_complete_count"] == 18
    assert queue["summary"]["next_official_code"] is None
