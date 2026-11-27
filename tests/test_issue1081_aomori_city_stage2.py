from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MID = "jp-local-022012"
SOURCES_PATH = ROOT / "data/catalog/aomori_city_project_sources.json"
SELECTION_PATH = ROOT / "data/catalog/aomori_city_priority_project_selection.json"
PROJECTS_PATH = ROOT / "data/reviewed/aomori-city/projects.json"
KPIS_PATH = ROOT / "data/reviewed/aomori-city/project_kpis.json"
PACKETS_PATH = ROOT / "data/reviewed/aomori-city/project_evidence_packets.json"
REGISTRY_PATH = ROOT / "apps/web/lib/projectRegistry.ts"

EXPECTED_IDS = [
    "jp-local-022012-project-2024-regional-industry",
    "jp-local-022012-project-2024-future-industry",
    "jp-local-022012-project-2024-market-development",
    "jp-local-022012-project-2024-tourism-demand",
    "jp-local-022012-project-2024-collaboration-exchange",
    "jp-local-022012-project-2024-future-talent",
    "jp-local-022012-project-2024-culture-sports",
    "jp-local-022012-project-2024-health-medical",
    "jp-local-022012-project-2024-elderly-disability-care",
    "jp-local-022012-project-2024-mutual-respect-society",
    "jp-local-022012-project-2024-safe-secure-life",
    "jp-local-022012-project-2024-compact-city",
    "jp-local-022012-project-2024-disaster-snow",
    "jp-local-022012-project-2024-urban-landscape-living",
    "jp-local-022012-project-2024-transport-environment",
    "jp-local-022012-project-2024-natural-environment",
    "jp-local-022012-project-2024-decarbonization-circular",
]

EXPECTED_TITLES = [
    "活力ある地域産業の育成",
    "時代の変化を先取りした産業振興",
    "地域の特性を活かした市場開拓",
    "国内外の観光需要の取り込み",
    "連携や交流による地域活力の強化",
    "未来を担う人財の育成",
    "誰もが文化・スポーツに親しめる機会の充実",
    "生涯を通じた健康づくり・持続可能な医療提供体制の推進",
    "高齢者や障がい者が住み慣れた地域で安心して暮らせる環境づくり",
    "誰もが互いに尊重し、支え合う社会の推進",
    "安全・安心な市民生活・地域社会の確保",
    "コンパクト・プラス・ネットワークの都市づくり",
    "災害防止・雪対策の充実",
    "都市景観・居住環境の充実",
    "社会情勢の変化に対応した交通環境の充実",
    "未来につなぐ自然環境の保全・快適な生活環境の確保",
    "脱炭素・循環型社会の実現",
]

# The seventeen policies sit under the three basic policies of the
# comprehensive plan: 5 / 6 / 6.
EXPECTED_PILLARS = (
    ["仕事をつくる"] * 5 + ["人をまもり・そだてる"] * 6 + ["まちをデザインする"] * 6
)
EXPECTED_POLICIES = (
    [f"政策{i}" for i in range(1, 6)]
    + [f"政策{i}" for i in range(1, 7)]
    + [f"政策{i}" for i in range(1, 7)]
)

EXPECTED_POLICY_AREAS = [
    "industry",
    "industry",
    "industry",
    "tourism",
    "other",
    "childcare",
    "culture",
    "health",
    "welfare",
    "governance",
    "safety",
    "infrastructure",
    "disaster_prevention",
    "housing",
    "transport",
    "environment",
    "environment",
]

# Target indicators per policy in the FY2024 results report
# (令和6年度主要な施策の成果及び予算の執行実績に関する報告書):
# 113 in total, including one re-listed indicator.
EXPECTED_KPI_COUNTS = [9, 4, 2, 5, 5, 14, 9, 10, 12, 3, 10, 4, 5, 3, 9, 4, 5]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validator(name: str) -> Draft202012Validator:
    schema = load(ROOT / "schemas" / name)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def test_aomori_city_project_sources_are_schema_valid() -> None:
    catalog = load(SOURCES_PATH)
    validator("source_catalog.schema.json").validate(catalog)
    ids = [record["id"] for record in catalog["records"]]
    assert len(ids) == len(set(ids)) == 3
    assert all(
        record["municipality_key"] == "aomori-city" for record in catalog["records"]
    )


