from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/catalog/sendai_challenge_project_reviews_part13.json"
EVIDENCE_PATH = ROOT / "data/evidence/sendai_challenge_project_reviews_part13_evidence.json"
MANIFEST_PATH = ROOT / "data/catalog/sendai_phase13_review_manifest.json"
SCHEMA_PATH = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sendai_challenge_part13_counts_and_coverage_are_exact():
    data = load(DATA_PATH)
    summary = data["summary"]

    assert summary["prior_reviewed_record_count"] == 36
    assert summary["batch_reviewed_record_count"] == 3
    assert summary["cumulative_reviewed_record_count"] == 39
    assert summary["total_source_project_count"] == 108
    assert summary["remaining_record_count"] == 69
    assert summary["complete"] is False


def test_sendai_challenge_part13_records_are_exact_and_source_reported():
    records = load(DATA_PATH)["records"]
    assert len(records) == 3
    assert [record["project_name_ja"] for record in records] == [
        "地域づくりパートナーサポート事業",
        "クロス・センダイ・ラボによる公民連携推進事業",
        "まち再生・まち育て活動支援事業",
    ]
    assert [record["source_pdf_page_index_0_based"] for record in records] == [
        49,
        50,
        50,
    ]
    assert [record["source_reported_evaluation"] for record in records] == [
        "circle",
        "circle",
        "double_circle",
    ]
    assert [record["responsible_bureau_ja"] for record in records] == [
        "市民局・各区",
        "まちづくり政策局",
        "都市整備局",
    ]
    assert [record["lead_section_ja"] for record in records] == [
        "市民局　市民協働推進課・地域政策課",
        "プロジェクト推進課",
        "都心まちづくり課",
    ]


def test_sendai_challenge_part13_evidence_is_one_to_one_and_valid():
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


def test_sendai_part13_preserves_rating_and_causality_boundaries():
    data = load(DATA_PATH)
    evidence = load(EVIDENCE_PATH)
    records = {record["id"]: record for record in data["records"]}
    packets = {packet["subject_id"]: packet for packet in evidence}

    assert records["cross-sendai-lab-public-private-collaboration"][
        "source_reported_evaluation"
    ] == "circle"
    assert records["urban-regeneration-community-development-support"][
        "source_reported_evaluation"
    ] == "double_circle"
    assert "2段組み" in packets[
        "cross-sendai-lab-public-private-collaboration"
    ]["claims"][0]["location_note"]
    assert "因果評価" in packets[
        "urban-regeneration-community-development-support"
    ]["claims"][0]["review_note"]
    assert "causal claim" in data["quality_boundary"]


def test_sendai_manifest_advances_to_thirty_nine_without_claiming_completion():
    manifest = load(MANIFEST_PATH)
    facts = {fact["id"]: fact for fact in manifest["reviewed_facts"]}
    part13 = facts["sendai-challenge-project-records-part13"]
    batches = [
        fact
        for fact in manifest["reviewed_facts"]
        if fact["id"].startswith("sendai-challenge-project-records-part")
    ]
    cumulative_reviewed = sum(fact["value"] for fact in batches)
    remaining = 108 - cumulative_reviewed

    assert part13["value"] == 3
    assert part13["cumulative_value"] == 39
    assert part13["source_reported_breakdown"] == {
        "circle": 2,
        "double_circle": 1,
    }
    assert "残り69事業" in part13["interpretation_boundary"]
    assert cumulative_reviewed >= 39
    assert f"{cumulative_reviewed}事業を個票レビュー済み" in manifest[
        "remaining_work"
    ][0]
    assert f"残り{remaining}事業" in manifest["remaining_work"][0]
    assert "independent Jichi Insight achievement scores" in manifest[
        "quality_boundary"
    ]
