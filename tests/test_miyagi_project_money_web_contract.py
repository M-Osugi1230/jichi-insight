from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "apps/web/app/municipalities/phase10/miyagi-money/page.tsx"
LIB = ROOT / "apps/web/lib/miyagiProjectMoney.ts"
LAYOUT = ROOT / "apps/web/app/municipalities/phase10/layout.tsx"
SITEMAP = ROOT / "apps/web/app/sitemap.ts"


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_miyagi_money_page_publishes_reviewed_summary_and_boundaries():
    page = text(PAGE)

    assert "627事業の予算と決算を、施策単位で照合" in page
    assert "同一施策、同一事業名、同一部局、同一担当課" in page
    assert "金額の接続と、成果の評価を分ける" in page
    assert "令和8年度予算額と令和6年度決算額は異なる年度" in page
    assert "miyagiProjectMoneyLinkage.summary" in page
    assert "miyagiProjectMoneyRecords" in page
    assert "settlement_candidates.length" in page


def test_miyagi_money_library_loads_all_four_registry_parts():
    library = text(LIB)

    for number in range(1, 5):
        assert f"miyagi_project_money_linkage_part_{number:02d}.json" in library
    assert "miyagi_project_money_linkage.json" in library
    assert "同一事業系列へ接続" in library
    assert "追加確認が必要" in library
    assert "前年度同一事業なし" in library


def test_miyagi_money_route_is_in_navigation_and_sitemap():
    route = "/municipalities/phase10/miyagi-money"

    assert route in text(LAYOUT)
    assert "宮城県627事業の予算・決算接続" in text(LAYOUT)
    assert route in text(SITEMAP)
