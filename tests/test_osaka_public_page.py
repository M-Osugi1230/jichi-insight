from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE_PATH = ROOT / "apps/web/app/municipalities/osaka/page.tsx"
LIB_PATH = ROOT / "apps/web/lib/osakaIndicators.ts"
EXPLORER_PATH = ROOT / "apps/web/components/OsakaIndicatorExplorer.tsx"
SITEMAP_PATH = ROOT / "apps/web/app/sitemap.ts"
NATIONWIDE_PATH = ROOT / "apps/web/app/municipalities/page.tsx"


def test_osaka_page_exposes_reviewed_scope_without_claiming_achievement():
    page = PAGE_PATH.read_text(encoding="utf-8")
    explorer = EXPLORER_PATH.read_text(encoding="utf-8")

    assert "大阪府の戦略目標とWell-Beingを、同じ点数にしない。" in page
    assert "政策の達成判定ではありません" in page
    assert "名目GDP80兆円" in page
    assert "旧戦略の実績" in page
    assert "事業費を指標達成の因果関係として扱いません" in page
    assert "政策評価 未判定" in explorer


def test_osaka_page_supports_layer_and_scale_boundaries():
    page = PAGE_PATH.read_text(encoding="utf-8")
    explorer = EXPLORER_PATH.read_text(encoding="utf-8")
    model = LIB_PATH.read_text(encoding="utf-8")

    assert "83指標を、レイヤー・分野・値から探す。" in page
    assert "指標レイヤー" in explorer
    assert "主観・Well-Being" in explorer
    assert "0〜10点尺度" in explorer
    assert "逆転項目" in explorer
    assert "初回調査待ち" in explorer
    assert "separate_lineage" in model
    assert "rank" in model
    assert "cumulative" in model


def test_osaka_route_is_linked_from_nationwide_page_and_sitemap():
    sitemap = SITEMAP_PATH.read_text(encoding="utf-8")
    nationwide = NATIONWIDE_PATH.read_text(encoding="utf-8")

    assert '"/municipalities/osaka"' in sitemap
    assert 'href="/municipalities/osaka"' in nationwide
    assert "大阪府の政策指標を見る" in nationwide
