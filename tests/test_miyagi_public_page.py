from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "apps/web/app/municipalities/miyagi/page.tsx"
STYLES = ROOT / "apps/web/app/municipalities/miyagi/page.module.css"
COVERAGE = ROOT / "apps/web/lib/nationwideCoverage.ts"
MUNICIPALITIES = ROOT / "apps/web/app/municipalities/page.tsx"
SITEMAP = ROOT / "apps/web/app/sitemap.ts"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_miyagi_page_copy_and_boundaries():
    page = read(PAGE)
    assert STYLES.is_file()
    assert "柱1〜3と取組1〜13" in page
    assert "次は取組14の目標101〜104" in page
    assert "累計値。単年度値ではありません。" in page
    assert "成果の達成率ではなく" in page
    assert "direction.display_order <= 3" in page


def test_miyagi_page_links_and_dynamic_counts():
    coverage = read(COVERAGE)
    municipalities = read(MUNICIPALITIES)
    sitemap = read(SITEMAP)
    assert 'record.prefecture_code === "04"' in coverage
    assert '"/municipalities/miyagi"' in coverage
    assert 'href="/municipalities/miyagi"' in municipalities
    assert "miyagiPolicyReviewStats.reviewedTargetGroups" in municipalities
    assert "miyagiPolicyReviewStats.remainingTargetGroups" in municipalities
    assert "miyagiPolicyReviewStats.reviewedIndicatorSeries" in municipalities
    assert "次は取組14の目標101〜104" in municipalities
    assert '"/municipalities/miyagi"' in sitemap
