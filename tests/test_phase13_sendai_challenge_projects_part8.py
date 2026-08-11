from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/catalog/sendai_challenge_project_reviews_part8.json"
EVIDENCE_PATH = ROOT / "data/evidence/sendai_challenge_project_reviews_part8_evidence.json"
MANIFEST_PATH = ROOT / "data/catalog/sendai_phase13_review_manifest.json"
SCHEMA_PATH = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sendai_challenge_part8_counts_and_coverage_are_exact():
    data = load(DATA_PATH)
    summary = data["summary"]

    assert summary["prior_reviewed_record_count"] == 21
    assert summary["batch_reviewed_record_count"] == 3
    assert summary["cumulative_reviewed_record_count"] == 24
    assert summary["total_source_project_count"] == 108
    assert summary["remaining_record_count"] == 84
    assert summary["complete"] is False


def test_sendai_challenge_part8_records_are_exact_and_source_reported():
    records = load(DATA_PATH)["records"]
    assert len(records) == 3
    assert [record["project_name_ja"] for record in records] == [
        "仙台市流域治水推進モデル事業",
        "道路整備・防災対策推進事業",
        "地域密着で取り組む火災のないまちづくり事業",
    ]
    assert [record["source_pdf_page_index_0_based"] for record in records] == [
        30,
        31,
        32,
    ]
    assert [record["source_reported_evaluation"] for record in records] == [
        "circle",
        "circle",
        "double_circle",
    ]
    assert [record["responsible_bureau_ja"] for record in records] == [
        "危機管理局・経済局・建設局・教育局・宮城野区",
        "建設局",
        "消防局",
    ]
    assert [record["lead_section_ja"] for record in records] == [
        "建設局　下水道計画課",
        "道路計画課",
        "予防課",
    ]


def test_sendai_challenge_part8_evidence_is_one_to_one_and_valid():
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


def test_sendai_manifest_advances_to_twenty_four_without_claiming_completion():
    manifest = load(MANIFEST_PATH)
    facts = {fact["id"]: fact for fact in manifest["reviewed_facts"]}
    part8 = facts["sendai-challenge-project-records-part8"]
    batches = [
        fact
        for fact in manifest["reviewed_facts"]
        if fact["id"].startswith("sendai-challenge-project-records-part")
    ]
    cumulative_reviewed = sum(fact["value"] for fact in batches)
    remaining = 108 - cumulative_reviewed

    assert part8["value"] == 3
    assert part8["cumulative_value"] == 24
    assert part8["source_reported_breakdown"] == {"circle": 2, "double_circle": 1}
    assert "残り84事業" in part8["interpretation_boundary"]
    assert cumulative_reviewed >= 24
    assert f"{cumulative_reviewed}事業を個票レビュー済み" in manifest["remaining_work"][0]
    assert f"残り{remaining}事業" in manifest["remaining_work"][0]
    assert "independent Jichi Insight achievement scores" in manifest[
        "quality_boundary"
    ]
