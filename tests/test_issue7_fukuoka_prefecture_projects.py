from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

PROJECTS_PATH = "data/reviewed/fukuoka-prefecture/projects.json"
KPIS_PATH = "data/reviewed/fukuoka-prefecture/project_kpis.json"
PACKETS_PATH = "data/reviewed/fukuoka-prefecture/project_evidence_packets.json"
SOURCES_PATH = "data/catalog/fukuoka_project_sources.json"
SELECTION_PATH = "data/catalog/fukuoka_priority_project_selection.json"

MIRAI = "jp-local-400009-project-2025-mirai-kodomo-challenge"
HITORI = "jp-local-400009-project-2025-single-parent-employment-support"
KANSHO = "jp-local-400009-project-2025-infectious-disease-prevention"


def load_json(path: str) -> Any:
    with (ROOT / path).open(encoding="utf-8") as handle:
        return json.load(handle)


def assert_valid(schema_path: str, instance: Any) -> None:
    validator = Draft202012Validator(
        load_json(schema_path),
        format_checker=FormatChecker(),
    )
    errors = list(validator.iter_errors(instance))
    assert errors == [], "; ".join(error.message for error in errors)


def projects_by_id() -> dict[str, Any]:
    return {record["id"]: record for record in load_json(PROJECTS_PATH)}


def test_fukuoka_prefecture_projects_match_schemas() -> None:
    assert_valid("schemas/source_catalog.schema.json", load_json(SOURCES_PATH))
    for record in load_json(PROJECTS_PATH):
        assert_valid("schemas/project.schema.json", record)
    for record in load_json(KPIS_PATH):
        assert_valid("schemas/kpi.schema.json", record)
    for packet in load_json(PACKETS_PATH):
        assert_valid("schemas/evidence_packet.schema.json", packet)


def test_selection_rule_and_population() -> None:
    selection = load_json(SELECTION_PATH)
    assert selection["population"]["project_count"] == 266
    assert selection["population"]["fiscal_year"] == 2025
    selections = selection["selections"]
    assert [item["pillar"] for item in selections] == [
        "世界を視野に、未来を見据えて成長し、発展する",
        "誰もが住み慣れたところで働き、長く元気に暮らし、子どもを安心して産み育てることができる",
        "感染症や災害に負けない強靭な社会をつくる",
    ]
    # One project per pillar: the first listed under the pillar's first
    # initiative in the official plan-system index of the evaluation report.
    assert [item["evaluation_number"] for item in selections] == [46, 84, 66]
    assert [item["project_id"] for item in selections] == [MIRAI, HITORI, KANSHO]
    projects = projects_by_id()
    for item in selections:
        record = projects[item["project_id"]]
        assert record["series_id"] == item["series_id"]
        assert record["official_title"] == item["official_title"]
        assert record["fiscal_year"] == 2025
        assert record["review_status"] == "reviewed"


def test_project_budget_records_and_draft_stage_honesty() -> None:
    projects = projects_by_id()
    expected = {
        MIRAI: (118_155_000, 258_445_000, 284_117_000),
        HITORI: (40_795_000, 75_866_000, 52_365_000),
        KANSHO: (65_512_000, 86_006_000, 85_963_000),
    }
    for project_id, (settlement, initial, draft) in expected.items():
        records = {
            (item["kind"], item["fiscal_year"]): item
            for item in projects[project_id]["budget_records"]
        }
        assert records[("settlement", 2024)]["amount_yen"] == settlement
        assert records[("initial_budget", 2025)]["amount_yen"] == initial
        assert records[("initial_budget", 2026)]["amount_yen"] == draft
        # The FY2026 figure printed in the evaluation sheets is the draft
        # budget amount (per the report's own note); the note must say so and
        # must never present it as the enacted budget.
        draft_note = records[("initial_budget", 2026)]["note"]
        assert "予算案の額" in draft_note
        assert "成立後の当初予算額とは扱わない" in draft_note


