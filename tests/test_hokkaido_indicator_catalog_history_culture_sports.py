import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
CATALOG = POLICY / "hokkaido_indicator_catalog_history_culture_sports.json"
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
    assert (data["indicator_number_start"], data["indicator_number_end"]) == (
        103,
        108,
    )
    assert [item["indicator_number"] for item in data["items"]] == list(
        range(103, 109)
    )
    assert [item["source_page"] for item in data["items"]] == list(
        range(1, 7)
    )


def test_catalog_matches_verified_page_index():
    data = load(CATALOG)
    page_index = load(
        ROOT / "data/catalog/hokkaido_indicator_page_index.json"
    )["records"]
    index = {item["indicator_number"]: item for item in page_index}
    for item in data["items"]:
        page = index[item["indicator_number"]]
        assert page["source_id"] == data["source_id"]
        assert page["page_number"] == item["source_page"]
        assert page["policy_field_id"] == data["policy_field_id"]


def test_exact_names_values_and_periods_are_preserved():
    items = {
        item["indicator_number"]: item
        for item in load(CATALOG)["items"]
    }
    names = [
        items[number]["indicator_name_original"]
        for number in range(103, 109)
    ]
    assert names == [
        "北海道博物館の利用者数",
        "文化会館１館当たりの年間入館者数",
        "アイヌ民族が先住民族であることの認知度",
        "成人の週１回以上スポーツ実施率",
        "本道出身のオリンピック･パラリンピック出場者数",
        "本道出身者のオリンピック･パラリンピックメダル総獲得数",
    ]
    values = [
        [value["value"] for value in items[number]["series"][0]["values"]]
        for number in range(103, 109)
    ]
    assert values == [
        [124391, 152500, 168100],
        [44262, 78000, 78000],
        [84.7, 93.7, 100],
        [62.0, 70.0, 70.0],
        [29, None, None],
        [7, None, None],
    ]
    assert [
        value["period"]
        for value in items[106]["series"][0]["values"]
    ] == ["2021年", "2027年", "2031年"]
    assert [
        value["period"]
        for value in items[107]["series"][0]["values"]
    ] == ["2021年夏季・2022年冬季", "2026年", "2034年"]


def test_past_high_targets_remain_conditional():
    items = {
        item["indicator_number"]: item
        for item in load(CATALOG)["items"]
    }
    references = [(107, "過去最高値60人"), (108, "過去最高値8個")]
    for number, reference_text in references:
        values = items[number]["series"][0]["values"]
        assert values[0]["status"] == "numeric"
        assert all(value["status"] == "conditional" for value in values[1:])
        assert all(value["value"] is None for value in values[1:])
        assert [
            value["value_text_original"] for value in values[1:]
        ] == ["過去最高値", "過去最高値"]
        assert reference_text in items[number]["comparability_note_original"]


def test_reference_breakdowns_and_publication_dates_are_excluded():
    items = {
        item["indicator_number"]: item
        for item in load(CATALOG)["items"]
    }
    assert "北海道観光客数" in items[103]["comparability_note_original"]
    assert "過去推移" in items[104]["comparability_note_original"]
    assert "設問内訳" in items[105]["comparability_note_original"]
    assert "4月1日時点" in items[106]["comparability_note_original"]
    assert "夏季・冬季" in items[107]["comparability_note_original"]
    assert (
        "オリンピック・パラリンピック別内訳"
        in items[108]["comparability_note_original"]
    )


def test_catalog_keeps_actuals_and_evaluations_unlinked():
    items = load(CATALOG)["items"]
    assert all(item["actual_linkage_status"] == "not_linked" for item in items)
    assert all(item["evaluation_status"] == "not_assessed" for item in items)
