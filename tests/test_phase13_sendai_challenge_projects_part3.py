from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/catalog/sendai_challenge_project_reviews_part3.json"
EVIDENCE_PATH = ROOT / "data/evidence/sendai_challenge_project_reviews_part3_evidence.json"
MANIFEST_PATH = ROOT / "data/catalog/sendai_phase13_review_manifest.json"
SCHEMA_PATH = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sendai_challenge_part3_counts_and_coverage_are_exact():
    data = load(DATA_PATH)
    summary = data["summary"]

    assert summary["prior_reviewed_record_count"] == 6
    assert summary["batch_reviewed_record_count"] == 3
    assert summary["cumulative_reviewed_record_count"] == 9
    assert summary["total_source_project_count"] == 108
    assert summary["remaining_record_count"] == 99
    assert summary["complete"] is False


def test_sendai_challenge_part3_records_are_exact_and_source_reported():
    records = load(DATA_PATH)["records"]
    assert len(records) == 3
    assert [record["project_name_ja"] for record in records] == [
        "市民協働によるみどりのまちづくり事業",
        "市街地のグリーンインフラ推進事業",
        "杜の都の風土を育む景観形成推進事業",
    ]
    assert [record["source_pdf_page_index_0_based"] for record in records] == [
        13,
        14,
        15,
    ]
    assert [record["source_reported_evaluation"] for record in records] == [
        "double_circle",
        "circle",
        "circle",
    ]
    assert [record["responsible_bureau_ja"] for record in records] == [
        "建設局",
        "建設局",
        "都市整備局",
    ]
    assert [record["lead_section_ja"] for record in records] == [
        "百年の杜推進課",
        "百年の杜推進課",
        "都市景観課",
    ]


def test_sendai_challenge_part3_evidence_is_one_to_one_and_valid():
    data = load(DATA_PATH)
    packets = load(EVIDENCE_PATH)
    schema = load(SCHEMA_PATH)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    assert len(packets) == 3
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in data["records"]
    }
    assert all(list(validator.iter_errors(packet)) == [] for packet in packets)
    assert all(packet["subject_type"] == "project" for packet in packets)
    assert all(packet["review_status"] == "reviewed" for packet in packets)


def test_sendai_manifest_advances_to_nine_without_claiming_completion():
    manifest = load(MANIFEST_PATH)
    facts = {fact["id"]: fact for fact in manifest["reviewed_facts"]}
    part3 = facts["sendai-challenge-project-records-part3"]

    assert part3["value"] == 3
    assert part3["cumulative_value"] == 9
    assert part3["source_reported_breakdown"] == {
        "double_circle": 1,
        "circle": 2,
    }
    assert "残り99事業" in manifest["remaining_work"][0]
    assert "independent Jichi Insight achievement scores" in manifest[
        "quality_boundary"
    ]
