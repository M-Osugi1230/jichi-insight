"""Guard the public Phase 15 coverage page against premature Reviewed claims."""

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
WEB_ROOT = ROOT / "apps/web"
STATUS_TO_SUMMARY = {
    "reviewed_complete": "reviewed_complete_count",
    "review_in_progress": "review_in_progress_count",
    "pending_record_review": "pending_record_review_count",
    "blocked_source_inventory": "blocked_source_inventory_count",
}


def test_phase15_public_counts_are_derived_from_valid_canonical_state():
    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    records = queue["execution_queue"]
    summary = queue["summary"]
    counts = Counter(record["status"] for record in records)

    assert len(records) == summary["target_count"] == 67
    assert len({record["official_code"] for record in records}) == len(records)
    assert set(counts).issubset(STATUS_TO_SUMMARY)
    assert sum(counts.values()) == len(records)

    for status, summary_key in STATUS_TO_SUMMARY.items():
        assert counts[status] == summary[summary_key]

    for record in records:
        assert (ROOT / record["source_inventory_path"]).is_file()
        if record["status"] == "reviewed_complete":
            assert record["completion_path"]
            assert (ROOT / record["completion_path"]).is_file()
        else:
            assert record["completion_path"] is None


def test_public_review_page_discloses_boundaries_and_excludes_staging_data():
    page = (WEB_ROOT / "app/review-progress/page.tsx").read_text(encoding="utf-8")
    model = (WEB_ROOT / "lib/phase15Progress.ts").read_text(encoding="utf-8")
    header = (WEB_ROOT / "components/SiteHeader.tsx").read_text(encoding="utf-8")
    sitemap = (WEB_ROOT / "app/sitemap.ts").read_text(encoding="utf-8")

    assert "phase15Progress.municipalities.map" in page
    assert 'phase15_core_capital_review_queue.json' in model
    assert "レビュー完了" in page
    assert "作業中の候補データ" in page
    assert 'record.status === "reviewed_complete" && record.completionPath' in page
    assert "data/candidates/" not in model
    assert "/review-progress" in header
    assert '"/review-progress"' in sitemap
