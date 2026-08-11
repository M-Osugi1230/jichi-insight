from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/reviewed/sendai-city/challenge_project_batch_1.json"
EVIDENCE_PATH = ROOT / "data/reviewed/sendai-city/challenge_project_batch_1_evidence.json"
SOURCE_PATH = ROOT / "data/catalog/sendai_phase13_sources.json"
MANIFEST_PATH = ROOT / "data/catalog/sendai_phase13_review_manifest.json"
EVIDENCE_SCHEMA_PATH = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sendai_challenge_batch_1_scope_and_counts_are_exact():
    data = load(DATA_PATH)
    scope = data["scope"]

    assert data["official_code"] == "041009"
    assert data["review_status"] == "reviewed_partial"
    assert scope["challenge_project_number"] == 1
    assert scope["challenge_project_title"] == "杜と水の都プロジェクト"
    assert scope["reviewed_measure_count"] == 3
    assert scope["reviewed_priority_project_count"] == 11
    assert scope["reviewed_kpi_count"] == 7
    assert scope["total_challenge_priority_project_count"] == 108

    measures = data["measures"]
    assert [measure["sequence"] for measure in measures] == [1, 2, 3]
    assert sum(len(measure["priority_projects"]) for measure in measures) == 11
    assert sum(len(measure["kpis"]) for measure in measures) == 7


def test_sendai_challenge_batch_1_preserves_exact_measure_titles_and_pages():
    measures = load(DATA_PATH)["measures"]

    assert [measure["title"] for measure in measures] == [
        "勾当台・定禅寺通エリア活性化",
        "海浜エリア活性化",
        "みどりでつながるまちづくり",
    ]
    assert [measure["evidence_location"]["pdf_page_index"] for measure in measures] == [
        9,
        10,
        11,
    ]
    assert [measure["evidence_location"]["printed_page"] for measure in measures] == [
        7,
        8,
        9,
    ]


def test_sendai_challenge_batch_1_preserves_multi_series_and_target_types():
    measures = {measure["id"]: measure for measure in load(DATA_PATH)["measures"]}

    kotodai = measures["sendai-challenge-01-measure-01"]
    activities = kotodai["kpis"][0]
    activity_volume = kotodai["kpis"][1]
    assert activities["baseline"] == {
        "fiscal_year": 2023,
        "weekday": 9,
        "holiday": 8,
    }
    assert activities["target"]["type"] == "at_least_baseline"
    assert activity_volume["baseline"] == {
        "fiscal_year": 2023,
        "weekday": 10.25,
        "holiday": 17.58,
    }

    coast = measures["sendai-challenge-01-measure-02"]
    assert coast["kpis"][0]["baseline"]["value"] == 735_212
    assert coast["kpis"][0]["target"]["value"] == 800_000
    assert coast["kpis"][1]["baseline"]["value"] == 64.7
    assert coast["kpis"][1]["target"]["value"] == 100.0

    green = measures["sendai-challenge-01-measure-03"]
    assert green["kpis"][0]["baseline"] is None
    assert green["kpis"][0]["target"]["value"] == 1000
    assert green["kpis"][1]["target"] == {
        "type": "at_least",
        "value": 13,
        "period": "各年度",
    }
    assert green["kpis"][2]["baseline"]["value"] == 31.0
    assert green["kpis"][2]["target"]["type"] == "at_least_baseline"

    assert all(
        kpi["actual"] is None and kpi["assessment"] == "not_assessable"
        for measure in measures.values()
        for kpi in measure["kpis"]
    )


def test_sendai_challenge_batch_1_priority_projects_are_exact():
    measures = {measure["id"]: measure for measure in load(DATA_PATH)["measures"]}

    measure_1_projects = measures["sendai-challenge-01-measure-01"]["priority_projects"]
    measure_2_projects = measures["sendai-challenge-01-measure-02"]["priority_projects"]
    measure_3_projects = measures["sendai-challenge-01-measure-03"]["priority_projects"]

    assert [item["title"] for item in measure_1_projects] == [
        "新本庁舎整備事業",
        "勾当台公園及び周辺再整備事業",
        "西公園再整備事業",
    ]
    assert [item["title"] for item in measure_2_projects] == [
        "海浜エリア活性化事業",
        "東部地域移転跡地利活用推進事業",
        "海岸公園整備事業",
    ]
    assert [item["title"] for item in measure_3_projects] == [
        "市民協働によるみどりのまちづくり事業",
        "市街地のグリーンインフラ推進事業",
        "杜の都の風土を育む景観形成推進事業",
        "広瀬川創生・清流保全事業",
        "青葉山公園整備事業",
    ]


def test_sendai_challenge_batch_1_evidence_is_one_to_one_and_schema_valid():
    data = load(DATA_PATH)
    packets = load(EVIDENCE_PATH)
    schema = load(EVIDENCE_SCHEMA_PATH)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    assert len(packets) == 3
    assert {packet["subject_id"] for packet in packets} == {
        measure["id"] for measure in data["measures"]
    }
    assert all(list(validator.iter_errors(packet)) == [] for packet in packets)
    assert all(packet["subject_type"] == "project" for packet in packets)
    assert all(packet["review_status"] == "reviewed" for packet in packets)
    assert all(
        claim["decision"] == "accepted"
        for packet in packets
        for claim in packet["claims"]
    )


def test_sendai_challenge_batch_1_source_and_manifest_boundaries_are_explicit():
    sources = {record["id"]: record for record in load(SOURCE_PATH)["records"]}
    manifest = load(MANIFEST_PATH)
    facts = {fact["id"]: fact for fact in manifest["reviewed_facts"]}

    source = sources["sendai-city-implementation-plan-2024-2026-pdf"]
    assert source["organization"] == "仙台市"
    assert source["source_kind"] == "pdf"
    assert source["review_status"] == "reviewed_pages_5_11"
    assert "全108重点事業" in source["boundary"]

    batch = facts["sendai-challenge-project-batch-1"]
    assert batch["value"] == 11
    assert batch["measure_count"] == 3
    assert batch["kpi_count"] == 7
    assert batch["review_status"] == "reviewed_partial"
    assert "カバレッジ率" in batch["interpretation_boundary"]
    assert "重複掲載" in manifest["remaining_work"][0]
