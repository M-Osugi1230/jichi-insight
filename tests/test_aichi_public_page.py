from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE_PATH = ROOT / "apps/web/app/municipalities/aichi/page.tsx"
LIB_PATH = ROOT / "apps/web/lib/aichiIndicators.ts"
EXPLORER_PATH = ROOT / "apps/web/components/AichiIndicatorExplorer.tsx"
SITEMAP_PATH = ROOT / "apps/web/app/sitemap.ts"
NATIONWIDE_PATH = ROOT / "apps/web/app/municipalities/page.tsx"


def test_aichi_public_page_exposes_reviewed_scope_without_claiming_achievement():
    page = PAGE_PATH.read_text(encoding="utf-8")

    assert "愛知県の目標と年次現状値を、定義を変えずに読む。" in page
    assert "政策成果の独自評価ではありません" in page
    assert "56指標" in page
    assert "政策評価 未判定" in EXPLORER_PATH.read_text(encoding="utf-8")
    assert "管理事業評価" in page
    assert "自動転用していません" in page


def test_aichi_page_supports_search_and_semantic_boundaries():
    explorer = EXPLORER_PATH.read_text(encoding="utf-8")
    data_model = LIB_PATH.read_text(encoding="utf-8")

    assert "指標名・値・年度から探す" in explorer
    assert "政策の方向性" in explorer
    assert "再掲・重複集計しない" in explorer
    assert "進捗目標の改定あり" in explorer
    assert "数値目標なし" in explorer
    assert "comparability_note_original" in explorer
    assert "multi_period_average" in data_model
    assert "cumulative" in data_model
    assert "missing" in data_model


def test_aichi_route_is_linked_from_nationwide_page_and_sitemap():
    sitemap = SITEMAP_PATH.read_text(encoding="utf-8")
    nationwide = NATIONWIDE_PATH.read_text(encoding="utf-8")

    assert '"/municipalities/aichi"' in sitemap
    assert 'href="/municipalities/aichi"' in nationwide
    assert "愛知県の進捗指標を見る" in nationwide