def test_selection_rule_is_plan_listing_order() -> None:
    selection = load(SELECTION_PATH)
    assert selection["municipality_id"] == MID
    assert selection["issue"] == 1081
    assert selection["population"]["item_count"] == 17
    assert selection["population"]["unit"] == "policy"
    assert "金額の大小では選ばない" in selection["selection_rule"]
    selected = selection["selections"]
    assert [item["project_id"] for item in selected] == EXPECTED_IDS
    assert [item["official_title"] for item in selected] == EXPECTED_TITLES
    assert [item["policy"] for item in selected] == EXPECTED_POLICIES
    assert [item["pillar"] for item in selected] == EXPECTED_PILLARS
    # The plan prints no responsible bureau per policy.
    assert [item["department"] for item in selected] == [None] * 17


def test_registration_unit_is_the_policy() -> None:
    # Stage 1's plan_review fixed the registration unit as the
    # policy (17 items). The FY2024 results report follows the same
    # basic-policy / policy / measure hierarchy, and its A-D grades
    # exist only per indicator, so each policy carries all of its
    # measures' indicators as KPIs.
    selection = load(SELECTION_PATH)
    description = selection["population"]["description"]
    assert "登録単位は政策とした" in description
    assert "対応付けは行っていない" in description
    for packet in load(PACKETS_PATH):
        claim = next(c for c in packet["claims"] if c["field"] == "registration_unit")
        assert "「政策」とした" in claim["statement"]
        assert "対応付けは行っていない" in claim["statement"]


def test_selected_projects_match_records() -> None:
    projects = {record["id"]: record for record in load(PROJECTS_PATH)}
    selection = load(SELECTION_PATH)
    assert len(projects) == 17
    for item in selection["selections"]:
        record = projects[item["project_id"]]
        validator("project.schema.json").validate(record)
        assert record["series_id"] == item["series_id"]
        assert record["official_title"] == item["official_title"]
        assert record["parent_policy"] == item["pillar"]
        assert record["responsible_department"] is None
        assert record["municipality_id"] == MID
        assert record["fiscal_year"] == 2024
        assert record["review_status"] == "reviewed"
        # Stage 3 has not run for Aomori City (the 2023 mayoral
        # election bulletin could not be located in stage 1), so no
        # promise links are registered.
        assert record["related_promise_ids"] == []
        assert "target_population" in record
    areas = [projects[pid]["policy_area"] for pid in EXPECTED_IDS]
    assert areas == EXPECTED_POLICY_AREAS


def test_budget_amounts_are_unregistered_with_reasons() -> None:
    # The FY2024 results report prints settlement amounts per
    # project (initiative) only; no total per policy is published.
    # Amounts therefore stay null and are never aggregated from the
    # per-initiative figures or zero-filled.
    for record in load(PROJECTS_PATH):
        assert len(record["budget_records"]) == 1
        budget = record["budget_records"][0]
        assert budget["kind"] == "settlement"
        assert budget["fiscal_year"] == 2024
        assert budget["amount_yen"] is None
        assert "未登録" in budget["note"]
        assert "0では補完しない" in budget["note"]


def test_official_evaluation_is_unpublished_and_documented() -> None:
    # The report grades each indicator (A-D) but publishes no
    # overall rating per policy, so official_evaluation stays null
    # and the gap is documented.
    for record in load(PROJECTS_PATH):
        assert record["official_evaluation"] is None
    for packet in load(PACKETS_PATH):
        claim = next(c for c in packet["claims"] if c["field"] == "official_evaluation")
        assert "総合評価（評定）を公表していない" in claim["statement"]
        assert "欠損明示" in claim["statement"]


def test_review_is_delegated_not_owner_review() -> None:
    # The review/promotion decision rests on the owner's 2026-11-15
    # delegation to Muse and must not be recorded as the owner's
    # own review.
    for packet in load(PACKETS_PATH):
        claim = next(c for c in packet["claims"] if c["field"] == "review_provenance")
        assert "2026-11-15" in claim["statement"]
        assert "所有者本人のレビューとしては記録しない" in claim["statement"]


