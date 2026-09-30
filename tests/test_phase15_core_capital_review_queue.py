from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
QUEUE_SCHEMA = ROOT / "schemas/phase15_core_capital_review_queue.schema.json"
REGISTRY = ROOT / "data/catalog/phase14_core_capital_target_registry.json"
PHASE14_COMPLETION = ROOT / "data/catalog/phase14_completion.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_phase15_queue_validates():
    validator = Draft202012Validator(
        load(QUEUE_SCHEMA), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(load(QUEUE))) == []


def test_phase15_queue_matches_all_phase14_complete_targets():
    queue = load(QUEUE)
    registry = load(REGISTRY)
    completion = load(PHASE14_COMPLETION)

    assert completion["status"] == "complete"
    assert completion["coverage"]["source_inventory_complete_count"] == 67

    phase14 = {row["official_code"]: row for row in registry["targets"]}
    phase15 = {row["official_code"]: row for row in queue["execution_queue"]}

    assert len(phase14) == len(phase15) == 67
    assert set(phase14) == set(phase15)

    for code, target in phase14.items():
        queued = phase15[code]
        assert target["status"] == "source_inventory_complete"
        assert queued["phase14_sequence"] == target["sequence"]
        assert queued["phase14_wave"] == target["wave"]
        assert queued["name_ja"] == target["name_ja"]
        assert queued["prefecture_name_ja"] == target["prefecture_name_ja"]
        assert queued["municipality_type"] == target["municipality_type"]


def test_phase15_starts_with_one_review_target_and_no_blocked_inventory():
    queue = load(QUEUE)
    statuses = [row["status"] for row in queue["execution_queue"]]

    assert statuses.count("reviewed_complete") == 0
    assert statuses.count("review_in_progress") == 1
    assert statuses.count("pending_record_review") == 66
    assert queue["blocked_source_inventories"] == []
    assert queue["summary"] == {
        "eligible_review_queue_count": 67,
        "reviewed_complete_count": 0,
        "review_in_progress_count": 1,
        "pending_record_review_count": 66,
        "blocked_source_inventory_count": 0,
        "next_official_code": "402036",
    }


def test_phase15_reference_work_starts_with_kurume():
    queue = load(QUEUE)
    first = min(queue["execution_queue"], key=lambda row: row["review_sequence"])

    assert first["official_code"] == "402036"
    assert first["name_ja"] == "久留米市"
    assert first["phase14_wave"] == 8
    assert first["status"] == "review_in_progress"
