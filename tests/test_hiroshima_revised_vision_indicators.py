import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
PART_PATHS = [
    ROOT / "data/reviewed/hiroshima_revised_vision_indicators_part1.json",
    ROOT / "data/reviewed/hiroshima_revised_vision_indicators_part2.json",
    ROOT / "data/reviewed/hiroshima_revised_vision_indicators_part3.json",
]
SCHEMA_PATH = ROOT / "schemas/hiroshima_revised_vision_indicators.schema.json"
MANIFEST_PATH = (
    ROOT / "data/catalog/hiroshima_revised_vision_indicator_review_manifest.json"
)
MANIFEST_SCHEMA_PATH = (
    ROOT / "schemas/hiroshima_revised_vision_indicator_review_manifest.schema.json"
)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def records():
    return [record for path in PART_PATHS for record in load(path)["records"]]


def test_hiroshima_parts_and_manifest_match_schemas():
    validator = Draft202012Validator(load(SCHEMA_PATH), format_checker=FormatChecker())
    for path in PART_PATHS:
        document = load(path)
        assert list(validator.iter_errors(document)) == []
        assert document["record_count"] == len(document["records"])

    manifest_validator = Draft202012Validator(
        load(MANIFEST_SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert list(manifest_validator.iter_errors(load(MANIFEST_PATH))) == []


def test_hiroshima_has_complete_current_indicator_sequence_and_evidence():
    items = records()
    manifest = load(MANIFEST_PATH)
    expected_ids = [
        f"hiroshima-vision-indicator-{number:03d}" for number in range(1, 63)
    ]
    expected_evidence = [
        f"hiroshima-vision-evidence-{number:03d}" for number in range(1, 63)
    ]

    assert len(items) == 62
    assert [item["id"] for item in items] == expected_ids
    assert [item["evidence_id"] for item in items] == expected_evidence
    assert len({item["evidence_id"] for item in items}) == 62
    assert manifest["reviewed_indicator_count"] == 62
    assert manifest["evidence_packet_count"] == 62
    assert sorted({item["page"] for item in items}) == [109, 111, 113, 115, 117, 119, 121]


def test_hiroshima_excludes_deleted_rows_and_does_not_infer_achievement():
    items = records()
    assert all("削除" not in item["name"] for item in items)
    assert all(item["review"] == "reviewed" for item in items)
    assert all(item["assessment"] == "not_assessed" for item in items)
    assert load(MANIFEST_PATH)["policy_achievement_assessed_indicator_count"] == 0


def test_hiroshima_preserves_pending_measurements_and_target_periods():
    items = {item["name"]: item for item in records()}
    pending = [
        item
        for item in items.values()
        if item["current"] in {"―", "令和8年度に新たに調査"}
    ]
    assert len(pending) == 3
    assert load(MANIFEST_PATH)["pending_measurement_indicator_count"] == 3
    assert items[
        "悩みごとがあるとき、だれにも相談できない、相談したくないと回答した子供の割合"
    ]["target_period"] == "R10"
    assert items["健康寿命の延伸"]["target_period"] == "R10"
    assert items["広島空港利用者数"]["target_period"] == "R12"


def test_hiroshima_preserves_qualitative_comparators_and_average_windows():
    items = {item["name"]: item for item in records()}
    health = items["健康寿命の延伸"]
    peace = items["核兵器廃絶に向けた国際的な合意形成"]
    fishery = items["海面漁業生産額"]

    assert "全国平均" in health["baseline"] and "全国平均" in health["current"]
    assert "全ての国が参加" in peace["target"]
    assert fishery["baseline"].endswith("（H28-R2平均）")
    assert fishery["current"].endswith("（R1-R5平均）")
    assert fishery["target"].endswith("（R8-R12平均）")


def test_hiroshima_preserves_decrease_direction_and_revisions_in_text():
    items = {item["name"]: item for item in records()}
    assert items["刑法犯認知件数"]["change"] == "revised_target"
    assert items["年間渋滞損失時間"]["change"] == "continued_decrease"
    assert items["働くところが少ないと感じる中山間地域の住民の割合"][
        "change"
    ] == "replacement_decrease"
    assert items["産業廃棄物の再生利用率"]["change"] == "revised_definition"
