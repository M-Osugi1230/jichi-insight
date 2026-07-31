from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_kanto_depth_page_publishes_review_evidence_and_boundaries():
    page = read("apps/web/app/municipalities/phase10/kanto/page.tsx")
    loader = read("apps/web/lib/phase10RegionalDepth.ts")
    shared_css = read(
        "apps/web/app/municipalities/phase10/tohoku/page.module.css"
    )

    for required in (
        "関東6県も、同じ5層をReviewed化。",
        "6県×5層の公式資料と、残る接続作業。",
        "新旧計画、政策評価、公共事業評価を混同しない。",
        "5層Reviewed",
        "関東の次は、中部8県を同じ工程で確認する。",
    ):
        assert required in page

    assert "phase10_kanto_depth_reviews.json" in loader
    assert "loadPhase10KantoDepth" in loader
    assert "regionalDepthLabels" in loader
    assert ".prefectureGrid" in shared_css
    assert ".sourceList" in shared_css
    assert ".nextAction" in shared_css


def test_phase10_navigation_and_sitemap_link_kanto_page():
    layout = read("apps/web/app/municipalities/phase10/layout.tsx")
    sitemap = read("apps/web/app/sitemap.ts")

    assert 'href="/municipalities/phase10/kanto"' in layout
    assert "関東6県の深掘り" in layout
    assert '"/municipalities/phase10/kanto"' in sitemap
