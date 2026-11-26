from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MID = "jp-local-072010"
SOURCES_PATH = ROOT / "data/catalog/fukushima_city_project_sources.json"
SELECTION_PATH = ROOT / "data/catalog/fukushima_city_priority_project_selection.json"
PROJECTS_PATH = ROOT / "data/reviewed/fukushima-city/projects.json"
KPIS_PATH = ROOT / "data/reviewed/fukushima-city/project_kpis.json"
PACKETS_PATH = ROOT / "data/reviewed/fukushima-city/project_evidence_packets.json"

EXPECTED_IDS = [
    "jp-local-072010-project-2025-childcare-education",
    "jp-local-072010-project-2025-radiation-recovery",
    "jp-local-072010-project-2025-disaster-measures",
    "jp-local-072010-project-2025-health-medical-welfare",
    "jp-local-072010-project-2025-culture-arts",
    "jp-local-072010-project-2025-decarbonization-circular",
    "jp-local-072010-project-2025-agriculture-commerce-industry",
    "jp-local-072010-project-2025-lively-city",
    "jp-local-072010-project-2025-migration-settlement",
    "jp-local-072010-project-2025-citizen-co-creation",
    "jp-local-072010-project-2025-city-brand",
    "jp-local-072010-project-2025-ict-transformation",
]

EXPECTED_TITLES = [
    "子どもたちの未来が広がる子育て・教育の新ステージの実現",
    "復興・創生のための放射線対策と風評払拭の推進",
    "災害対策の強化",
    "安心して暮らせる健康・医療・福祉の総合的な推進",
    "豊かな文化芸術の振興と発信",
    "脱炭素社会の実現と循環型社会の構築",
    "「人」と「活力」であふれる農業・商工業の実現",
    "福島らしい個性とにぎわいのあるまちづくり",
    "移住・定住に向けた支援・受入体制の強化",
    "市民総活躍と市民共創のまちづくり",
    "新たな施策への挑戦と発信による都市ブランド力の向上",
    "ICTを活用した行政・経済・社会の変革",
]

# The twelve priority measures sit under the six basic policies of
# the basic vision: measures 1 / 2-4 / 5-6 / 7-9 / 10-11 / 12.
EXPECTED_PILLARS = [
    "基本方針1 子どもたちの未来が広がるまち",
    "基本方針2 暮らしを支える安心安全のまち",
    "基本方針2 暮らしを支える安心安全のまち",
    "基本方針2 暮らしを支える安心安全のまち",
    "基本方針3 次世代へ文化と環境をつなぐまち",
    "基本方針3 次世代へ文化と環境をつなぐまち",
    "基本方針4 産業とにぎわいを生み出す活力躍動のまち",
    "基本方針4 産業とにぎわいを生み出す活力躍動のまち",
    "基本方針4 産業とにぎわいを生み出す活力躍動のまち",
    "基本方針5 新ステージに向けて共創・挑戦・発信するまち",
    "基本方針5 新ステージに向けて共創・挑戦・発信するまち",
    "基本方針6 効率的で質の高い行財政経営",
]
EXPECTED_POLICIES = [f"重点施策{i}" for i in range(1, 13)]

# Stage 3 (Issue #1035) connected the mayor's 2025 election-bulletin
# promises to the priority measures by wording and content
# (confidence capped at low / inferred); four measures received no
# link and four promises stayed unconnected.
_TERM = f"{MID}-executive-2025-12-08"
EXPECTED_PROMISE_LINKS = {
    f"{MID}-project-2025-childcare-education": [
        f"{_TERM}-promise-007",
        f"{_TERM}-promise-014",
    ],
    f"{MID}-project-2025-radiation-recovery": [],
    f"{MID}-project-2025-disaster-measures": [f"{_TERM}-promise-015"],
    f"{MID}-project-2025-health-medical-welfare": [f"{_TERM}-promise-011"],
    f"{MID}-project-2025-culture-arts": [f"{_TERM}-promise-009"],
    f"{MID}-project-2025-decarbonization-circular": [f"{_TERM}-promise-013"],
    f"{MID}-project-2025-agriculture-commerce-industry": [],
    f"{MID}-project-2025-lively-city": [
        f"{_TERM}-promise-005",
        f"{_TERM}-promise-006",
    ],
    f"{MID}-project-2025-migration-settlement": [],
    f"{MID}-project-2025-citizen-co-creation": [f"{_TERM}-promise-003"],
    f"{MID}-project-2025-city-brand": [],
    f"{MID}-project-2025-ict-transformation": [
        f"{_TERM}-promise-001",
        f"{_TERM}-promise-002",
    ],
}

