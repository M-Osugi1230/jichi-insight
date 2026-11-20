from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MID = "jp-local-141305"
SOURCES_PATH = ROOT / "data/catalog/kawasaki_project_sources.json"
SELECTION_PATH = ROOT / "data/catalog/kawasaki_priority_project_selection.json"
PROJECTS_PATH = ROOT / "data/reviewed/kawasaki-city/projects.json"
KPIS_PATH = ROOT / "data/reviewed/kawasaki-city/project_kpis.json"
PACKETS_PATH = ROOT / "data/reviewed/kawasaki-city/project_evidence_packets.json"

PILLARS = [
    "基本政策1 生命を守り生き生きと暮らすことができるまちづくり",
    "基本政策2 子どもを安心して育てることのできるふるさとづくり",
    "基本政策3 市民生活を豊かにする環境づくり",
    "基本政策4 活力と魅力あふれる力強い都市づくり",
    "基本政策5 誰もが生きがいを持てる市民自治の地域づくり",
]

EXPECTED_IDS = [
    "jp-local-141305-project-2026-disaster-response-capacity",
    "jp-local-141305-project-2026-community-disaster-prevention",
    "jp-local-141305-project-2026-childcare-capacity",
    "jp-local-141305-project-2026-childcare-quality",
    "jp-local-141305-project-2026-decarbonization-strategy",
    "jp-local-141305-project-2026-renewable-energy-promotion",
    "jp-local-141305-project-2026-startup-support",
    "jp-local-141305-project-2026-shin-kawasaki-sozo-no-mori",
    "jp-local-141305-project-2026-urban-community",
    "jp-local-141305-project-2026-neighborhood-association-support",
]

EXPECTED_TITLES = [
    "災害対応力強化事業",
    "地域防災推進事業",
    "保育・幼児教育の提供体制確保事業",
    "保育・幼児教育の質の維持・向上事業",
    "脱炭素戦略推進事業",
    "再エネ導入等促進事業",
    "スタートアップ支援事業",
    "新川崎・創造のもり推進事業",
    "都市型コミュニティ形成推進事業",
    "町内会・自治会活動支援事業",
]

EXPECTED_MEASURES = [
    "地域防災力の向上",
    "地域防災力の向上",
    "子ども・子育て支援の推進",
    "子ども・子育て支援の推進",
    "脱炭素化の推進",
    "脱炭素化の推進",
    "イノベーション創出の推進",
    "イノベーション創出の推進",
    "協働・連携による地域づくり",
    "協働・連携による地域づくり",
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validator(name: str) -> Draft202012Validator:
    schema = load(ROOT / "schemas" / name)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def test_kawasaki_project_sources_are_schema_valid() -> None:
    catalog = load(SOURCES_PATH)
    validator("source_catalog.schema.json").validate(catalog)
    ids = [record["id"] for record in catalog["records"]]
    assert len(ids) == len(set(ids)) == 14
    assert all(record["municipality_key"] == "kawasaki-city" for record in catalog["records"])


def test_selection_rule_is_listing_order_by_basic_policy() -> None:
    selection = load(SELECTION_PATH)
    assert selection["municipality_id"] == MID
    assert selection["issue"] == 793
    assert selection["population"]["fiscal_year"] == 2026
    # The 4th implementation plan itself states the hierarchy as 5 basic
    # policies, 18 policies, 48 measures and 350 administrative projects;
    # the appendix list (1) publishes all of them in listing order.
    assert selection["population"]["project_count"] == 350
    assert selection["population"]["basic_policy_count"] == 5
    assert selection["population"]["policy_count"] == 18
    assert selection["population"]["measure_count"] == 48
    assert selection["selection_rule"]["pillars"] == PILLARS
    assert "金額の大小では選ばない" in selection["selection_rule"]["description"]
    selected = selection["selections"]
    assert [item["project_id"] for item in selected] == EXPECTED_IDS
    assert [item["official_title"] for item in selected] == EXPECTED_TITLES
    assert [item["policy"] for item in selected] == EXPECTED_MEASURES
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
        # The 4th implementation plan does not print a responsible
        # department per project, so both stay explicitly null.
        assert record["responsible_department"] is None
        assert item["department"] is None
        assert record["municipality_id"] == MID
        assert record["fiscal_year"] == 2026
        assert record["review_status"] == "reviewed"
        assert record["related_promise_ids"] == []


def test_budget_amounts_are_explicitly_unregistered() -> None:
    # Kawasaki publishes no per-project FY2026 initial budget: the 4th
    # implementation plan prints no amounts, the latest published
    # evaluation sheets (FY2025) belong to the 3rd-plan framework and
    # their budget tables end at FY2025, and the FY2026 "main projects"
    # budget list is a partial budget-book list with no official mapping
    # to plan projects. Amounts therefore stay null instead of being
    # filled with 0 or carried over from another plan version.
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
    # No official evaluation of 4th-plan projects is published yet: the
    # plan's progress management evaluates projects annually as part of
    # their measure, after implementation. The FY2025 sheets evaluate
    # 3rd-plan projects and are not carried across plan versions.
    for record in load(PROJECTS_PATH):
        assert record["official_evaluation"] is None
    packets = load(PACKETS_PATH)
    for packet in packets:
        joined = "".join(packet["open_questions"])
        assert "公式評価は未登録" in joined
        assert "金額は未登録" in joined


def test_no_kpi_is_fabricated() -> None:
    # The plan's outcome indicators are set per measure, not per project,
    # and the "main outputs" in the plan are narrative plan-period
    # expectations without actuals or city assessments, so project KPIs
    # stay explicitly empty.
    for record in load(PROJECTS_PATH):
        assert record["kpis"] == []
    assert load(KPIS_PATH) == []
    packets = load(PACKETS_PATH)
    for packet in packets:
        joined = "".join(packet["open_questions"])
        assert "KPIは未登録" in joined


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
