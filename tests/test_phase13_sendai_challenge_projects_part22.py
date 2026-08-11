from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/catalog/sendai_challenge_project_reviews_part22.json"
EVIDENCE_PATH = ROOT / "data/evidence/sendai_challenge_project_reviews_part22_evidence.json"
SCHEMA_PATH = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sendai_challenge_part22_counts_and_coverage_are_exact():
    summary = load(DATA_PATH)["summary"]
    assert summary == {
        "prior_reviewed_record_count": 63,
        "batch_reviewed_record_count": 3,
        "cumulative_reviewed_record_count": 66,
        "total_source_project_count": 108,
        "remaining_record_count": 42,
        "complete": False,
    }


def test_sendai_challenge_part22_records_are_exact_and_source_reported():
    records = load(DATA_PATH)["records"]
    assert [record["project_name_ja"] for record in records] == [
        "せんだい・アート・ノード・プロジェクト事業",
        "ダイバーシティ推進事業",
        "女性の活躍推進事業",
    ]
    assert [record["source_pdf_page_index_0_based"] for record in records] == [77, 78, 79]
    assert all(record["source_reported_evaluation"] == "circle" for record in records)
    assert [record["lead_section_ja"] for record in records] == [
        "生涯学習課",
        "ダイバーシティ推進課",
        "男女共同参画課",
    ]


def test_sendai_challenge_part22_evidence_is_one_to_one_and_valid():
    data = load(DATA_PATH)
    packets = load(EVIDENCE_PATH)
    validator = Draft202012Validator(
        load(SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert len(packets) == 3
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in data["records"]
    }
    assert {packet["id"] for packet in packets} == {
        record["evidence_id"] for record in data["records"]
    }
    assert all(list(validator.iter_errors(packet)) == [] for packet in packets)


def test_sendai_part22_preserves_causality_boundaries():
    data = load(DATA_PATH)
    evidence = load(EVIDENCE_PATH)
    assert all(
        "独自" in packet["claims"][0]["review_note"]
        for packet in evidence
    )
    assert "causal claim" in data["quality_boundary"]