EXPECTED_POLICY_AREAS = [
    "childcare",
    "environment",
    "disaster_prevention",
    "health",
    "culture",
    "environment",
    "industry",
    "tourism",
    "other",
    "governance",
    "other",
    "digital",
]

# Outcome indicators per priority measure in the FY2025 results
# book (令和7年度新ステージ実行プラン結果): 28 in total.
EXPECTED_KPI_COUNTS = [2, 2, 2, 3, 2, 2, 4, 2, 2, 3, 2, 2]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validator(name: str) -> Draft202012Validator:
    schema = load(ROOT / "schemas" / name)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def test_fukushima_city_project_sources_are_schema_valid() -> None:
    catalog = load(SOURCES_PATH)
    validator("source_catalog.schema.json").validate(catalog)
    ids = [record["id"] for record in catalog["records"]]
    assert len(ids) == len(set(ids)) == 8
    assert all(
        record["municipality_key"] == "fukushima-city" for record in catalog["records"]
    )


def test_selection_rule_is_plan_listing_order() -> None:
    selection = load(SELECTION_PATH)
    assert selection["municipality_id"] == MID
    assert selection["issue"] == 1023
    assert selection["population"]["item_count"] == 12
    assert selection["population"]["unit"] == "priority_measure"
    assert "金額の大小では選ばない" in selection["selection_rule"]
    selected = selection["selections"]
    assert [item["project_id"] for item in selected] == EXPECTED_IDS
    assert [item["official_title"] for item in selected] == EXPECTED_TITLES
    assert [item["policy"] for item in selected] == EXPECTED_POLICIES
    assert [item["pillar"] for item in selected] == EXPECTED_PILLARS
    # The priority measures are cross-cutting packages; neither the
    # basic vision nor the results book names a responsible bureau
    # per measure.
    assert [item["department"] for item in selected] == [None] * 12


def test_registration_unit_is_the_priority_measure() -> None:
    # The basic vision designates twelve priority measures, and the
    # execution plan results book publishes baselines, targets,
    # actuals and A-D grades per priority-measure indicator, while
    # the basic policies carry no indicators or grades. The
    # registration unit is therefore the priority measure, and the
    # settlement attachment (organised by bureau) is never mapped
    # onto measures.
    selection = load(SELECTION_PATH)
    description = selection["population"]["description"]
    assert "登録単位は重点施策とした" in description
    assert "対応付けは行っていない" in description
    for packet in load(PACKETS_PATH):
        claim = next(c for c in packet["claims"] if c["field"] == "registration_unit")
        assert "本登録の単位は、重点施策とした" in claim["statement"]
        assert "対応付けは行っていない" in claim["statement"]


def test_selected_projects_match_records() -> None:
    projects = {record["id"]: record for record in load(PROJECTS_PATH)}
    selection = load(SELECTION_PATH)
    assert len(projects) == 12
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
        # Stage 2 registered no promise links; stage 3 (Issue #1035)
        # connected them (see EXPECTED_PROMISE_LINKS).
        assert record["related_promise_ids"] == EXPECTED_PROMISE_LINKS[
            record["id"]
        ]
    areas = [projects[pid]["policy_area"] for pid in EXPECTED_IDS]
    assert areas == EXPECTED_POLICY_AREAS


def test_budget_amounts_are_unregistered_with_reasons() -> None:
    # No official publication states an amount per priority
    # measure: the results book lists amounts per initiative only,
    # and the settlement attachment is organised by bureau rather
    # than by the plan framework. Amounts therefore stay null and
    # are never aggregated or zero-filled by this registration.
    for record in load(PROJECTS_PATH):
        assert len(record["budget_records"]) == 1
        budget = record["budget_records"][0]
        assert budget["kind"] == "settlement"
        assert budget["fiscal_year"] == 2025
        assert budget["amount_yen"] is None
        assert "未登録とした" in budget["note"]
        assert "0では補完しない" in budget["note"]


