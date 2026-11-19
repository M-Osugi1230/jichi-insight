from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MID = "jp-local-012041"
SOURCES_PATH = ROOT / "data/catalog/asahikawa_project_sources.json"
SELECTION_PATH = ROOT / "data/catalog/asahikawa_priority_project_selection.json"
PROJECTS_PATH = ROOT / "data/reviewed/asahikawa-city/projects.json"
KPIS_PATH = ROOT / "data/reviewed/asahikawa-city/project_kpis.json"
PACKETS_PATH = ROOT / "data/reviewed/asahikawa-city/project_evidence_packets.json"

PILLARS = [
    "基本目標1 すくすくと子どもが育ち、誰もが健やかに暮らせるまちを目指します",
    "基本目標2 たくましく未来を拓く人材を育み、生涯を通じて学べるまちを目指します",
    "基本目標3 活力と賑わいにあふれ、経済が力強く発展するまちを目指します",
    "基本目標4 自然と共生し、安全・安心な社会を支える強靱なまちを目指します",
    "基本目標5 互いに支え合い、共に築くまちを目指します",
]

EXPECTED_AMOUNTS = {
    "jp-local-012041-project-2026-developmental-support-counseling": 30_928_000,
    "jp-local-012041-project-2026-child-family-counseling": 57_813_000,
    "jp-local-012041-project-2026-education-support-center": 16_449_000,
    "jp-local-012041-project-2026-english-education-promotion": 40_203_000,
    "jp-local-012041-project-2026-agricultural-products-distribution": 36_096_000,
    "jp-local-012041-project-2026-clean-agriculture-research": 380_000,
    "jp-local-012041-project-2026-roads-bridges-improvement": 754_829_000,
    "jp-local-012041-project-2026-road-drainage-improvement": 3_000_000_000,
    "jp-local-012041-project-2026-collaborative-community-development": 4_150_000,
    "jp-local-012041-project-2026-peace-city-charter-promotion": 911_000,
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validator(name: str) -> Draft202012Validator:
    schema = load(ROOT / "schemas" / name)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def test_asahikawa_project_sources_are_schema_valid() -> None:
    catalog = load(SOURCES_PATH)
    validator("source_catalog.schema.json").validate(catalog)
    ids = [record["id"] for record in catalog["records"]]
    assert len(ids) == len(set(ids)) == 6
    assert all(
        record["municipality_key"] == "asahikawa-city" for record in catalog["records"]
    )


def test_selection_rule_is_listing_order_by_pillar() -> None:
    selection = load(SELECTION_PATH)
    assert selection["municipality_id"] == MID
    assert selection["issue"] == 742
    assert selection["population"]["fiscal_year"] == 2026
    # The plan document states no total project count; 396 is the count
    # confirmed by machine extraction from the plan's project tables and is
    # documented in the catalog as a lower bound.
    assert selection["population"]["project_count"] == 396
    assert selection["population"]["policy_count"] == 13
    assert selection["population"]["expansion_measure_count"] == 61
    assert selection["selection_rule"]["pillars"] == PILLARS
    assert "金額の大小では選ばない" in selection["selection_rule"]["description"]
    selected = selection["selections"]
    assert [item["project_id"] for item in selected] == list(EXPECTED_AMOUNTS)
    assert [item["pillar"] for item in selected] == [
        pillar for pillar in PILLARS for _ in range(2)
    ]
    assert selection["expansion_rule"]["total_count"] == 10


def test_selected_projects_match_records() -> None:
    projects = {record["id"]: record for record in load(PROJECTS_PATH)}
    selection = load(SELECTION_PATH)
    assert len(projects) == 10
    for item in selection["selections"]:
        record = projects[item["project_id"]]
        assert record["series_id"] == item["series_id"]
        assert record["official_title"] == item["official_title"]
        assert record["parent_policy"] == item["policy"]
        assert record["responsible_department"] == item["department"]
        assert record["municipality_id"] == MID
        assert record["fiscal_year"] == 2026
        assert record["review_status"] == "reviewed"
        assert record["related_promise_ids"] == []


def test_budget_records_are_enacted_initial_budget_only() -> None:
    for record in load(PROJECTS_PATH):
        assert len(record["budget_records"]) == 1
        budget = record["budget_records"][0]
        assert budget["kind"] == "initial_budget"
        assert budget["fiscal_year"] == 2026
        assert budget["amount_yen"] == EXPECTED_AMOUNTS[record["id"]]
        # The FY2026 general account budget was enacted on 2026-03-26
        # (bill No. 14, adopted as proposed), so the registered amounts are
        # the enacted initial budget, never a draft-stage figure.
        assert "原案可決され" in budget["note"]
        assert "予算案段階の額ではない" in budget["note"]


def test_road_amounts_come_from_expenditure_not_bond_breakdown() -> None:
    # Roads/bridges and road-drainage amounts also appear in the revenue
    # (municipal bond) section of the budget detail book as bond-financed
    # portions (233,000 and 2,893,000 thousand yen). Those are inner
    # breakdowns, not project totals; the registered amounts must be the
    # expenditure-side totals.
    projects = {record["id"]: record for record in load(PROJECTS_PATH)}
    roads = projects["jp-local-012041-project-2026-roads-bridges-improvement"]
    drainage = projects["jp-local-012041-project-2026-road-drainage-improvement"]
    assert roads["budget_records"][0]["amount_yen"] == 754_829_000
    assert drainage["budget_records"][0]["amount_yen"] == 3_000_000_000
    assert "市債分の内数" in roads["budget_records"][0]["note"]
    assert "市債分の内数" in drainage["budget_records"][0]["note"]


def test_no_evaluation_or_kpi_is_fabricated() -> None:
    # Asahikawa publishes no project-level official rating (the plan
    # inspection report is narrative at basic-policy level) and no
    # project-level KPI (plan indicators are set per expansion measure).
    # Both must stay explicitly empty instead of being filled from the
    # policy-level narrative or measure-level indicators.
    for record in load(PROJECTS_PATH):
        assert record["official_evaluation"] is None
        assert record["kpis"] == []
    assert load(KPIS_PATH) == []
    packets = load(PACKETS_PATH)
    for packet in packets:
        joined = "".join(packet["open_questions"])
        assert "公式評価" in joined
        assert "KPI" in joined


def test_projects_and_packets_are_schema_valid() -> None:
    project_validator = validator("project.schema.json")
    packet_validator = validator("evidence_packet.schema.json")
    projects = load(PROJECTS_PATH)
    for record in projects:
        project_validator.validate(record)
    packets = load(PACKETS_PATH)
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in projects
    }
    for packet in packets:
        packet_validator.validate(packet)
        assert packet["subject_type"] == "project"
        assert packet["review_status"] == "reviewed"


def test_source_references_resolve() -> None:
    known = {record["id"] for record in load(SOURCES_PATH)["records"]}
    for record in load(PROJECTS_PATH):
        assert set(record["sources"]) <= known
    for packet in load(PACKETS_PATH):
        for claim in packet["claims"]:
            assert set(claim["source_ids"]) <= known
    selection = load(SELECTION_PATH)
    assert set(selection["population"]["source_ids"]) <= known
