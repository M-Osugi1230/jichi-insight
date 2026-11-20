from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MID = "jp-local-112038"
SOURCES_PATH = ROOT / "data/catalog/kawaguchi_city_project_sources.json"
SELECTION_PATH = ROOT / "data/catalog/kawaguchi_city_priority_project_selection.json"
PROJECTS_PATH = ROOT / "data/reviewed/kawaguchi-city/projects.json"
KPIS_PATH = ROOT / "data/reviewed/kawaguchi-city/project_kpis.json"
PACKETS_PATH = ROOT / "data/reviewed/kawaguchi-city/project_evidence_packets.json"

PILLARS = [
    "めざす姿I 健康で、自分らしく生き生きと暮らせるまち",
    "めざす姿II 誰もがお互いを認め合い、安心して暮らせるまち",
    "めざす姿III こどもをみんなで育み、こどもが輝き活躍するまち",
    "めざす姿IV 学びとスポーツ・文化に親しみ、自己実現ができるまち",
    "めざす姿V にぎわいと魅力があり、伝統と未来が響き合うまち",
    "めざす姿VI 都市と自然が調和した、うるおいとやすらぎのあるまち",
    "めざす姿VII 誰もが安全で快適に暮らせるまち",
    "めざす姿VIII 持続可能で自立したまち",
]

EXPECTED_IDS = [
    "jp-local-112038-project-2026-healthy-life",
    "jp-local-112038-project-2026-disaster-resilient-safe-city",
    "jp-local-112038-project-2026-child-wellbeing-support",
    "jp-local-112038-project-2026-lifelong-learning-sports",
    "jp-local-112038-project-2026-economic-activity-employment",
    "jp-local-112038-project-2026-water-and-greenery",
    "jp-local-112038-project-2026-planned-urban-development",
    "jp-local-112038-project-2026-multi-stakeholder-collaboration",
    "jp-local-112038-project-2026-elderly-healthy-active-life",
    "jp-local-112038-project-2026-mutual-respect-community",
]

EXPECTED_TITLES = [
    "健康な心と身体を育むまちづくり",
    "災害や危機に強く、誰もが安全・安心に暮らせるまちづくり",
    "すべてのこどもの幸せにつながる支援の推進",
    "生涯学習・スポーツができる環境づくり",
    "経済活動の持続的発展と安定した雇用の確保",
    "豊かな水と緑に親しむ空間づくり",
    "住・工・商・緑が調和した計画的なまちづくり",
    "多様な主体と進めるまちづくり",
    "高齢者が健やかに暮らし、活躍できるまちづくり",
    "互いに尊重し合い、地域で生き生きと活動しやすい環境づくり",
]

# First measure of each of the eight goals, then the second measure of
# goals I and II (the listing-order cycle continues).
EXPECTED_PARENTS = PILLARS + [PILLARS[0], PILLARS[1]]

