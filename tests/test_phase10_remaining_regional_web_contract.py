from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_shared_regional_page_preserves_review_boundaries():
    component = read("apps/web/components/Phase10RegionalDepthPage.tsx")
    loader = read("apps/web/lib/phase10RegionalDepth.ts")

    for required in (
        "5層Reviewed",
        "次の接続",
        "資料確認だけで達成・未達を判定しません。",
        "regionalDepthLabels",
        "source.boundary",
        "record.next_linkage",
    ):
        assert required in component

    for loader_name in (
        "loadPhase10KinkiDepth",
        "loadPhase10ChugokuDepth",
        "loadPhase10ShikokuDepth",
        "loadPhase10KyushuDepth",
    ):
        assert loader_name in loader


def test_remaining_regional_pages_use_shared_component():
    pages = {
        "kinki": "近畿6府県も、同じ5層をReviewed化。",
        "chugoku": "中国4県も、同じ5層をReviewed化。",
        "shikoku": "四国3県も、同じ5層をReviewed化。",
        "kyushu": "九州6県も、同じ5層をReviewed化。",
    }

    for slug, title in pages.items():
        page = read(f"apps/web/app/municipalities/phase10/{slug}/page.tsx")
        assert "Phase10RegionalDepthPage" in page
        assert title in page
        assert "Reviewed" in page


def test_navigation_sitemap_and_index_cover_all_regional_pages():
    layout = read("apps/web/app/municipalities/phase10/layout.tsx")
    sitemap = read("apps/web/app/sitemap.ts")
    index = read("data/catalog/phase10_regional_depth_index.json")

    for slug in (
        "tohoku",
        "kanto",
        "chubu",
        "kinki",
        "chugoku",
        "shikoku",
        "kyushu",
    ):
        route = f"/municipalities/phase10/{slug}"
        assert f'href="{route}"' in layout
        assert f'"{route}"' in sitemap
        assert f'"route":"{route}"' in index
        assert f'"slug":"{slug}"' in index