def test_kpis_follow_the_published_indicator_grades() -> None:
    projects = load(PROJECTS_PATH)
    counts = [len(record["kpis"]) for record in projects]
    assert counts == EXPECTED_KPI_COUNTS
    assert sum(counts) == 113
    by_project = {
        record["id"]: {kpi["name"]: kpi for kpi in record["kpis"]}
        for record in projects
    }
    care = by_project["jp-local-022012-project-2024-elderly-disability-care"]
    supporters = care["認知症サポーター数"]
    values = (supporters["baseline"], supporters["target"], supporters["actual"])
    assert values == (22600, 26951, 23797)
    assert supporters["assessment"] == "achieved"
    assert supporters["unit"] == "人"
    life = by_project["jp-local-022012-project-2024-elderly-disability-care"]
    users = life["生活支援のための障害福祉サービス等の利用者数"]
    assert (users["baseline"], users["target"], users["actual"]) == (56042, 70224, 59306)
    assert users["assessment"] == "mostly_achieved"
    health = by_project["jp-local-022012-project-2024-health-medical"]
    suicide = health["自殺による死亡率"]
    assert (suicide["baseline"], suicide["target"]) == (20.9, 13.2)
    assert suicide["actual"] is None
    assert suicide["assessment"] == "not_assessable"
    guidance = health["特定保健指導対象者の減少率"]
    assert (guidance["baseline"], guidance["target"]) == (-33.7, -25)
    assert guidance["actual"] is None
    market = by_project["jp-local-022012-project-2024-market-development"]
    shipments = market["製造品出荷額等"]
    assert (shipments["baseline"], shipments["target"]) == (1175, 1479)
    assert shipments["actual"] is None
    assert shipments["unit"] == "億円"
    compact = by_project["jp-local-022012-project-2024-compact-city"]
    density = compact["居住誘導区域内の居住人口密度"]
    assert (density["baseline"], density["target"], density["actual"]) == (49.4, 46.9, 48.7)
    pedestrians = compact["歩行者通行量"]
    assert pedestrians["baseline"] is None
    assert pedestrians["target"] is None
    assert pedestrians["actual"] is None
    assert pedestrians["assessment"] == "not_assessable"
    snow = by_project["jp-local-022012-project-2024-disaster-snow"]
    channels = snow["流・融雪溝整備延長"]
    assert (channels["baseline"], channels["target"], channels["actual"]) == (
        47226,
        52726,
        49533,
    )
    assert channels["assessment"] == "achieved"
    landscape = by_project["jp-local-022012-project-2024-urban-landscape-living"]
    relisted = landscape["居住誘導区域内の居住人口密度〔再掲〕"]
    assert (relisted["baseline"], relisted["target"], relisted["actual"]) == (
        49.4,
        46.9,
        48.7,
    )
    decarb = by_project["jp-local-022012-project-2024-decarbonization-circular"]
    ghg = decarb["温室効果ガス排出量削減率"]
    assert (ghg["baseline"], ghg["target"]) == (21.7, -42.5)
    assert ghg["actual"] is None
    # The grade distribution matches the report exactly:
    # A 59 / B 39 / C 4 / D 1 / ungraded 10.
    distribution = {}
    for record in projects:
        for kpi in record["kpis"]:
            distribution[kpi["assessment"]] = distribution.get(kpi["assessment"], 0) + 1
    assert distribution == {
        "achieved": 59,
        "mostly_achieved": 39,
        "partially_achieved": 4,
        "not_achieved": 1,
        "not_assessable": 10,
    }


def test_detailed_kpis_are_schema_valid_and_linked() -> None:
    kpis = load(KPIS_PATH)
    assert len(kpis) == 113
    project_ids = {record["id"] for record in load(PROJECTS_PATH)}
    for kpi in kpis:
        validator("kpi.schema.json").validate(kpi)
        assert kpi["project_id"] in project_ids
        assert kpi["id"].startswith(kpi["project_id"] + "-kpi-")
        assert kpi["target"]["period"] == "令和10年度"
        if kpi["assessment"] == "not_assessable":
            assert kpi["actuals"] == []
        else:
            assert "換算したものである" in kpi["definition"]
            assert len(kpi["actuals"]) == 1
            assert kpi["actuals"][0]["period"] == "令和6年度"
            assert kpi["actuals"][0]["status"] == "available"
    suicide = next(kpi for kpi in kpis if kpi["name"] == "自殺による死亡率")
    assert suicide["direction"] == "decrease"
    assert suicide["baseline"]["period"] == "令和4年度"
    assert suicide["baseline"]["value"] == 20.9
    pedestrians = next(kpi for kpi in kpis if kpi["name"] == "歩行者通行量")
    assert pedestrians["baseline"]["status"] == "not_published"
    assert pedestrians["baseline"]["value"] is None
    assert pedestrians["target"]["status"] == "not_published"
    assert pedestrians["target"]["value"] is None


def test_evidence_packets_are_schema_valid() -> None:
    packets = load(PACKETS_PATH)
    assert len(packets) == 17
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
            "review_provenance",
        }


def test_web_registry_wires_aomori_city() -> None:
    text = REGISTRY_PATH.read_text(encoding="utf-8")
    assert '"aomori-city"' in text
    assert "aomoriCityProjects" in text
    assert "aomori_city_project_sources.json" in text
    assert "data/reviewed/aomori-city/projects.json" in text