def test_official_evaluation_is_unpublished_and_documented() -> None:
    # The results book grades each outcome indicator (A/B/C/D) but
    # publishes no overall rating per priority measure, so
    # official_evaluation stays null and the gap is documented.
    for record in load(PROJECTS_PATH):
        assert record["official_evaluation"] is None
    for packet in load(PACKETS_PATH):
        claim = next(c for c in packet["claims"] if c["field"] == "official_evaluation")
        assert "総合評価は公表されていない" in claim["statement"]
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
    assert sum(counts) == 28
    by_project = {
        record["id"]: {kpi["name"]: kpi for kpi in record["kpis"]}
        for record in projects
    }
    m1 = by_project["jp-local-072010-project-2025-childcare-education"]
    satisfaction = m1["「子育てしやすいまちだと思う」と答えた市民の割合"]
    values = (satisfaction["baseline"], satisfaction["target"], satisfaction["actual"])
    assert values == (48.8, 67.6, 42.8)
    assert satisfaction["assessment"] == "not_achieved"
    fertility = m1["合計特殊出生率"]
    assert (fertility["baseline"], fertility["target"], fertility["actual"]) == (1.35, 1.7, 1.09)
    assert fertility["unit"] == "－"
    m3 = by_project["jp-local-072010-project-2025-disaster-measures"]
    areas = m3["地区防災マップ・防災計画の策定地区数"]
    assert (areas["baseline"], areas["target"], areas["actual"]) == (0, 14, 14)
    assert areas["assessment"] == "achieved"
    # Healthy life expectancy at 65 is published separately for men
    # and women; the values stay in the published string form.
    m4 = by_project["jp-local-072010-project-2025-health-medical-welfare"]
    longevity = m4["お達者度（65歳健康寿命）"]
    assert longevity["baseline"] == "男性17.52・女性20.58"
    assert longevity["target"] == "男性17.92・女性20.94"
    assert longevity["actual"] == "男性17.78・女性20.53"
    assert longevity["assessment"] == "not_achieved"
    # Net GHG emissions decrease towards the target; the FY2025
    # column of the results book carries FY2023 emission values.
    m6 = by_project["jp-local-072010-project-2025-decarbonization-circular"]
    ghg = m6["温室効果ガス実質排出量"]
    assert (ghg["baseline"], ghg["target"], ghg["actual"]) == (2100, 1687, 1676)
    assert ghg["assessment"] == "achieved"
    m7 = by_project["jp-local-072010-project-2025-agriculture-commerce-industry"]
    shipments = m7["製造品出荷額等"]
    assert (shipments["baseline"], shipments["target"], shipments["actual"]) == (5637, 5637, 4743)
    assert shipments["assessment"] == "mostly_achieved"
    vacant = m7["中心市街地空き店舗数"]
    assert (vacant["baseline"], vacant["target"], vacant["actual"]) == (110, 80, 90)
    assert vacant["assessment"] == "partially_achieved"
    m9 = by_project["jp-local-072010-project-2025-migration-settlement"]
    social = m9["人口の社会動態（20歳～39歳）"]
    assert (social["baseline"], social["target"], social["actual"]) == (-650, -325, -742)
    assert social["assessment"] == "not_achieved"
    m10 = by_project["jp-local-072010-project-2025-citizen-co-creation"]
    initiatives = m10["「ふくしま共創のまちづくり計画」における取り組み数"]
    assert (initiatives["baseline"], initiatives["target"], initiatives["actual"]) == (0, 411, 388)
    assert initiatives["assessment"] == "mostly_achieved"
    m11 = by_project["jp-local-072010-project-2025-city-brand"]
    donations = m11["元気ふくしま・ふるさと寄附金額"]
    values = (donations["baseline"], donations["target"], donations["actual"])
    assert values == (145645, 2400000, 1838356)
    assert donations["assessment"] == "partially_achieved"


def test_detailed_kpis_are_schema_valid_and_linked() -> None:
    kpis = load(KPIS_PATH)
    assert len(kpis) == 28
    project_ids = {record["id"] for record in load(PROJECTS_PATH)}
    for kpi in kpis:
        validator("kpi.schema.json").validate(kpi)
        assert kpi["project_id"] in project_ids
        assert kpi["id"].startswith(kpi["project_id"] + "-kpi-")
        assert "換算したものである" in kpi["definition"]
        assert kpi["baseline"]["status"] == "available"
        assert kpi["target"]["period"] == "令和7年度"
        assert kpi["actuals"][0]["period"] == "令和7年度"
        assert kpi["actuals"][0]["status"] == "available"
    ghg = next(kpi for kpi in kpis if kpi["name"] == "温室効果ガス実質排出量")
    assert ghg["direction"] == "decrease"
    assert ghg["unit"] == "千t-CO2"
    assert ghg["baseline"]["period"] == "平成29年度"
    shipments = next(kpi for kpi in kpis if kpi["name"] == "製造品出荷額等")
    assert shipments["direction"] == "maintain"


def test_evidence_packets_are_schema_valid() -> None:
    packets = load(PACKETS_PATH)
    assert len(packets) == 12
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
