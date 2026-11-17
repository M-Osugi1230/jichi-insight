from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

PROJECTS_PATH = "data/reviewed/kitakyushu-city/projects.json"
KPIS_PATH = "data/reviewed/kitakyushu-city/project_kpis.json"
PACKETS_PATH = "data/reviewed/kitakyushu-city/project_evidence_packets.json"
SOURCES_PATH = "data/catalog/kitakyushu_project_sources.json"
SELECTION_PATH = "data/catalog/kitakyushu_priority_project_selection.json"

MEGA = "jp-local-401005-project-2024-mega-region-promotion"
LINE = "jp-local-401005-project-2024-information-dissemination"
STOCK = "jp-local-401005-project-2024-disaster-stockpile"


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


def test_kitakyushu_projects_match_schemas() -> None:
    assert_valid("schemas/source_catalog.schema.json", load_json(SOURCES_PATH))
    for record in load_json(PROJECTS_PATH):
        assert_valid("schemas/project.schema.json", record)
    for record in load_json(KPIS_PATH):
        assert_valid("schemas/kpi.schema.json", record)
    for packet in load_json(PACKETS_PATH):
        assert_valid("schemas/evidence_packet.schema.json", packet)


def test_selection_rule_and_population() -> None:
    selection = load_json(SELECTION_PATH)
    assert selection["population"]["project_count"] == 198
    assert selection["population"]["fiscal_year"] == 2024
    selections = selection["selections"]
    assert [item["pillar"] for item in selections] == [
        "I「稼げるまち」の実現",
        "II「彩りあるまち」の実現",
        "III「安らぐまち」の実現",
    ]
    # One project per pillar, each the first in its bureau's official listing.
    assert [item["bureau_project_number"] for item in selections] == [1, 1, 1]
    assert [item["project_id"] for item in selections] == [MEGA, LINE, STOCK]
    projects = projects_by_id()
    for item in selections:
        record = projects[item["project_id"]]
        assert record["series_id"] == item["series_id"]
        assert record["official_title"] == item["official_title"]
        assert record["fiscal_year"] == 2024
        assert record["review_status"] == "reviewed"


def test_project_budget_records_and_settlement_stage_honesty() -> None:
    projects = projects_by_id()
    expected = {
        MEGA: (15_970_000, 5_621_000),
        LINE: (43_249_000, 37_486_000),
        STOCK: (19_263_000, 22_364_000),
    }
    for project_id, (initial, settlement) in expected.items():
        records = {item["kind"]: item for item in projects[project_id]["budget_records"]}
        assert records["initial_budget"]["amount_yen"] == initial
        assert records["initial_budget"]["fiscal_year"] == 2024
        assert records["settlement"]["amount_yen"] == settlement
        assert records["settlement"]["fiscal_year"] == 2024
        # The evaluation report was published before the FY2024 settlement was
        # certified by the assembly; the note must not claim certification.
        assert "認定前" in records["settlement"]["note"]
        assert "認定済み" not in records["settlement"]["note"].replace(
            "認定済みの確定値とは扱わない", ""
        )


def test_kpi_baseline_target_actual_are_separated() -> None:
    kpis = {record["id"]: record for record in load_json(KPIS_PATH)}
    assert len(kpis) == 4
    for record in kpis.values():
        project = projects_by_id()[record["project_id"]]
        assert record["review_status"] == "reviewed"
        assert record["causality_note"]
        embedded = {item["name"]: item for item in project["kpis"]}
        summary = embedded[record["name"]]
        assert summary["baseline"] == record["baseline"]["value"]
        assert summary["target"] == record["target"]["value"]
        assert summary["assessment"] == record["assessment"]

    line = kpis[f"{LINE}-kpi-line-friends"]
    assert line["baseline"]["value"] == 81_343
    assert line["baseline"]["period"] == "令和5年度"
    assert line["target"]["value"] == 90_000
    assert line["target"]["period"] == "令和6年度"
    assert line["actuals"] == [
        {
            "period": "令和6年度",
            "value": 92_857,
            "status": "available",
            "source_ids": ["kitakyushu-admin-eval-fy2024-mayor"],
        }
    ]
    assert line["assessment"] == "achieved"

    guests = kpis[f"{MEGA}-kpi-overnight-guests"]
    assert guests["baseline"]["value"] == 2338
    assert guests["target"]["value"] == 2268
    # FY2024 actuals were still being compiled in the source: not published,
    # never filled with an estimate.
    assert guests["actuals"][0]["value"] is None
    assert guests["actuals"][0]["status"] == "not_published"
    assert guests["assessment"] == "not_assessable"

    stock = kpis[f"{STOCK}-kpi-stockpile-adequacy"]
    assert stock["direction"] == "maintain"
    assert stock["baseline"]["value"] == stock["target"]["value"]
    assert stock["actuals"][0]["value"] == stock["target"]["value"]
    assert stock["assessment"] == "achieved"


def test_official_evaluation_is_the_citys_not_ours() -> None:
    projects = projects_by_id()
    assert projects[MEGA]["official_evaluation"]["rating"] == "概ね順調"
    assert projects[LINE]["official_evaluation"]["rating"] == "順調"
    assert projects[STOCK]["official_evaluation"]["rating"] == "順調"
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
    for record in projects_by_id().values():
        assert set(record["sources"]) <= source_ids
    for record in load_json(KPIS_PATH):
        assert set(record["sources"]) <= source_ids


def test_parent_policy_missing_is_explicit_not_invented() -> None:
    projects = projects_by_id()
    assert projects[MEGA]["parent_policy"] == "メガリージョンの視点による近隣市町との連携"
    # The source sheets print no policy name for these two projects.
    assert projects[LINE]["parent_policy"] is None
    assert projects[STOCK]["parent_policy"] is None
