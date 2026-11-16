"""State-synchronization regression checks.

Unlike the fixed-string checks in test_public_beta_release_readiness.py,
the expectations here are derived from the canonical Phase 15 review
queue (data/catalog/phase15_core_capital_review_queue.json), so the
public documents must move when the canonical data moves.
"""

import json
import re
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
CHECKLIST_PATH = ROOT / "docs/RELEASE_CHECKLIST.md"
README_PATH = ROOT / "README.md"


def _queue():
    return json.loads(QUEUE_PATH.read_text(encoding="utf-8"))


def _checklist_section(checklist: str, heading: str) -> str:
    """Return the body of a `## <heading>` section of the checklist."""
    match = re.search(
        rf"^## {re.escape(heading)}\s*$(.*?)(?=^## |\Z)",
        checklist,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert match, f"checklist is missing the '## {heading}' section"
    return match.group(1)


def test_queue_summary_matches_execution_queue_entries():
    """The canonical summary must agree with the queue entries themselves."""
    queue = _queue()
    summary = queue["summary"]
    counts = Counter(entry["status"] for entry in queue["execution_queue"])

    assert summary["target_count"] == len(queue["execution_queue"])
    assert summary["reviewed_complete_count"] == counts["reviewed_complete"]
    assert summary["pending_record_review_count"] == counts["pending_record_review"]
    assert summary["review_in_progress_count"] == counts["review_in_progress"]
    accounted = (
        summary["reviewed_complete_count"]
        + summary["review_in_progress_count"]
        + summary["pending_record_review_count"]
        + summary["blocked_source_inventory_count"]
    )
    assert accounted == summary["target_count"]


def test_checklist_phase15_line_matches_canonical_queue():
    """The checklist's Phase 15 position line must state the queue's counts."""
    summary = _queue()["summary"]
    checklist = CHECKLIST_PATH.read_text(encoding="utf-8")
    position = _checklist_section(checklist, "Current release position")

    # The trailing parenthetical carries the queue's update date; only the
    # counts are pinned here so a date-only refresh does not break the test.
    match = re.search(
        r"Phase 15: (\d+)/(\d+)自治体 reviewed_complete、"
        r"(\d+)自治体 pending_record_review",
        position,
    )
    assert match, "checklist 'Current release position' has no Phase 15 count line"
    reviewed, target, pending = (int(group) for group in match.groups())
    assert reviewed == summary["reviewed_complete_count"]
    assert target == summary["target_count"]
    assert pending == summary["pending_record_review_count"]


def test_readme_and_checklist_agree_on_release_stage():
    """README's Product status must name the same release stage as the checklist."""
    checklist = CHECKLIST_PATH.read_text(encoding="utf-8")
    position = _checklist_section(checklist, "Current release position")

    stage_match = re.search(r"公開状態: \*\*(.+?)（(.+?)）\*\*", position)
    assert stage_match, "checklist does not state 公開状態 as '**<ja>（<en>）**'"
    stage_ja, stage_en = stage_match.group(1), stage_match.group(2)

    readme = README_PATH.read_text(encoding="utf-8")
    status_match = re.search(
        r"^## Product status\s*$(.*?)(?=^## |\Z)",
        readme,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert status_match, "README is missing the '## Product status' section"
    status_section = status_match.group(1)
    assert stage_en in status_section
    assert stage_ja in status_section


def test_checklist_next_target_matches_canonical_queue():
    """If the checklist names the next review target, it must be the queue's."""
    queue = _queue()
    next_code = queue["summary"]["next_official_code"]
    if next_code is None:
        # The queue is complete: there is no next review target to name.
        assert queue["summary"]["pending_record_review_count"] == 0
        assert all(
            entry["status"] == "reviewed_complete"
            for entry in queue["execution_queue"]
        )
        return
    next_entries = [e for e in queue["execution_queue"] if e["official_code"] == next_code]
    assert len(next_entries) == 1, "next_official_code must identify exactly one queue entry"
    next_name = next_entries[0]["name_ja"]

    checklist = CHECKLIST_PATH.read_text(encoding="utf-8")
    naming_lines = [line for line in checklist.splitlines() if next_name in line]
    if not naming_lines:
        pytest.skip(
            f"checklist never names the next target ({next_name}); "
            "nothing to synchronize against"
        )
    assert any("次" in line for line in naming_lines), (
        f"checklist mentions {next_name} but not as the next review target"
    )
