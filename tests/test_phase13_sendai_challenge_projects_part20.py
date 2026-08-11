from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/catalog/sendai_challenge_project_reviews_part20.json"
EVIDENCE_PATH = ROOT / "data/evidence/sendai_challenge_project_reviews_part20_evidence.json"
MANIFEST_PATH = ROOT / "data/catalog/sendai_phase13_review_manifest.json"
SCHEMA_PATH = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sendai_challenge_part20_counts_and_coverage_are_exact():
    summary = load(DATA_PATH)["summary"]
    assert summary == {
        "prior_reviewed_record_count": 57,
        "batch_reviewed_record_count": 3,
        "cumulative_reviewed_record_count": 60,
        "total_source_project_count": 108,
        "remaining_record_count": 48,
        "complete": False,
    }


def test_sendai_challenge_part20_records_are_exact_and_source_reported():
    records = load(DATA_PATH)["records"]
    assert [record["project_name_ja"] for record in records] == [
        "ICT教育推進事業",
        "仙台自分づくり教育推進事業",
        "コミュニティ・スクール推進事業",
    ]
    assert [record["source_pdf_page_index_0_based"] for record in records] == [70, 71, 72]
    assert all(record["source_reported_evaluation"] == "circle" for record in records)
    assert [record["lead_section_ja"] for record in records] == [
        "教育指導課",
        "学びの連携推進室",
        "学びの連携推進室",
    ]


def test_sendai_challenge_part20_evidence_is_one_to_one_and_valid():
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


def test_sendai_part20_preserves_causality_boundaries():
    data = load(DATA_PATH)
    evidence = load(EVIDENCE_PATH)
    assert all(
        "独自" in packet["claims"][0]["review_note"]
        for packet in evidence
    )
    assert "causal claim" in data["quality_boundary"]


def test_sendai_manifest_batch_advances_to_sixty_without_claiming_completion():
    manifest = load(MANIFEST_PATH)
    facts = {fact["id"]: fact for fact in manifest["reviewed_facts"]}
    assert facts["sendai-challenge-project-records-part18"]["cumulative_value"] == 54
    assert facts["sendai-challenge-project-records-part19"]["cumulative_value"] == 57
    assert facts["sendai-challenge-project-records-part20"]["cumulative_value"] == 60
    batches = [
        fact
        for fact in manifest["reviewed_facts"]
        if fact["id"].startswith("sendai-challenge-project-records-part")
    ]
    cumulative_reviewed = sum(fact["value"] for fact in batches)
    assert cumulative_reviewed == 60
    assert "60事業を個票レビュー済み" in manifest["remaining_work"][0]
    assert "残り48事業" in manifest["remaining_work"][0]
    assert "independent Jichi Insight achievement scores" in manifest[
        "quality_boundary"
    ]
