from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

PROJECTS_PATH = "data/reviewed/osaka-city/projects.json"
KPIS_PATH = "data/reviewed/osaka-city/project_kpis.json"
PACKETS_PATH = "data/reviewed/osaka-city/project_evidence_packets.json"
SOURCES_PATH = "data/catalog/osaka_city_project_sources.json"
SELECTION_PATH = "data/catalog/osaka_city_priority_project_selection.json"

P1 = "jp-local-271004-project-2026-seamless-pregnancy-childcare-support"
P2 = "jp-local-271004-project-2026-children-youth-development"
P3 = "jp-local-271004-project-2026-child-abuse-prevention"
P4 = "jp-local-271004-project-2026-healthy-city-osaka"
P5 = "jp-local-271004-project-2026-elderly-secure-living"
P6 = "jp-local-271004-project-2026-disaster-prevention-mitigation"
P7 = "jp-local-271004-project-2026-city-attraction-creation"
P8 = "jp-local-271004-project-2026-innovation-cycle"
P9 = "jp-local-271004-project-2026-sme-promotion"
P10 = "jp-local-271004-project-2026-redesign-osaka-dx"
PROJECT_IDS = [P1, P2, P3, P4, P5, P6, P7, P8, P9, P10]

EXPECTED_RATINGS = {
    P1: "D",
    P2: "A",
    P3: "C",
    P4: "ー（未測定等）",
    P5: "A",
    P6: "A",
    P7: "A",
    P8: "A",
    P9: "A",
    P10: "A",
}

