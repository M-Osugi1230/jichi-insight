import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data/reviewed/osaka_beyond_expo_indicators.json"
EVIDENCE_PATH = ROOT / "data/evidence/osaka_beyond_expo_indicator_evidence.json"
MANIFEST_PATH = ROOT / "data/catalog/osaka_beyond_expo_indicator_review_manifest.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_name: str, instance):
    schema = load(ROOT / "schemas" / schema_name)
    errors = sorted(
        Draft202012Validator(
            schema,
            format_checker=FormatChecker(),
        ).iter_errors(instance),
        key=lambda error: list(error.path),
    )
    assert not errors, [error.message for error in errors]


def test_osaka_catalog_evidence_and_manifest_are_schema_valid():
    validate("osaka_beyond_expo_indicators.schema.json", load(CATALOG_PATH))
    validate(
        "osaka_beyond_expo_indicator_evidence.schema.json",
        load(EVIDENCE_PATH),
    )
    validate(
        "osaka_beyond_expo_indicator_review_manifest.schema.json",
        load(MANIFEST_PATH),
    )


def test_osaka_indicator_counts_match_canonical_data():
    catalog = load(CATALOG_PATH)
    evidence = load(EVIDENCE_PATH)
    manifest = load(MANIFEST_PATH)
    items = catalog["items"]
    series = [series for item in items for series in item["series"]]

    assert len(items) == 83
    assert [item["display_order"] for item in items] == list(range(1, 84))
    assert len(series) == 91
    assert sum(item["indicator_layer"] == "strategy_target" for item in items) == 1
    assert sum(item["indicator_layer"] == "objective_kpi" for item in items) == 27
    assert sum(item["indicator_layer"] == "subjective_wellbeing" for item in items) == 55
    assert evidence["packet_count"] == len(evidence["packets"]) == 83
    assert manifest["reviewed_indicator_row_count"] == 83
    assert manifest["reviewed_indicator_series_count"] == 91
    assert manifest["status"] == "complete"


def test_osaka_evidence_covers_every_indicator_once():
    catalog_ids = {item["id"] for item in load(CATALOG_PATH)["items"]}
    evidence = load(EVIDENCE_PATH)
    subject_ids = [packet["subject_id"] for packet in evidence["packets"]]

    assert set(subject_ids) == catalog_ids
    assert len(subject_ids) == len(set(subject_ids))
    assert all(packet["review_status"] == "reviewed" for packet in evidence["packets"])
    assert all(len(packet["claims"]) >= 2 for packet in evidence["packets"])


def test_osaka_preserves_explicit_target_and_latest_state_kpi_boundary():
    items = load(CATALOG_PATH)["items"]
    target = items[0]
    objective = [item for item in items if item["indicator_layer"] == "objective_kpi"]

    assert target["indicator_name_original"] == "2040年代に名目GDP80兆円を実現"
    assert target["series"][0]["values"] == [
        {
            "role": "target",
            "period": "2040年代",
            "value": 80,
            "value_text_original": "80兆円",
            "status": "numeric",
            "operator": "exact",
            "aggregation_scope": "single_period",
        }
    ]
    assert all(
        value["role"] == "current"
        for item in objective
        for series in item["series"]
        for value in series["values"]
    )
    assert all("個別の数値目標" in item["comparability_note_original"] for item in objective)


def test_osaka_preserves_multiple_series_and_rank_direction():
    items = {item["indicator_name_original"]: item for item in load(CATALOG_PATH)["items"]}

    visitors = items["来阪者数"]
    assert [series["label_original"] for series in visitors["series"]] == ["日本人", "外国人"]

    healthy = items["府民の健康寿命"]
    assert [series["label_original"] for series in healthy["series"]] == ["男性", "女性"]

    city_rank = items["世界の都市総合力ランキング（森記念財団）"]
    assert [series["label_original"] for series in city_rank["series"]] == ["経済", "研究・開発"]
    assert all(series["direction"] == "decrease" for series in city_rank["series"])
    assert all(
        value["aggregation_scope"] == "rank"
        for series in city_rank["series"]
        for value in series["values"]
    )


def test_osaka_preserves_subjective_scales_missing_values_and_reverse_item():
    items = load(CATALOG_PATH)["items"]
    subjective = [item for item in items if item["indicator_layer"] == "subjective_wellbeing"]
    original = [item for item in subjective if item["category_original"] == "大阪府独自指標"]

    assert len(subjective) == 55
    assert len(original) == 5
    assert all(item["response_scale"] == "1_to_5" for item in original)
    assert all(
        value["status"] == "missing" and value["value"] is None
        for item in original
        for value in item["series"][0]["values"]
    )

    happiness = next(
        item
        for item in subjective
        if item["indicator_name_original"] == "現在、あなたはどの程度幸せですか"
    )
    assert happiness["response_scale"] == "0_to_10"
    assert [value["value"] for value in happiness["series"][0]["values"]] == [6.6, 6.0]

    noise = next(
        item
        for item in subjective
        if item["indicator_name_original"] == "自宅の近辺では、騒音に悩まされている"
    )
    assert noise["response_scale"] == "1_to_5_reversed"
    assert "逆転項目" in noise["comparability_note_original"]


def test_osaka_keeps_legacy_actuals_and_business_list_separate():
    catalog = load(CATALOG_PATH)
    manifest = load(MANIFEST_PATH)

    assert all(item["legacy_vision_linkage_status"] == "separate_lineage" for item in catalog["items"])
    assert all(item["business_list_linkage_status"] == "not_linked" for item in catalog["items"])
    assert all(item["policy_achievement_assessment_status"] == "not_assessed" for item in catalog["items"])
    assert manifest["legacy_vision_linked_series_count"] == 0
    assert manifest["business_list_linked_indicator_count"] == 0
    assert manifest["policy_achievement_assessed_indicator_count"] == 0
