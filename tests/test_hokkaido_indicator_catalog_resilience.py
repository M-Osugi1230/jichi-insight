import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
CATALOG = POLICY / "hokkaido_indicator_catalog_resilience.json"
SCHEMA = ROOT / "schemas/hokkaido_indicator_catalog.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_catalog_schema_sequence_and_pages():
    data = load(CATALOG)
    validator = Draft202012Validator(
        load(SCHEMA),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(data)) == []
    assert (data["indicator_number_start"], data["indicator_number_end"]) == (86, 91)
    assert [item["indicator_number"] for item in data["items"]] == list(range(86, 92))
    assert [item["source_page"] for item in data["items"]] == list(range(1, 7))


def test_catalog_matches_verified_page_index():
    data = load(CATALOG)
    index = {
        item["indicator_number"]: item
        for item in load(ROOT / "data/catalog/hokkaido_indicator_page_index.json")[
            "records"
        ]
    }
    for item in data["items"]:
        page = index[item["indicator_number"]]
        assert page["source_id"] == data["source_id"]
        assert page["page_number"] == item["source_page"]
        assert page["policy_field_id"] == data["policy_field_id"]


def test_exact_names_values_and_snapshot_scopes_are_preserved():
    items = {item["indicator_number"]: item for item in load(CATALOG)["items"]}
    assert [items[number]["indicator_name_original"] for number in range(86, 92)] == [
        "一定の浸水被害を防止できる河川の整備延長",
        "土砂災害から保全される人家戸数",
        "高波等被害のおそれのある人家戸数",
        "緊急輸送道路上の橋梁の耐震化率",
        "災害拠点病院における浸水等対策率",
        "自主防災組織活動カバー率",
    ]
    assert [
        [value["value"] for value in items[number]["series"][0]["values"]]
        for number in range(86, 92)
    ] == [
        [3145, 3210, 3280],
        [26900, 29000, 31000],
        [37590, 36940, 36440],
        [65.2, 67.0, 71.8],
        [73.3, 86.0, 100],
        [75.6, 86.2, 87.7],
    ]
    assert all(
        items[number]["series"][0]["temporal_scope"] == "snapshot"
        for number in range(86, 92)
    )
    assert all(
        value["aggregation_scope"] == "snapshot"
        for number in range(86, 92)
        for value in items[number]["series"][0]["values"]
    )


def test_reference_breakdowns_missing_years_and_publication_lags_are_separated():
    items = {item["indicator_number"]: item for item in load(CATALOG)["items"]}
    assert "公表時期" in items[86]["comparability_note_original"]
    assert "翌年3月頃" in items[87]["comparability_note_original"]
    assert "データがない年" in items[88]["comparability_note_original"]
    assert "建設管理部所管地域別" in items[89]["comparability_note_original"]
    assert "対象15病院" in items[90]["comparability_note_original"]
    assert "2020年度以前" in items[90]["comparability_note_original"]
    assert "振興局別" in items[91]["comparability_note_original"]
    assert "翌年1月頃" in items[91]["comparability_note_original"]
    assert all(len(items[number]["series"]) == 1 for number in range(86, 92))


def test_catalog_keeps_actuals_and_evaluations_unlinked():
    items = load(CATALOG)["items"]
    assert all(item["actual_linkage_status"] == "not_linked" for item in items)
    assert all(item["evaluation_status"] == "not_assessed" for item in items)
