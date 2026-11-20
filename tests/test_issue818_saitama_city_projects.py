from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

PROJECTS_PATH = "data/reviewed/saitama-city/projects.json"
KPIS_PATH = "data/reviewed/saitama-city/project_kpis.json"
PACKETS_PATH = "data/reviewed/saitama-city/project_evidence_packets.json"
SOURCES_PATH = "data/catalog/saitama_city_project_sources.json"
SELECTION_PATH = "data/catalog/saitama_city_priority_project_selection.json"

P1 = "jp-local-111007-project-2024-community-association-membership"
P2 = "jp-local-111007-project-2024-energy-saving-renewables-promotion"
P3 = "jp-local-111007-project-2024-citizen-health-promotion"
P4 = "jp-local-111007-project-2024-active-learning-promotion"
P5 = "jp-local-111007-project-2024-traffic-safety-facilities"
P6 = "jp-local-111007-project-2024-care-prevention-promotion"
P7 = "jp-local-111007-project-2024-maternal-child-health-support"
P8 = "jp-local-111007-project-2024-iwatsuki-ningyo-museum-culture"
P9 = "jp-local-111007-project-2024-omiya-station-gcs"
P10 = "jp-local-111007-project-2024-utility-pole-removal"
PROJECT_IDS = [P1, P2, P3, P4, P5, P6, P7, P8, P9, P10]

SELECTED_TITLES = [
    "自治会への加入促進",
    "市民・事業者との連携による省エネ・創エネ化の促進",
    "市民の主体的な健康づくりの推進",
    "アクティブ・ラーニングの推進",
    "交通安全施設設置の推進",
    "介護予防の推進",
    "妊娠期からの親と子の健康づくり支援",
    "岩槻人形博物館を拠点とした人形文化の振興・発信",
    "大宮駅グランドセントラルステーション化構想の推進",
    "無電柱化の推進",
]

BUSINESS_CODES = [
    "01-1-1-01", "02-1-1-01", "03-1-1-01", "04-1-1-01", "05-1-1-01",
    "06-1-1-01", "07-1-1-01", "08-1-1-01", "09-1-1-01", "10-1-1-01",
]

# (initial_budget, settlement) in yen, from the FY2024 report sheets.
EXPECTED_BUDGETS = {
    P1: (369286000, 356290867),
    P2: (207920000, 202199803),
    P3: (92707000, 43509145),
    P4: (280192000, 278003379),
    P5: (149945000, 143266740),
    P6: (120197000, 106822498),
    P7: (1084646000, 1116183889),
    P8: (118752000, 103431950),
    P9: (102995000, 77772107),
    P10: (1303086208, 1022063225),
}

EXPECTED_RATINGS = {
    P1: "A：目標を上回って達成",
    P2: "C：目標を未達成",
    P3: "A：目標を上回って達成",
    P4: "B：目標をおおむね達成",
    P5: "C：目標を未達成",
    P6: "B：目標をおおむね達成",
    P7: "B：目標をおおむね達成",
    P8: "C：目標を未達成",
    P9: "C：目標を未達成",
    P10: "B：目標をおおむね達成",
}