EXPECTED_KPI_COUNTS = {
    "jp-local-112038-project-2026-healthy-life": 4,
    "jp-local-112038-project-2026-disaster-resilient-safe-city": 3,
    "jp-local-112038-project-2026-child-wellbeing-support": 4,
    "jp-local-112038-project-2026-lifelong-learning-sports": 3,
    "jp-local-112038-project-2026-economic-activity-employment": 3,
    "jp-local-112038-project-2026-water-and-greenery": 3,
    "jp-local-112038-project-2026-planned-urban-development": 2,
    "jp-local-112038-project-2026-multi-stakeholder-collaboration": 3,
    "jp-local-112038-project-2026-elderly-healthy-active-life": 3,
    "jp-local-112038-project-2026-mutual-respect-community": 4,
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validator(name: str) -> Draft202012Validator:
    schema = load(ROOT / "schemas" / name)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def test_kawaguchi_project_sources_are_schema_valid() -> None:
    catalog = load(SOURCES_PATH)
    validator("source_catalog.schema.json").validate(catalog)
    ids = [record["id"] for record in catalog["records"]]
    assert len(ids) == len(set(ids)) == 13
    assert all(record["municipality_key"] == "kawaguchi-city" for record in catalog["records"])


def test_selection_rule_is_listing_order_by_goal() -> None:
    selection = load(SELECTION_PATH)
    assert selection["municipality_id"] == MID
    assert selection["issue"] == 818
    assert selection["population"]["fiscal_year"] == 2026
    # The population is the 23 measures of the first basic plan of the 6th
    # comprehensive plan; the summary table of the FY2026 implementation
    # plan states 23 measures, 74 unit measures and 798 implementation
    # projects (enterprise accounts excluded).
    assert selection["population"]["goal_count"] == 8
    assert selection["population"]["measure_count"] == 23
    assert selection["population"]["unit_measure_count"] == 74
    assert selection["population"]["implementation_project_count"] == 798
    assert selection["population"]["featured_project_count"] == 128
    assert selection["selection_rule"]["pillars"] == PILLARS
    assert "金額の大小では選ばない" in selection["selection_rule"]["description"]
    selected = selection["selections"]
    assert [item["project_id"] for item in selected] == EXPECTED_IDS
    assert [item["official_title"] for item in selected] == EXPECTED_TITLES
    assert [item["policy"] for item in selected] == EXPECTED_PARENTS
    assert [item["pillar"] for item in selected] == EXPECTED_PARENTS
    assert selection["expansion_rule"]["total_count"] == 10


def test_registration_unit_is_the_measure() -> None:
    # The registration unit is the basic plan's measure (施策): it is the
    # unit that carries the published target indicators and the A-D
    # comprehensive rating of the administrative evaluation. Unit measures
    # carry neither, and the FY2026 project-level evaluation reports
    # (事務事業評価の調書) are not published yet.
    selection = load(SELECTION_PATH)
    assert "登録単位は施策とした" in selection["population"]["description"]
    for packet in load(PACKETS_PATH):
        claim = next(c for c in packet["claims"] if c["field"] == "registration_unit")
        assert "事務事業評価の対象だが" in claim["statement"]
        assert "本段階では事業単位の" in claim["statement"]


def test_selected_projects_match_records() -> None:
    projects = {record["id"]: record for record in load(PROJECTS_PATH)}
    selection = load(SELECTION_PATH)
    assert len(projects) == 10
    for item in selection["selections"]:
        record = projects[item["project_id"]]
        assert record["series_id"] == item["series_id"]
        assert record["official_title"] == item["official_title"]
        assert record["parent_policy"] == item["policy"]
        # The plan documents print no department per measure (departments
        # appear only per target indicator), so both stay explicitly null.
        assert record["responsible_department"] is None
        assert item["department"] is None
        assert record["municipality_id"] == MID
        assert record["fiscal_year"] == 2026
        assert record["review_status"] == "reviewed"
        # Stage 3 (promises) has not run yet, so no promise links exist.
        assert record["related_promise_ids"] == []


def test_budget_amounts_are_explicitly_unregistered() -> None:
    # Kawaguchi publishes no per-measure FY2026 budget: the implementation
    # plan's summary table gives totals per goal and amounts per featured
    # project only. Summing featured projects into a measure total would
    # fabricate a figure, so amounts stay null instead of 0.
    for record in load(PROJECTS_PATH):
        assert len(record["budget_records"]) == 1
        budget = record["budget_records"][0]
        assert budget["kind"] == "initial_budget"
        assert budget["fiscal_year"] == 2026
        assert budget["amount_yen"] is None
        assert "未登録とした" in budget["note"]
        assert "0では補完しない" in budget["note"]
        assert "原案可決" in budget["note"]


def test_official_evaluation_is_explicitly_unregistered() -> None:
    # FY2026 is the first year of the 6th plan; the administrative
    # evaluation rates the previous fiscal year, so no rating for these
    # measures is published yet. The 5th plan's ratings belong to a
    # different measure framework and are not carried over.
    for record in load(PROJECTS_PATH):
        assert record["official_evaluation"] is None
    packets = load(PACKETS_PATH)
    for packet in packets:
        joined = "".join(packet["open_questions"])
        assert "公式評価は未登録" in joined
        assert "金額は未登録" in joined


def test_kpis_match_implementation_plan_tables() -> None:
    kpis = {record["id"]: record for record in load(KPIS_PATH)}
    assert len(kpis) == 32
    projects = {record["id"]: record for record in load(PROJECTS_PATH)}
    counts = {}
    for record in kpis.values():
        validator("kpi.schema.json").validate(record)
        counts[record["project_id"]] = counts.get(record["project_id"], 0) + 1
        # Every KPI registers the plan's published baseline, the interim
        # target (FY2030) as target, and the FY2025 actual printed in the
        # implementation plan; the official achievement judgement is not
        # published, so the assessment stays in_progress.
        assert record["assessment"] == "in_progress"
        assert record["baseline"]["status"] == "available"
        assert record["target"]["period"] == "2030年度（中間目標）"
        assert len(record["actuals"]) == 1
        assert record["actuals"][0]["status"] == "available"
        embedded = {item["name"]: item for item in projects[record["project_id"]]["kpis"]}
        match = embedded[record["name"]]
        assert match["baseline"] == record["baseline"]["value"]
        assert match["target"] == record["target"]["value"]
        assert match["actual"] == record["actuals"][0]["value"]
        assert match["unit"] == record["unit"]
    assert counts == EXPECTED_KPI_COUNTS

    p1 = "jp-local-112038-project-2026-healthy-life"
    checkup = kpis[f"{p1}-kpi-specific-health-checkup-rate"]
    assert checkup["baseline"]["value"] == 35.7
    assert checkup["baseline"]["period"] == "2023年度"
    assert checkup["target"]["value"] == 45.0
    assert checkup["actuals"][0]["value"] == 33.7
    # The final target (FY2035) is preserved in the definition, not dropped.
    assert "最終目標は「60.0」" in checkup["definition"]
    male = kpis[f"{p1}-kpi-healthy-life-expectancy-at-65-male"]
    assert male["baseline"]["value"] == 17.27
    assert male["target"]["value"] == 18.12
    assert male["target"]["value"] != male["baseline"]["value"]

    p9 = "jp-local-112038-project-2026-elderly-healthy-active-life"
    care_rate = kpis[f"{p9}-kpi-long-term-care-certification-rate"]
    assert care_rate["direction"] == "decrease"
    # Qualitative targets are registered verbatim as printed strings.
    assert care_rate["target"]["value"] == "R12推計値（19.6）を下回る"

    p2 = "jp-local-112038-project-2026-disaster-resilient-safe-city"
    offenses = kpis[f"{p2}-kpi-penal-code-offenses-recognized"]
    assert offenses["baseline"]["value"] == 4529
    assert offenses["baseline"]["period"] == "2024年中"
    assert offenses["actuals"][0]["value"] == 4417
    assert offenses["direction"] == "decrease"


def test_projects_and_packets_are_schema_valid() -> None:
    project_validator = validator("project.schema.json")
    packet_validator = validator("evidence_packet.schema.json")
    projects = load(PROJECTS_PATH)
    for record in projects:
        project_validator.validate(record)
    packets = load(PACKETS_PATH)
    assert {packet["subject_id"] for packet in packets} == {record["id"] for record in projects}
    for packet in packets:
        packet_validator.validate(packet)
        assert packet["subject_type"] == "project"
        assert packet["review_status"] == "reviewed"


def test_source_references_resolve() -> None:
    known = {record["id"] for record in load(SOURCES_PATH)["records"]}
    for record in load(PROJECTS_PATH):
        assert set(record["sources"]) <= known
    for record in load(KPIS_PATH):
        assert set(record["sources"]) <= known
        for obs in [record["baseline"], record["target"], *record["actuals"]]:
            assert set(obs["source_ids"]) <= known
    for packet in load(PACKETS_PATH):
        for claim in packet["claims"]:
            assert set(claim["source_ids"]) <= known
    selection = load(SELECTION_PATH)
    assert set(selection["population"]["source_ids"]) <= known
    for item in selection["selections"]:
        assert set(item["source_ids"]) <= known
