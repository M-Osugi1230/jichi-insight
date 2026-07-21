import json
from pathlib import Path
import re

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATHS = [
    ROOT / f"data/reviewed/okinawa_midterm_indicators_part{part}.json"
    for part in range(1, 5)
]
EVIDENCE_PATHS = [
    ROOT / f"data/evidence/okinawa_midterm_indicator_evidence_part{part}.json"
    for part in range(1, 5)
]
CATALOG_SCHEMA_PATH = ROOT / "schemas/okinawa_midterm_indicators.schema.json"
EVIDENCE_SCHEMA_PATH = (
    ROOT / "schemas/okinawa_midterm_indicator_evidence.schema.json"
)
MANIFEST_PATH = ROOT / "data/catalog/okinawa_midterm_indicator_review_manifest.json"
MANIFEST_SCHEMA_PATH = (
    ROOT / "schemas/okinawa_midterm_indicator_review_manifest.schema.json"
)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def records():
    return [record for path in CATALOG_PATHS for record in load(path)["records"]]


def packets():
    return [packet for path in EVIDENCE_PATHS for packet in load(path)["packets"]]


def test_okinawa_catalog_evidence_and_manifest_match_schemas():
    catalog_validator = Draft202012Validator(
        load(CATALOG_SCHEMA_PATH), format_checker=FormatChecker()
    )
    evidence_validator = Draft202012Validator(
        load(EVIDENCE_SCHEMA_PATH), format_checker=FormatChecker()
    )
    for path in CATALOG_PATHS:
        document = load(path)
        assert list(catalog_validator.iter_errors(document)) == []
        assert document["record_count"] == len(document["records"]) == 94
    for path in EVIDENCE_PATHS:
        document = load(path)
        assert list(evidence_validator.iter_errors(document)) == []
        assert document["packet_count"] == len(document["packets"]) == 94

    manifest_validator = Draft202012Validator(
        load(MANIFEST_SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert list(manifest_validator.iter_errors(load(MANIFEST_PATH))) == []


def test_okinawa_has_complete_major_and_outcome_sequences():
    items = records()
    manifest = load(MANIFEST_PATH)
    assert len(items) == 376
    assert [item["display_order"] for item in items] == list(range(1, 377))
    assert [item["indicator_id"] for item in items] == [
        f"okinawa-midterm-indicator-{number:03d}" for number in range(1, 377)
    ]
    assert all(item["indicator_layer"] == "major" for item in items[:37])
    assert all(item["indicator_layer"] == "outcome" for item in items[37:])
    assert manifest["major_indicator_count"] == 37
    assert manifest["outcome_indicator_count"] == 339


def test_okinawa_evidence_is_one_to_one_and_keeps_all_claims():
    items = records()
    evidence = packets()
    assert len(evidence) == 376
    assert [packet["subject_id"] for packet in evidence] == [
        item["indicator_id"] for item in items
    ]
    assert [packet["id"] for packet in evidence] == [
        item["evidence_id"] for item in items
    ]
    assert len({packet["subject_id"] for packet in evidence}) == 376
    assert all(packet["review_status"] == "reviewed" for packet in evidence)
    assert all(
        {claim["field"] for claim in packet["claims"]}
        == {"policy", "indicator_name", "baseline", "target_r9", "national_current"}
        for packet in evidence
    )


def test_okinawa_preserves_national_island_sdgs_and_qualitative_boundaries():
    items = records()
    manifest = load(MANIFEST_PATH)
    national_present = sum(
        item["national_current_original"] not in {None, "－", "-"} for item in items
    )
    island = sum(bool(item["remote_island_marker_original"]) for item in items)
    sdgs = sum(bool(item["sdgs_priority_original"]) for item in items)
    qualitative = sum(
        not re.search(r"[0-9０-９]", item["target_r9_original"]) for item in items
    )
    assert national_present == manifest["national_comparator_present_count"] == 174
    assert island == manifest["remote_island_indicator_count"] == 32
    assert sdgs == manifest["sdgs_linked_indicator_count"] == 43
    assert qualitative == manifest["qualitative_target_count"] == 9


def test_okinawa_preserves_multi_series_and_missing_national_values():
    items = {item["indicator_name_original"].replace(" ", ""): item for item in records()}
    life = items["平均寿命"]
    incidents = items["米軍基地関係事件・事故数（刑法犯等含む）"]
    island_population = items[
        "小・中規模離島と本島過疎地域の人口及び生産年齢人口の割合"
    ]

    assert "男性80.73年" in life["baseline_original"]
    assert "女性87.88年" in life["baseline_original"]
    assert "男性82.15年" in life["target_r9_original"]
    assert "女性88.80年" in life["target_r9_original"]
    assert incidents["target_r9_original"].replace(" ", "") == "可能な限り減少させる"
    assert incidents["national_current_original"] == "－"
    assert "小中離島" in island_population["baseline_original"]
    assert "本島過疎" in island_population["target_r9_original"]


def test_okinawa_excludes_activity_indicators_and_does_not_infer_achievement():
    items = records()
    manifest = load(MANIFEST_PATH)
    assert manifest["activity_indicator_included_count"] == 0
    assert manifest["policy_achievement_assessed_indicator_count"] == 0
    assert all(
        item["policy_achievement_assessment_status"] == "not_assessed"
        for item in items
    )
    assert manifest["duplicate_indicator_name_count"] == 0
    assert len({item["indicator_name_original"] for item in items}) == 376
