from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_chubu_page_publishes_reviewed_sources_and_boundaries():
    page = read("apps/web/app/municipalities/phase10/chubu/page.tsx")
    loader = read("apps/web/lib/phase10RegionalDepth.ts")
    phase10_loader = read("apps/web/lib/phase10.ts")
    uniformity = read("data/catalog/phase10_uniformity.json")

    for required in (
        "中部8県も、同じ5層をReviewed化。",
        "8県×5層の公式資料と、残る接続作業。",
        "岐阜県は包括的な年度実績資料を追加確保",
        "5層Reviewed",
        "次の接続",
    ):
        assert required in page

    assert "loadPhase10ChubuDepth" in loader
    assert "phase10_regional_depth_index.json" in loader
    assert "phase10_regional_depth_index.json" in phase10_loader
    assert "atLeastDepth" in phase10_loader
    assert '"annual_actuals": "linked"' in uniformity
    assert '"settlement": "linked"' in uniformity


def test_chubu_route_is_linked_and_indexed():
    layout = read("apps/web/app/municipalities/phase10/layout.tsx")
    sitemap = read("apps/web/app/sitemap.ts")

    assert 'href="/municipalities/phase10/chubu"' in layout
    assert '"/municipalities/phase10/chubu"' in sitemap
