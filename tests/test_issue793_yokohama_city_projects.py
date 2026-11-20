from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

PROJECTS_PATH = "data/reviewed/yokohama-city/projects.json"
KPIS_PATH = "data/reviewed/yokohama-city/project_kpis.json"
PACKETS_PATH = "data/reviewed/yokohama-city/project_evidence_packets.json"
SOURCES_PATH = "data/catalog/yokohama_city_project_sources.json"
SELECTION_PATH = "data/catalog/yokohama_city_priority_project_selection.json"

P1 = "jp-local-141003-project-2026-crime-prevention-pedestrian-safety"
P2 = "jp-local-141003-project-2026-earthquake-disaster-prevention"
P3 = "jp-local-141003-project-2026-medical-emergency-health"
P4 = "jp-local-141003-project-2026-childcare-support"
P5 = "jp-local-141003-project-2026-education-environment"
P6 = "jp-local-141003-project-2026-elderly-support"
P7 = "jp-local-141003-project-2026-disability-support"
P8 = "jp-local-141003-project-2026-community-living-environment"
P9 = "jp-local-141003-project-2026-citizen-mobility"
P10 = "jp-local-141003-project-2026-tourism-mice"
PROJECT_IDS = [P1, P2, P3, P4, P5, P6, P7, P8, P9, P10]

SELECTED_TITLES = [
    "防犯、歩行者の安心・安全",
    "地震防災対策",
    "医療・救急・保健",
    "子育て支援",
    "教育環境の整備（ソフト・ハード）",
    "高齢者支援",
    "障害児・者支援",
    "地域の生活環境",
    "市民の移動手段の確保",
    "観光・MICE",
]

