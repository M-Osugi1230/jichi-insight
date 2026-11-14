"""Regression checks for honest Public beta release metadata and daily monitoring."""

import json
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

    assert "公開状態: **pre-alpha**" in checklist
    assert "15,327個票" in checklist
    assert "67/67の公式Source Inventory完了" in checklist
    assert "Phase 15の全67自治体レビュー完了はPublic betaの必須条件ではない" in checklist
    assert "Wave 3の残る38県を個票接続または最大到達深度へ引き上げ" not in checklist
    assert "次の対象は青森県" not in checklist
    assert "issues/12" in checklist


def test_sitemap_avoids_unverified_unchanging_last_modified_dates():
    sitemap = (ROOT / "apps/web/app/sitemap.ts").read_text(encoding="utf-8")

    assert '"/review-progress"' in sitemap
    assert "lastModified:" not in sitemap
    assert 'new Date("2026-08-01")' not in sitemap


def test_existing_production_smoke_is_scheduled_daily():
    workflow = (
        ROOT / ".github/workflows/production-smoke.yml"
    ).read_text(encoding="utf-8")

    assert "  workflow_dispatch:" in workflow
    assert "  workflow_run:" in workflow
    assert '    - cron: "23 0 * * *"' in workflow
    assert "bash scripts/check_production.sh" in workflow
    assert "Upload smoke report" in workflow


def test_beta_is_not_announced_before_human_release_gate():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    checklist = (ROOT / "docs/RELEASE_CHECKLIST.md").read_text(encoding="utf-8")

    assert "pre-alpha" in readme
    assert "Go / No-Go" in checklist
    assert "外部法務" in checklist
    assert "訂正・反論" in checklist
