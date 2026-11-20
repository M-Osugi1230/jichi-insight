from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

PROJECTS_PATH = "data/reviewed/sapporo-city/projects.json"
KPIS_PATH = "data/reviewed/sapporo-city/project_kpis.json"
PACKETS_PATH = "data/reviewed/sapporo-city/project_evidence_packets.json"
SOURCES_PATH = "data/catalog/sapporo_city_project_sources.json"
SELECTION_PATH = "data/catalog/sapporo_city_priority_project_selection.json"

FUTURE = "jp-local-011002-project-2026-future-creation-plan-promotion"
EMPLOYMENT = "jp-local-011002-project-2026-employment-volunteer-experience"
MULTICULTURAL = "jp-local-011002-project-2026-multicultural-coexistence-promotion"
DISASTER_HQ = "jp-local-011002-project-2026-disaster-hq-function-strengthening"
HOMETOWN_TAX = "jp-local-011002-project-2026-hometown-tax-utilization"
ATHLETE = "jp-local-011002-project-2026-athlete-discovery-development"
GX = "jp-local-011002-project-2026-gx-investment-promotion"
LAND_USE = "jp-local-011002-project-2026-land-use-plan-formulation"
DV = "jp-local-011002-project-2026-dv-countermeasures-promotion"
SENIOR = "jp-local-011002-project-2026-senior-university-operation"

ROUND1_IDS = [
    FUTURE,
    EMPLOYMENT,
    MULTICULTURAL,
    DISASTER_HQ,
    HOMETOWN_TAX,
    ATHLETE,
    GX,
    LAND_USE,
]
ROUND2_IDS = [DV, SENIOR]

FIELD1 = "まちづくりの分野1 子ども・若者"
FIELD2 = "まちづくりの分野2 生活・暮らし"
FIELD3 = "まちづくりの分野3 地域"
FIELD4 = "まちづくりの分野4 安全・安心"
FIELD5 = "まちづくりの分野5 経済"
FIELD6 = "まちづくりの分野6 スポーツ・文化"
FIELD7 = "まちづくりの分野7 環境"
FIELD8 = "まちづくりの分野8 都市空間"
PILLARS = [FIELD1, FIELD2, FIELD3, FIELD4, FIELD5, FIELD6, FIELD7, FIELD8]


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


def test_sapporo_city_projects_match_schemas() -> None:
    assert_valid("schemas/source_catalog.schema.json", load_json(SOURCES_PATH))
    for record in load_json(PROJECTS_PATH):
        assert_valid("schemas/project.schema.json", record)
    for record in load_json(KPIS_PATH):
        assert_valid("schemas/kpi.schema.json", record)
    for packet in load_json(PACKETS_PATH):
        assert_valid("schemas/evidence_packet.schema.json", packet)


def test_selection_rule_and_population() -> None:
    selection = load_json(SELECTION_PATH)
    # The population is defined as an intersection because Sapporo City has
    # no single official priority-project list.
    assert "交差集合" in selection["population"]["description"]
    assert selection["population"]["fiscal_year"] == 2026
    assert selection["population"]["policy_count"] == 8
    assert selection["issue"] == 742
    assert selection["scope"] == "expanded"
    assert selection["expansion_rule"]["added_count"] == 2
    assert selection["expansion_rule"]["total_count"] == 10
    selections = selection["selections"]
    assert len(selections) == 10
    # Round 1 takes the first qualifying principal project of each of the
    # eight plan fields in book order; round 2 continues fields 1 and 2.
    assert [item["project_id"] for item in selections] == ROUND1_IDS + ROUND2_IDS
    assert [item["pillar"] for item in selections[:8]] == PILLARS
    assert [item["pillar"] for item in selections[8:]] == [FIELD1, FIELD2]
    projects = projects_by_id()
    for item in selections:
        record = projects[item["project_id"]]
        assert record["series_id"] == item["series_id"]
        assert record["official_title"] == item["official_title"]
        assert record["fiscal_year"] == 2026
        assert record["review_status"] == "reviewed"
    skipped = selection["skipped"]
    skipped_titles = {item["official_title"] for item in skipped}
    # The first principal projects of fields 6 and 8 have plan targets but
    # no standalone FY2026 major-project amount, so they stay on record as
    # skipped instead of being force-matched to another project's item.
    assert skipped_titles == {
        "藻岩山スキー場運営体制強化支援事業",
        "歩きたくなるまちづくり推進事業",
    }
    assert skipped_titles.isdisjoint(
        {record["official_title"] for record in projects.values()}
    )


