"""Regression checks for honest public release metadata and daily monitoring."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_release_checklist_reflects_completed_record_and_inventory_phases():
    checklist = (ROOT / "docs/RELEASE_CHECKLIST.md").read_text(encoding="utf-8")
    phase11 = json.loads(
        (ROOT / "data/catalog/phase11_completion.json").read_text(encoding="utf-8")
    )
    phase14 = json.loads(
        (ROOT / "data/catalog/phase14_completion.json").read_text(encoding="utf-8")
    )

    assert phase11["status"] == "complete"
    assert phase11["record_summary"]["total_records"] == 15327
    assert phase14["status"] == "complete"
    assert phase14["coverage"]["source_inventory_complete_count"] == 67

    assert "公開状態: **正式公開（Public release）**" in checklist
    assert "15,327個票" in checklist
    assert "67/67の公式Source Inventory完了" in checklist
    assert "Phase 15の全67自治体レビュー完了はPublic betaの必須条件ではない" in checklist
    assert "Wave 3の残る38県を個票接続または最大到達深度へ引き上げ" not in checklist
    assert "次の対象は青森県" not in checklist
    assert "issues/12" in checklist


def test_sitemap_last_modified_dates_come_from_canonical_records():
    sitemap = (ROOT / "apps/web/app/sitemap.ts").read_text(encoding="utf-8")

    assert '"/review-progress"' in sitemap
    # lastModified may only be derived from verifiable repository data:
    # Phase 15 completion dates and the canonical queue's updated_at stamp.
    # Hardcoded or unchanging date literals remain forbidden.
    assert "completedAt" in sitemap
    assert "phase15Progress.updatedAt" in sitemap
    assert 'new Date("' not in sitemap
    assert not re.search(r"\d{4}-\d{2}-\d{2}", sitemap)


def test_existing_production_smoke_is_scheduled_daily():
    workflow = (
        ROOT / ".github/workflows/production-smoke.yml"
    ).read_text(encoding="utf-8")

    assert "  workflow_dispatch:" in workflow
    assert "  workflow_run:" in workflow
    assert '    - cron: "23 0 * * *"' in workflow
    assert "bash scripts/check_production.sh" in workflow
    assert "Upload smoke report" in workflow


def test_beta_announcement_is_backed_by_the_recorded_human_release_gate():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    checklist = (ROOT / "docs/RELEASE_CHECKLIST.md").read_text(encoding="utf-8")

    assert "Public release" in readme
    assert "pre-alpha" not in readme
    assert "Go / No-Go" in checklist
    assert "外部法務" in checklist
    assert "訂正・反論" in checklist
    # The human release gate passed on 2026-11-15: the publication owner's
    # approval is recorded in the checklist, and items that remain
    # unimplemented at launch stay visibly marked as such.
    assert "公開責任者・大杉邑大が正式Public betaへの移行を承認" in checklist
    assert "未実施であることを本記録に明記したうえでPublic betaへ移行する" in checklist
