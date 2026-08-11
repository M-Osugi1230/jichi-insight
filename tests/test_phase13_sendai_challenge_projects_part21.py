from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/catalog/sendai_challenge_project_reviews_part21.json"
EVIDENCE_PATH = ROOT / "data/evidence/sendai_challenge_project_reviews_part21_evidence.json"
SCHEMA_PATH = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sendai_challenge_part21_counts_and_coverage_are_exact():
    summary = load(DATA_PATH)["summary"]
    assert summary == {
        "prior_reviewed_record_count": 60,
        "batch_reviewed_record_count": 3,
        "cumulative_reviewed_record_count": 63,
        "total_source_project_count": 108,
        "remaining_record_count": 45,
        "complete": False,
    }


def test_sendai_challenge_part21_records_are_exact_and_source_reported():
    records = load(DATA_PATH)["records"]
    assert [record["project_name_ja"] for record in records] == [
        "不登校児童生徒等支援事業",
        "特別支援教育推進事業",
        "文化芸術によるまちの魅力づくり事業",
    ]
    assert [record["source_pdf_page_index_0_based"] for record in records] == [73, 74, 76]
    assert [record["source_reported_evaluation"] for record in records] == [
        "circle",
        "circle",
        "triangle",
    ]
    assert [record["lead_section_ja"] for record in records] == [
        "教育相談課",
        "特別支援教育課",
        "文化振興課",
    ]


def test_sendai_challenge_part21_evidence_is_one_to_one_and_valid():
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


def test_sendai_part21_preserves_triangle_and_causality_boundaries():
    data = load(DATA_PATH)
    packets = {packet["subject_id"]: packet for packet in load(EVIDENCE_PATH)}
    culture = next(
        record
        for record in data["records"]
        if record["id"] == "culture-arts-city-attractiveness"
    )
    assert culture["source_reported_evaluation"] == "triangle"
    assert "基準値を下回った" in packets["culture-arts-city-attractiveness"][
        "claims"
    ][0]["location_note"]
    assert "独自の低評価" in packets["culture-arts-city-attractiveness"][
        "claims"
    ][0]["review_note"]
    assert "causal" in data["quality_boundary"]
