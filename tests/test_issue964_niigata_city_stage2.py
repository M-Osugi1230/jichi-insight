from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MID = "jp-local-151009"
SOURCES_PATH = ROOT / "data/catalog/niigata_city_project_sources.json"
SELECTION_PATH = ROOT / "data/catalog/niigata_city_priority_project_selection.json"
PROJECTS_PATH = ROOT / "data/reviewed/niigata-city/projects.json"
KPIS_PATH = ROOT / "data/reviewed/niigata-city/project_kpis.json"
PACKETS_PATH = ROOT / "data/reviewed/niigata-city/project_evidence_packets.json"

EXPECTED_IDS = [
    "jp-local-151009-project-2025-urban-functions-hub",
    "jp-local-151009-project-2025-business-growth",
    "jp-local-151009-project-2025-profitable-agriculture",
    "jp-local-151009-project-2025-exchange-population",
    "jp-local-151009-project-2025-migration-settlement",
    "jp-local-151009-project-2025-inclusive-society",
    "jp-local-151009-project-2025-childcare-talent",
    "jp-local-151009-project-2025-work-life-balance",
    "jp-local-151009-project-2025-decarbonized-circular-society",
    "jp-local-151009-project-2025-disaster-resilient-city",
]

EXPECTED_TITLES = [
    "都市機能の充実と拠点性の向上",
    "地域企業の経営力強化、新たなビジネスや成長産業の創出・育成",
    "豊富な田園資源を活かした儲かる農業の実現",
    "魅力と拠点性を活かした交流人口の拡大",
    "新潟暮らしの魅力発信と多様な支援による移住・定住の促進",
    "誰もが個性と能力を発揮しながら、心豊かに暮らせる社会の実現",
    "子どもと子育てにやさしいまちづくりと新潟の将来を担う人材の育成",
    "仕事と生活の調和（ワーク・ライフ・バランス）の実現",
    "脱炭素・循環型社会の実現",
    "安心・安全で災害に強いまちづくり",
]

# The ten priority strategies sit under two overarching themes of
# the Niigata City Comprehensive Plan 2030: strategies 1-5 under
# "都市の活力向上" and strategies 6-10 under "住民福祉の向上".
EXPECTED_PILLARS = ["都市の活力向上"] * 5 + ["住民福祉の向上"] * 5
EXPECTED_POLICIES = [f"重点戦略{i}" for i in range(1, 11)]

EXPECTED_POLICY_AREAS = [
    "infrastructure",
    "industry",
    "agriculture",
    "tourism",
    "other",
    "welfare",
    "childcare",
    "employment",
    "environment",
    "disaster_prevention",
]

# Policy indicators per strategy in the FY2025 progress report
# (資料1, section VI): 22 in total.
EXPECTED_KPI_COUNTS = [2, 2, 3, 3, 2, 2, 2, 2, 2, 2]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validator(name: str) -> Draft202012Validator:
    schema = load(ROOT / "schemas" / name)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def test_niigata_city_project_sources_are_schema_valid() -> None:
    catalog = load(SOURCES_PATH)
    validator("source_catalog.schema.json").validate(catalog)
    ids = [record["id"] for record in catalog["records"]]
    assert len(ids) == len(set(ids)) == 9
    assert all(
        record["municipality_key"] == "niigata-city" for record in catalog["records"]
    )


def test_selection_rule_is_plan_listing_order() -> None:
    selection = load(SELECTION_PATH)
    assert selection["municipality_id"] == MID
    assert selection["issue"] == 964
    assert selection["population"]["item_count"] == 10
    assert selection["population"]["unit"] == "strategy"
    assert "金額の大小では選ばない" in selection["selection_rule"]
    selected = selection["selections"]
    assert [item["project_id"] for item in selected] == EXPECTED_IDS
    assert [item["official_title"] for item in selected] == EXPECTED_TITLES
    assert [item["policy"] for item in selected] == EXPECTED_POLICIES
    assert [item["pillar"] for item in selected] == EXPECTED_PILLARS
    # The strategies are cross-cutting policy packages; the plan
    # names no responsible bureau per strategy.
    assert [item["department"] for item in selected] == [None] * 10


def test_registration_unit_is_the_priority_strategy() -> None:
    # The basic plan designates the policy indicators of the ten
    # priority strategies as their KPIs, and the FY2025 progress
    # report publishes progress and grades per strategy, while no
    # per-policy progress publication exists. The registration unit
    # is therefore the strategy, and the settlement attachment
    # (organised by bureau) is never mapped onto strategies.
    selection = load(SELECTION_PATH)
    description = selection["population"]["description"]
    assert "登録単位は重点戦略とした" in description
    assert "主要施策成果説明書" in description
    assert "対応付けは行っていない" in description
    for packet in load(PACKETS_PATH):
        claim = next(c for c in packet["claims"] if c["field"] == "registration_unit")
        assert "本登録の単位は、重点戦略とした" in claim["statement"]
        assert "対応付けは行っていない" in claim["statement"]


def test_selected_projects_match_records() -> None:
    projects = {record["id"]: record for record in load(PROJECTS_PATH)}
    selection = load(SELECTION_PATH)
    assert len(projects) == 10
    for item in selection["selections"]:
        record = projects[item["project_id"]]
        validator("project.schema.json").validate(record)
        assert record["series_id"] == item["series_id"]
        assert record["official_title"] == item["official_title"]
        assert record["parent_policy"] == item["pillar"]
        assert record["responsible_department"] is None
        assert record["municipality_id"] == MID
        assert record["fiscal_year"] == 2025
        assert record["review_status"] == "reviewed"
        # Promise links are stage 3 work; stage 2 registers none.
        assert record["related_promise_ids"] == []
    areas = [projects[pid]["policy_area"] for pid in EXPECTED_IDS]
    assert areas == EXPECTED_POLICY_AREAS


