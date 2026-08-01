from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_tohoku_depth_page_publishes_review_evidence_and_boundaries():
    page = read("apps/web/app/municipalities/phase10/tohoku/page.tsx")
    css = read("apps/web/app/municipalities/phase10/tohoku/page.module.css")
    loader = read("apps/web/lib/phase10RegionalDepth.ts")
    index = read("data/catalog/phase10_regional_depth_index.json")

    for required in (
        "東北5県も、同じ5層をReviewed化。",
        "5県×5層の公式資料と、残る接続作業。",
        "旧計画と現行計画、予算と決算を混ぜない。",
        "5層Reviewed",
        "東北の次は、関東6県を同じ工程で確認する。",
    ):
        assert required in page

    assert "phase10_tohoku_depth_reviews.json" in index
    assert "loadPhase10TohokuDepth" in loader
    assert "loadPhase10RegionalDepthBySlug" in loader
    assert "regionalDepthLabels" in loader
    assert ".prefectureGrid" in css
    assert ".sourceList" in css
    assert ".nextAction" in css


def test_phase10_navigation_and_sitemap_link_tohoku_page():
    layout = read("apps/web/app/municipalities/phase10/layout.tsx")
    layout_css = read("apps/web/app/municipalities/phase10/layout.module.css")
    sitemap = read("apps/web/app/sitemap.ts")

    assert 'href="/municipalities/phase10/tohoku"' in layout
    assert "東北5県の深掘り" in layout
    assert ".phaseNav" in layout_css
    assert '"/municipalities/phase10/tohoku"' in sitemap
