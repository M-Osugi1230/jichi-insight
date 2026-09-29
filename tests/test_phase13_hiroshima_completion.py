from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_hiroshima_completion_contract():
    completion = load("data/catalog/hiroshima_phase13_completion.json")
    schema = load("schemas/hiroshima_phase13_completion.schema.json")
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    assert list(validator.iter_errors(completion)) == []
    assert completion["review_package"]["counts"] == {
        "plan_layers": 3,
        "current_implementation_plan_period_years": 6,
        "separately_identified_current_annual_result_packages": 0,
        "fiscal_top_line_records": 3,
    }
    assert all(completion["quality_gate"].values())


def test_hiroshima_fiscal_and_result_boundary():
    fiscal = load("data/reviewed/hiroshima-city/fiscal_records.json")
    assert {record["amount_yen"] for record in fiscal} == {
        794_011_359_000,
        720_118_240_000,
        716_676_720_000,
    }

    progress = load("data/catalog/hiroshima_current_progress_availability.json")
    current_result = progress["current_separate_annual_result"]
    assert current_result["status"] == (
        "not_separately_identified_in_declared_v1_sources"
    )
    assert "同一視しない" in current_result["boundary"]


def test_hiroshima_is_complete_in_final_phase13_queue():
    queue = load("data/catalog/phase13_designated_city_review_queue.json")
    by_code = {row["official_code"]: row["status"] for row in queue["execution_queue"]}

    assert by_code["341002"] == "reviewed_complete"
    assert queue["status"] == "complete"
    assert queue["summary"]["reviewed_complete_count"] == 18
    assert queue["summary"]["next_official_code"] is None