EXPECTED_KPI_COUNTS = {
    P1: 6,
    P2: 13,
    P3: 11,
    P4: 4,
    P5: 4,
    P6: 4,
    P7: 4,
    P8: 4,
    P9: 6,
    P10: 6,
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


def test_yokohama_city_projects_match_schemas() -> None:
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
    assert selection["scope"] == "expanded"
    assert selection["municipality_id"] == "jp-local-141003"
    assert selection["municipality_key"] == "yokohama-city"
    # The population is the plan's 33 measure groups (施策群) under the
    # 14 policy groups of the Yokohama City Medium-Term Plan 2026-2029.
    population = selection["population"]
    assert population["policy_group_count"] == 14
    assert population["measure_group_count"] == 33
    assert len(population["measure_groups"]) == 33
    assert len(selection["selection_rule"]["pillars"]) == 14
    # Round-robin over the 14 policy groups in the plan's official
    # order, taking the first measure group of each group until 10 are
    # selected (policy groups 01-10). Amounts are never used.
    selections = selection["selections"]
    assert [item["official_title"] for item in selections] == SELECTED_TITLES
    projects = projects_by_id()
    assert [record["official_title"] for record in
            (projects[pid] for pid in PROJECT_IDS)] == SELECTED_TITLES
    for record in projects.values():
        assert record["fiscal_year"] == 2026
        assert record["review_status"] == "reviewed"
        # Each measure group spans several bureaus, so no single
        # responsible department is assigned (the bureau of each
        # indicator is recorded in the KPI definitions instead).
        assert record["responsible_department"] is None
        # Stage 3 (Issue #798) connected three measure groups to the
        # 2026 mayoral bulletin promises by wording and content
        # (confidence capped at low / inferred); the other seven
        # series still assert no link.
        expected_links = {
            "jp-local-141003-project-2026-earthquake-disaster-prevention": [
                "jp-local-141003-executive-2026-10-18-promise-001"
            ],
            "jp-local-141003-project-2026-tourism-mice": [
                "jp-local-141003-executive-2026-10-18-promise-005"
            ],
            "jp-local-141003-project-2026-childcare-support": [
                "jp-local-141003-executive-2026-10-18-promise-008"
            ],
        }
        assert record["related_promise_ids"] == expected_links.get(record["id"], [])
    skipped = selection["skipped"]
    assert len(skipped) == 23
    skipped_titles = {item["official_title"] for item in skipped}
    assert skipped_titles.isdisjoint(set(SELECTED_TITLES))
    assert skipped_titles | set(SELECTED_TITLES) == {
        item["name"] for item in population["measure_groups"]
    }
    for item in skipped:
        assert "未選定" in item["reason"]


def test_budget_amounts_are_null_with_explicit_reason() -> None:
    projects = projects_by_id()
    assert set(projects) == set(PROJECT_IDS)
    for record in projects.values():
        records = record["budget_records"]
        assert [item["kind"] for item in records] == ["initial_budget"]
        budget = records[0]
        # The city publishes initial-budget amounts per bureau/project,
        # not per measure group, and the FY2026 budget was passed on
        # 2026-03-24, before this plan was adopted on 2026-06-05, so no
        # official mapping exists: the amount stays null instead of
        # being estimated or zero-filled.
        assert budget["amount_yen"] is None
        assert budget["fiscal_year"] == 2026
        assert "施策群単位の金額は公表していない" in budget["note"]
        assert "市第76号議案" in budget["note"]
        assert "可決" in budget["note"]


def test_official_evaluation_is_null_with_explicit_reason() -> None:
    # The plan starts in FY2026 and no per-measure-group official
    # evaluation (施策評価) has been published yet, so the field stays
    # null and the gap is documented in the evidence packets.
    for record in projects_by_id().values():
        assert record["official_evaluation"] is None
    packets = {packet["subject_id"]: packet for packet in load_json(PACKETS_PATH)}
    for packet in packets.values():
        claims = [c for c in packet["claims"] if c["field"] == "official_evaluation"]
        assert len(claims) == 1
        assert "公表されていない" in claims[0]["statement"]


def test_kpi_baseline_target_actual_are_separated() -> None:
    kpis = {record["id"]: record for record in load_json(KPIS_PATH)}
    assert len(kpis) == 62
    projects = projects_by_id()
    counts = {pid: 0 for pid in PROJECT_IDS}
    for record in kpis.values():
        project = projects[record["project_id"]]
        counts[record["project_id"]] += 1
        assert record["review_status"] == "reviewed"
        # The plan period has just started: no actuals are published
        # yet, so every KPI stays in_progress with empty actuals.
        assert record["assessment"] == "in_progress"
        assert record["actuals"] == []
        embedded = {item["name"]: item for item in project["kpis"]}
        summary = embedded[record["name"]]
        assert summary["baseline"] == record["baseline"]["value"]
        assert summary["target"] == record["target"]["value"]
        assert summary["assessment"] == record["assessment"]
        assert summary["actual"] is None
    assert counts == EXPECTED_KPI_COUNTS

    lighting = kpis[f"{P1}-kpi-nighttime-lighting-coverage"]
    assert lighting["baseline"]["value"] == 70
    assert lighting["target"]["value"] == 100
    assert lighting["direction"] == "increase"

    screening = kpis[f"{P3}-kpi-cancer-screening-participants"]
    assert screening["baseline"]["value"] == 595159
    assert screening["baseline"]["period"].startswith("令和6年度時点")
    assert screening["target"]["value"] == 700000

    # The combined plan indicators are split into separate KPI records:
    # inpatient completion by phase and cancer detailed-exam rates by
    # cancer site.
    assert kpis[f"{P3}-kpi-inpatient-local-completion-acute"]["baseline"]["value"] == 84.4
    assert kpis[f"{P3}-kpi-inpatient-local-completion-recovery"]["target"]["value"] == 91.0
    assert kpis[f"{P3}-kpi-cancer-detailed-exam-rate-colorectal"]["baseline"]["value"] == 66.0

    outings = kpis[f"{P9}-kpi-districts-with-increased-outings"]
    # The plan shows "-" for this indicator's current value: it stays
    # unpublished instead of being zero-filled.
    assert outings["baseline"]["value"] is None
    assert outings["baseline"]["status"] == "not_published"
    assert outings["target"]["value"] == 53

    consumption = kpis[f"{P10}-kpi-tourism-consumption"]
    assert consumption["baseline"]["value"] == 4564
    assert consumption["target"]["value"] == 5500
    assert consumption["unit"] == "億円"


def test_every_project_has_an_evidence_packet_and_known_sources() -> None:
    source_ids = {record["id"] for record in load_json(SOURCES_PATH)["records"]}
    packets = {packet["subject_id"]: packet for packet in load_json(PACKETS_PATH)}
    assert set(packets) == set(projects_by_id())
    for packet in packets.values():
        assert packet["subject_type"] == "project"
        assert packet["review_status"] == "reviewed"
        fields = {claim["field"] for claim in packet["claims"]}
        assert {"official_title", "parent_policy", "purpose", "kpis",
                "budget_records.initial_budget", "official_evaluation"} <= fields
        for claim in packet["claims"]:
            assert set(claim["source_ids"]) <= source_ids
        budget_claims = [
            claim for claim in packet["claims"]
            if claim["field"] == "budget_records.initial_budget"
        ]
        assert "金額は未登録とした" in budget_claims[0]["statement"]
    for record in projects_by_id().values():
        assert set(record["sources"]) <= source_ids
    for record in load_json(KPIS_PATH):
        assert set(record["sources"]) <= source_ids


def test_source_availability_is_honest() -> None:
    sources = {record["id"]: record for record in load_json(SOURCES_PATH)["records"]}
    assert len(sources) == 6
    for record in sources.values():
        assert record["availability"] == "published"
        assert record["municipality_key"] == "yokohama-city"
    chapter4 = sources["yokohama-city-medium-term-plan-2026-2029-chapter4-pdf"]
    assert "施策指標" in chapter4["notes"]
    budget = sources["yokohama-city-budget-fy2026-siryou-pdf"]
    assert "施策群単位の金額" in budget["notes"]
