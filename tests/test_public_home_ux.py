"""Guard the public homepage clarity, evidence boundaries, and navigation usability."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "apps/web"
PHASE15 = ROOT / "data/catalog/phase15_core_capital_review_queue.json"


def test_public_home_cites_the_canonical_phase15_progress():
    homepage = (WEB / "app/page.tsx").read_text(encoding="utf-8")
    progress = (WEB / "lib/phase15Progress.ts").read_text(encoding="utf-8")
    queue = json.loads(PHASE15.read_text(encoding="utf-8"))

    assert queue["summary"]["target_count"] == 67
    assert 'import { phase15Progress } from "@/lib/phase15Progress";' in homepage
    assert "phase15Progress.reviewed" in homepage
    assert "phase15Progress.total" in homepage
    assert "phase15Progress.inProgress" in homepage
    assert "phase15Progress.nextMunicipality" in homepage
    assert "phase15_core_capital_review_queue.json" in progress
    assert "未確認候補は審査済みデータとして表示しません" in homepage
    assert "次は、個票の一対一接続" not in homepage
    assert "公開中・pre-alpha" in homepage


def test_public_home_keeps_the_critical_journey_and_smoke_copy():
    homepage = (WEB / "app/page.tsx").read_text(encoding="utf-8")
    assert "47都道府県から探す" in homepage
    assert 'href="/municipalities"' in homepage
    assert 'href="/review-progress"' in homepage
    assert 'href="/data-quality"' in homepage
    assert 'href="/methodology"' in homepage
    assert "自治体を、" in homepage
    assert "政策達成評価" in homepage
    assert 'aria-label="Phase 15 詳細レビューの完了状況"' in homepage


def test_navigation_has_a_skip_link_and_accessible_target_on_all_pages():
    header = (WEB / "components/SiteHeader.tsx").read_text(encoding="utf-8")
    styles = (WEB / "app/globals.css").read_text(encoding="utf-8")

    assert 'className="skipLink" href="#page-content"' in header
    assert 'id="page-content" className="skipTarget" tabIndex={-1}' in header
    assert 'aria-label="主要ナビゲーション"' in header
    assert 'aria-label="モバイルナビゲーション"' in header
    assert ".skipLink:focus" in styles
    assert "scroll-margin-top: 88px" in styles


def test_public_home_and_footer_are_responsive():
    home_css = (WEB / "app/page.module.css").read_text(encoding="utf-8")
    global_css = (WEB / "app/globals.css").read_text(encoding="utf-8")

    for selector in (".reviewGrid", ".reviewCard", ".reviewStatusNote"):
        assert selector in home_css
    assert "@media (max-width: 760px)" in home_css
    assert "grid-template-columns: repeat(3, minmax(0, 1fr))" in home_css
    assert "repeat(3, minmax(130px, 0.65fr))" in global_css
    assert ".footerMission { grid-column: auto; }" in global_css
