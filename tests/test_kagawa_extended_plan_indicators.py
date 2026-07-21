import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_PATHS = [
    ROOT / "data/evidence/kagawa_extended_plan_indicator_evidence_part1.json",
    ROOT / "data/evidence/kagawa_extended_plan_indicator_evidence_part2.json",
    ROOT / "data/evidence/kagawa_extended_plan_indicator_evidence_part3.json",
]
EVIDENCE_SCHEMA_PATH = (
    ROOT / "schemas/kagawa_extended_plan_indicator_evidence.schema.json"
)
MANIFEST_PATH = (
    ROOT / "data/catalog/kagawa_extended_plan_indicator_review_manifest.json"
)
MANIFEST_SCHEMA_PATH = (
    ROOT / "schemas/kagawa_extended_plan_indicator_review_manifest.schema.json"
)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def packets():
    return [packet for path in EVIDENCE_PATHS for packet in load(path)["packets"]]


def claims(packet):
    return {claim["field"]: claim["value_original"] for claim in packet["claims"]}


def test_kagawa_evidence_and_manifest_match_schemas():
    evidence_validator = Draft202012Validator(
        load(EVIDENCE_SCHEMA_PATH), format_checker=FormatChecker()
    )
    for path in EVIDENCE_PATHS:
        document = load(path)
        assert list(evidence_validator.iter_errors(document)) == []
        assert document["packet_count"] == len(document["packets"]) == 45

    manifest_validator = Draft202012Validator(
        load(MANIFEST_SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert list(manifest_validator.iter_errors(load(MANIFEST_PATH))) == []


def test_kagawa_has_all_135_indicators_and_one_to_one_evidence():
    items = packets()
    expected_subjects = [
        f"kagawa-plan-indicator-{number:03d}" for number in range(1, 136)
    ]
    expected_evidence = [
        f"kagawa-plan-evidence-{number:03d}" for number in range(1, 136)
    ]
    assert len(items) == 135
    assert [item["subject_id"] for item in items] == expected_subjects
    assert [item["id"] for item in items] == expected_evidence
    assert len({item["subject_id"] for item in items}) == 135
    assert all(item["review_status"] == "reviewed" for item in items)
    assert all(
        set(claims(item)) == {"indicator_name", "current_value", "target_r7", "target_r8"}
        for item in items
    )


def test_kagawa_preserves_reposts_without_duplicate_unique_count():
    manifest = load(MANIFEST_PATH)
    assert manifest["reviewed_indicator_count"] == 135
    assert manifest["display_occurrence_count"] == 141
    assert manifest["reposted_indicator_count"] == 6
    assert manifest["reposted_indicator_numbers"] == [7, 14, 50, 66, 67, 96]
    assert manifest["display_occurrence_count"] - manifest["reviewed_indicator_count"] == 6


def test_kagawa_preserves_old_and_extended_targets():
    items = packets()
    revised = sum(
        claims(item)["target_r7"] != claims(item)["target_r8"] for item in items
    )
    assert revised == load(MANIFEST_PATH)["target_revision_count"] == 87

    first = claims(items[0])
    assert first["target_r7"] == "23.4％"
    assert first["target_r8"] == "35.1％"

    waiting = claims(items[1])
    assert "年度当初" in waiting["current_value"]
    assert "年度途中" in waiting["current_value"]
    assert "R9年度" in waiting["target_r8"]


def test_kagawa_preserves_corrections_cumulative_periods_and_reference_target():
    items = {item["subject_id"]: claims(item) for item in packets()}
    technology = items["kagawa-plan-indicator-066"]
    international = items["kagawa-plan-indicator-096"]
    population = items["kagawa-plan-indicator-135"]

    assert "160件" in technology["current_value"]
    assert "→168件" in technology["current_value"]
    assert "R3～7年度" in international["target_r7"]
    assert "R3～8年度" in international["target_r8"]
    assert population["indicator_name"].replace(" ", "") == "県人口"
    assert population["target_r7"] == "925千人 （R7年）"
    assert population["target_r8"] == "901千人 （R12年）"


def test_kagawa_does_not_infer_policy_achievement():
    manifest = load(MANIFEST_PATH)
    assert manifest["policy_achievement_assessed_indicator_count"] == 0
    assert manifest["indicators_with_current_value_count"] == 135
    assert all(item["source_pdf_page"] in range(3, 18) for item in packets())
