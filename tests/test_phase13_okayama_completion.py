from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_okayama_completion_contract():
    completion = load("data/catalog/okayama_phase13_completion.json")
    schema = load("schemas/okayama_phase13_completion.schema.json")
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    assert list(validator.iter_errors(completion)) == []
    assert completion["review_package"]["counts"] == {
        "perspectives": 4,
        "basic_directions": 8,
        "policies": 30,
        "measures": 99,
        "current_completed_annual_results": 0,
        "fiscal_top_line_records": 3,
    }
    assert all(completion["quality_gate"].values())


def test_okayama_source_precision_and_availability():
    fiscal = load("data/reviewed/okayama-city/fiscal_records.json")
    notes = " ".join(record["note"] for record in fiscal)
    assert "source" in notes or "余" in notes
    # Stage 1 (Issue #954) superseded the Phase 13 total for FY2026
    # with the exact thousand-yen figure from the June 2026
    # supplementary budget's pre-supplement column (429,863,382
    # thousand yen) and added the FY2026 local-tax record; the
    # Phase 13 completion snapshot above keeps its original counts.
    assert {record["amount_yen"] for record in fiscal} == {
        429_863_382_000,
        143_589_274_000,
        406_500_000_000,
        387_700_000_000,
    }

    progress = load("data/catalog/okayama_current_progress_availability.json")
    assert progress["current_plan_lane"]["annual_result_status"] == "not_yet_available"


def test_okayama_is_complete_in_final_phase13_queue():
    queue = load("data/catalog/phase13_designated_city_review_queue.json")
    by_code = {row["official_code"]: row["status"] for row in queue["execution_queue"]}

    assert by_code["331007"] == "reviewed_complete"
    assert queue["status"] == "complete"
    assert queue["summary"]["reviewed_complete_count"] == 18
    assert queue["summary"]["next_official_code"] is None
