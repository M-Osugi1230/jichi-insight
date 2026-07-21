from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE_PATH = ROOT / "apps/web/app/municipalities/tokyo/page.tsx"
LIB_PATH = ROOT / "apps/web/lib/tokyoPolicyTargets.ts"
SITEMAP_PATH = ROOT / "apps/web/app/sitemap.ts"
NATIONWIDE_PAGE_PATH = ROOT / "apps/web/app/municipalities/page.tsx"
EXPLORER_PATH = ROOT / "apps/web/components/CoverageExplorer.tsx"


def test_tokyo_public_page_exposes_reviewed_scope_without_claiming_achievement():
    page = PAGE_PATH.read_text(encoding="utf-8")

    assert "東京都の政策目標を、値と条件を変えずに読む。" in page
    assert "政策成果の達成率ではなく" in page
    assert "年度実績 未接続" in page
    assert "政策評価 未判定" in page
    assert "未Reviewedページは数値を公開せず" in page
    assert "目標・実績・評価を、同じ資料として扱わない。" in page
    assert "tokyoPolicyTargetStats.reviewedTargetGroups" in page
    assert "tokyoPolicyTargetStats.reviewedSeries" in page


def test_tokyo_page_renders_semantic_boundaries_and_official_sources():
    page = PAGE_PATH.read_text(encoding="utf-8")
    data_model = LIB_PATH.read_text(encoding="utf-8")

    assert "population_scope_original" in page
    assert "comparability_note_original" in page
    assert "tokyoValueRoleLabel" in page
    assert "tokyoValueDisplay" in page
    assert "target.source_page" in page
    assert "minimum" in data_model
    assert "maintain" in data_model
    assert "qualitative" in data_model


def test_tokyo_route_is_linked_from_nationwide_page_and_sitemap():
    nationwide_page = NATIONWIDE_PAGE_PATH.read_text(encoding="utf-8")
    sitemap = SITEMAP_PATH.read_text(encoding="utf-8")
    explorer = EXPLORER_PATH.read_text(encoding="utf-8")

    assert 'href="/municipalities/tokyo"' in nationwide_page
    assert '"/municipalities/tokyo"' in sitemap
    assert 'prefectureCode === "13"' in explorer
    assert 'category === "kpi_source"' in explorer
    assert 'return "reviewed"' in explorer
