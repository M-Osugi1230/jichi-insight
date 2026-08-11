from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/catalog/sendai_challenge_project_reviews_part4.json"
EVIDENCE_PATH = ROOT / "data/evidence/sendai_challenge_project_reviews_part4_evidence.json"
MANIFEST_PATH = ROOT / "data/catalog/sendai_phase13_review_manifest.json"
SCHEMA_PATH = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sendai_challenge_part4_counts_and_coverage_are_exact():
    data = load(DATA_PATH)
    summary = data["summary"]

    assert summary["prior_reviewed_record_count"] == 9
    assert summary["batch_reviewed_record_count"] == 3
    assert summary["cumulative_reviewed_record_count"] == 12
    assert summary["total_source_project_count"] == 108
    assert summary["remaining_record_count"] == 96
    assert summary["complete"] is False


def test_sendai_challenge_part4_records_are_exact_and_source_reported():
    records = load(DATA_PATH)["records"]
    assert len(records) == 3
    assert [record["project_name_ja"] for record in records] == [
        "広瀬川創生・清流保全事業",
        "青葉山公園整備事業",
        "防災環境都市づくり推進事業",
    ]
    assert [record["source_pdf_page_index_0_based"] for record in records] == [
        16,
        17,
        19,
    ]
    assert [record["source_reported_evaluation"] for record in records] == [
        "circle",
        "circle",
        "double_circle",
    ]
    assert [record["responsible_bureau_ja"] for record in records] == [
        "建設局",
        "建設局",
        "まちづくり政策局",
    ]
    assert [record["lead_section_ja"] for record in records] == [
        "百年の杜推進課",
        "公園整備課",
        "防災環境都市推進室",
    ]


def test_sendai_challenge_part4_evidence_is_one_to_one_and_valid():
    data = load(DATA_PATH)
    packets = load(EVIDENCE_PATH)
    schema = load(SCHEMA_PATH)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    assert len(packets) == 3
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in data["records"]
    }
    assert {packet["id"] for packet in packets} == {
        record["evidence_id"] for record in data["records"]
    }
    assert all(list(validator.iter_errors(packet)) == [] for packet in packets)
    assert all(packet["subject_type"] == "project" for packet in packets)
    assert all(packet["review_status"] == "reviewed" for packet in packets)


def test_sendai_manifest_advances_to_twelve_without_claiming_completion():
    manifest = load(MANIFEST_PATH)
    facts = {fact["id"]: fact for fact in manifest["reviewed_facts"]}
    part4 = facts["sendai-challenge-project-records-part4"]

    assert part4["value"] == 3
    assert part4["cumulative_value"] == 12
    assert part4["source_reported_breakdown"] == {
        "double_circle": 1,
        "circle": 2,
    }
    assert "残り96事業" in manifest["remaining_work"][0]
    assert "independent Jichi Insight achievement scores" in manifest[
        "quality_boundary"
    ]
