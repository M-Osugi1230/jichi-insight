from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/catalog/phase14_core_capital_target_registry.json"
REGISTRY_SCHEMA = ROOT / "schemas/phase14_core_capital_target_registry.schema.json"
QUEUE = ROOT / "data/catalog/phase14_core_capital_execution_queue.json"
QUEUE_SCHEMA = ROOT / "schemas/phase14_core_capital_execution_queue.schema.json"
PHASE13 = ROOT / "data/catalog/phase13_completion.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_path: Path, instance):
    schema = load(schema_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return list(validator.iter_errors(instance))


def check_digit(code5: str) -> str:
    weights = (6, 5, 4, 3, 2)
    total = sum(int(digit) * weight for digit, weight in zip(code5, weights, strict=True))
    remainder = 11 - (total % 11)
    if remainder >= 10:
        remainder = 0
    return str(remainder)


def test_phase14_registry_and_queue_match_schemas():
    assert validate(REGISTRY_SCHEMA, load(REGISTRY)) == []
    assert validate(QUEUE_SCHEMA, load(QUEUE)) == []


def test_phase14_target_universe_has_exact_declared_counts():
    registry = load(REGISTRY)
    targets = registry["targets"]

    assert len(targets) == 67
    assert len({row["official_code"] for row in targets}) == 67
    assert len({row["standard_area_code"] for row in targets}) == 67
    assert sum(row["core_city"] for row in targets) == 62
    assert sum(row["prefectural_capital"] for row in targets) == 32
    assert sum(
        row["core_city"] and row["prefectural_capital"] for row in targets
    ) == 27

    capital_only = {
        row["name_ja"]
        for row in targets
        if row["prefectural_capital"] and not row["core_city"]
    }
    assert capital_only == {"新宿区", "津市", "山口市", "徳島市", "佐賀市"}


def test_phase14_six_digit_codes_match_standard_area_codes():
    registry = load(REGISTRY)

    for row in registry["targets"]:
        area_code = row["standard_area_code"]
        assert row["official_code"] == area_code + check_digit(area_code)


def test_phase14_excludes_all_phase13_designated_cities():
    registry = load(REGISTRY)
    phase13 = load(PHASE13)

    phase14_codes = {row["official_code"] for row in registry["targets"]}
    phase13_codes = {
        row["official_code"] for row in phase13["reference_implementations"]
    }
    phase13_codes.update(
        row["official_code"] for row in phase13["reviewed_completion_contracts"]
    )

    assert len(phase13_codes) == 20
    assert phase14_codes.isdisjoint(phase13_codes)


def test_phase14_wave_distribution_and_statuses_are_canonical():
    registry = load(REGISTRY)
    queue = load(QUEUE)
    targets = registry["targets"]

    by_wave = Counter(row["wave"] for row in targets)
    assert by_wave == {
        1: 10,
        2: 12,
        3: 6,
        4: 6,
        5: 14,
        6: 7,
        7: 4,
        8: 8,
    }

    statuses = Counter(row["status"] for row in targets)
    assert statuses == {"source_inventory_complete": 67}

    summary = queue["summary"]
    assert queue["status"] == "complete"
    assert summary["source_inventory_complete_count"] == 67
    assert summary["source_inventory_in_progress_count"] == 0
    assert summary["pending_source_inventory_count"] == 0
    assert summary["next_official_code"] is None

    wave1 = next(row for row in queue["waves"] if row["wave"] == 1)
    wave2 = next(row for row in queue["waves"] if row["wave"] == 2)
    wave3 = next(row for row in queue["waves"] if row["wave"] == 3)
    wave4 = next(row for row in queue["waves"] if row["wave"] == 4)
    wave5 = next(row for row in queue["waves"] if row["wave"] == 5)
    wave6 = next(row for row in queue["waves"] if row["wave"] == 6)
    wave7 = next(row for row in queue["waves"] if row["wave"] == 7)
    wave8 = next(row for row in queue["waves"] if row["wave"] == 8)
    assert wave1["status"] == "complete"
    assert wave1["source_inventory_complete_count"] == 10
    assert wave1["source_inventory_in_progress_count"] == 0
    assert wave1["pending_count"] == 0
    assert wave2["status"] == "complete"
    assert wave2["source_inventory_complete_count"] == 12
    assert wave2["source_inventory_in_progress_count"] == 0
    assert wave2["pending_count"] == 0
    assert wave3["status"] == "complete"
    assert wave3["source_inventory_complete_count"] == 6
    assert wave3["source_inventory_in_progress_count"] == 0
    assert wave3["pending_count"] == 0
    assert wave4["status"] == "complete"
    assert wave4["source_inventory_complete_count"] == 6
    assert wave4["source_inventory_in_progress_count"] == 0
    assert wave4["pending_count"] == 0
    assert wave5["status"] == "complete"
    assert wave5["source_inventory_complete_count"] == 14
    assert wave5["source_inventory_in_progress_count"] == 0
    assert wave5["pending_count"] == 0
    assert wave6["status"] == "complete"
    assert wave6["source_inventory_complete_count"] == 7
    assert wave6["source_inventory_in_progress_count"] == 0
    assert wave6["pending_count"] == 0
    assert wave7["status"] == "complete"
    assert wave7["source_inventory_complete_count"] == 4
    assert wave7["source_inventory_in_progress_count"] == 0
    assert wave7["pending_count"] == 0
    assert wave8["status"] == "complete"
    assert wave8["source_inventory_complete_count"] == 8
    assert wave8["source_inventory_in_progress_count"] == 0
    assert wave8["pending_count"] == 0


def test_phase14_has_no_remaining_execution_target():
    registry = load(REGISTRY)
    current = [
        row
        for row in registry["targets"]
        if row["status"] == "source_inventory_in_progress"
    ]
    pending = [
        row
        for row in registry["targets"]
        if row["status"] == "pending_source_inventory"
    ]

    assert current == []
    assert pending == []
