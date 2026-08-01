from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "apps/web/app/municipalities/phase10/fukuoka-projects/page.tsx"
LIB = ROOT / "apps/web/lib/fukuokaProjectLinkage.ts"
LAYOUT = ROOT / "apps/web/app/municipalities/phase10/layout.tsx"
SITEMAP = ROOT / "apps/web/app/sitemap.ts"


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_fukuoka_project_page_exposes_candidate_boundaries():
    page = text(PAGE)

    assert "266重点事業を、予算・決算・118目標へ照合" in page
    assert "候補は、完成済みの接続ではない" in page
    assert "県全体のLinked件数に加算しません" in page
    assert "別年度・別役割の金額" in page
    assert "17目標" in page
    assert "fukuokaProjectLinkageRecords" in page
    assert "record.budget_matches.map" in page
    assert "record.settlement_matches.map" in page


def test_fukuoka_project_library_loads_all_three_parts():
    library = text(LIB)

    for number in range(1, 4):
        assert f"fukuoka_project_linkage_part_{number:02d}.json" in library
    assert "fukuoka_project_linkage.json" in library
    assert "完全名称一致候補" in library
    assert "追加確認が必要" in library
    assert "金額資料への接続なし" in library


def test_fukuoka_project_route_is_in_navigation_and_sitemap():
    route = "/municipalities/phase10/fukuoka-projects"

    assert route in text(LAYOUT)
    assert "福岡県266重点事業の接続候補" in text(LAYOUT)
    assert route in text(SITEMAP)
