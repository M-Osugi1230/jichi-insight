"""Issue #742: Hokkaido Prefecture priority projects (cluster 3, stage 2).

The population is the prefecture's FY2025 policy evaluation (basic
evaluation): all 121 measures organised along the Hokkaido Comprehensive
Plan's policy structure. Ten measures are selected by round-robin over
the plan's three basic directions (pillars in official listing order),
taking, per pillar, the first-listed measure of the pillar's first
policy-direction group in the official evaluation list — never by
amount. Amounts are the measure-level budget totals printed at the head
of each basic evaluation sheet (thousand yen, converted to yen); the
sheets label the column simply "budget amount", and the values are
recorded as initial budgets with that caveat documented, never as
settlements. The overall judgement is the prefecture's own four-stage
rating from the primary evaluation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

PROJECTS_PATH = "data/reviewed/hokkaido-prefecture/projects.json"
KPIS_PATH = "data/reviewed/hokkaido-prefecture/project_kpis.json"
PACKETS_PATH = "data/reviewed/hokkaido-prefecture/project_evidence_packets.json"
SOURCES_PATH = "data/catalog/hokkaido_project_sources.json"
SELECTION_PATH = "data/catalog/hokkaido_priority_project_selection.json"

MID = "jp-local-010006"
# slug -> (official title, overall rating, measure code)
SLUGS = {
    "agricultural-rural-infrastructure": ("農業農村整備の推進", "概ね順調", "0601"),
    "marriage-childbirth-support": ("結婚・出産環境支援の充実", "やや遅れている", "0402"),
    "regional-revitalization": ("地域創生の推進", "概ね順調", "0208"),
    "visitor-attraction": ("誘客活動の推進", "やや遅れている", "0503"),
    "competency-education": ("新しい時代に必要となる資質・能力の育成", "やや遅れている", "1101"),
    "international-exchange": ("海外交流拡大の推進", "順調", "0212"),
    "global-warming-countermeasures": ("地球温暖化対策の推進", "順調", "0506"),
    "regional-healthcare": ("地域医療の確保", "やや遅れている", "0409"),
    "agricultural-disaster-prevention": (
        "農業農村基盤整備における防災・減災対策の推進",
        "順調",
        "0608",
    ),
    "digital-company-clustering": ("デジタル関連企業の集積", "順調", "0510"),
}
# slug -> (FY2023, FY2024, FY2025 initial budget in yen), as printed at
# the head of each basic evaluation sheet (thousand yen x 1000).
EXPECTED_BUDGETS = {
    "agricultural-rural-infrastructure": (69_211_617_000, 70_714_760_000, 72_575_852_000),
    "marriage-childbirth-support": (407_642_000, 279_143_000, 252_691_000),
    "regional-revitalization": (664_060_000, 839_746_000, 1_155_071_000),
    "visitor-attraction": (21_802_202_000, 953_639_000, 870_896_000),
    "competency-education": (24_866_276_000, 24_650_952_000, 24_677_329_000),
    "international-exchange": (233_060_000, 260_595_000, 281_698_000),
    "global-warming-countermeasures": (367_691_000, 364_617_000, 301_503_000),
    "regional-healthcare": (636_296_948_000, 626_007_278_000, 630_527_753_000),
    "agricultural-disaster-prevention": (23_385_479_000, 23_943_331_000, 27_116_725_000),
    "digital-company-clustering": (37_410_000, 41_224_000, 38_007_000),
}
EXPECTED_PILLARS = [
    "食",
    "子ども・子育て",
    "地域づくり",
    "観光",
    "教育・学び",
    "グローバル化",
    "ゼロカーボン",
    "医療・福祉",
    "北海道の強靱化",
    "デジタル",
]


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
    return {record["id"] for record in load_json(SOURCES_PATH)["records"]}


def test_hokkaido_projects_match_schemas() -> None:
    assert_valid("schemas/source_catalog.schema.json", load_json(SOURCES_PATH))
    for record in load_json(PROJECTS_PATH):
        assert_valid("schemas/project.schema.json", record)
    for record in load_json(KPIS_PATH):
        assert_valid("schemas/kpi.schema.json", record)
    for packet in load_json(PACKETS_PATH):
        assert_valid("schemas/evidence_packet.schema.json", packet)


def test_selection_rule_and_population() -> None:
    selection = load_json(SELECTION_PATH)
    assert selection["issue"] == 742
    assert selection["population"]["project_count"] == 121
    assert selection["population"]["fiscal_year"] == 2025
    assert selection["scope"] == "initial"
    assert selection["selection_rule"]["pillars"] == EXPECTED_PILLARS
    selections = selection["selections"]
    assert len(selections) == 10
    projects = projects_by_id()
    assert len(projects) == 10
    assert [item["measure_code"] for item in selections] == [
        "0601",
        "0402",
        "0208",
        "0503",
        "1101",
        "0212",
        "0506",
        "0409",
        "0608",
        "0510",
    ]
    for item in selections:
        record = projects[item["project_id"]]
        assert record["series_id"] == item["series_id"]
        assert record["official_title"] == item["official_title"]
        assert record["parent_policy"] == item["initiative"]
        assert record["fiscal_year"] == 2025
        assert record["review_status"] == "reviewed"
        assert set(item["source_ids"]) <= known_source_ids()


def test_project_budget_records_are_sheet_budgets_not_settlements() -> None:
    projects = projects_by_id()
    assert set(projects) == {project_id(slug) for slug in SLUGS}
    for slug, amounts in EXPECTED_BUDGETS.items():
        records = {
            (item["kind"], item["fiscal_year"]): item
            for item in projects[project_id(slug)]["budget_records"]
        }
        # Only initial budgets are registered; no settlement or execution
        # figure exists at measure level in the sheets.
        assert set(records) == {
            ("initial_budget", 2023),
            ("initial_budget", 2024),
            ("initial_budget", 2025),
        }
        for fiscal_year, amount in zip((2023, 2024, 2025), amounts, strict=True):
            record = records[("initial_budget", fiscal_year)]
            assert record["amount_yen"] == amount
            # The note must never present the sheet's "budget amount" as
            # a settlement figure.
            assert "決算額ではない" in record["note"]


def test_kpi_records_match_embedded_summaries() -> None:
    kpis = load_json(KPIS_PATH)
    assert len(kpis) == 21
    projects = projects_by_id()
    for record in kpis:
        assert record["review_status"] == "reviewed"
        assert record["baseline"] is None
        assert set(record["sources"]) <= known_source_ids()
        project = projects[record["project_id"]]
        embedded = {item["name"]: item for item in project["kpis"]}
        summary = embedded[record["name"]]
        assert summary["baseline"] is None
        assert summary["target"] == record["target"]["value"]
        assert summary["assessment"] == record["assessment"]
        # The embedded actual is the latest published actual.
        assert record["actuals"][-1]["value"] == summary["actual"]
        assert record["actuals"][-1]["period"] == record["target"]["period"]

    fertility = {r["id"]: r for r in kpis}[
        f"{project_id('marriage-childbirth-support')}-kpi-total-fertility-rate"
    ]
    # The sheet prints no unit for the fertility rate ("-" in the unit
    # column); the registered unit keeps that printed form.
    assert fertility["unit"] == "－"
    assert fertility["target"]["value"] == 1.15
    assert fertility["actuals"][-1]["value"] == 1.01
    assert fertility["assessment"] == "partially_achieved"

    physicians = {r["id"]: r for r in kpis}[
        f"{project_id('regional-healthcare')}-kpi-physician-distribution-areas"
    ]
    assert physicians["target"]["value"] == 21
    assert physicians["actuals"][-1]["value"] == 2
    assert physicians["assessment"] == "not_achieved"

    ghg = {r["id"]: r for r in kpis}[
        f"{project_id('global-warming-countermeasures')}-kpi-greenhouse-gas-emissions"
    ]
    assert ghg["direction"] == "decrease"
    assert ghg["target"]["value"] == 5498
    assert ghg["actuals"][-1]["value"] == 4881
    assert ghg["assessment"] == "achieved"


def test_official_evaluation_is_the_prefectures_not_ours() -> None:
    projects = projects_by_id()
    for slug, (title, rating, _code) in SLUGS.items():
        record = projects[project_id(slug)]
        assert record["official_title"] == title
        assert record["official_evaluation"]["rating"] == rating
        # The sheets publish no single-word direction label; the
        # follow-up policies are recorded in the evidence packet instead.
        assert record["official_evaluation"]["direction"] is None
        assert "Jichi Insight独自の評価ではない" in record["official_evaluation"]["note"]
        # Governor promises are registered in stage 3 of the cluster;
        # until then the link list stays empty.
        assert record["related_promise_ids"] == []


def test_every_project_has_an_evidence_packet_and_known_sources() -> None:
    source_ids = known_source_ids()
    packets = {packet["subject_id"]: packet for packet in load_json(PACKETS_PATH)}
    assert set(packets) == set(projects_by_id())
    for packet in packets.values():
        assert packet["subject_type"] == "project"
        assert packet["review_status"] == "reviewed"
        for claim in packet["claims"]:
            assert set(claim["source_ids"]) <= source_ids
        # Unregistered contract/assembly/audit links, the not-yet-done
        # promise linkage and the absence of measure-level settlements
        # stay explicit open questions.
        assert any("未登録" in question for question in packet["open_questions"])
        assert any("段階3" in question for question in packet["open_questions"])
    for record in projects_by_id().values():
        assert set(record["sources"]) <= source_ids


def test_documented_anomalies_are_kept_visible() -> None:
    packets = {p["subject_id"]: p for p in load_json(PACKETS_PATH)}
    visitor = packets[project_id("visitor-attraction")]
    # The FY2023 budget printed for visitor attraction is an order of
    # magnitude larger than the following years; it is registered as
    # printed and the absence of a stated reason is an open question.
    assert any("21,802,202千円" in question for question in visitor["open_questions"])
    education = packets[project_id("competency-education")]
    # The primary evaluation's indicator grade is printed "C*" (with an
    # asterisk) whose meaning the sheet text does not explain.
    assert any("Ｃ※" in question for question in education["open_questions"])
