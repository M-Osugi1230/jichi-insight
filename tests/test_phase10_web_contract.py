from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase10_public_page_and_loader_exist():
    page = read("apps/web/app/municipalities/phase10/page.tsx")
    loader = read("apps/web/lib/phase10.ts")
    css = read("apps/web/app/municipalities/phase10/phase10.module.css")

    for required in (
        "目標から、実績・予算・事業へつなぐ。",
        "資料がある",
        "9地域拠点の接続状態。",
        "政策評価は未判定",
        "宮城県：年度実績の次に、予算・事業・契約をつなぐ。",
        "公式資料入口",
        "事業・契約 入口確認",
    ):
        assert required in page

    assert "phase10_execution_queue.json" in loader
    assert "phase10_wave1_source_inventory.json" in loader
    assert "loadPhase10SourceInventory" in loader
    assert "phase10SourcesByPrefecture" in loader
    assert "phase10DepthLabel" in loader
    assert ".prefectureGrid" in css
    assert ".sourceList" in css


def test_phase10_is_linked_from_phase9_and_sitemap():
    phase9 = read("apps/web/app/municipalities/phase9/page.tsx")
    sitemap = read("apps/web/app/sitemap.ts")

    assert 'href="/municipalities/phase10"' in phase9
    assert '"/municipalities/phase10"' in sitemap