def test_project_budget_records_are_enacted_amounts() -> None:
    projects = projects_by_id()
    expected = {
        FUTURE: 23_000_000,
        EMPLOYMENT: 23_000_000,
        MULTICULTURAL: 75_000_000,
        DISASTER_HQ: 3_400_000,
        HOMETOWN_TAX: 2_978_000_000,
        ATHLETE: 56_000_000,
        GX: 187_000_000,
        LAND_USE: 11_000_000,
        DV: 25_000_000,
        SENIOR: 5_200_000,
    }
    assert set(projects) == set(expected)
    for project_id, initial in expected.items():
        records = projects[project_id]["budget_records"]
        # Settlement amounts are not registered: no official per-project
        # settlement figures could be confirmed, and the gap is stated in
        # the evidence packets instead of being filled from other documents.
        assert [item["kind"] for item in records] == ["initial_budget"]
        record = records[0]
        assert record["amount_yen"] == initial
        assert record["fiscal_year"] == 2026
        # The FY2026 budget bill (Bill No. 1) was passed on 2026-03-26 with
        # no amendment recorded, so the note must state the enacted stage
        # and never present the amounts as proposal-stage figures.
        assert "成立後の当初予算額" in record["note"]
        assert "議案第1号" in record["note"]
        assert "予算案段階" not in record["note"]


def test_kpi_baseline_target_actual_are_separated() -> None:
    kpis = {record["id"]: record for record in load_json(KPIS_PATH)}
    assert len(kpis) == 10
    projects = projects_by_id()
    for record in kpis.values():
        project = projects[record["project_id"]]
        assert record["review_status"] == "reviewed"
        assert record["causality_note"]
        # Sapporo City publishes no per-project actuals for plan targets
        # (progress reports are plan-wide aggregates), so actuals stay
        # empty and the embedded summary keeps actual as null.
        assert record["actuals"] == []
        assert record["assessment"] == "in_progress"
        embedded = {item["name"]: item for item in project["kpis"]}
        summary = embedded[record["name"]]
        assert summary["baseline"] == record["baseline"]["value"]
        assert summary["target"] == record["target"]["value"]
        assert summary["actual"] is None
        assert summary["assessment"] == record["assessment"]

    hometown = kpis[f"{HOMETOWN_TAX}-kpi-portal-donation-amount"]
    assert hometown["baseline"]["value"] == 1521152
    assert hometown["target"]["value"] == 5000000
    assert hometown["unit"] == "千円"
    assert hometown["direction"] == "increase"

    disaster = kpis[f"{DISASTER_HQ}-kpi-disaster-hq-function-maintenance-rate"]
    # The printed target equals the baseline (100%); the direction is
    # recorded as maintain, exactly as printed in the plan book.
    assert disaster["baseline"]["value"] == 100
    assert disaster["target"]["value"] == 100
    assert disaster["direction"] == "maintain"

    dv = kpis[f"{DV}-kpi-dv-no-consultation-share"]
    assert dv["baseline"]["value"] == 37
    assert dv["target"]["value"] == 20
    assert dv["direction"] == "decrease"

    future = kpis[f"{FUTURE}-kpi-future-creation-plan-indicator-achievement-rate"]
    # The plan book prints "-" for the 2022 value; the baseline stays
    # unpublished instead of being filled with zero.
    assert future["baseline"]["value"] is None
    assert future["baseline"]["status"] == "not_published"
    assert future["target"]["value"] == 60

    gx = kpis[f"{GX}-kpi-renewable-energy-share"]
    assert gx["baseline"]["value"] is None
    assert gx["baseline"]["status"] == "not_published"
    assert gx["target"]["value"] == 42

    land_use = kpis[f"{LAND_USE}-kpi-master-plan-revision"]
    # The target is a milestone (revision of the master plan in FY2025),
    # not a number; it is recorded as the printed string.
    assert land_use["target"]["value"] == "改定"
    assert land_use["target"]["period"] == "2025年度"
    assert land_use["direction"] == "not_applicable"

    senior = kpis[f"{SENIOR}-kpi-senior-university-graduates-community-activity-share"]
    assert senior["baseline"]["value"] == 44.4
    assert senior["target"]["value"] == 60


