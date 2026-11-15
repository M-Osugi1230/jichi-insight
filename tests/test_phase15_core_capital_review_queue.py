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
        "reviewed_complete": 12,
        "pending_record_review": 55,
    }
    assert queue["summary"] == {
        "target_count": 67,
        "reviewed_complete_count": 12,
        "review_in_progress_count": 0,
        "pending_record_review_count": 55,
        "blocked_source_inventory_count": 0,
        "next_official_code": "072044",
    }

    completed = [
        row
        for row in queue["execution_queue"]
        if row["status"] == "reviewed_complete"
    ]
    assert [row["name_ja"] for row in completed] == [
        "函館市",
        "旭川市",
        "青森市",
        "八戸市",
        "盛岡市",
        "秋田市",
        "山形市",
        "福島市",
        "郡山市",
        "宇都宮市",
        "前橋市",
        "高崎市",
    ]
    assert completed[0]["completion_path"] == "data/catalog/hakodate_phase15_completion.json"
    assert completed[1]["completion_path"] == "data/catalog/asahikawa_phase15_completion.json"
    assert completed[2]["completion_path"] == "data/catalog/aomori_phase15_completion.json"
    assert completed[3]["completion_path"] == "data/catalog/hachinohe_phase15_completion.json"
    assert completed[4]["completion_path"] == "data/catalog/morioka_phase15_completion.json"
    assert completed[5]["completion_path"] == "data/catalog/akita_phase15_completion.json"
    assert completed[6]["completion_path"] == "data/catalog/yamagata_phase15_completion.json"
    assert completed[7]["completion_path"] == "data/catalog/fukushima_phase15_completion.json"
    assert completed[8]["completion_path"] == "data/catalog/koriyama_phase15_completion.json"
    assert completed[9]["completion_path"] == "data/catalog/utsunomiya_phase15_completion.json"
    assert completed[10]["completion_path"] == "data/catalog/maebashi_phase15_completion.json"
    assert completed[11]["completion_path"] == "data/catalog/takasaki_phase15_completion.json"

    current = [
        row
        for row in queue["execution_queue"]
        if row["status"] == "review_in_progress"
    ]
    assert current == []

    pending = [
        row
        for row in queue["execution_queue"]
        if row["status"] == "pending_record_review"
    ]
    assert pending[0]["name_ja"] == "いわき市"
    assert pending[0]["official_code"] == "072044"
    assert pending[0]["sequence"] == 10
    assert pending[0]["wave"] == 1
    assert pending[0]["completion_path"] is None


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
