"""Relational consistency guards for the canonical Phase 15 review queue.

The snapshot-style checks live elsewhere on purpose:

- exact summary values and current status counts:
  test_phase15_core_capital_review_queue.py
- summary counts re-derived from execution_queue, official-code uniqueness
  and the allowed status set: test_phase15_public_progress.py
- field shapes and the per-entry status enum:
  schemas/phase15_core_capital_review_queue.schema.json

What those tests do not pin down is the relational meaning of
summary.next_official_code and the integrity of the execution order itself.
Those invariants are guarded here, expressed relative to the queue's own
contents so they keep passing as reviews legitimately advance.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"


def load_queue():
    return json.loads(QUEUE.read_text(encoding="utf-8"))


def test_phase15_next_official_code_tracks_review_frontier():
    queue = load_queue()
    records = queue["execution_queue"]
    next_code = queue["summary"]["next_official_code"]

    by_code = {row["official_code"]: row for row in records}
    in_progress = [
        row for row in records if row["status"] == "review_in_progress"
    ]
    pending = [
        row for row in records if row["status"] == "pending_record_review"
    ]

    if in_progress:
        # Same convention as the Phase 13 queue tests: the "next"
        # municipality is the one currently under review.
        assert next_code == in_progress[0]["official_code"]
    if not in_progress and not pending:
        # A fully reviewed queue has no next municipality.
        assert next_code is None
    if next_code is not None:
        # The public progress page resolves next_official_code to a queue
        # entry to display its name, so it must point at real, unfinished
        # work recorded in the queue itself.
        assert next_code in by_code
        assert by_code[next_code]["status"] != "reviewed_complete"


def test_phase15_sequence_numbers_define_a_single_execution_order():
    queue = load_queue()
    records = queue["execution_queue"]

    # execution_order is "phase14_registry_sequence": the queue is worked
    # in listed order, so sequence numbers must be unique, contiguous and
    # ascending in file order.
    sequences = [row["sequence"] for row in records]
    assert sequences == list(range(1, len(records) + 1))