EXPECTED_KPI_COUNTS = {
    P1: 4, P2: 3, P3: 4, P4: 2, P5: 2, P6: 2, P7: 4, P8: 2, P9: 1, P10: 2,
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


def test_saitama_city_projects_match_schemas() -> None:
    assert_valid("schemas/source_catalog.schema.json", load_json(SOURCES_PATH))
    for record in load_json(PROJECTS_PATH):
        assert_valid("schemas/project.schema.json", record)
    for record in load_json(KPIS_PATH):
        assert_valid("schemas/kpi.schema.json", record)
    for packet in load_json(PACKETS_PATH):
        assert_valid("schemas/evidence_packet.schema.json", packet)


def test_selection_rule_and_population() -> None:
    selection = load_json(SELECTION_PATH)
    assert selection["issue"] == 818
    assert selection["scope"] == "expanded"
    assert selection["municipality_id"] == "jp-local-111007"
    assert selection["municipality_key"] == "saitama-city"
    population = selection["population"]
    # The population is the 299 businesses (excluding cross-listings)
    # that received a business evaluation sheet in the FY2024 report.
    # Measure sheets (63 measures) carry no amounts, so the business is
    # the registration unit.
    assert population["business_count"] == 299
    assert population["field_count"] == 11
    assert population["measure_count"] == 63
    assert population["fiscal_year"] == 2024
    assert len(selection["selection_rule"]["pillars"]) == 11
    selections = selection["selections"]
    assert [item["official_title"] for item in selections] == SELECTED_TITLES
    assert [item["business_code"] for item in selections] == BUSINESS_CODES
    projects = projects_by_id()
    assert [projects[pid]["official_title"] for pid in PROJECT_IDS] == SELECTED_TITLES
    for record in projects.values():
        assert record["fiscal_year"] == 2024
        assert record["review_status"] == "reviewed"
        assert record["related_promise_ids"] == []
    skipped = selection["skipped"]
    assert len(skipped) == 1
    assert skipped[0]["official_title"] == "東日本連携の推進による地域経済活性化"
    assert "10件に達したため未選定" in skipped[0]["reason"]


def test_budget_amounts_are_registered_from_evaluation_sheets() -> None:
    projects = projects_by_id()
    assert set(projects) == set(PROJECT_IDS)
    for pid, (initial, settlement) in EXPECTED_BUDGETS.items():
        records = projects[pid]["budget_records"]
        assert [item["kind"] for item in records] == ["initial_budget", "settlement"]
        assert records[0]["amount_yen"] == initial
        assert records[0]["fiscal_year"] == 2024
        assert "前年度繰越額を含む" in records[0]["note"]
        assert records[1]["amount_yen"] == settlement
        assert records[1]["fiscal_year"] == 2024
        assert "翌年度繰越額を除く" in records[1]["note"]


def test_official_evaluation_is_the_city_business_rating() -> None:
    projects = projects_by_id()
    for pid, rating in EXPECTED_RATINGS.items():
        evaluation = projects[pid]["official_evaluation"]
        assert evaluation["rating"] == rating
        assert evaluation["direction"] is None
        # The rating is the city's internal business evaluation, not a
        # Jichi Insight judgement, and the contribution grade is I for
        # every selected business.
        assert "Jichi Insight独自の評価ではない" in evaluation["note"]
        assert "I 貢献している" in evaluation["note"]


def test_kpi_values_and_assessments() -> None:
    kpis = {record["id"]: record for record in load_json(KPIS_PATH)}
    assert len(kpis) == 26
    projects = projects_by_id()
    counts = {pid: 0 for pid in PROJECT_IDS}
    grouped: dict[str, list] = {}
    for record in load_json(KPIS_PATH):
        grouped.setdefault(record["project_id"], []).append(record)
    for pid, records in grouped.items():
        counts[pid] = len(records)
        embedded = projects[pid]["kpis"]
        # Embedded summaries follow the same order as the KPI records
        # (two KPIs in project P2 share one printed name, so matching
        # must be positional, not by name).
        assert len(embedded) == len(records)
        for record, summary in zip(records, embedded):
            assert record["review_status"] == "reviewed"
            assert summary["name"] == record["name"]
            assert summary["baseline"] == (
                record["baseline"]["value"] if record["baseline"] else None
            )
            assert summary["target"] == (
                record["target"]["value"] if record["target"] else None
            )
            assert summary["actual"] == (
                record["actuals"][0]["value"] if record["actuals"] else None
            )
            assert summary["assessment"] == record["assessment"]
    assert counts == EXPECTED_KPI_COUNTS

    # P1: the household-growth KPI keeps the printed direction of the
    # change (a decrease is a negative value), and the ICT-support KPI
    # is a text milestone.
    growth = kpis[f"{P1}-kpi-community-association-household-growth"]
    assert growth["baseline"]["value"] == 848
    assert growth["target"]["value"] == 2000
    assert growth["actuals"][0]["value"] == -3255
    assert growth["assessment"] == "not_achieved"
    ict = kpis[f"{P1}-kpi-community-association-ict-support"]
    assert ict["actuals"][0]["value"] == "34自治会導入"
    assert ict["direction"] == "not_applicable"

    # P2: the two same-named household GHG rows are registered as
    # separate KPIs; the row without a FY2024 classification stays
    # not_assessable instead of inheriting the other row's grade.
    ghg_old = kpis[f"{P2}-kpi-household-ghg-emissions-1"]
    assert ghg_old["assessment"] == "not_assessable"
    assert ghg_old["baseline"]["value"] == 216
    assert ghg_old["actuals"][0]["value"] == 167
    ghg_new = kpis[f"{P2}-kpi-household-ghg-emissions-2"]
    assert ghg_new["assessment"] == "mostly_achieved"
    assert ghg_new["target"]["value"] == 154
    assert ghg_new["actuals"][0]["value"] == 147
    assert ghg_new["actuals"][0]["period"] == "令和4年度"

    # P3: survey-year lag is explicit (FY2024 evaluation uses FY2021
    # survey values), and the A+ classification maps to achieved.
    activity = kpis[f"{P3}-kpi-physical-activity-rate"]
    assert activity["target"]["value"] == 48.4
    assert activity["actuals"][0]["value"] == 46.2
    assert activity["actuals"][0]["period"] == "令和3年度"
    network = kpis[f"{P3}-kpi-healthy-network-members"]
    assert network["actuals"][0]["value"] == 187
    assert network["assessment"] == "achieved"

    # P7: indicators that started after the reference year keep an
    # unpublished baseline instead of a zero or a later year's value.
    relief = kpis[f"{P7}-kpi-postpartum-care-relief-rate"]
    assert relief["baseline"]["value"] is None
    assert relief["baseline"]["status"] == "not_published"
    assert relief["actuals"][0]["value"] == 97

    # P8: the awareness KPI keeps the two printed components as one
    # text value.
    awareness = kpis[f"{P8}-kpi-museum-awareness"]
    assert awareness["actuals"][0]["value"] == "①45.5％ ②30.1％"
    assert awareness["assessment"] == "mostly_achieved"

    # P10: printed target and actual are both 65.7, but the city's
    # classification is C (growth-rate basis); the record follows the
    # city's classification, not the displayed equality.
    barrier = kpis[f"{P10}-kpi-barrier-free-route-pole-removal-rate"]
    assert barrier["target"]["value"] == 65.7
    assert barrier["actuals"][0]["value"] == 65.7
    assert barrier["assessment"] == "not_achieved"
    assert "伸び率" in barrier["definition"]


def test_every_project_has_an_evidence_packet_and_known_sources() -> None:
    source_ids = {record["id"] for record in load_json(SOURCES_PATH)["records"]}
    packets = {packet["subject_id"]: packet for packet in load_json(PACKETS_PATH)}
    assert set(packets) == set(projects_by_id())
    for packet in packets.values():
        assert packet["subject_type"] == "project"
        assert packet["review_status"] == "reviewed"
        fields = {claim["field"] for claim in packet["claims"]}
        assert {
            "registration_unit", "official_title", "parent_policy", "purpose",
            "responsible_department", "kpis", "budget_records.initial_budget",
            "budget_records.settlement", "official_evaluation",
        } <= fields
        for claim in packet["claims"]:
            assert set(claim["source_ids"]) <= source_ids
        unit_claims = [
            claim for claim in packet["claims"] if claim["field"] == "registration_unit"
        ]
        # The unit decision is documented in every packet: measure
        # sheets carry no amounts, business sheets carry all three.
        assert "金額（事業費）は施策単位では公表されない" in unit_claims[0]["statement"]
        assert "引き継いではいない" in unit_claims[0]["statement"]
    for record in projects_by_id().values():
        assert set(record["sources"]) <= source_ids
    for record in load_json(KPIS_PATH):
        assert set(record["sources"]) <= source_ids


def test_source_availability_is_honest() -> None:
    sources = {record["id"]: record for record in load_json(SOURCES_PATH)["records"]}
    assert len(sources) == 4
    for record in sources.values():
        assert record["availability"] == "published"
        assert record["municipality_key"] == "saitama-city"
    report = sources["saitama-city-implementation-status-report-fy2024-pdf"]
    assert "299事業" in report["notes"]
    impl = sources["saitama-city-implementation-plan-2026-2030-page"]
    assert "引き継いでいない" in impl["notes"]
