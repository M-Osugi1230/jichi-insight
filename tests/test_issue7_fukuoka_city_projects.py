from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

PROJECTS_PATH = "data/reviewed/fukuoka-city/projects.json"
KPIS_PATH = "data/reviewed/fukuoka-city/project_kpis.json"
PACKETS_PATH = "data/reviewed/fukuoka-city/project_evidence_packets.json"
SOURCES_PATH = "data/catalog/fukuoka_city_project_sources.json"
SELECTION_PATH = "data/catalog/fukuoka_city_priority_project_selection.json"

UNIVERSAL = "jp-local-401307-project-2025-universal-city-promotion"
CHILD = "jp-local-401307-project-2025-child-rights-voice-support"
POINTS = "jp-local-401307-project-2025-fukuoka-points"


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


def test_fukuoka_city_projects_match_schemas() -> None:
    assert_valid("schemas/source_catalog.schema.json", load_json(SOURCES_PATH))
    for record in load_json(PROJECTS_PATH):
        assert_valid("schemas/project.schema.json", record)
    for record in load_json(KPIS_PATH):
        assert_valid("schemas/kpi.schema.json", record)
    for packet in load_json(PACKETS_PATH):
        assert_valid("schemas/evidence_packet.schema.json", packet)


def test_selection_rule_and_population() -> None:
    selection = load_json(SELECTION_PATH)
    # The population is defined as an intersection because Fukuoka City has
    # no single official priority-project list and no current project-level
    # administrative evaluation system.
    assert "重要施策に掲載された事業 ∩ 施策評価の対象事業" in selection["population"]["description"]
    assert selection["population"]["fiscal_year"] == 2025
    assert selection["population"]["policy_count"] == 30
    selections = selection["selections"]
    assert [item["pillar"] for item in selections] == [
        "目標1 一人ひとりが心豊かに暮らし、自分らしく輝いている",
        "目標2 すべての子ども・若者が夢を描きながら健やかに成長している",
        "目標3 地域の人々がつながり、支え合い、安全・安心に暮らしている",
    ]
    assert [item["project_id"] for item in selections] == [UNIVERSAL, CHILD, POINTS]
    projects = projects_by_id()
    for item in selections:
        record = projects[item["project_id"]]
        assert record["series_id"] == item["series_id"]
        assert record["official_title"] == item["official_title"]
        assert record["fiscal_year"] == 2025
        assert record["review_status"] == "reviewed"
    # The first-listed project of policy 3-1 could not be connected to a
    # project-level budget figure, so the rule moved to the next project and
    # the skip is on record.
    skipped = selection["skipped"]
    assert [item["official_title"] for item in skipped] == ["共創の地域づくり"]
    assert "束ね" in skipped[0]["reason"]


def test_project_budget_records_and_stage_honesty() -> None:
    projects = projects_by_id()
    expected = {
        UNIVERSAL: 7_893_000,
        CHILD: 30_809_000,
        POINTS: 60_718_000,
    }
    for project_id, initial in expected.items():
        records = projects[project_id]["budget_records"]
        # Settlement amounts are not registered: the per-project settlement
        # briefing documents could not be obtained, and the gap is stated in
        # the evidence packets instead of being filled from other documents.
        assert [item["kind"] for item in records] == ["initial_budget"]
        record = records[0]
        assert record["amount_yen"] == initial
        assert record["fiscal_year"] == 2025
        # The amounts come from initial-budget-proposal documents; the note
        # must keep that stage explicit and never claim enacted figures.
        assert "当初予算案" in record["note"]
        assert "成立値とは扱わない" in record["note"]


def test_kpi_baseline_target_actual_are_separated() -> None:
    kpis = {record["id"]: record for record in load_json(KPIS_PATH)}
    assert len(kpis) == 3
    for record in kpis.values():
        project = projects_by_id()[record["project_id"]]
        assert record["review_status"] == "reviewed"
        assert record["causality_note"]
        embedded = {item["name"]: item for item in project["kpis"]}
        summary = embedded[record["name"]]
        assert summary["baseline"] == record["baseline"]["value"]
        assert summary["target"] == record["target"]["value"]
        assert summary["assessment"] == record["assessment"]

    awareness = kpis[f"{UNIVERSAL}-kpi-universal-design-awareness"]
    assert awareness["baseline"]["value"] == 62.7
    assert awareness["target"]["value"] == 70
    assert awareness["actuals"][0]["value"] == 66.2
    assert awareness["actuals"][0]["period"] == "2025年度"
    assert awareness["assessment"] == "in_progress"

    voice = kpis[f"{CHILD}-kpi-children-voice-not-valued-share"]
    assert voice["direction"] == "decrease"
    # The baseline is 5.3% (FY2023) and the latest value is 9.7%: the
    # indicator worsened, matching the city's official D rating. The two
    # values must never be swapped.
    assert voice["baseline"]["value"] == 5.3
    assert voice["baseline"]["period"] == "2023年度"
    assert voice["target"]["value"] == "3％未満"
    assert voice["actuals"][0]["value"] == 9.7
    assert voice["assessment"] == "not_achieved"

    districts = kpis[f"{POINTS}-kpi-point-adoption-districts"]
    assert districts["baseline"]["value"] == 9
    assert districts["target"]["value"] == 100
    assert districts["actuals"][0]["value"] == 64
    assert districts["assessment"] == "in_progress"


def test_official_evaluation_is_the_citys_policy_level_not_ours() -> None:
    projects = projects_by_id()
    for record in projects.values():
        evaluation = record["official_evaluation"]
        assert evaluation["rating"] == "概ね順調"
        # Fukuoka City evaluates policies, not individual projects; the note
        # must say so and must not present the rating as our own judgement.
        assert "施策単位" in evaluation["note"]
        assert "Jichi Insight独自の評価ではない" in evaluation["note"]
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
        # Unregistered settlement amounts and contract/assembly/audit links
        # stay explicit open questions.
        assert any("決算額は未登録" in question for question in packet["open_questions"])
        assert any("未登録" in question for question in packet["open_questions"])
    for record in projects_by_id().values():
        assert set(record["sources"]) <= source_ids
    for record in load_json(KPIS_PATH):
        assert set(record["sources"]) <= source_ids


def test_budget_source_availability_is_honest() -> None:
    sources = {record["id"]: record for record in load_json(SOURCES_PATH)["records"]}
    # The General Affairs Bureau briefing was submitted to the assembly
    # committee, but its official URL now returns 404; the record must not
    # claim it is still published.
    briefing = sources["fukuoka-city-budget-briefing-general-affairs-fy2025"]
    assert briefing["availability"] == "not_found"
    assert "Internet Archive" in briefing["notes"]
    book = sources["fukuoka-city-budget-proposal-book1-fy2025"]
    assert book["availability"] == "published"
    assert "当初予算案" in book["notes"]
