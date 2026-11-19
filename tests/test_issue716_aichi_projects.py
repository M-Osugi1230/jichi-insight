"""Issue #716: Aichi Prefecture priority projects (cluster 2, stage 2).

The population is the prefecture's FY2025 management-project evaluation
(296 management projects). One project is selected per direction of
Aichi Vision 2030, anchored on the direction's first major policy and
chosen by listing order in the official results list, never by amount.
Amounts are the evaluation sheets' total cost (personnel + project +
debt service). FY2026 amounts are published only in 100-million-yen
units in the budget-reflection list, so they are recorded as rounded
figures with that caveat in the note.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

PROJECTS_PATH = "data/reviewed/aichi-prefecture/projects.json"
KPIS_PATH = "data/reviewed/aichi-prefecture/project_kpis.json"
PACKETS_PATH = "data/reviewed/aichi-prefecture/project_evidence_packets.json"
SOURCES_PATH = "data/catalog/aichi_project_sources.json"
POLICY_SOURCES_PATH = "data/catalog/aichi_policy_sources.json"
SELECTION_PATH = "data/catalog/aichi_priority_project_selection.json"

MID = "jp-local-230006"
TERM = "jp-local-230006-executive-2023-02-15"
# Governor promises registered in stage 3 (Issue #722) link back to
# these projects; the promise-side lists are pinned in
# tests/test_issue722_aichi_prefecture_promise_registration.py.
EXPECTED_PROMISE_LINKS = {
    "infectious-disease-control": [f"{TERM}-promise-002"],
    "high-school-education-promotion": [f"{TERM}-promise-005"],
    "gender-equality-promotion": [f"{TERM}-promise-005"],
    "child-rearing-support": [f"{TERM}-promise-005"],
    "worker-welfare-promotion": [f"{TERM}-promise-005"],
    "station-ai-project": [f"{TERM}-promise-004"],
    "aichi-sky-expo-management": [f"{TERM}-promise-004"],
    "transport-measures": [f"{TERM}-promise-003"],
    "ghibli-park-promotion": [f"{TERM}-promise-001"],
    "global-warming-countermeasures": [f"{TERM}-promise-009"],
}
SLUGS = {
    "infectious-disease-control": ("感染症対策事業", "C：相当程度進展あり", "拡大"),
    "high-school-education-promotion": ("高等学校教育振興事業", "C：相当程度進展あり", "現行水準"),
    "gender-equality-promotion": ("男女共同参画推進事業", "C：相当程度進展あり", "現行水準"),
    "child-rearing-support": ("子育て支援事業", "C：相当程度進展あり", "縮小"),
    "worker-welfare-promotion": ("勤労者福祉推進事業", "C：相当程度進展あり", "現行水準"),
    "station-ai-project": ("STATION Aiプロジェクト推進事業", "C：相当程度進展あり", "拡大"),
    "aichi-sky-expo-management": ("愛知県国際展示場管理運営事業", "B：目標達成", "現行水準"),
    "transport-measures": ("交通対策事業", "B：目標達成", "縮小"),
    "ghibli-park-promotion": ("ジブリパーク推進事業", "B：目標達成", "現行水準"),
    "global-warming-countermeasures": ("地球温暖化対策事業", "C：相当程度進展あり", "縮小"),
}
# (FY2024 initial budget, FY2024 settlement, FY2025 initial budget,
#  FY2026 initial budget as published in 100-million-yen units)
EXPECTED_BUDGETS = {
    "infectious-disease-control": (3_931_895_000, 4_159_956_000, 2_698_658_000, 3_120_000_000),
    "high-school-education-promotion": (1_490_352_000, 1_987_758_000, 1_753_212_000, 1_770_000_000),
    "gender-equality-promotion": (263_346_000, 250_825_000, 262_169_000, 270_000_000),
    "child-rearing-support": (20_878_938_000, 18_749_473_000, 20_879_035_000, 18_580_000_000),
    "worker-welfare-promotion": (1_829_676_000, 1_594_596_000, 1_634_502_000, 1_630_000_000),
    "station-ai-project": (13_235_623_000, 14_159_751_000, 2_530_642_000, 3_010_000_000),
    "aichi-sky-expo-management": (2_442_688_000, 2_420_911_000, 2_398_032_000, 2_480_000_000),
    "transport-measures": (3_063_346_000, 2_785_467_000, 3_489_977_000, 3_290_000_000),
    "ghibli-park-promotion": (1_509_248_000, 2_512_308_000, 1_797_501_000, 1_830_000_000),
    "global-warming-countermeasures": (2_050_712_000, 1_607_482_000, 3_011_505_000, 2_510_000_000),
}


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


def project_id(slug: str) -> str:
    return f"{MID}-project-2025-{slug}"


def known_source_ids() -> set[str]:
    ids = {record["id"] for record in load_json(SOURCES_PATH)["records"]}
    ids.update(record["id"] for record in load_json(POLICY_SOURCES_PATH)["records"])
    return ids


def test_aichi_projects_match_schemas() -> None:
    assert_valid("schemas/source_catalog.schema.json", load_json(SOURCES_PATH))
    for record in load_json(PROJECTS_PATH):
        assert_valid("schemas/project.schema.json", record)
    for record in load_json(KPIS_PATH):
        assert_valid("schemas/kpi.schema.json", record)
    for packet in load_json(PACKETS_PATH):
        assert_valid("schemas/evidence_packet.schema.json", packet)


def test_selection_rule_and_population() -> None:
    selection = load_json(SELECTION_PATH)
    assert selection["issue"] == 716
    assert selection["population"]["project_count"] == 296
    assert selection["population"]["fiscal_year"] == 2025
    assert selection["scope"] == "initial"
    assert len(selection["selection_rule"]["pillars"]) == 10
    selections = selection["selections"]
    assert len(selections) == 10
    projects = projects_by_id()
    assert len(projects) == 10
    assert [item["management_project_code"] for item in selections] == [
        "3050", "6070", "1640", "3110", "3710",
        "3532", "1053", "1080", "0035", "2560",
    ]
    for item in selections:
        record = projects[item["project_id"]]
        assert record["series_id"] == item["series_id"]
        assert record["official_title"] == item["official_title"]
        assert record["parent_policy"] == item["initiative"]
        assert record["fiscal_year"] == 2025
        assert record["review_status"] == "reviewed"
        assert set(item["source_ids"]) <= known_source_ids()


def test_project_budget_records_and_fy2026_rounding_honesty() -> None:
    projects = projects_by_id()
    assert set(projects) == {project_id(slug) for slug in SLUGS}
    for slug, (initial24, settlement24, initial25, initial26) in EXPECTED_BUDGETS.items():
        records = {
            (item["kind"], item["fiscal_year"]): item
            for item in projects[project_id(slug)]["budget_records"]
        }
        assert records[("initial_budget", 2024)]["amount_yen"] == initial24
        assert records[("settlement", 2024)]["amount_yen"] == settlement24
        assert records[("initial_budget", 2025)]["amount_yen"] == initial25
        assert records[("initial_budget", 2026)]["amount_yen"] == initial26
        # The FY2026 figure is published only in 100-million-yen units in
        # the reflection list; the note must never present it as an exact
        # thousand-yen figure.
        fy26_note = records[("initial_budget", 2026)]["note"]
        assert "億円単位" in fy26_note
        assert "確定額ではない" in fy26_note
        # The FY2025 figure is the enacted initial budget from the sheet.
        assert "成立後" in records[("initial_budget", 2025)]["note"]


def test_kpi_records_match_embedded_summaries() -> None:
    kpis = load_json(KPIS_PATH)
    assert len(kpis) == 32
    projects = projects_by_id()
    for record in kpis:
        assert record["review_status"] == "reviewed"
        assert record["causality_note"]
        assert set(record["sources"]) <= known_source_ids()
        project = projects[record["project_id"]]
        embedded = {item["name"]: item for item in project["kpis"]}
        summary = embedded[record["name"]]
        baseline_value = None if record["baseline"] is None else record["baseline"]["value"]
        assert summary["baseline"] == baseline_value
        assert summary["target"] == record["target"]["value"]
        assert summary["assessment"] == record["assessment"]
        # FY2025 values in the sheets are projections (見込), so the
        # actuals stop at the FY2024 actual.
        assert [item["period"] for item in record["actuals"]] == ["令和6年度"]
        assert record["actuals"][0]["value"] == summary["actual"]

    visitors = {r["id"]: r for r in kpis}[
        f"{project_id('ghibli-park-promotion')}-kpi-memorial-park-visitors"
    ]
    assert visitors["target"]["value"] == 2_800_000
    assert visitors["actuals"][0]["value"] == 2_940_000
    assert visitors["assessment"] == "achieved"

    zev = {r["id"]: r for r in kpis}[
        f"{project_id('global-warming-countermeasures')}-kpi-zev-sales-share"
    ]
    assert zev["target"]["value"] == 13.4
    assert zev["actuals"][0]["value"] == 3.5
    assert zev["assessment"] == "not_achieved"

    floor_users = {r["id"]: r for r in kpis}[
        f"{project_id('worker-welfare-promotion')}-kpi-support-floor-users"
    ]
    # The target is qualitative ("exceed the previous year") and the
    # sheet prints no previous-year value, so it stays not assessable.
    assert floor_users["target"]["value"] == "前年度実績を上回る値"
    assert floor_users["assessment"] == "not_assessable"


def test_official_evaluation_is_the_prefectures_not_ours() -> None:
    projects = projects_by_id()
    for slug, (title, rating, direction) in SLUGS.items():
        record = projects[project_id(slug)]
        assert record["official_title"] == title
        assert record["official_evaluation"]["rating"] == rating
        assert record["official_evaluation"]["direction"] == direction
        assert "Jichi Insight独自の評価ではない" in record["official_evaluation"]["note"]
        # Governor promises were registered in stage 3 (Issue #722);
        # the project-side links are pinned here and cross-checked
        # bidirectionally in the stage-3 registration test.
        assert record["related_promise_ids"] == EXPECTED_PROMISE_LINKS[slug]


def test_every_project_has_an_evidence_packet_and_known_sources() -> None:
    source_ids = known_source_ids()
    packets = {packet["subject_id"]: packet for packet in load_json(PACKETS_PATH)}
    assert set(packets) == set(projects_by_id())
    for packet in packets.values():
        assert packet["subject_type"] == "project"
        assert packet["review_status"] == "reviewed"
        for claim in packet["claims"]:
            assert set(claim["source_ids"]) <= source_ids
        # Unregistered contract/assembly/audit links and the unlinked
        # promise registry stay explicit open questions.
        assert any("未登録" in question for question in packet["open_questions"])
        assert any("概数" in question for question in packet["open_questions"])
    for record in projects_by_id().values():
        assert set(record["sources"]) <= source_ids


def test_documented_cross_source_discrepancy_for_high_school_project() -> None:
    packet = {p["subject_id"]: p for p in load_json(PACKETS_PATH)}[
        project_id("high-school-education-promotion")
    ]
    # The results list prints FY2024 settlement as 20.0 oku yen while the
    # sheet's total is 1,987,758 thousand yen; the sheet value is used
    # and the discrepancy is documented, not silently resolved.
    assert any("20.0億円" in question for question in packet["open_questions"])
    record = projects_by_id()[project_id("high-school-education-promotion")]
    settlement = {
        (item["kind"], item["fiscal_year"]): item for item in record["budget_records"]
    }[("settlement", 2024)]
    assert settlement["amount_yen"] == 1_987_758_000
