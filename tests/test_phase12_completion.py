from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
COMPLETION_PATH = ROOT / "data/catalog/phase12_completion.json"
SCHEMA_PATH = ROOT / "schemas/phase12_completion.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_phase12_completion_matches_schema():
    completion = load(COMPLETION_PATH)
    validator = Draft202012Validator(
        load(SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(completion)) == []


def test_phase12_completion_is_derived_from_phase12_and_phase13_queues():
    completion = load(COMPLETION_PATH)
    phase12 = load(ROOT / completion["execution_queue_path"])
    phase13 = load(ROOT / completion["phase13_queue_path"])
    summary = completion["summary"]
    phase12_statuses = [item["status"] for item in phase12["execution_queue"]]

    assert phase12["status"] == "complete"
    assert summary["designated_city_count"] == (
        len(phase12["reference_implementations"]) + len(phase12["execution_queue"])
    ) == 20
    assert summary["reviewed_reference_count"] == len(
        phase12["reference_implementations"]
    ) == 2
    assert summary["source_inventory_complete_count"] == phase12_statuses.count(
        "source_inventory_complete"
    ) == 18
    assert summary["source_inventory_partial_count"] == phase12_statuses.count(
        "source_inventory_partial"
    ) == 0
    assert summary["pending_source_inventory_count"] == phase12_statuses.count(
        "pending_source_inventory"
    ) == 0
    assert summary["phase13_eligible_count"] == len(phase13["execution_queue"]) == 18
    assert summary["phase13_blocked_source_inventory_count"] == len(
        phase13["blocked_source_inventories"]
    ) == 0


def test_phase12_completion_does_not_promote_inventory_to_reviewed_or_invent_evidence():
    completion = load(COMPLETION_PATH)
    phase12 = load(ROOT / completion["execution_queue_path"])

    for item in phase12["execution_queue"]:
        inventory = load(ROOT / item["inventory_path"])
        assert inventory["status"] == "source_inventory_complete"
        assert inventory["review_status"] == "indexed_not_reviewed"

    boundary = completion["completion_boundary"]
    rule = completion["promotion_rule"]
    assert "does not mean all municipality records are Reviewed" in boundary
    assert "policy achievement" in boundary
    assert "Not-yet-published" in rule
    assert "legacy substitution or inference" in rule
