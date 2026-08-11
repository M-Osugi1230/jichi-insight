from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/catalog/sendai_challenge_project_reviews_part16.json"
EVIDENCE_PATH = ROOT / "data/evidence/sendai_challenge_project_reviews_part16_evidence.json"
MANIFEST_PATH = ROOT / "data/catalog/sendai_phase13_review_manifest.json"
SCHEMA_PATH = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sendai_challenge_part16_counts_and_coverage_are_exact():
    data = load(DATA_PATH)
    summary = data["summary"]

    assert summary["prior_reviewed_record_count"] == 45
    assert summary["batch_reviewed_record_count"] == 3
    assert summary["cumulative_reviewed_record_count"] == 48
    assert summary["total_source_project_count"] == 108
    assert summary["remaining_record_count"] == 60
    assert summary["complete"] is False


def test_sendai_challenge_part16_records_are_exact_and_source_reported():
    records = load(DATA_PATH)["records"]
    assert len(records) == 3
    assert [record["project_name_ja"] for record in records] == [
        "秋保地区活性化事業",
        "泉中央地区活性化事業",
        "地域交通運行確保・運行支援事業",
    ]
    assert [record["source_pdf_page_index_0_based"] for record in records] == [55, 56, 56]
    assert [record["source_reported_evaluation"] for record in records] == [
        "double_circle",
        "circle",
        "double_circle",
    ]
    assert [record["responsible_bureau_ja"] for record in records] == [
        "太白区　秋保総合支所",
        "泉区",
        "都市整備局",
    ]
    assert [record["lead_section_ja"] for record in records] == [
        "まちづくり推進課",
        "泉中央地区活性化推進室",
        "地域交通推進課",
    ]


def test_sendai_challenge_part16_evidence_is_one_to_one_and_valid():
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


def test_sendai_part16_preserves_source_rating_and_causality_boundaries():
    data = load(DATA_PATH)
    evidence = load(EVIDENCE_PATH)
    records = {record["id"]: record for record in data["records"]}

    assert records["akiu-district-revitalization"]["source_reported_evaluation"] == "double_circle"
    assert records["izumi-central-district-revitalization"]["source_reported_evaluation"] == "circle"
    assert records["regional-transport-operation-support"]["source_reported_evaluation"] == "double_circle"
    assert all("独自" in packet["claims"][0]["review_note"] for packet in evidence)
    assert "causal claim" in data["quality_boundary"]


def test_sendai_manifest_advances_to_forty_eight_without_claiming_completion():
    manifest = load(MANIFEST_PATH)
    facts = {fact["id"]: fact for fact in manifest["reviewed_facts"]}
    part16 = facts["sendai-challenge-project-records-part16"]
    batches = [
        fact
        for fact in manifest["reviewed_facts"]
        if fact["id"].startswith("sendai-challenge-project-records-part")
    ]
    cumulative_reviewed = sum(fact["value"] for fact in batches)
    remaining = 108 - cumulative_reviewed

    assert part16["value"] == 3
    assert part16["cumulative_value"] == 48
    assert part16["source_reported_breakdown"] == {"double_circle": 2, "circle": 1}
    assert "残り60事業" in part16["interpretation_boundary"]
    assert cumulative_reviewed >= 48
    assert f"{cumulative_reviewed}事業を個票レビュー済み" in manifest["remaining_work"][0]
    assert f"残り{remaining}事業" in manifest["remaining_work"][0]
    assert "independent Jichi Insight achievement scores" in manifest["quality_boundary"]