SELECTED_TITLES = [
    "妊娠前からの切れ目ない支援の充実と幼児教育・保育の質の向上",
    "こども・青少年の生きる力の育成",
    "児童虐待防止体制の強化",
    "健康都市大阪の実現",
    "高齢者等が安心して暮らせる社会の実現",
    "防災・減災対策の推進",
    "大阪の都市魅力の創造・発信",
    "大阪の強みを活かし、イノベーションが次々と生まれる好循環づくり",
    "中小企業振興と経済成長の担い手の育成",
    "「Re-Designおおさか～大阪市DX戦略～」に基づく事業・施策の立案及び推進",
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


def test_osaka_city_projects_match_schemas() -> None:
    assert_valid("schemas/source_catalog.schema.json", load_json(SOURCES_PATH))
    for record in load_json(PROJECTS_PATH):
        assert_valid("schemas/project.schema.json", record)
    for record in load_json(KPIS_PATH):
        assert_valid("schemas/kpi.schema.json", record)
    for packet in load_json(PACKETS_PATH):
        assert_valid("schemas/evidence_packet.schema.json", packet)


def test_selection_rule_and_population() -> None:
    selection = load_json(SELECTION_PATH)
    assert selection["issue"] == 768
    assert selection["scope"] == "expanded"
    assert selection["municipality_id"] == "jp-local-271004"
    # The population is the strategy's 25 concrete measures.
    population = selection["population"]["projects"]
    assert len(population) == 25
    # Round-robin over the four basic goals in book order: goal 1-4 first
    # measures, then goals 1-3 second measures, then goals 1-3 third
    # measures (goal 4 has a single measure). Amounts are never used.
    selections = selection["selections"]
    assert [item["official_title"] for item in selections] == SELECTED_TITLES
    projects = projects_by_id()
    assert [record["official_title"] for record in
            (projects[pid] for pid in PROJECT_IDS)] == SELECTED_TITLES
    for record in projects.values():
        assert record["fiscal_year"] == 2026
        assert record["review_status"] == "reviewed"
        # Osaka City assigns no single department to a strategy measure.
        assert record["responsible_department"] is None
        assert record["related_promise_ids"] == []
    skipped = selection["skipped"]
    assert len(skipped) == 15
    skipped_titles = {item["official_title"] for item in skipped}
    assert skipped_titles.isdisjoint(set(SELECTED_TITLES))
    assert skipped_titles | set(SELECTED_TITLES) == {
        item["name"] for item in population
    }
    for item in skipped:
        assert "巡回選定で10件に達したため未選定" in item["reason"]


def test_budget_amounts_are_null_with_explicit_reason() -> None:
    projects = projects_by_id()
    assert set(projects) == set(PROJECT_IDS)
    for record in projects.values():
        records = record["budget_records"]
        assert [item["kind"] for item in records] == ["initial_budget"]
        budget = records[0]
        # The strategy measures have no published per-measure FY2026
        # initial-budget amount (the city publishes amounts per budget
        # project, with no official mapping to strategy measures), so the
        # amount stays null instead of being estimated or zero-filled.
        assert budget["amount_yen"] is None
        assert budget["fiscal_year"] == 2026
        assert "単位の金額は公表していない" in budget["note"]
        # The FY2026 budget was passed as proposed on 2026-03-27 with an
        # attached resolution on the general account bill.
        assert "原案どおり可決" in budget["note"]
        assert "附帯決議" in budget["note"]


def test_official_evaluation_is_registered_from_city_verification() -> None:
    projects = projects_by_id()
    for project_id, rating in EXPECTED_RATINGS.items():
        evaluation = projects[project_id]["official_evaluation"]
        assert evaluation is not None
        assert evaluation["rating"] == rating
        # The rating is Osaka City's own FY2025 verification result, not
        # a Jichi Insight judgement.
        assert "大阪市の公式評価であり" in evaluation["note"]
        assert "令和7年度効果検証" in evaluation["note"]


def test_kpi_baseline_target_actual_are_separated() -> None:
    kpis = {record["id"]: record for record in load_json(KPIS_PATH)}
    assert len(kpis) == 42
    projects = projects_by_id()
    for record in kpis.values():
        project = projects[record["project_id"]]
        assert record["review_status"] == "reviewed"
        embedded = {item["name"]: item for item in project["kpis"]}
        summary = embedded[record["name"]]
        assert summary["baseline"] == record["baseline"]["value"]
        assert summary["target"] == record["target"]["value"]
        assert summary["assessment"] == record["assessment"]
        if record["actuals"]:
            assert summary["actual"] == record["actuals"][-1]["value"]
        else:
            assert summary["actual"] is None

    waitlist = kpis[f"{P1}-kpi-childcare-waitlist"]
    assert waitlist["baseline"]["value"] == 2341
    assert waitlist["target"]["value"] == "解消"
    assert waitlist["actuals"][0]["value"] == 2543
    # The city's mark for this KPI is ▲ (not achieved, other measures'
    # influence), which maps to not_achieved.
    assert waitlist["assessment"] == "not_achieved"
    assert waitlist["direction"] == "decrease"
    assert waitlist["causality_note"]

    abuse = kpis[f"{P3}-kpi-serious-child-abuse"]
    assert abuse["baseline"]["value"] == 2
    assert abuse["target"]["value"] == 0
    assert abuse["actuals"][0]["value"] == 1
    # The city's mark is △ (not achieved, progress made).
    assert abuse["assessment"] == "not_achieved"

    healthy = kpis[f"{P4}-kpi-healthy-life-expectancy"]
    # Healthy life expectancy was not measured in the FY2025
    # verification; the actual stays unpublished instead of zero-filled.
    assert healthy["actuals"][0]["value"] is None
    assert healthy["actuals"][0]["status"] == "not_published"
    assert healthy["assessment"] == "not_assessable"

    sales_di = kpis[f"{P9}-kpi-sme-sales-di"]
    # The DI actuals are published for two fiscal years.
    assert [item["value"] for item in sales_di["actuals"]] == [27, 33]

    research = kpis[f"{P9}-kpi-industry-research-projects"]
    # The baseline was not measured before FY2022 per the city; it stays
    # unpublished.
    assert research["baseline"]["value"] is None
    assert research["baseline"]["status"] == "not_published"
    assert research["target"]["value"] == 625
    assert research["actuals"][0]["value"] == 467

    # KPIs newly created by the September 2026 strategy revision are
    # registered with unpublished baseline/actuals and in_progress.
    for kpi_id in (
        f"{P7}-kpi-culture-arts-satisfaction",
        f"{P8}-kpi-global-startups",
        f"{P10}-kpi-online-usage-rate",
    ):
        record = kpis[kpi_id]
        assert record["assessment"] == "in_progress"
        assert record["actuals"] == []
        assert record["baseline"]["status"] == "not_published"


def test_every_project_has_an_evidence_packet_and_known_sources() -> None:
    source_ids = {record["id"] for record in load_json(SOURCES_PATH)["records"]}
    packets = {packet["subject_id"]: packet for packet in load_json(PACKETS_PATH)}
    assert set(packets) == set(projects_by_id())
    for packet in packets.values():
        assert packet["subject_type"] == "project"
        assert packet["review_status"] == "reviewed"
        fields = {claim["field"] for claim in packet["claims"]}
        assert {"project_unit", "selection", "kpis", "official_evaluation",
                "budget_amount", "responsible_department"} <= fields
        for claim in packet["claims"]:
            assert set(claim["source_ids"]) <= source_ids
        budget_claims = [
            claim for claim in packet["claims"] if claim["field"] == "budget_amount"
        ]
        assert "金額はnullとし" in budget_claims[0]["statement"]
    for record in projects_by_id().values():
        assert set(record["sources"]) <= source_ids
    for record in load_json(KPIS_PATH):
        assert set(record["sources"]) <= source_ids


def test_source_availability_is_honest() -> None:
    sources = {record["id"]: record for record in load_json(SOURCES_PATH)["records"]}
    assert len(sources) == 6
    for record in sources.values():
        assert record["availability"] == "published"
        assert record["municipality_key"] == "osaka-city"
    # The appendix is the per-KPI primary source used for registration.
    appendix = sources["osaka-city-future-city-strategy-verification-fy2025-appendix-pdf"]
    assert "KPI別達成状況" in appendix["title"] or "KPI" in appendix["notes"]
    budget = sources["osaka-city-budget-fy2026-page"]
    assert "施策単位の金額は公表されていない" in budget["notes"]
