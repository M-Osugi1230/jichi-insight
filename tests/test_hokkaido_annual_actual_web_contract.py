from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "apps/web/app/municipalities/phase10/hokkaido-actuals/page.tsx"
LIB = ROOT / "apps/web/lib/hokkaidoAnnualActuals.ts"
LAYOUT = ROOT / "apps/web/app/municipalities/phase10/layout.tsx"
SITEMAP = ROOT / "apps/web/app/sitemap.ts"


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_hokkaido_page_publishes_linkage_and_definition_boundaries():
    page = text(PAGE)

    assert "108指標を、公式番号で年度実績へ接続" in page
    assert "同じ番号でも、定義や単位が違えばつながない" in page
    assert "summary.partial_record_count" in page
    assert "単位スケール" in page
    assert "政策達成判定" in page
    assert "達成・未達の判断を分離" in page
    assert "hokkaidoAnnualActualRecords" in page
    assert "related_source_locations.length" in page


def test_hokkaido_library_loads_both_registry_parts():
    library = text(LIB)

    assert "hokkaido_annual_actual_linkage.json" in library
    assert "hokkaido_annual_actual_linkage_part_01.json" in library
    assert "hokkaido_annual_actual_linkage_part_02.json" in library
    assert "年度実績へ接続" in library
    assert "版・定義の確認が必要" in library
    assert "目標版が変更" in library
    assert "単位スケールの換算が必要" in library


def test_hokkaido_route_is_in_navigation_and_sitemap():
    route = "/municipalities/phase10/hokkaido-actuals"

    assert route in text(LAYOUT)
    assert "北海道108指標の実績接続" in text(LAYOUT)
    assert route in text(SITEMAP)
