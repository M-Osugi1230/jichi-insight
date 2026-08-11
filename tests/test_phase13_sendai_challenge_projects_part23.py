from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/catalog/sendai_challenge_project_reviews_part23.json"
EVIDENCE_PATH = ROOT / "data/evidence/sendai_challenge_project_reviews_part23_evidence.json"
MANIFEST_PATH = ROOT / "data/catalog/sendai_phase13_review_manifest.json"
SCHEMA_PATH = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sendai_challenge_part23_counts_and_coverage_are_exact():
    summary = load(DATA_PATH)["summary"]
    assert summary == {
        "prior_reviewed_record_count": 66,
        "batch_reviewed_record_count": 3,
        "cumulative_reviewed_record_count": 69,
        "total_source_project_count": 108,
        "remaining_record_count": 39,
        "complete": False,
    }


def test_sendai_challenge_part23_records_are_exact_and_source_reported():
    records = load(DATA_PATH)["records"]
    assert [record["project_name_ja"] for record in records] == [
        "障害者就労支援体制整備事業",
        "高齢者社会参加・生きがいづくり促進事業",
        "介護人材確保事業",
    ]
    assert [record["source_pdf_page_index_0_based"] for record in records] == [80, 81, 82]
    assert all(record["source_reported_evaluation"] == "circle" for record in records)
    assert [record["lead_section_ja"] for record in records] == [
        "障害企画課",
        "高齢企画課",
        "介護保険課",
    ]


def test_sendai_challenge_part23_evidence_is_one_to_one_and_valid():
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


def test_sendai_part23_preserves_causality_boundaries():
    data = load(DATA_PATH)
    evidence = load(EVIDENCE_PATH)
    assert all(
        "独自" in packet["claims"][0]["review_note"]
        for packet in evidence
    )
    assert "causal claim" in data["quality_boundary"]


def test_sendai_manifest_batch_advances_to_sixty_nine_without_completion():
    manifest = load(MANIFEST_PATH)
    facts = {fact["id"]: fact for fact in manifest["reviewed_facts"]}
    assert facts["sendai-challenge-project-records-part21"]["cumulative_value"] == 63
    assert facts["sendai-challenge-project-records-part22"]["cumulative_value"] == 66
    assert facts["sendai-challenge-project-records-part23"]["cumulative_value"] == 69
    batches = [
        fact
        for fact in manifest["reviewed_facts"]
        if fact["id"].startswith("sendai-challenge-project-records-part")
    ]
    assert sum(fact["value"] for fact in batches) == 69
    assert "69事業を個票レビュー済み" in manifest["remaining_work"][0]
    assert "残り39事業" in manifest["remaining_work"][0]
