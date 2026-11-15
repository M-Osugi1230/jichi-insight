"""Public UI v2 contracts: user-first navigation must not weaken data provenance."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "apps" / "web"


def source(relative: str) -> str:
    return (WEB / relative).read_text(encoding="utf-8")


def test_home_search_is_restricted_to_reviewed_coverage():
    home = source("app/page.tsx")
    search = source("components/MunicipalityQuickSearch.tsx")

    assert "reviewedPrefectureCoverage.map" in home
    assert "loadPhase15CitySummaries().map" in home
    assert "MunicipalityQuickSearch entries={searchEntries}" in home
    assert "data/candidates" not in home
    assert 'kind: "prefecture" as const' in home
    assert 'kind: "city" as const' in home
    assert "全国すべての市区町村ではありません" in search
    assert 'type="search"' in search
    assert 'role="search"' in search
    assert 'aria-live="polite"' in search
    assert "firstResult.current?.focus()" in search


def test_directory_places_real_search_before_administrative_metrics():
    page = source("app/municipalities/page.tsx")
    assert page.index("<CoverageExplorer />") < page.index(
        'className={styles.overview}'
    )
    assert 'id="prefectures"' in page
    assert 'id="reviewed-cities"' in page
    assert "すべての市区町村が同じ深さで閲覧できるわけではありません" in page


def test_city_profile_shows_provenance_and_separates_budget_from_settlement():
    page = source("app/municipalities/[slug]/page.tsx")
    overview = source("components/CityOverview.tsx")

    assert "<CityOverview city={city} />" in page
    assert '"initial_budget"' in overview
    assert '"settlement"' in overview
    assert '"total_revenue"' in overview
    assert '"total_expenditure"' in overview
    assert 'record.valueStatus !== "available"' in overview
    assert "record.amountYen === null" in overview
    assert "record.sources[0].officialUrl" in overview
    assert "原資料の値（円換算）" in overview
    assert "小数第1位まで丸めた概数" in overview
    assert "単純な増減比較や政策達成評価は行いません" in overview
    assert "city.lastVerifiedAt" in overview
    assert "city.completionBoundary" in page
    assert "city.qualityBoundary" in page


def test_city_profile_jump_links_have_matching_anchors():
    page = source("app/municipalities/[slug]/page.tsx")
    overview = source("components/CityOverview.tsx")

    for anchor in (
        "city-summary-title",
        "promise-title",
        "money-title",
        "linkage-title",
        "sources-title",
        "boundary-title",
    ):
        assert f'href="#{anchor}"' in overview
        assert f'id="{anchor}"' in overview + page


def test_verified_values_are_still_displayed_exactly_in_detail():
    page = source("app/municipalities/[slug]/page.tsx")
    assert "formatYen(record.amountYen)" in page
    assert "record.note" in page
    assert "record.periodStart" in page
    assert "record.periodEnd" in page
    assert "record.sources.map" in page
    assert "判定レコードを作成していません" in page
