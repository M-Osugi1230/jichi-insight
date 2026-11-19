from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MID = "jp-local-232114"
SOURCES_PATH = ROOT / "data/catalog/toyota_project_sources.json"
SELECTION_PATH = ROOT / "data/catalog/toyota_priority_project_selection.json"
PROJECTS_PATH = ROOT / "data/reviewed/toyota-city/projects.json"
KPIS_PATH = ROOT / "data/reviewed/toyota-city/project_kpis.json"
PACKETS_PATH = ROOT / "data/reviewed/toyota-city/project_evidence_packets.json"

PILLARS = [
    "取組目標① こどもが多様な生き方・暮らし方を選択できる",
    "取組目標② 誰もがつながり合いの中で安心して自分らしく暮らすことができる",
    "取組目標③ 産業中枢都市として深化し続ける",
    "取組目標④ 将来を展望した都市環境の形成を進める",
    "取組目標⑤ 脱炭素社会の実現に挑戦する",
]

EXPECTED_AMOUNTS = {
    "jp-local-232114-project-2026-regional-club-activities": 387_353_000,
    "jp-local-232114-project-2026-community-sports-promotion": 31_940_000,
    "jp-local-232114-project-2026-youth-meeting-opportunities": 6_520_000,
    "jp-local-232114-project-2026-youth-life-design-support": 5_961_000,
    "jp-local-232114-project-2026-capital-investment-promotion": 1_631_838_000,
    "jp-local-232114-project-2026-new-business-development-support": 24_761_000,
    "jp-local-232114-project-2026-quality-building-development-support": 903_400_000,
    "jp-local-232114-project-2026-station-area-housing-land-supply": 7_500_000,
    "jp-local-232114-project-2026-zero-carbon-network-action": 10_000_000,
    "jp-local-232114-project-2026-plastic-products-recycling": 20_355_000,
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validator(name: str) -> Draft202012Validator:
    schema = load(ROOT / "schemas" / name)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def test_toyota_project_sources_are_schema_valid() -> None:
    catalog = load(SOURCES_PATH)
    validator("source_catalog.schema.json").validate(catalog)
    ids = [record["id"] for record in catalog["records"]]
    assert len(ids) == len(set(ids)) == 5
    assert all(
        record["municipality_key"] == "toyota-city" for record in catalog["records"]
    )


def test_selection_rule_is_listing_order_by_pillar() -> None:
    selection = load(SELECTION_PATH)
    assert selection["municipality_id"] == MID
    assert selection["issue"] == 716
    assert selection["population"]["fiscal_year"] == 2026
    assert selection["population"]["project_count"] == 234
    assert selection["population"]["policy_count"] == 30
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
        # The FY2026 general account budget was enacted on 2026-03-18
        # (bill No. 45, adopted as proposed), so the registered amounts are
        # the enacted initial budget, never a draft-stage figure.
        assert "原案可決され" in budget["note"]
        assert "予算案段階の額ではない" in budget["note"]


def test_no_evaluation_or_kpi_is_fabricated() -> None:
    # Toyota publishes no project-level official rating and no project-level
    # KPI. Both must stay explicitly empty instead of being filled from the
    # policy-level narrative of the rolling-results publication.
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
