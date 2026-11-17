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
SHIN_JIDAI = "jp-local-401005-project-2024-shin-jidai-youth-challenge"
WOMEN = "jp-local-401005-project-2024-women-perspective-policy"
CITY_PROMO = "jp-local-401005-project-2024-city-promotion"
SUMARAKU = "jp-local-401005-project-2024-sumaraku-ward-office"
SHELTER = "jp-local-401005-project-2024-community-shelter-operation"
DRILL = "jp-local-401005-project-2024-city-disaster-drill"
FOREIGN = "jp-local-401005-project-2024-foreign-resident-coexistence"


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
    # Pilot: one project per pillar, each the first in the official listing.
    pilot = selections[:3]
    assert [item["pillar"] for item in pilot] == [
        "I「稼げるまち」の実現",
        "II「彩りあるまち」の実現",
        "III「安らぐまち」の実現",
    ]
    assert [item["bureau_project_number"] for item in pilot] == [1, 1, 1]
    assert [item["project_id"] for item in pilot] == [MEGA, LINE, STOCK]
    # Scale-up: the next two projects per pillar in publication order, plus
    # the first abolished project (lifecycle end) in publication order.
    added = selections[3:]
    assert [(item["pillar"], item["bureau"], item["bureau_project_number"]) for item in added] == [
        ("I「稼げるまち」の実現", "政策局", 2),
        ("I「稼げるまち」の実現", "政策局", 3),
        ("II「彩りあるまち」の実現", "市長公室", 2),
        ("II「彩りあるまち」の実現", "政策局", 5),
        ("III「安らぐまち」の実現", "危機管理室", 2),
        ("III「安らぐまち」の実現", "危機管理室", 3),
        ("III「安らぐまち」の実現", "政策局", 6),
    ]
    assert [item["project_id"] for item in added] == [
        SHIN_JIDAI,
        WOMEN,
        CITY_PROMO,
        SUMARAKU,
        SHELTER,
        DRILL,
        FOREIGN,
    ]
    assert all(item["selection_round"] == "scale" for item in added)
    assert selection["expansion_rule"]["total_count"] == 10
    assert len(selections) == 10
    assert len(projects_by_id()) == 10
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
        SHIN_JIDAI: (50_000_000, 45_654_000),
        WOMEN: (5_000_000, 4_636_000),
        CITY_PROMO: (71_037_000, 69_624_000),
        SUMARAKU: (287_583_000, 207_806_000),
        SHELTER: (7_600_000, 5_790_000),
        DRILL: (6_000_000, 3_982_000),
        FOREIGN: (65_821_000, 64_266_000),
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
    assert len(kpis) == 13
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

    promo = kpis[f"{CITY_PROMO}-kpi-city-affection"]
    assert promo["baseline"]["value"] == 87.0
    assert promo["baseline"]["period"] == "令和5年度"
    assert promo["target"]["value"] == 90.0
    assert promo["target"]["period"] == "令和6年度"
    assert promo["actuals"][0]["value"] == 85.2
    # Printed achievement rate is 94.7%: mostly achieved, not achieved.
    assert promo["assessment"] == "mostly_achieved"

    online = kpis[f"{SUMARAKU}-kpi-online-application-rate"]
    assert online["baseline"]["value"] == 24.0
    assert online["baseline"]["period"] == "令和4年度"
    # The 45.0% target belongs to FY2027, so the FY2024 actual is mid-course.
    assert online["target"]["value"] == 45.0
    assert online["target"]["period"] == "令和7年度"
    assert online["actuals"][0]["value"] == 40.1
    assert online["assessment"] == "in_progress"

    work_time = kpis[f"{SUMARAKU}-kpi-window-work-time-reduction"]
    assert work_time["direction"] == "decrease"
    # Reductions are recorded as negative values (▲50.0% target for FY2029).
    assert work_time["target"]["value"] == -50.0
    assert work_time["actuals"][0]["value"] == -45.5
    assert work_time["assessment"] == "in_progress"

    youth = kpis[f"{SHIN_JIDAI}-kpi-youth-activity-image"]
    # No baseline or target value is printed in the source (both are "―");
    # the FY2024 actual must not be promoted into either slot.
    assert youth["baseline"]["value"] is None
    assert youth["target"]["value"] is None
    assert youth["target"]["period"] == "令和8年度"
    assert youth["actuals"][0]["value"] == 8.6
    assert youth["assessment"] == "not_assessable"

    livability = kpis[f"{FOREIGN}-kpi-foreign-resident-livability"]
    assert livability["baseline"]["value"] == 72.4
    # The survey runs once every five years: no target or FY2024 actual exists.
    assert livability["target"]["value"] is None
    assert livability["actuals"][0]["value"] is None
    assert livability["actuals"][0]["status"] == "not_published"
    assert livability["assessment"] == "not_assessable"


