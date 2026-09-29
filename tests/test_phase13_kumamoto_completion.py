from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_kumamoto_completion_contract():
    completion = load("data/catalog/kumamoto_phase13_completion.json")
    schema = load("schemas/kumamoto_phase13_completion.schema.json")
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    assert list(validator.iter_errors(completion)) == []
    assert completion["review_package"]["counts"] == {
        "plan_layers": 3,
        "visions": 8,
        "fy2026_priority_items": 4,
        "reviewed_current_evaluation_fiscal_years": 1,
        "accountability_roles": 2,
        "fiscal_top_line_records": 3,
    }
    assert all(completion["quality_gate"].values())


def test_kumamoto_current_progress_roles_are_separate():
    progress = load("data/catalog/kumamoto_current_progress_review_summary.json")

    assert progress["reporting_fiscal_year"] == 2024
    assert progress["administrative_evaluation"]["status"] == "published"
    assert progress["deliberative_review"]["actor"] == "熊本市総合計画審議会"
    assert (
        progress["administrative_evaluation"]["evidence_role"]
        != "external_deliberative_review"
    )
    assert "独自評価へ変換しない" in progress["administrative_evaluation"]["boundary"]


def test_kumamoto_fiscal_top_lines_and_lineage():
    fiscal = {
        record["id"]: record
        for record in load("data/reviewed/kumamoto-city/fiscal_records.json")
    }

    assert (
        fiscal["jp-local-431001-fiscal-2026-total-revenue"]["amount_yen"]
        == 437_840_000_000
    )
    assert (
        fiscal["jp-local-431001-fiscal-2024-total-revenue"]["amount_yen"]
        == 428_730_240_000
    )
    assert (
        fiscal["jp-local-431001-fiscal-2024-total-expenditure"]["amount_yen"]
        == 419_712_090_000
    )
    assert (
        "原案どおり可決"
        in fiscal["jp-local-431001-fiscal-2026-total-revenue"]["metric_label"]
    )


def test_kumamoto_queue_is_final_city_complete():
    queue = load("data/catalog/phase13_designated_city_review_queue.json")
    by_code = {row["official_code"]: row["status"] for row in queue["execution_queue"]}

    assert by_code["431001"] == "reviewed_complete"
    assert all(row["status"] == "reviewed_complete" for row in queue["execution_queue"])
    assert queue["summary"]["reviewed_complete_count"] == 18
    assert queue["summary"]["review_in_progress_count"] == 0
    assert queue["summary"]["pending_record_review_count"] == 0
