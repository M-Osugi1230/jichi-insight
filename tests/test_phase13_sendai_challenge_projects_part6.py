from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/catalog/sendai_challenge_project_reviews_part6.json"
EVIDENCE_PATH = ROOT / "data/evidence/sendai_challenge_project_reviews_part6_evidence.json"
MANIFEST_PATH = ROOT / "data/catalog/sendai_phase13_review_manifest.json"
SCHEMA_PATH = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sendai_challenge_part6_counts_and_coverage_are_exact():
    data = load(DATA_PATH)
    summary = data["summary"]

    assert summary["prior_reviewed_record_count"] == 15
    assert summary["batch_reviewed_record_count"] == 3
    assert summary["cumulative_reviewed_record_count"] == 18
    assert summary["total_source_project_count"] == 108
    assert summary["remaining_record_count"] == 90
    assert summary["complete"] is False


def test_sendai_challenge_part6_records_are_exact_and_source_reported():
    records = load(DATA_PATH)["records"]
    assert len(records) == 3
    assert [record["project_name_ja"] for record in records] == [
        "ごみ減量・リサイクル推進事業",
        "環境配慮行動促進事業",
        "南蒲生浄化センター消化ガス発電事業",
    ]
    assert [record["source_pdf_page_index_0_based"] for record in records] == [
        24,
        25,
        26,
    ]
    assert [record["source_reported_evaluation"] for record in records] == [
        "circle",
        "circle",
        "circle",
    ]
    assert [record["responsible_bureau_ja"] for record in records] == [
        "環境局",
        "環境局",
        "建設局",
    ]
    assert [record["lead_section_ja"] for record in records] == [
        "資源循環企画課",
        "環境共生課",
        "下水道計画課",
    ]


def test_sendai_challenge_part6_evidence_is_one_to_one_and_valid():
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


def test_sendai_manifest_keeps_part6_history_without_freezing_later_progress():
    manifest = load(MANIFEST_PATH)
    facts = {fact["id"]: fact for fact in manifest["reviewed_facts"]}
    part6 = facts["sendai-challenge-project-records-part6"]

    assert part6["value"] == 3
    assert part6["cumulative_value"] == 18
    assert part6["source_reported_breakdown"] == {"circle": 3}
    assert "累計18/108" in part6["interpretation_boundary"]
    assert "残り90事業" in part6["interpretation_boundary"]
    assert "independent Jichi Insight achievement scores" in manifest[
        "quality_boundary"
    ]
