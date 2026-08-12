from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/catalog/sendai_challenge_project_reviews_part27.json"
EVIDENCE_PATH = ROOT / "data/evidence/sendai_challenge_project_reviews_part27_evidence.json"
SCHEMA_PATH = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sendai_challenge_part27_counts_and_coverage_are_exact():
    summary = load(DATA_PATH)["summary"]
    assert summary == {
        "prior_reviewed_record_count": 78,
        "batch_reviewed_record_count": 3,
        "cumulative_reviewed_record_count": 81,
        "total_source_project_count": 108,
        "remaining_record_count": 27,
        "complete": False,
    }


def test_sendai_challenge_part27_records_are_exact_and_source_reported():
    records = load(DATA_PATH)["records"]
    assert [record["project_name_ja"] for record in records] == [
        "地域中核企業輩出支援事業",
        "多様な人材の確保・定着事業",
        "中小企業販路開拓支援事業",
    ]
    assert [record["source_pdf_page_index_0_based"] for record in records] == [95, 96, 97]
    assert [record["source_reported_evaluation"] for record in records] == [
        "circle",
        "circle",
        "triangle",
    ]
    assert [record["lead_section_ja"] for record in records] == [
        "中小企業支援課",
        "商業・人材支援課",
        "中小企業支援課",
    ]


def test_sendai_challenge_part27_evidence_is_one_to_one_and_valid():
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


def test_sendai_part27_preserves_triangle_and_causality_boundaries():
    data = load(DATA_PATH)
    evidence = load(EVIDENCE_PATH)
    assert data["records"][2]["source_reported_evaluation"] == "triangle"
    assert "独自の低評価" in evidence[2]["claims"][0]["review_note"]
    assert "causal claim" in data["quality_boundary"]
