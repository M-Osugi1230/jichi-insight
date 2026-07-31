from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase10_public_page_and_uniform_loader_exist():
    page = read("apps/web/app/municipalities/phase10/page.tsx")
    loader = read("apps/web/lib/phase10.ts")
    css = read("apps/web/app/municipalities/phase10/phase10.module.css")

    for required in (
        "47都道府県を、同じ深さまで掘る。",
        "深い県だけで、全国対応とは呼ばない。",
        "全47都道府県の深度差を、そのまま表示。",
        "部分完了なし",
        "目標へ接続",
        "公式資料入口",
        "予算 / 決算 入口以上",
    ):
        assert required in page

    assert "phase10_uniformity.json" in loader
    assert "loadPhase10Uniformity" in loader
    assert "phase10UniformRecords" in loader
    assert "phase10UniformSummary" in loader
    assert ".depthMatrix" in css
    assert '.depthState[data-state="linked"]' in css


def test_phase10_is_linked_from_phase9_and_sitemap():
    phase9 = read("apps/web/app/municipalities/phase9/page.tsx")
    sitemap = read("apps/web/app/sitemap.ts")

    assert 'href="/municipalities/phase10"' in phase9
    assert '"/municipalities/phase10"' in sitemap