def test_official_evaluation_gap_is_explicit() -> None:
    projects = projects_by_id()
    for record in projects.values():
        # Sapporo City publishes no per-project official evaluation for
        # Action Plan 2023 projects; the field stays null and the gap is
        # stated in each evidence packet rather than filled by our own
        # judgement.
        assert record["official_evaluation"] is None
        # Promise links were registered in Hokkaido cluster stage 3
        # (Issue #749): the multicultural coexistence project links to
        # the coexistence-ordinance promise and the GX investment project
        # to the zero-carbon promise; all other projects stay unlinked.
        # Exact bidirectional consistency is asserted by
        # tests/test_issue749_sapporo_promise_registration.py.
        expected_links = {
            "jp-local-011002-project-2026-multicultural-coexistence-promotion": [
                "jp-local-011002-executive-2023-05-02-promise-008"
            ],
            "jp-local-011002-project-2026-gx-investment-promotion": [
                "jp-local-011002-executive-2023-05-02-promise-009"
            ],
        }
        assert record["related_promise_ids"] == expected_links.get(record["id"], [])
    packets = {packet["subject_id"]: packet for packet in load_json(PACKETS_PATH)}
    for packet in packets.values():
        evaluation_claims = [
            claim for claim in packet["claims"] if claim["field"] == "official_evaluation"
        ]
        assert len(evaluation_claims) == 1
        assert "事業単位の公式評価を公表していない" in evaluation_claims[0]["statement"]


def test_every_project_has_an_evidence_packet_and_known_sources() -> None:
    source_ids = {record["id"] for record in load_json(SOURCES_PATH)["records"]}
    packets = {packet["subject_id"]: packet for packet in load_json(PACKETS_PATH)}
    assert set(packets) == set(projects_by_id())
    for packet in packets.values():
        assert packet["subject_type"] == "project"
        assert packet["review_status"] == "reviewed"
        for claim in packet["claims"]:
            assert set(claim["source_ids"]) <= source_ids
        # Unregistered settlement amounts stay explicit open questions.
        assert any("決算額は未登録" in question for question in packet["open_questions"])
        assert any("未登録" in question for question in packet["open_questions"])
    for record in projects_by_id().values():
        assert set(record["sources"]) <= source_ids
    for record in load_json(KPIS_PATH):
        assert set(record["sources"]) <= source_ids


def test_source_availability_is_honest() -> None:
    sources = {record["id"]: record for record in load_json(SOURCES_PATH)["records"]}
    for record in sources.values():
        assert record["availability"] == "published"
        assert record["municipality_key"] == "sapporo-city"
    # The 2026 progress report is plan-wide aggregates only; the catalog
    # says so, which is why no per-project evaluation is registered.
    progress = sources["sapporo-city-action-plan-2023-progress-2026-pdf"]
    assert "事業単位の評価・実績値は掲載されていない" in progress["notes"]
    # The voting results table records Bill No. 1 as passed with no
    # amendment; the catalog note keeps that wording.
    kekka = sources["sapporo-city-assembly-fy2026-session1-results-pdf"]
    assert "修正の記載はない" in kekka["notes"]
