from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPLETION_PATH = ROOT / "data/catalog/phase12_completion.json"
PHASE13_QUEUE_PATH = ROOT / "data/catalog/phase13_designated_city_review_queue.json"
ROADMAP_PATH = ROOT / "docs/ROADMAP.md"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_phase12_completion_is_reflected_in_roadmap():
    completion = load(COMPLETION_PATH)
    roadmap = ROADMAP_PATH.read_text(encoding="utf-8")

    assert completion["status"] == "complete"
    assert "## Phase 12 — Designated-city source inventory" in roadmap
    phase12_section = roadmap.split("## Phase 12 — Designated-city source inventory", 1)[
        1
    ].split("## Phase 13 — Designated-city record review", 1)[0]
    assert "Status: `complete`（2026-08-12）" in phase12_section
    assert "Source inventory complete: 18 / 18" in phase12_section
    assert "Source inventory partial: 0" in phase12_section
    assert "未公開または別立てされていない層" in phase12_section


def test_phase13_roadmap_matches_canonical_queue_summary():
    queue = load(PHASE13_QUEUE_PATH)
    summary = queue["summary"]
    roadmap = ROADMAP_PATH.read_text(encoding="utf-8")
    phase13_section = roadmap.split("## Phase 13 — Designated-city record review", 1)[
        1
    ].split("## After Phase 13", 1)[0]

    assert (
        f"Review queue eligible: {summary['eligible_review_queue_count']}市"
        in phase13_section
    )
    assert (
        f"Reviewed complete: {summary['reviewed_complete_count']}市"
        in phase13_section
    )
    assert (
        f"Review in progress: {summary['review_in_progress_count']}市"
        in phase13_section
    )
    assert (
        f"Pending record review: {summary['pending_record_review_count']}市"
        in phase13_section
    )
    assert (
        f"Blocked source inventory: {summary['blocked_source_inventory_count']}市"
        in phase13_section
    )
