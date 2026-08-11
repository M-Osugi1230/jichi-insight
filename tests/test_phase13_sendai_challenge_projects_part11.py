from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/catalog/sendai_challenge_project_reviews_part11.json"
EVIDENCE_PATH = ROOT / "data/evidence/sendai_challenge_project_reviews_part11_evidence.json"
MANIFEST_PATH = ROOT / "data/catalog/sendai_phase13_review_manifest.json"
SCHEMA_PATH = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sendai_challenge_part11_counts_and_coverage_are_exact():
    data = load(DATA_PATH)
    summary = data["summary"]

    assert summary["prior_reviewed_record_count"] == 30
    assert summary["batch_reviewed_record_count"] == 3
    assert summary["cumulative_reviewed_record_count"] == 33
    assert summary["total_source_project_count"] == 108
    assert summary["remaining_record_count"] == 75
    assert summary["complete"] is False


def test_sendai_challenge_part11_records_are_exact_and_source_reported():
    records = load(DATA_PATH)["records"]
    assert len(records) == 3
    assert [record["project_name_ja"] for record in records] == [
        "自殺対策事業",
        "障害者相談支援体制推進事業",
        "高齢者生活支援事業",
    ]
    assert [record["source_pdf_page_index_0_based"] for record in records] == [
        41,
        42,
        43,
    ]
    assert [record["source_reported_evaluation"] for record in records] == [
        "circle",
        "circle",
        "circle",
    ]
    assert [record["responsible_bureau_ja"] for record in records] == [
        "健康福祉局",
        "健康福祉局",
        "健康福祉局",
    ]
    assert [record["lead_section_ja"] for record in records] == [
        "障害者支援課",
        "障害者支援課",
        "地域包括ケア推進課",
    ]


def test_sendai_challenge_part11_evidence_is_one_to_one_and_valid():
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


def test_sendai_part11_does_not_promote_source_effect_language_to_causality():
    data = load(DATA_PATH)
    evidence = load(EVIDENCE_PATH)
    suicide = next(record for record in data["records"] if record["id"] == "suicide-prevention")
    packet = next(packet for packet in evidence if packet["subject_id"] == suicide["id"])

    assert suicide["review_status"] == "reviewed_core_evaluation"
    assert suicide["source_reported_evaluation"] == "circle"
    assert "因果評価" in packet["claims"][0]["review_note"]
    assert "causal claim" in data["quality_boundary"]


def test_sendai_manifest_advances_to_thirty_three_without_claiming_completion():
    manifest = load(MANIFEST_PATH)
    facts = {fact["id"]: fact for fact in manifest["reviewed_facts"]}
    part11 = facts["sendai-challenge-project-records-part11"]
    batches = [
        fact
        for fact in manifest["reviewed_facts"]
        if fact["id"].startswith("sendai-challenge-project-records-part")
    ]
    cumulative_reviewed = sum(fact["value"] for fact in batches)
    remaining = 108 - cumulative_reviewed

    assert part11["value"] == 3
    assert part11["cumulative_value"] == 33
    assert part11["source_reported_breakdown"] == {"circle": 3}
    assert "残り75事業" in part11["interpretation_boundary"]
    assert cumulative_reviewed >= 33
    assert f"{cumulative_reviewed}事業を個票レビュー済み" in manifest["remaining_work"][0]
    assert f"残り{remaining}事業" in manifest["remaining_work"][0]
    assert "independent Jichi Insight achievement scores" in manifest[
        "quality_boundary"
    ]