def test_budget_amounts_are_unregistered_with_reasons() -> None:
    # No official publication states an amount per priority
    # strategy: the progress report carries no amounts, the
    # implementation plan lists measures without amount totals, and
    # the settlement attachment is organised by bureau rather than
    # by the plan framework. Amounts therefore stay null.
    for record in load(PROJECTS_PATH):
        assert len(record["budget_records"]) == 1
        budget = record["budget_records"][0]
        assert budget["kind"] == "settlement"
        assert budget["fiscal_year"] == 2025
        assert budget["amount_yen"] is None
        assert "未登録とした" in budget["note"]
        assert "0では補完しない" in budget["note"]


def test_official_evaluation_is_unpublished_and_documented() -> None:
    # The progress report grades each policy indicator (A/B/C/-)
    # but publishes no overall rating per strategy, so
    # official_evaluation stays null and the gap is documented.
    for record in load(PROJECTS_PATH):
        assert record["official_evaluation"] is None
    for packet in load(PACKETS_PATH):
        claim = next(c for c in packet["claims"] if c["field"] == "official_evaluation")
        assert "総合評価は公表されていない" in claim["statement"]
        assert "欠損明示" in claim["statement"]


def test_kpis_follow_the_published_indicator_grades() -> None:
    projects = load(PROJECTS_PATH)
    counts = [len(record["kpis"]) for record in projects]
    assert counts == EXPECTED_KPI_COUNTS
    assert sum(counts) == 22
    by_project = {
        record["id"]: {kpi["name"]: kpi for kpi in record["kpis"]}
        for record in projects
    }
    s1 = by_project["jp-local-151009-project-2025-urban-functions-hub"]
    land = s1["都心エリアの平均地価変動率"]
    assert (land["baseline"], land["target"], land["actual"]) == (0.9, 2.0, 2.7)
    assert land["assessment"] == "achieved"
    s2 = by_project["jp-local-151009-project-2025-business-growth"]
    income = s2["一人当たり市民所得"]
    assert (income["baseline"], income["target"], income["actual"]) == (3025, 3139, 3050)
    assert income["assessment"] == "mostly_achieved"
    # The job-related migration indicator is published under both
    # strategy 2 and strategy 5 with identical values.
    s5 = by_project["jp-local-151009-project-2025-migration-settlement"]
    for holder in (s2, s5):
        migration = holder["職業を理由とした県外との転出入数"]
        assert migration["baseline"] == "2,008人転出超過"
        assert migration["actual"] == "1,790人転出超過（推計値）"
        assert migration["assessment"] == "mostly_achieved"
    s9 = by_project["jp-local-151009-project-2025-decarbonized-circular-society"]
    ghg = s9["市域から排出される温室効果ガスの削減量（平成25年度比）"]
    assert (ghg["baseline"], ghg["actual"]) == (-18.8, -36.3)
    assert ghg["target"] == "前年度（△30.7％）より削減"
    assert ghg["assessment"] == "achieved"
    # Strategy 7's planned-children indicator is surveyed only
    # every few years: no FY2025 guide line or actual was
    # published, so both stay null (never zero-filled) and the
    # assessment is not_assessable.
    s7 = by_project["jp-local-151009-project-2025-childcare-talent"]
    children = s7["夫婦が実際にもつ予定の子どもの人数"]
    assert children["baseline"] == 2.21
    assert children["target"] is None
    assert children["actual"] is None
    assert children["assessment"] == "not_assessable"


def test_detailed_kpis_are_schema_valid_and_linked() -> None:
    kpis = load(KPIS_PATH)
    assert len(kpis) == 22
    project_ids = {record["id"] for record in load(PROJECTS_PATH)}
    for kpi in kpis:
        validator("kpi.schema.json").validate(kpi)
        assert kpi["project_id"] in project_ids
        assert kpi["id"].startswith(kpi["project_id"] + "-kpi-")
        assert "換算したものである" in kpi["definition"]
    children = next(kpi for kpi in kpis if kpi["name"] == "夫婦が実際にもつ予定の子どもの人数")
    assert children["target"]["status"] == "not_applicable"
    assert children["target"]["value"] is None
    assert children["actuals"][0]["status"] == "not_published"
    assert children["actuals"][0]["value"] is None
    assert children["baseline"]["value"] == 2.21


def test_evidence_packets_are_schema_valid() -> None:
    packets = load(PACKETS_PATH)
    assert len(packets) == 10
    project_ids = {record["id"] for record in load(PROJECTS_PATH)}
    for packet in packets:
        validator("evidence_packet.schema.json").validate(packet)
        assert packet["subject_type"] == "project"
        assert packet["subject_id"] in project_ids
        assert packet["id"] == f"evidence-{packet['subject_id']}"
        fields = {claim["field"] for claim in packet["claims"]}
        assert fields == {
            "registration_unit",
            "official_title",
            "parent_policy",
            "purpose",
            "responsible_department",
            "official_evaluation",
            "budget_records.settlement",
            "kpis",
        }
