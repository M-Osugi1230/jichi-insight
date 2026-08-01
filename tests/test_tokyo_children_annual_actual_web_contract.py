from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "apps/web/app/municipalities/phase10/tokyo-children-actuals/page.tsx"
LIB = ROOT / "apps/web/lib/tokyoChildrenActuals.ts"
LAYOUT = ROOT / "apps/web/app/municipalities/phase10/layout.tsx"
SITEMAP = ROOT / "apps/web/app/sitemap.ts"


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_tokyo_children_page_publishes_version_and_conflict_boundaries():
    page = text(PAGE)

    assert "子供分野8目標を、同じ戦略内の政策レビューへ接続" in page
    assert "旧「未来の東京」戦略の実績は混ぜず" in page
    assert "同じ戦略でも、文書の時点差を上書きしない" in page
    assert "44自治体" in page
    assert "47自治体" in page
    assert "政策達成判定" in page
    assert "tokyoChildrenAnnualActualRecords" in page
    assert "Object.entries(record.conflict)" in page


def test_tokyo_children_library_keeps_linked_and_partial_states_distinct():
    library = text(LIB)

    assert "tokyo_children_annual_actual_linkage.json" in library
    assert "年度実績へ接続" in library
    assert "文書間の差異を確認" in library
    assert "実績期間が不一致" in library
    assert "実績値と期間が不一致" in library


def test_tokyo_children_route_is_in_navigation_and_sitemap():
    route = "/municipalities/phase10/tokyo-children-actuals"

    assert route in text(LAYOUT)
    assert "東京都子供分野8目標の実績接続" in text(LAYOUT)
    assert route in text(SITEMAP)
