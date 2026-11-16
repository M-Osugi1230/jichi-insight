"""Contracts for the map-first homepage (no false municipality coverage)."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "apps/web"


def read(path: str) -> str:
    return (WEB / path).read_text(encoding="utf-8")


def test_map_has_all_47_known_prefectures_and_cc0_attribution():
    text = read("lib/japanMapPaths.ts")
    assert "CC0 1.0 Universal" in text
    assert "lalamalink/japan-map-svg" in text
    payload = text.split("export const japanMapPaths: JapanMapPath[] = ", 1)[1]
    records = json.loads(payload.strip().rstrip(";"))
    actual = {(record["code"], record["name"]) for record in records}
    catalog_path = ROOT / "data/catalog/prefecture_coverage.json"
    registry = json.loads(catalog_path.read_text(encoding="utf-8"))
    expected = {
        (record["prefecture_code"], record["name"])
        for record in registry["records"]
    }
    assert len(records) == len(actual) == 47
    assert actual == expected
    assert all(record["d"].startswith("M ") for record in records)


def test_map_navigation_uses_only_published_prefectures_and_reviewed_cities():
    home = read("app/page.tsx")
    map_component = read("components/JapanMapExplorer.tsx")
    assert "reviewedPrefectureCoverage.map" in home
    assert "loadPhase15CitySummaries().map" in home
    assert "prefectures={reviewedPrefectureCoverage.map" in home
    assert "cities={loadPhase15CitySummaries().map" in home
    assert "data/candidates" not in home + map_component
    assert 'item.prefecture === selected.name' in map_component
    assert "市の詳細は一次資料レビュー完了分のみ公開" in map_component
    assert "この都道府県では、市の詳細レビュー済みページはまだありません。" in map_component


def test_map_selection_is_keyboard_accessible_and_has_text_alternative():
    map_component = read("components/JapanMapExplorer.tsx")
    assert "event.key === \"Enter\"" in map_component
    assert "event.key === \" \"" in map_component
    assert "tabIndex={0}" in map_component
    assert "aria-pressed={isSelected}" in map_component
    assert 'role="button"' in map_component
    assert "regionPrefectures.map" in map_component
    assert "reviewedCities.map" in map_component
    assert 'aria-live="polite"' in map_component
    assert 'href="/municipalities#prefectures"' in map_component


def test_long_form_home_content_is_optional_and_not_the_first_screen():
    home = read("app/page.tsx")
    styles = read("app/page.module.css")
    assert home.index("<JapanMapExplorer") < home.index("styles.mapDeepDive")
    assert "<details className={styles.mapDeepDive}>" in home
    assert "MunicipalityQuickSearch entries={searchEntries}" in home
    assert ".mapQuickLinks" in styles
    assert ".mapDeepDive" in styles
    assert "@media (max-width: 760px)" in read("components/JapanMapExplorer.module.css")
