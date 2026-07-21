import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
INDICATOR_PATHS = [
    ROOT / "data/reviewed/okinawa_midterm_major_indicators.json",
    ROOT / "data/reviewed/okinawa_midterm_outcome_indicators_part1.json",
    ROOT / "data/reviewed/okinawa_midterm_outcome_indicators_part2.json",
    ROOT / "data/reviewed/okinawa_midterm_outcome_indicators_part3.json",
]
EVIDENCE_PATHS = [
    ROOT / "data/evidence/okinawa_midterm_major_indicator_evidence.json",
    ROOT / "data/evidence/okinawa_midterm_outcome_indicator_evidence_part1.json",
    ROOT / "data/evidence/okinawa_midterm_outcome_indicator_evidence_part2.json",
    ROOT / "data/evidence/okinawa_midterm_outcome_indicator_evidence_part3.json",
]
INDICATOR_SCHEMA_PATH = ROOT / "schemas/okinawa_midterm_indicators.schema.json"
EVIDENCE_SCHEMA_PATH = ROOT / "schemas/okinawa_midterm_indicator_evidence.schema.json"
MANIFEST_PATH = ROOT / "data/catalog/okinawa_midterm_indicator_review_manifest.json"
MANIFEST_SCHEMA_PATH = (
    ROOT / "schemas/okinawa_midterm_indicator_review_manifest.schema.json"
)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def indicators():
    return [
        record
        for path in INDICATOR_PATHS
        for record in load(path)["records"]
    ]


def packets():
    return [
        packet
        for path in EVIDENCE_PATHS
        for packet in load(path)["packets"]
    ]


def test_okinawa_documents_match_schemas():
    indicator_validator = Draft202012Validator(
        load(INDICATOR_SCHEMA_PATH), format_checker=FormatChecker()
    )
    for path in INDICATOR_PATHS:
        document = load(path)
        assert list(indicator_validator.iter_errors(document)) == []
        assert document["record_count"] == len(document["records"])

    evidence_validator = Draft202012Validator(
        load(EVIDENCE_SCHEMA_PATH), format_checker=FormatChecker()
    )
    for path in EVIDENCE_PATHS:
        document = load(path)
        assert list(evidence_validator.iter_errors(document)) == []
        assert document["packet_count"] == len(document["packets"])

    manifest_validator = Draft202012Validator(
        load(MANIFEST_SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert list(manifest_validator.iter_errors(load(MANIFEST_PATH))) == []


def test_okinawa_has_complete_major_and_outcome_sequences():
    items = indicators()
    major = [item for item in items if item["indicator_level"] == "major"]
    outcome = [item for item in items if item["indicator_level"] == "outcome"]

    assert len(items) == 375
    assert [item["sequence"] for item in major] == list(range(1, 37))
    assert [item["sequence"] for item in outcome] == list(range(1, 340))
    assert len({item["id"] for item in items}) == 375
    assert len({item["policy_code_original"] for item in items}) == 375
    assert all(5 <= item["source_pdf_page"] <= 11 for item in major)
    assert all(12 <= item["source_pdf_page"] <= 71 for item in outcome)


def test_okinawa_evidence_is_one_to_one_and_preserves_all_claims():
    items = indicators()
    evidence = packets()
    claim_fields = {
        "policy_code",
        "policy_title",
        "indicator_name",
        "baseline",
        "target_r9",
        "national_current",
        "rationale_source",
        "island_indicator",
        "sdgs_priority",
    }

    assert len(evidence) == 375
    assert {packet["subject_id"] for packet in evidence} == {
        item["id"] for item in items
    }
    assert {packet["id"] for packet in evidence} == {
        item["evidence_id"] for item in items
    }
    assert all(
        {claim["field"] for claim in packet["claims"]} == claim_fields
        for packet in evidence
    )


def test_okinawa_semantic_counts_match_manifest():
    items = indicators()
    manifest = load(MANIFEST_PATH)

    assert manifest["reviewed_indicator_count"] == len(items) == 375
    assert manifest["major_indicator_count"] == sum(
        item["indicator_level"] == "major" for item in items
    ) == 36
    assert manifest["outcome_indicator_count"] == sum(
        item["indicator_level"] == "outcome" for item in items
    ) == 339
    assert manifest["island_indicator_count"] == sum(
        item["is_island_indicator"] for item in items
    ) == 32
    assert manifest["sdgs_priority_indicator_count"] == sum(
        item["has_sdgs_priority"] for item in items
    ) == 43
    assert manifest["qualitative_target_count"] == sum(
        item["target_value_kind"] == "qualitative" for item in items
    ) == 9
    assert manifest["national_comparison_provided_count"] == sum(
        item["national_comparison_status"] == "provided" for item in items
    ) == 174


def test_okinawa_preserves_source_anomaly_without_correction():
    item = next(
        item
        for item in indicators()
        if item["policy_code_original"] == "１－（１）－ア－①"
    )
    packet = next(
        packet for packet in packets() if packet["subject_id"] == item["id"]
    )

    assert item["indicator_name_original"] == "再生可能エネルギー 電源比率"
    assert item["target_r9_original"] == "876万t-CO₂"
    assert item["source_value_note"] is not None
    assert packet["source_value_note"] == item["source_value_note"]
    assert load(MANIFEST_PATH)["source_value_note_count"] == 1


def test_okinawa_does_not_infer_policy_achievement_or_merge_activity_data():
    items = indicators()
    manifest = load(MANIFEST_PATH)

    assert all(item["review_status"] == "reviewed" for item in items)
    assert all(
        item["policy_achievement_assessment_status"] == "not_assessed"
        for item in items
    )
    assert {item["indicator_level"] for item in items} == {"major", "outcome"}
    assert manifest["policy_achievement_assessed_indicator_count"] == 0
    assert "活動指標" in manifest["quality_note"]
    assert "PDCA" in manifest["quality_note"]
