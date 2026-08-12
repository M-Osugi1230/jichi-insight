from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas/evidence_packet.schema.json"
MANIFEST_PATH = ROOT / "data/catalog/sendai_phase13_review_manifest.json"
PARTS = range(30, 37)
EXPECTED_CUMULATIVE = {
    30: 90,
    31: 93,
    32: 96,
    33: 99,
    34: 102,
    35: 105,
    36: 108,
}
EXPECTED_REMAINING = {
    30: 18,
    31: 15,
    32: 12,
    33: 9,
    34: 6,
    35: 3,
    36: 0,
}
EXPECTED_RATINGS = {
    30: ["double_circle", "circle", "triangle"],
    31: ["circle", "double_circle", "circle"],
    32: ["triangle", "circle", "circle"],
    33: ["circle", "circle", "circle"],
    34: ["circle", "circle", "circle"],
    35: ["circle", "circle", "circle"],
    36: ["circle", "circle", "circle"],
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def catalog_path(part: int) -> Path:
    return ROOT / (
        f"data/catalog/sendai_challenge_project_reviews_part{part}.json"
    )


def evidence_path(part: int) -> Path:
    return ROOT / (
        f"data/evidence/sendai_challenge_project_reviews_part{part}_evidence.json"
    )


def test_final_sendai_batches_form_exact_87_to_108_sequence():
    previous = 87
    for part in PARTS:
        summary = load(catalog_path(part))["summary"]
        assert summary["prior_reviewed_record_count"] == previous
        assert summary["batch_reviewed_record_count"] == 3
        assert (
            summary["cumulative_reviewed_record_count"]
            == EXPECTED_CUMULATIVE[part]
        )
        assert summary["total_source_project_count"] == 108
        assert summary["remaining_record_count"] == EXPECTED_REMAINING[part]
        assert summary["complete"] is (part == 36)
        previous = EXPECTED_CUMULATIVE[part]


def test_final_sendai_batches_preserve_source_reported_ratings():
    for part in PARTS:
        data = load(catalog_path(part))
        records = data["records"]
        ratings = [record["source_reported_evaluation"] for record in records]
        assert len(records) == 3
        assert ratings == EXPECTED_RATINGS[part]
        assert all(
            record["review_status"] == "reviewed_core_evaluation"
            for record in records
        )
        assert "causal claim" in data["quality_boundary"]


def test_final_sendai_batches_have_one_to_one_valid_evidence():
    validator = Draft202012Validator(
        load(SCHEMA_PATH), format_checker=FormatChecker()
    )
    for part in PARTS:
        records = load(catalog_path(part))["records"]
        packets = load(evidence_path(part))
        assert len(packets) == 3
        assert {packet["subject_id"] for packet in packets} == {
            record["id"] for record in records
        }
        assert {packet["id"] for packet in packets} == {
            record["evidence_id"] for record in records
        }
        assert all(list(validator.iter_errors(packet)) == [] for packet in packets)
        assert all(
            "独自" in packet["claims"][0]["review_note"]
            for packet in packets
        )


def test_sendai_manifest_closes_core_sequence_without_overclaiming_phase13():
    manifest = load(MANIFEST_PATH)
    facts = {fact["id"]: fact for fact in manifest["reviewed_facts"]}
    for part, cumulative in EXPECTED_CUMULATIVE.items():
        fact = facts[f"sendai-challenge-project-records-part{part}"]
        assert fact["value"] == 3
        assert fact["cumulative_value"] == cumulative

    batches = [
        fact
        for fact in manifest["reviewed_facts"]
        if fact["id"].startswith("sendai-challenge-project-records-part")
    ]
    cumulative_values = [
        fact.get("cumulative_value", fact["value"]) for fact in batches
    ]
    assert len(batches) == 36
    assert sum(fact["value"] for fact in batches) == 108
    assert max(cumulative_values) == 108
    assert manifest["status"] == "review_in_progress"
    assert "108 of 108" in manifest["quality_boundary"]
    assert (
        "independent Jichi Insight achievement scores"
        in manifest["quality_boundary"]
    )
    assert any("市民意識調査" in item for item in manifest["remaining_work"])
    assert any("予算・決算" in item for item in manifest["remaining_work"])
