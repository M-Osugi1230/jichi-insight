from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_fukuoka_actual_loader_preserves_separate_linkage_layer():
    loader = read("apps/web/lib/fukuokaAnnualActuals.ts")

    for required in (
        "fukuoka_annual_actual_linkage.json",
        "fukuoka_annual_actual_linkage_part_01.json",
        "fukuoka_annual_actual_linkage_part_02.json",
        "fukuoka_annual_actual_linkage_part_03.json",
        "fukuoka_annual_actual_linkage_part_04.json",
        "fukuokaAnnualActualForTarget",
        "fukuokaAnnualActualStatusLabel",
        'linked: "年度実績へ接続"',
        'partial: "目標版の再確認"',
        'not_linked: "別資料を探索"',
    ):
        assert required in loader


def test_fukuoka_actual_page_publishes_counts_values_and_boundaries():
    page = read(
        "apps/web/app/municipalities/phase10/fukuoka-actuals/page.tsx"
    )
    css = read(
        "apps/web/app/municipalities/phase10/fukuoka-actuals/page.module.css"
    )

    for required in (
        "118目標を、年度実績へ一件ずつ照合。",
        "年度実績へ接続",
        "目標版の再確認",
        "別資料を探索",
        "接続と評価を分ける。",
        "PDF {actual.source_pdf_page}頁",
        "報告書の目標値を別版として保持",
        "実績接続後も政策達成評価は行いません。",
    ):
        assert required in page

    assert ".actualTable" in css
    assert '.status[data-status="partial"]' in css
    assert '.status[data-status="not_linked"]' in css


def test_fukuoka_actual_page_is_linked_and_indexed():
    layout = read("apps/web/app/municipalities/phase10/layout.tsx")
    sitemap = read("apps/web/app/sitemap.ts")
    route = "/municipalities/phase10/fukuoka-actuals"

    assert f'href="{route}"' in layout
    assert "福岡県118目標の実績接続" in layout
    assert f'"{route}"' in sitemap