def test_official_evaluation_is_the_citys_not_ours() -> None:
    projects = projects_by_id()
    assert projects[MEGA]["official_evaluation"]["rating"] == "概ね順調"
    assert projects[LINE]["official_evaluation"]["rating"] == "順調"
    assert projects[STOCK]["official_evaluation"]["rating"] == "順調"
    expected_directions = {
        MEGA: "継続",
        LINE: "継続",
        STOCK: "継続",
        SHIN_JIDAI: "継続",
        WOMEN: "継続",
        CITY_PROMO: "継続",
        SUMARAKU: "拡充",
        SHELTER: "継続",
        DRILL: "継続",
        FOREIGN: "廃止",
    }
    for project_id, direction in expected_directions.items():
        record = projects[project_id]
        assert record["official_evaluation"]["direction"] == direction
    for record in projects.values():
        assert "Jichi Insight独自の評価ではない" in record["official_evaluation"]["note"]
    # Issue #8 registered the mayor's 34 manifesto items and linked the
    # ones with defensible, wording-based connections. Links are pinned
    # exactly here; unlinked projects keep an empty list (not "no data").
    term = "jp-local-401005-executive-2023-02-20"
    expected_links = {
        MEGA: [],
        LINE: [f"{term}-promise-005", f"{term}-promise-033"],
        STOCK: [f"{term}-promise-029"],
        SHIN_JIDAI: [f"{term}-promise-020"],
        WOMEN: [f"{term}-promise-013"],
        CITY_PROMO: [f"{term}-promise-033", f"{term}-promise-034"],
        SUMARAKU: [f"{term}-promise-005"],
        SHELTER: [f"{term}-promise-029"],
        DRILL: [],
        FOREIGN: [],
    }
    for project_id, promise_ids in expected_links.items():
        assert projects[project_id]["related_promise_ids"] == promise_ids


def test_lifecycle_end_project_is_the_abolished_one() -> None:
    projects = projects_by_id()
    abolished = [
        record
        for record in projects.values()
        if record["official_evaluation"]["direction"] == "廃止"
    ]
    # At most one completed/abolished project may be included; it is the
    # foreign-resident coexistence project, whose work continues under a
    # successor project from FY2025 (a reorganisation, not a disappearance).
    assert [record["id"] for record in abolished] == [FOREIGN]
    note = projects[FOREIGN]["official_evaluation"]["note"]
    assert "外国人材の受入れ環境整備事業" in note


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
    # The source sheets print no policy name for these projects.
    assert projects[LINE]["parent_policy"] is None
    assert projects[STOCK]["parent_policy"] is None
    assert projects[SHELTER]["parent_policy"] is None
    assert projects[SHIN_JIDAI]["parent_policy"] == "若者のチャレンジ支援"
    assert projects[WOMEN]["parent_policy"] == "女性のキャリア形成支援"
    assert projects[CITY_PROMO]["parent_policy"] == (
        "都市ブランドの確立（ポジティブな情報発信による北九州市のイメージアップ）"
    )
    assert projects[SUMARAKU]["parent_policy"] == "DXによる市民サービス向上"
    assert projects[DRILL]["parent_policy"] == "自助・共助・公助による防災力のさらなる強化"
    assert projects[FOREIGN]["parent_policy"] == "外国人との共生社会の実現に向けた環境整備"
