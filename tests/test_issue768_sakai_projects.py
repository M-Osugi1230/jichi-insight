from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MID = "jp-local-271403"
SOURCES_PATH = ROOT / "data/catalog/sakai_project_sources.json"
SELECTION_PATH = ROOT / "data/catalog/sakai_priority_project_selection.json"
PROJECTS_PATH = ROOT / "data/reviewed/sakai-city/projects.json"
KPIS_PATH = ROOT / "data/reviewed/sakai-city/project_kpis.json"
PACKETS_PATH = ROOT / "data/reviewed/sakai-city/project_evidence_packets.json"

PILLARS = [
    "重点戦略1 堺の特色ある歴史文化 ～Legacy～",
    "重点戦略2 人生100年時代の健康・福祉 ～Well-being～",
    "重点戦略3 将来に希望が持てる子育て・教育 ～Children's future～",
    "重点戦略4 人や企業を惹きつける都市魅力 ～Attractiveness～",
    "重点戦略5 強くしなやかな都市基盤 ～Resilience～",
]

EXPECTED_AMOUNTS = {
    "jp-local-271403-project-2026-world-heritage-preservation-utilization": 45_573_000,
    "jp-local-271403-project-2026-mozu-kofun-group-management": 36_447_000,
    "jp-local-271403-project-2026-oral-health-center-subsidy": 48_015_000,
    "jp-local-271403-project-2026-nurse-workforce-measures": 37_162_000,
    "jp-local-271403-project-2026-actual-cost-supplementary-benefit": 11_192_000,
    "jp-local-271403-project-2026-child-supporter-training": 6_228_000,
    "jp-local-271403-project-2026-public-private-demonstration-projects": 8_000_000,
    "jp-local-271403-project-2026-city-os-utilization": 21_911_000,
    "jp-local-271403-project-2026-crisis-management-system": 414_310_000,
    "jp-local-271403-project-2026-disaster-stockpile-development": 183_721_000,
}

NO_EVALUATION_ID = "jp-local-271403-project-2026-public-private-demonstration-projects"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validator(name: str) -> Draft202012Validator:
    schema = load(ROOT / "schemas" / name)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def test_sakai_project_sources_are_schema_valid() -> None:
    catalog = load(SOURCES_PATH)
    validator("source_catalog.schema.json").validate(catalog)
    ids = [record["id"] for record in catalog["records"]]
    assert len(ids) == len(set(ids)) == 22
    assert all(record["municipality_key"] == "sakai-city" for record in catalog["records"])


def test_selection_rule_is_listing_order_by_strategy() -> None:
    selection = load(SELECTION_PATH)
    assert selection["municipality_id"] == MID
    assert selection["issue"] == 768
    assert selection["population"]["fiscal_year"] == 2026
    # 482 published sheets (483 files on the official index minus the
    # errata file, which is not a project sheet): 480 continuing FY2025
    # projects plus 2 new FY2026 projects.
    assert selection["population"]["project_count"] == 482
    # 399 sheets declare a link to exactly one of the five priority
    # strategies (coordinate-level extraction from each sheet's plan
    # positioning block); 83 declare no link and stay out of selection.
    assert selection["population"]["strategy_linked_count"] == 399
    assert selection["population"]["strategy_unlinked_count"] == 83
    assert selection["selection_rule"]["pillars"] == PILLARS
    assert "金額の大小では選ばない" in selection["selection_rule"]["description"]
    selected = selection["selections"]
    assert [item["project_id"] for item in selected] == list(EXPECTED_AMOUNTS)
    assert [item["pillar"] for item in selected] == [pillar for pillar in PILLARS for _ in range(2)]
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
        # Each amount is the project cost (a) printed in section III of the
        # FY2026 evaluation sheet, published on 2026-08-13 after the
        # FY2026 general account budget was enacted on 2026-03-26, so the
        # registered amounts are the enacted initial budget, never a
        # draft-stage figure. Personnel costs (b) are not included.
        assert "予算案段階の額ではない" in budget["note"]
        assert "人件費（b）は含まない" in budget["note"]


def test_official_evaluation_comes_from_sheet_item20() -> None:
    # Nine of the ten sheets carry the city's own necessity/effectiveness
    # rating in section V item 20 (both "高い"); the public-private
    # demonstration project sheet has no item 20 (the field is filled only
    # for projects whose previous-year check year was FY2025), so its
    # evaluation stays explicitly null instead of being filled from the
    # narrative opinions in items 18/19.
    for record in load(PROJECTS_PATH):
        if record["id"] == NO_EVALUATION_ID:
            assert record["official_evaluation"] is None
        else:
            evaluation = record["official_evaluation"]
            assert evaluation["rating"] == "必要性：高い／有効性：高い"
            assert "Jichi Insight独自の評価ではない" in evaluation["note"]


def test_no_kpi_is_fabricated() -> None:
    # The Basic Plan 2030 KPIs (29) are set per policy measure, and no
    # official source maps them uniformly to individual projects, so
    # project KPIs stay explicitly empty. The sheets' own outcome/activity
    # indicators are project management indicators, not plan KPIs, and the
    # FY2025-plan KPI contributions declared on some sheets belong to a
    # different plan version; neither is registered as a project KPI.
    for record in load(PROJECTS_PATH):
        assert record["kpis"] == []
    assert load(KPIS_PATH) == []
    packets = load(PACKETS_PATH)
    for packet in packets:
        joined = "".join(packet["open_questions"])
        assert "KPI" in joined
    no_eval = next(p for p in packets if p["subject_id"] == NO_EVALUATION_ID)
    assert "公式評価" in "".join(no_eval["open_questions"])


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
    for packet in load(PACKETS_PATH):
        for claim in packet["claims"]:
            assert set(claim["source_ids"]) <= known
    selection = load(SELECTION_PATH)
    assert set(selection["population"]["source_ids"]) <= known
    for item in selection["selections"]:
        assert set(item["source_ids"]) <= known
