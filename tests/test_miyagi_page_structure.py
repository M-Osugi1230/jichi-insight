from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "apps/web/app/municipalities/miyagi/page.tsx"
LIBRARY = ROOT / "apps/web/lib/miyagiPolicies.ts"
COVERAGE = ROOT / "apps/web/lib/nationwideCoverage.ts"
MUNICIPALITIES = ROOT / "apps/web/app/municipalities/page.tsx"
SITEMAP = ROOT / "apps/web/app/sitemap.ts"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_miyagi_page_uses_dynamic_catalog_totals_and_all_scopes():
    page = read(PAGE)
    library = read(LIBRARY)
    assert "miyagiPolicyReviewStats.reviewedTargetGroups" in page
    assert "miyagiPolicyReviewStats.remainingTargetGroups" in page
    assert "miyagiKpiScopes.map" in page
    assert "measure18Catalog.items" in library
    assert "measure18Evidence" in library
    assert "directionFourMeasures.slice(0, 4)" in library


def test_miyagi_page_is_linked_from_nationwide_surfaces():
    coverage = read(COVERAGE)
    municipalities = read(MUNICIPALITIES)
    sitemap = read(SITEMAP)
    assert 'record.prefecture_code === "04"' in coverage
    assert '"/municipalities/miyagi"' in coverage
    assert 'href="/municipalities/miyagi"' in municipalities
    assert "waveOnePolicyReviewQueue" in municipalities
    assert '"/municipalities/miyagi"' in sitemap
