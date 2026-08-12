from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/catalog/sendai_challenge_project_reviews_part26.json"
EVIDENCE_PATH = ROOT / "data/evidence/sendai_challenge_project_reviews_part26_evidence.json"
MANIFEST_PATH = ROOT / "data/catalog/sendai_phase13_review_manifest.json"
SCHEMA_PATH = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sendai_challenge_part26_counts_and_coverage_are_exact():
    summary = load(DATA_PATH)["summary"]
    assert summary == {
        "prior_reviewed_record_count": 75,
        "batch_reviewed_record_count": 3,
        "cumulative_reviewed_record_count": 78,
        "total_source_project_count": 108,
        "remaining_record_count": 30,
        "complete": False,
    }


def test_sendai_challenge_part26_records_are_exact_and_source_reported():
    records = load(DATA_PATH)["records"]
    assert [record["project_name_ja"] for record in records] == [
        "起業家・スタートアップ支援事業",
        "成長産業振興事業",
        "国家戦略特区推進事業",
    ]
    assert [record["source_pdf_page_index_0_based"] for record in records] == [91, 92, 93]
    assert [record["source_reported_evaluation"] for record in records] == [
        "double_circle",
        "double_circle",
        "circle",
    ]
    assert [record["lead_section_ja"] for record in records] == [
        "スタートアップ支援課",
        "イノベーション企画課・中小企業支援課",
        "プロジェクト推進課",
    ]


def test_sendai_challenge_part26_evidence_is_one_to_one_and_valid():
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


def test_sendai_part26_preserves_causality_boundaries():
    data = load(DATA_PATH)
    evidence = load(EVIDENCE_PATH)
    assert all(
        "独自" in packet["claims"][0]["review_note"]
        for packet in evidence
    )
    assert "causal claim" in data["quality_boundary"]


def test_sendai_manifest_keeps_part26_history_without_freezing_later_progress():
    manifest = load(MANIFEST_PATH)
    facts = {fact["id"]: fact for fact in manifest["reviewed_facts"]}
    assert facts["sendai-challenge-project-records-part24"]["cumulative_value"] == 72
    assert facts["sendai-challenge-project-records-part25"]["cumulative_value"] == 75
    assert facts["sendai-challenge-project-records-part26"]["cumulative_value"] == 78
    batches = [
        fact
        for fact in manifest["reviewed_facts"]
        if fact["id"].startswith("sendai-challenge-project-records-part")
    ]
    assert sum(fact["value"] for fact in batches) >= 78
    assert max(fact.get("cumulative_value", fact["value"]) for fact in batches) >= 78
    assert manifest["status"] == "review_in_progress"
    assert "independent Jichi Insight achievement scores" in manifest[
        "quality_boundary"
    ]