def test_kpi_baseline_target_actual_are_separated() -> None:
    kpis = {record["id"]: record for record in load_json(KPIS_PATH)}
    assert len(kpis) == 5
    for record in kpis.values():
        project = projects_by_id()[record["project_id"]]
        assert record["review_status"] == "reviewed"
        assert record["causality_note"]
        embedded = {item["name"]: item for item in project["kpis"]}
        summary = embedded[record["name"]]
        assert summary["baseline"] == record["baseline"]["value"]
        assert summary["target"] == record["target"]["value"]
        assert summary["assessment"] == record["assessment"]

    mirai = kpis[f"{MIRAI}-kpi-activity-municipalities"]
    assert mirai["baseline"]["value"] == 0
    assert mirai["baseline"]["period"] == "令和4年度"
    assert mirai["target"]["value"] == 60
    assert mirai["target"]["period"] == "令和6年度"
    assert [item["value"] for item in mirai["actuals"]] == [39, 46, 49]
    assert mirai["assessment"] == "not_achieved"

    rate = kpis[f"{HITORI}-kpi-employment-rate"]
    assert rate["baseline"]["value"] == 74.7
    assert rate["baseline"]["period"] == "令和元年度"
    assert rate["target"]["value"] == 77.7
    assert [item["value"] for item in rate["actuals"]] == [62.0, 66.0, 68.4, None]
    # The FY2025 actual was still being surveyed in the source: not
    # published, never filled with an estimate.
    assert rate["actuals"][-1]["status"] == "not_published"
    assert rate["assessment"] == "not_achieved"

    placements = kpis[f"{HITORI}-kpi-job-placements"]
    assert placements["baseline"]["value"] == 903
    # The target is a five-year cumulative figure, never an annual one.
    assert placements["target"]["value"] == 5000
    assert placements["target"]["period"] == "令和4年度～令和8年度累計"
    cumulative = placements["actuals"][-1]
    assert cumulative["period"] == "令和4年度～令和6年度累計"
    assert cumulative["value"] == 2249
    annual = [item["value"] for item in placements["actuals"][:3]]
    assert annual == [603, 819, 827]
    assert sum(annual) == cumulative["value"]
    assert placements["assessment"] == "in_progress"

    for suffix in ("designated-beds", "negative-pressure-beds"):
        beds = kpis[f"{KANSHO}-kpi-{suffix}"]
        assert beds["direction"] == "maintain"
        assert beds["baseline"]["value"] == 66
        assert beds["target"]["value"] == 66
        assert [item["value"] for item in beds["actuals"]] == [66, 66, 66, 66, 66]
        assert beds["assessment"] == "achieved"


def test_official_evaluation_is_the_prefectures_not_ours() -> None:
    projects = projects_by_id()
    assert projects[MIRAI]["official_evaluation"]["rating"] == "継続（改善）"
    assert projects[HITORI]["official_evaluation"]["rating"] == "継続（縮小）"
    assert projects[KANSHO]["official_evaluation"]["rating"] == "継続（一部改善）"
    for record in projects.values():
        assert record["official_evaluation"]["direction"] == "継続"
        assert "Jichi Insight独自の評価ではない" in record["official_evaluation"]["note"]
        # Promises are Issue #8: no fabricated links in the pilot.
        assert record["related_promise_ids"] == []


def test_every_project_has_an_evidence_packet_and_known_sources() -> None:
    source_ids = {record["id"] for record in load_json(SOURCES_PATH)["records"]}
    packets = {packet["subject_id"]: packet for packet in load_json(PACKETS_PATH)}
    assert set(packets) == set(projects_by_id())
    for packet in packets.values():
        assert packet["subject_type"] == "project"
        assert packet["review_status"] == "reviewed"
        for claim in packet["claims"]:
            assert set(claim["source_ids"]) <= source_ids
        # Unregistered contract/assembly/audit links stay explicit open questions.
        assert any("未登録" in question for question in packet["open_questions"])
        # The draft status of the FY2026 budget figure stays an open question.
        assert any("予算案の額" in question for question in packet["open_questions"])
    for record in projects_by_id().values():
        assert set(record["sources"]) <= source_ids
    for record in load_json(KPIS_PATH):
        assert set(record["sources"]) <= source_ids


def test_parent_policy_and_target_population_honesty() -> None:
    projects = projects_by_id()
    assert projects[MIRAI]["parent_policy"] == "次代を担う「人財」の育成"
    assert projects[HITORI]["parent_policy"] == "雇用対策の充実、魅力ある職場づくり"
    assert projects[KANSHO]["parent_policy"] == "感染症対策の推進"
    # The infectious-disease sheet states no separate target population;
    # it stays null instead of being inferred from the purpose text.
    assert projects[KANSHO]["target_population"] is None
    assert projects[MIRAI]["target_population"] == "次代を担うこどもたち"
