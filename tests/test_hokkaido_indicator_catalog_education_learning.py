import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = (
    ROOT
    / "data/entities/policy/"
    "hokkaido_indicator_catalog_education_learning.json"
)
SCHEMA_PATH = ROOT / "schemas/hokkaido_indicator_catalog.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_education_learning_catalog_matches_schema_and_sequence():
    catalog = load(CATALOG_PATH)
    validator = Draft202012Validator(
        load(SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(catalog)) == []
    assert catalog["indicator_number_start"] == 53
    assert catalog["indicator_number_end"] == 60
    assert [item["indicator_number"] for item in catalog["items"]] == list(
        range(53, 61)
    )
    assert [item["source_page"] for item in catalog["items"]] == list(
        range(1, 9)
    )


def test_catalog_matches_verified_page_index():
    catalog = load(CATALOG_PATH)
    index = load(ROOT / "data/catalog/hokkaido_indicator_page_index.json")
    pages = {item["indicator_number"]: item for item in index["records"]}
    for item in catalog["items"]:
        page = pages[item["indicator_number"]]
        assert page["source_id"] == catalog["source_id"]
        assert page["page_number"] == item["source_page"]
        assert page["policy_field_id"] == catalog["policy_field_id"]


def test_exact_names_and_values_are_preserved():
    items = {
        item["indicator_number"]: item
        for item in load(CATALOG_PATH)["items"]
    }
    assert [
        items[number]["indicator_name_original"]
        for number in range(53, 61)
    ] == [
        "全国学力・学習状況調査の平均正答率が全国以上の教科数",
        "体力・運動能力の全国比",
        "キャリア教育に資する体験的な学習活動の実施率",
        "授業におけるＩＣＴ機器の活用率",
        "生涯学習の成果を活用している住民の割合",
        "いじめはいけないことだと考える児童・生徒の割合",
        "いじめの解消状況",
        "少年千人当たりの刑法犯少年数",
    ]
    assert [
        [value["value"] for value in items[53]["series"][0]["values"]],
        [[value["value"] for value in series["values"]] for series in items[54]["series"]],
        [value["value"] for value in items[55]["series"][0]["values"]],
        [[value["value"] for value in series["values"]] for series in items[56]["series"]],
        [value["value"] for value in items[57]["series"][0]["values"]],
        [[value["value"] for value in series["values"]] for series in items[58]["series"]],
        [[value["value"] for value in series["values"]] for series in items[59]["series"]],
        [value["value"] for value in items[60]["series"][0]["values"]],
    ] == [
        [0, 4, 4],
        [[47.0, 50, 50], [48.2, 50, 50], [49.4, 50, 50], [49.6, 50, 50]],
        [42.7, 88.0, 100],
        [[70.1, 100, 100], [76.6, 100, 100]],
        [59.5, 80.0, 80.0],
        [[85.6, 100, 100], [82.6, 100, 100]],
        [[92.6, 100, 100], [93.6, 100, 100], [92.2, 100, 100]],
        [3.3, 1.8, 1.6],
    ]


def test_multiple_school_and_sex_series_are_preserved():
    items = {
        item["indicator_number"]: item
        for item in load(CATALOG_PATH)["items"]
    }
    assert [series["label"] for series in items[54]["series"]] == [
        "小学校男子", "小学校女子", "中学校男子", "中学校女子"
    ]
    assert [series["label"] for series in items[56]["series"]] == [
        "小学校", "中学校"
    ]
    assert [series["label"] for series in items[58]["series"]] == [
        "小学校", "中学校"
    ]
    assert [series["label"] for series in items[59]["series"]] == [
        "小学校", "中学校", "高校"
    ]


def test_explicit_zero_and_hundred_targets_are_numeric():
    items = {
        item["indicator_number"]: item
        for item in load(CATALOG_PATH)["items"]
    }
    assert items[53]["series"][0]["values"][0]["value"] == 0
    assert items[53]["series"][0]["values"][0]["status"] == "numeric"
    for number in (55, 56, 58, 59):
        assert all(
            value["status"] == "numeric"
            for series in items[number]["series"]
            for value in series["values"]
        )


def test_reference_graph_values_are_not_added_as_target_series():
    items = {
        item["indicator_number"]: item
        for item in load(CATALOG_PATH)["items"]
    }
    assert len(items[55]["series"]) == 1
    assert len(items[59]["series"]) == 3
    assert len(items[60]["series"]) == 1
    assert "参考掲載" in items[59]["comparability_note_original"]
    assert "総数や成人" in items[60]["comparability_note_original"]


def test_catalog_keeps_actuals_and_evaluations_unlinked():
    catalog = load(CATALOG_PATH)
    assert all(item["actual_linkage_status"] == "not_linked" for item in catalog["items"])
    assert all(item["evaluation_status"] == "not_assessed" for item in catalog["items"])
    assert not any("score" in item or "progress_rate" in item for item in catalog["items"])
