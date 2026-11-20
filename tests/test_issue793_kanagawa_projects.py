"""Issue #793: Kanagawa Prefecture priority projects (cluster 5, stage 2).

The population is the 13 projects of the implementation plan of the
"New Kanagawa Grand Design" (FY2024-FY2027), organised under five
themes. Ten project series are selected by round-robin over the five
themes in official listing order, taking projects in listing order
within each theme -- never by amount. Each series is registered as two
yearly records (FY2024 and FY2025), because the prefecture publishes a
yearly evaluation report with a four-stage official judgement per
project (primary evaluation by the prefecture's bureaus, final
evaluation by the Comprehensive Plan Council).

Amounts are the project-level initial-budget-based project costs
printed in section 4 of each evaluation report, in units of 100
million yen (project figures are rounded down below that unit), so the
yen conversion is exact only to that precision; no project-level
settlement or execution figure is published. KPI values are the ones
printed in the evaluation reports' KPI lists; the per-KPI assessment
is a mechanical mapping of the prefecture's published achievement-rate
bins (100% or more / 60% to under 100% / under 60%), not an official
per-KPI grade -- the prefecture publishes no per-KPI grade.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

PROJECTS_PATH = "data/reviewed/kanagawa-prefecture/projects.json"
KPIS_PATH = "data/reviewed/kanagawa-prefecture/project_kpis.json"
PACKETS_PATH = "data/reviewed/kanagawa-prefecture/project_evidence_packets.json"
SOURCES_PATH = "data/catalog/kanagawa_project_sources.json"
SELECTION_PATH = "data/catalog/kanagawa_priority_project_selection.json"

MID = "jp-local-140007"
# slug -> (official title, FY2024 secondary rating, FY2025 secondary rating)
SLUGS = {
    "children-and-youth": ("子ども・若者", "概ね順調に進んでいる", "概ね順調に進んでいる"),
    "economy-and-employment": ("経済・労働", "順調に進んでいる", "順調に進んでいる"),
    "livelihood-support": ("生活困窮", "概ね順調に進んでいる", "概ね順調に進んでいる"),
    "everyday-life-safety": ("くらしの安心", "概ね順調に進んでいる", "概ね順調に進んでいる"),
    "urban-infrastructure": ("都市基盤", "概ね順調に進んでいる", "順調に進んでいる"),
    "education": ("教育", "順調に進んでいる", "順調に進んでいる"),
    "agriculture-forestry-fisheries": ("農林水産", "順調に進んでいる", "順調に進んでいる"),
    "inclusive-society": ("共生社会", "やや遅れている", "やや遅れている"),
    "crisis-management": ("危機管理", "順調に進んでいる", "順調に進んでいる"),
    "mebyo-health-longevity": ("未病・健康長寿", "概ね順調に進んでいる", "概ね順調に進んでいる"),
}
SELECTION_ORDER = [
    "children-and-youth",
    "economy-and-employment",
    "livelihood-support",
    "everyday-life-safety",
    "urban-infrastructure",
    "education",
    "agriculture-forestry-fisheries",
    "inclusive-society",
    "crisis-management",
    "mebyo-health-longevity",
]
# slug -> (FY2024, FY2025, FY2026) project cost in yen, converted from
# the 100-million-yen figures printed in the evaluation reports.
EXPECTED_BUDGETS = {
    "children-and-youth": (122, 121, 327),
    "education": (98, 128, 162),
    "mebyo-health-longevity": (156, 224, 227),
    "economy-and-employment": (120, 131, 147),
    "agriculture-forestry-fisheries": (58, 76, 95),
    "livelihood-support": (6, 7, 9),
    "inclusive-society": (93, 108, 111),
    "everyday-life-safety": (80, 102, 120),
    "crisis-management": (611, 592, 616),
    "urban-infrastructure": (482, 642, 541),
}
EXPECTED_BUDGETS = {
    slug: tuple(v * 100_000_000 for v in values)
    for slug, values in EXPECTED_BUDGETS.items()
}
EXPECTED_THEMES = [
    "希望の持てる神奈川",
    "持続的に発展する神奈川",
    "自分らしく生きられる神奈川",
    "安心してくらせる神奈川",
    "神奈川を支える基盤づくり",
]
# slug -> number of component-measure KPIs per yearly record
EXPECTED_KPI_COUNTS = {
    "children-and-youth": 9,
    "education": 10,
    "mebyo-health-longevity": 9,
    "economy-and-employment": 9,
    "agriculture-forestry-fisheries": 7,
    "livelihood-support": 8,
    "inclusive-society": 10,
    "everyday-life-safety": 8,
    "crisis-management": 8,
    "urban-infrastructure": 7,
}
# slug -> number of project indicators (registered on the FY2025 record)
EXPECTED_INDICATOR_COUNTS = {
    "children-and-youth": 2,
    "education": 4,
    "mebyo-health-longevity": 4,
    "economy-and-employment": 5,
    "agriculture-forestry-fisheries": 2,
    "livelihood-support": 4,
    "inclusive-society": 3,
    "everyday-life-safety": 2,
    "crisis-management": 3,
    "urban-infrastructure": 2,
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


def project_id(year: int, slug: str) -> str:
    return f"{MID}-project-{year}-{slug}"


def known_source_ids() -> set[str]:
    return {record["id"] for record in load_json(SOURCES_PATH)["records"]}


def test_kanagawa_projects_match_schemas() -> None:
    assert_valid("schemas/source_catalog.schema.json", load_json(SOURCES_PATH))
    for record in load_json(PROJECTS_PATH):
        assert_valid("schemas/project.schema.json", record)
    for record in load_json(KPIS_PATH):
        assert_valid("schemas/kpi.schema.json", record)
    for packet in load_json(PACKETS_PATH):
        assert_valid("schemas/evidence_packet.schema.json", packet)


def test_selection_rule_and_population() -> None:
    selection = load_json(SELECTION_PATH)
    assert selection["issue"] == 793
    assert selection["population"]["project_count"] == 13
    assert selection["population"]["fiscal_year"] == 2025
    assert selection["scope"] == "initial"
    assert selection["selection_rule"]["pillars"] == EXPECTED_THEMES
    selections = selection["selections"]
    assert len(selections) == 10
    assert [item["project_number"] for item in selections] == [
        1, 6, 9, 11, 13, 2, 7, 10, 12, 3,
    ]
    projects = projects_by_id()
    assert len(projects) == 20
    for item, slug in zip(selections, SELECTION_ORDER, strict=True):
        assert item["series_id"] == f"{MID}-project-series-{slug}"
        assert item["project_id"] == project_id(2025, slug)
        for year in (2024, 2025):
            record = projects[project_id(year, slug)]
            assert record["series_id"] == item["series_id"]
            assert record["official_title"] == item["official_title"]
            assert record["parent_policy"] == item["theme"]
            assert record["review_status"] == "reviewed"
            # Governor promises are registered in stage 3.
            assert record["related_promise_ids"] == []
        assert set(item["source_ids"]) <= known_source_ids()


def test_project_budget_records_are_report_costs_not_settlements() -> None:
    projects = projects_by_id()
    for slug, amounts in EXPECTED_BUDGETS.items():
        for year, expected_years in (
            (2024, (2024, 2025)),
            (2025, (2024, 2025, 2026)),
        ):
            record = projects[project_id(year, slug)]
            records = {
                (item["kind"], item["fiscal_year"]): item
                for item in record["budget_records"]
            }
            assert set(records) == {
                ("initial_budget", y) for y in expected_years
            }
            for fiscal_year in expected_years:
                item = records[("initial_budget", fiscal_year)]
                assert item["amount_yen"] == amounts[fiscal_year - 2024]
                # The note must state the 100M-yen publication unit and
                # that no settlement figure is published.
                assert "億円単位" in item["note"]
                assert "決算額は公表されていない" in item["note"]


def test_kpi_records_match_embedded_summaries() -> None:
    kpis = load_json(KPIS_PATH)
    assert len(kpis) == 201
    projects = projects_by_id()
    counts: dict[str, dict[int, int]] = {}
    for record in kpis:
        assert record["review_status"] == "reviewed"
        assert set(record["sources"]) <= known_source_ids()
        project = projects[record["project_id"]]
        embedded = {item["name"]: item for item in project["kpis"]}
        summary = embedded[record["name"]]
        expected_baseline = (
            record["baseline"]["value"] if record["baseline"] else None
        )
        assert summary["baseline"] == expected_baseline
        assert summary["target"] == record["target"]["value"]
        assert summary["assessment"] == record["assessment"]
        assert summary["actual"] == record["actuals"][-1]["value"]
        counts.setdefault(record["project_id"], {"kpi": 0, "indicator": 0})
        kind = "indicator" if "-kpi-indicator-" in record["id"] else "kpi"
        counts[record["project_id"]][kind] += 1
    for slug, n in EXPECTED_KPI_COUNTS.items():
        assert counts[project_id(2024, slug)]["kpi"] == n
        assert counts[project_id(2025, slug)]["kpi"] == n
        assert counts[project_id(2024, slug)]["indicator"] == 0
        assert counts[project_id(2025, slug)]["indicator"] == (
            EXPECTED_INDICATOR_COUNTS[slug]
        )


def test_official_evaluation_is_the_prefectures_not_ours() -> None:
    projects = projects_by_id()
    for slug, (title, rating24, rating25) in SLUGS.items():
        for year, rating in ((2024, rating24), (2025, rating25)):
            record = projects[project_id(year, slug)]
            assert record["official_title"] == title
            assert record["official_evaluation"]["rating"] == rating
            assert record["official_evaluation"]["direction"] is None
            assert (
                "Jichi Insight独自の評価ではない"
                in record["official_evaluation"]["note"]
            )
            # The coordinating bureau is shown only as graphical marks
            # in the report, so it stays unregistered.
            assert record["responsible_department"] is None


def test_assessment_mapping_spot_checks() -> None:
    kpis = {record["id"]: record for record in load_json(KPIS_PATH)}
    # Achievement rate 37.8% (target 0 children on the waiting list,
    # actual 138) maps to not_achieved.
    waiting = kpis[project_id(2024, "children-and-youth") + "-kpi-waiting-children-daycare"]
    assert waiting["target"]["value"] == 0
    assert waiting["actuals"][-1]["value"] == 138
    assert waiting["assessment"] == "not_achieved"
    # The ICT KPI can no longer be measured (the survey question was
    # dropped), so both yearly records stay not_assessable.
    for year in (2024, 2025):
        ict = kpis[project_id(year, "education") + "-kpi-ict-usefulness-rate"]
        assert ict["actuals"][-1]["value"] is None
        assert ict["actuals"][-1]["status"] == "not_published"
        assert ict["assessment"] == "not_assessable"
    # The printed -250.0% rate for volunteer crime-prevention groups is
    # registered as printed and mapped mechanically.
    groups = kpis[
        project_id(2024, "everyday-life-safety")
        + "-kpi-volunteer-crime-prevention-groups"
    ]
    assert groups["actuals"][-1]["value"] == 2400
    assert groups["assessment"] == "not_achieved"
    # Errata-corrected indicator values are used: the FY2024 actual of
    # the local-food satisfaction indicator is 27.9%, not 27.2%.
    food = kpis[
        project_id(2025, "agriculture-forestry-fisheries")
        + "-kpi-indicator-local-food-satisfaction"
    ]
    actuals = {item["period"]: item["value"] for item in food["actuals"]}
    assert actuals["2024年度"] == 27.9
    assert actuals["2022年度"] == 27.9
    # The hospital-bed indicator baseline is the report's actual
    # (1,517 beds), not the plan-time projection (2,038 beds).
    beds = kpis[
        project_id(2025, "crisis-management")
        + "-kpi-indicator-agreement-hospital-beds"
    ]
    assert beds["baseline"]["value"] == 1517
    assert beds["target"]["value"] == 2200


def test_every_project_record_has_an_evidence_packet() -> None:
    source_ids = known_source_ids()
    packets = {packet["subject_id"]: packet for packet in load_json(PACKETS_PATH)}
    assert set(packets) == set(projects_by_id())
    for packet in packets.values():
        assert packet["subject_type"] == "project"
        assert packet["review_status"] == "reviewed"
        for claim in packet["claims"]:
            assert set(claim["source_ids"]) <= source_ids
        assert any("未登録" in q for q in packet["open_questions"])
        assert any("段階3" in q for q in packet["open_questions"])
    for record in projects_by_id().values():
        assert set(record["sources"]) <= source_ids
