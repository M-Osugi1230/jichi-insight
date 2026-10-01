from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
QUEUE_SCHEMA = ROOT / "schemas/phase15_core_capital_review_queue.schema.json"
PHASE14_REGISTRY = ROOT / "data/catalog/phase14_core_capital_target_registry.json"
PHASE14_COMPLETION = ROOT / "data/catalog/phase14_completion.json"
PHASE13_COMPLETION = ROOT / "data/catalog/phase13_completion.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_phase15_queue_validates_and_starts_from_phase14_completion():
    queue = load(QUEUE)
    validator = Draft202012Validator(
        load(QUEUE_SCHEMA), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(queue)) == []
    assert queue["phase"] == 15
    assert queue["status"] == "in_progress"
    assert queue["source_phase"] == 14
    assert queue["source_completion_path"] == "data/catalog/phase14_completion.json"
    assert load(PHASE14_COMPLETION)["status"] == "complete"


def test_phase15_queue_matches_exact_phase14_target_universe():
    queue = load(QUEUE)
    registry = load(PHASE14_REGISTRY)

    queued = queue["execution_queue"]
    targets = registry["targets"]

    assert len(queued) == len(targets) == 67
    assert [row["official_code"] for row in queued] == [
        row["official_code"] for row in targets
    ]
    assert [row["standard_area_code"] for row in queued] == [
        row["standard_area_code"] for row in targets
    ]
    assert [row["name_ja"] for row in queued] == [row["name_ja"] for row in targets]
    assert [row["wave"] for row in queued] == [row["wave"] for row in targets]

    for queued_row, target in zip(queued, targets, strict=True):
        assert target["status"] == "source_inventory_complete"
        assert queued_row["phase14_role"] == target["phase14_role"]
        assert queued_row["municipality_type"] == target["municipality_type"]


def test_phase15_queue_excludes_phase13_designated_cities():
    queue = load(QUEUE)
    phase13 = load(PHASE13_COMPLETION)

    phase15_codes = {row["official_code"] for row in queue["execution_queue"]}
    designated_codes = {
        row["official_code"] for row in phase13["reference_implementations"]
    }
    designated_codes.update(
        row["official_code"] for row in phase13["reviewed_completion_contracts"]
    )

    assert len(phase15_codes) == 67
    assert len(designated_codes) == 20
    assert phase15_codes.isdisjoint(designated_codes)


def test_phase15_current_statuses_are_canonical():
    queue = load(QUEUE)
    statuses = Counter(row["status"] for row in queue["execution_queue"])

    assert statuses == {
        "reviewed_complete": 3,
        "review_in_progress": 1,
        "pending_record_review": 63,
    }
    assert queue["summary"] == {
        "target_count": 67,
        "reviewed_complete_count": 3,
        "review_in_progress_count": 1,
        "pending_record_review_count": 63,
        "blocked_source_inventory_count": 0,
        "next_official_code": "022039",
    }

    completed = [
        row
        for row in queue["execution_queue"]
        if row["status"] == "reviewed_complete"
    ]
    assert [row["name_ja"] for row in completed] == ["函館市", "旭川市", "青森市"]
    assert completed[0]["completion_path"] == "data/catalog/hakodate_phase15_completion.json"
    assert completed[1]["completion_path"] == "data/catalog/asahikawa_phase15_completion.json"
    assert completed[2]["completion_path"] == "data/catalog/aomori_phase15_completion.json"

    current = [
        row
        for row in queue["execution_queue"]
        if row["status"] == "review_in_progress"
    ]
    assert len(current) == 1
    assert current[0]["name_ja"] == "八戸市"
    assert current[0]["official_code"] == "022039"
    assert current[0]["sequence"] == 4
    assert current[0]["wave"] == 1
    assert current[0]["completion_path"] is None


def test_phase15_all_source_inventories_exist_and_remain_unreviewed():
    queue = load(QUEUE)

    for row in queue["execution_queue"]:
        path = ROOT / row["source_inventory_path"]
        assert path.is_file(), row
        inventory = load(path)
        assert inventory["official_code"] == row["official_code"]
        assert inventory["name_ja"] == row["name_ja"]
        assert inventory["status"] == "source_inventory_complete"
        assert inventory["review_status"] == "indexed_not_reviewed"


def test_phase15_quality_gate_preserves_non_inference_and_fiscal_states():
    queue = load(QUEUE)
    gate = "\n".join(queue["quality_gate"])

    assert "record-level evidence locator" in gate
    assert "Proposal" in gate
    assert "enacted budget" in gate
    assert "supplementary budget" in gate
    assert "Historical or prior-plan evidence" in gate
    assert "Draft, transition, not-yet-published" in gate
    assert "independent Jichi Insight achievement judgments" in gate
    assert "causal attribution" in gate
    assert "cross-city comparison eligibility" in gate
    assert "regression tests" in gate
