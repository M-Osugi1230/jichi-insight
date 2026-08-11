from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/catalog/sendai_challenge_project_reviews_part14.json"
EVIDENCE_PATH = ROOT / "data/evidence/sendai_challenge_project_reviews_part14_evidence.json"
MANIFEST_PATH = ROOT / "data/catalog/sendai_phase13_review_manifest.json"
SCHEMA_PATH = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sendai_challenge_part14_counts_and_coverage_are_exact():
    data = load(DATA_PATH)
    summary = data["summary"]

    assert summary["prior_reviewed_record_count"] == 39
    assert summary["batch_reviewed_record_count"] == 3
    assert summary["cumulative_reviewed_record_count"] == 42
    assert summary["total_source_project_count"] == 108
    assert summary["remaining_record_count"] == 66
    assert summary["complete"] is False


def test_sendai_challenge_part14_records_are_exact_and_source_reported():
    records = load(DATA_PATH)["records"]
    assert len(records) == 3
    assert [record["project_name_ja"] for record in records] == [
        "宮城総合支所庁舎建替事業",
        "泉区役所建替事業",
        "公共交通利用促進事業",
    ]
    assert [record["source_pdf_page_index_0_based"] for record in records] == [51, 51, 52]
    assert [record["source_reported_evaluation"] for record in records] == [
        "circle",
        "circle",
        "circle",
    ]
    assert [record["responsible_bureau_ja"] for record in records] == [
        "青葉区　宮城総合支所",
        "財政局・都市整備局・泉区",
        "都市整備局",
    ]
    assert [record["lead_section_ja"] for record in records] == [
        "総務課",
        "泉区　泉中央地区活性化推進室",
        "公共交通推進課",
    ]


def test_sendai_challenge_part14_evidence_is_one_to_one_and_valid():
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


def test_sendai_part14_preserves_causality_boundaries():
    data = load(DATA_PATH)
    evidence = load(EVIDENCE_PATH)

    assert all(
        record["source_reported_evaluation"] == "circle"
        for record in data["records"]
    )
    assert all(
        "独自" in packet["claims"][0]["review_note"]
        for packet in evidence
    )
    assert "causal claim" in data["quality_boundary"]


def test_sendai_manifest_advances_to_forty_two_without_claiming_completion():
    manifest = load(MANIFEST_PATH)
    facts = {fact["id"]: fact for fact in manifest["reviewed_facts"]}
    part14 = facts["sendai-challenge-project-records-part14"]
    batches = [
        fact
        for fact in manifest["reviewed_facts"]
        if fact["id"].startswith("sendai-challenge-project-records-part")
    ]
    cumulative_reviewed = sum(fact["value"] for fact in batches)
    remaining = 108 - cumulative_reviewed

    assert part14["value"] == 3
    assert part14["cumulative_value"] == 42
    assert part14["source_reported_breakdown"] == {"circle": 3}
    assert "残り66事業" in part14["interpretation_boundary"]
    assert cumulative_reviewed >= 42
    assert f"{cumulative_reviewed}事業を個票レビュー済み" in manifest[
        "remaining_work"
    ][0]
    assert f"残り{remaining}事業" in manifest["remaining_work"][0]
    assert "independent Jichi Insight achievement scores" in manifest[
        "quality_boundary"
    ]
