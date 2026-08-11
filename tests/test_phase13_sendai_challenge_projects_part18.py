from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/catalog/sendai_challenge_project_reviews_part18.json"
EVIDENCE_PATH = ROOT / "data/evidence/sendai_challenge_project_reviews_part18_evidence.json"
SCHEMA_PATH = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sendai_challenge_part18_counts_and_coverage_are_exact():
    summary = load(DATA_PATH)["summary"]
    assert summary == {
        "prior_reviewed_record_count": 51,
        "batch_reviewed_record_count": 3,
        "cumulative_reviewed_record_count": 54,
        "total_source_project_count": 108,
        "remaining_record_count": 54,
        "complete": False,
    }


def test_sendai_challenge_part18_records_are_exact_and_source_reported():
    records = load(DATA_PATH)["records"]
    assert [record["project_name_ja"] for record in records] == [
        "子育て応援の機運醸成事業",
        "仕事と子育ての両立支援事業",
        "子どもの遊びの環境充実事業",
    ]
    assert [record["source_pdf_page_index_0_based"] for record in records] == [62, 63, 63]
    assert [record["source_reported_evaluation"] for record in records] == [
        "circle",
        "circle",
        "circle",
    ]
    assert [record["lead_section_ja"] for record in records] == [
        "子育て応援都市推進課",
        "総務課・子育て応援都市推進課",
        "子育て応援都市推進課",
    ]


def test_sendai_challenge_part18_evidence_is_one_to_one_and_valid():
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


def test_sendai_part18_preserves_page_and_causality_boundaries():
    data = load(DATA_PATH)
    evidence = {packet["subject_id"]: packet for packet in load(EVIDENCE_PATH)}
    assert "page index 63-64" in evidence[
        "child-play-environment-enhancement"
    ]["claims"][0]["location_note"]
    assert all(
        "独自" in packet["claims"][0]["review_note"]
        for packet in evidence.values()
    )
    assert "causal claim" in data["quality_boundary"]
