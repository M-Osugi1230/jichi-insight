from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase10_public_page_exposes_completion_and_boundaries():
    page = read("apps/web/app/municipalities/phase10/page.tsx")
    loader = read("apps/web/lib/phase10.ts")
    css = read("apps/web/app/municipalities/phase10/phase10.module.css")

    for required in (
        "47都道府県を、同じ深さまで掘る。",
        "2026年8月1日に全都道府県で完了しました。",
        "Phase 10 完了",
        "Completed on 2026-08-01",
        "文書スコープLinked",
        "不存在を断定しない公式検索結果までReviewed",
        "個別の目標、予算科目、事業",
        "政策の達成・未達は判定せず",
        "部分完了なし",
        "47都道府県すべてが共通ゲートへ到達",
        "全47都道府県が到達した共通深度",
        "未特定を不存在とは扱いません",
    ):
        assert required in page

    assert 'aria-label="Phase 10完了宣言"' in page
    assert 'aria-label="Phase 10完了状況"' in page
    assert "phase10_uniformity.json" in loader
    assert "phase10_reference_depth_reviews.json" in loader
    assert "phase10_anchor_depth_reviews.json" in loader
    assert "loadPhase10Uniformity" in loader
    assert "phase10UniformRecords" in loader
    assert "phase10UniformSummary" in loader
    assert "atLeastDepth" in loader
    assert ".depthMatrix" in css
    assert '.depthState[data-state="linked"]' in css
    assert ".reviewGrid" in css
    assert ".anchorReviewGrid" in css


def test_phase10_is_linked_from_phase9_and_sitemap():
    phase9 = read("apps/web/app/municipalities/phase9/page.tsx")
    sitemap = read("apps/web/app/sitemap.ts")

    assert 'href="/municipalities/phase10"' in phase9
    assert '"/municipalities/phase10"' in sitemap
