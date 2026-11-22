"""Issue #966: Kumamoto Prefecture priority projects (stage 2).

The registration unit is the measure (施策) of the "くまもと新時代
共創総合戦略" (FY2024-FY2027), because the strategy places 17
measures under the four basic directions of the "くまもと新時代
共創基本方針" and publishes a KPI table per measure (chapter 3:
baseline FY2023 in principle, target FY2027), and because the
FY2025 settlement annex "主要な施策の成果" (submitted August 2026
under Local Autonomy Act art. 233(5)) is edited in the same
framework and prints one budget/settlement pair (thousand yen) per
initiative block, so amounts connect at measure level by summing
the blocks that belong to the measure. Ten measures are selected
by round-robin across the four directions in the strategy's
published order (never by amount). The annex does not state
whether its budget figures are the initial or the revised budget,
so the budget records use kind "revised_budget" with that caveat
in the note (following the Chiba precedent). The prefecture
promises annual publication of KPI progress, but no publication
listing per-KPI actuals could be identified as of registration
(November 2026), so actuals stay unregistered (explicit missing
values) and every KPI assessment is not_assessable. Segmented KPIs
(by school level etc.) are registered as one table entry with
composite string values. The basic policy's vision-level indicator
(幸せだと感じている県民の割合) belongs to no measure and is not
registered as a measure KPI. Stage 3 has not registered the
governor's promises yet, so related_promise_ids stay empty.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
MID = "jp-local-430005"
BASE = ROOT / "data" / "reviewed" / "kumamoto-prefecture"
PREFIX = "jp-local-430005-project-2025-"

EXPECTED_KPI_COUNTS = {
    PREFIX + "children-youth-shining": 3,
    PREFIX + "family-childrearing-dreams": 1,
    PREFIX + "quality-education-human-resources": 5,
    PREFIX + "workforce-securing-development": 2,
    PREFIX + "industrial-hub": 12,
    PREFIX + "food-capital": 9,
    PREFIX + "nature-conservation": 2,
    PREFIX + "migration-related-population": 2,
    PREFIX + "creative-reconstruction": 1,
    PREFIX + "disaster-resilient-land": 6,
}
EXPECTED_PARENTS = {
    PREFIX + "children-youth-shining": "こどもたちが笑顔で育つ熊本",
    PREFIX + "family-childrearing-dreams": "こどもたちが笑顔で育つ熊本",
    PREFIX + "quality-education-human-resources": "こどもたちが笑顔で育つ熊本",
    PREFIX + "workforce-securing-development": "世界に開かれた活力あふれる熊本",
    PREFIX + "industrial-hub": "世界に開かれた活力あふれる熊本",
    PREFIX + "food-capital": "世界に開かれた活力あふれる熊本",
    PREFIX + "nature-conservation": "いつまでも続く豊かな熊本",
    PREFIX + "migration-related-population": "いつまでも続く豊かな熊本",
    PREFIX + "creative-reconstruction": "県民の命、健康、安全・安心を守る",
    PREFIX + "disaster-resilient-land": "県民の命、健康、安全・安心を守る",
}
# (revised_budget, settlement) in yen, summed from the FY2025
# annex's per-block printed pairs (thousand yen x 1000).
EXPECTED_AMOUNTS = {
    PREFIX + "children-youth-shining": (42_090_483_000, 39_668_028_000),
    PREFIX + "family-childrearing-dreams": (2_133_752_000, 1_908_873_000),
    PREFIX + "quality-education-human-resources": (25_680_987_000, 22_126_092_000),
    PREFIX + "workforce-securing-development": (923_836_000, 728_048_000),
    PREFIX + "industrial-hub": (81_510_835_000, 63_474_610_000),
    PREFIX + "food-capital": (44_319_127_000, 28_071_254_000),
    PREFIX + "nature-conservation": (3_920_010_000, 2_786_143_000),
    PREFIX + "migration-related-population": (1_157_325_000, 967_099_000),
    PREFIX + "creative-reconstruction": (107_153_053_000, 46_648_846_000),
    PREFIX + "disaster-resilient-land": (100_307_714_000, 58_476_443_000),
}
SOURCE_IDS = {
    "kumamoto-pref-plan-page",
    "kumamoto-pref-basic-policy",
    "kumamoto-pref-comprehensive-strategy",
    "kumamoto-pref-strategy-summary",
    "kumamoto-pref-major-measures-results-fy2025",
}


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _schema(name: str):
    return _load(ROOT / "schemas" / name)


def test_projects_validate_against_schema() -> None:
    projects = _load(BASE / "projects.json")
    schema = _schema("project.schema.json")
    for project in projects:
        jsonschema.validate(project, schema)
    assert len(projects) == 10
    for project in projects:
        assert project["municipality_id"] == MID
        assert project["fiscal_year"] == 2025
        assert project["review_status"] == "reviewed"
        # Stage 3 (governor promises) is not registered yet.
        assert project["related_promise_ids"] == []
        assert project["parent_policy"] == EXPECTED_PARENTS[project["id"]]
        assert project["responsible_department"] is None
        assert project["official_evaluation"] is None
        assert len(project["kpis"]) == EXPECTED_KPI_COUNTS[project["id"]]
        for kpi in project["kpis"]:
            assert kpi["actual"] is None
            assert kpi["assessment"] == "not_assessable"


def test_selection_catalog_covers_population() -> None:
    catalog = _load(
        ROOT / "data" / "catalog" / "kumamoto_prefecture_priority_project_selection.json"
    )
    assert catalog["issue"] == 966
    assert catalog["population"]["project_count"] == 17
    assert catalog["selection_rule"]["pillars"] == [
        "こどもたちが笑顔で育つ熊本",
        "世界に開かれた活力あふれる熊本",
        "いつまでも続く豊かな熊本",
        "県民の命、健康、安全・安心を守る",
    ]
    numbers = [s["area_number"] for s in catalog["selections"]]
    assert numbers == list(range(1, 11))
    # Round-robin order across the four directions.
    titles = [s["official_title"] for s in catalog["selections"]]
    assert titles == [
        "こども・若者がキラキラ輝く社会づくり",
        "「くまもとで働く」人材の確保・育成",
        "豊かな自然の保全",
        "「緑の流域治水」を核とした創造的復興",
        "家庭や子育てに夢を持てる社会づくり",
        "世界に伍する産業拠点熊本の創出",
        "移住定住、関係人口創出",
        "災害に強い県土づくり",
        "質の高い教育・未来を担う人材の育成",
        "「食のみやこ熊本県」の創造",
    ]
    projects = _load(BASE / "projects.json")
    assert {s["project_id"] for s in catalog["selections"]} == {p["id"] for p in projects}
    assert {s["series_id"] for s in catalog["selections"]} == {
        p["series_id"] for p in projects
    }


def test_budget_records_match_annex_sums() -> None:
    projects = _load(BASE / "projects.json")
    for project in projects:
        assert len(project["budget_records"]) == 2
        by_kind = {r["kind"]: r for r in project["budget_records"]}
        assert set(by_kind) == {"revised_budget", "settlement"}
        budget, settlement = EXPECTED_AMOUNTS[project["id"]]
        assert by_kind["revised_budget"]["amount_yen"] == budget
        assert by_kind["settlement"]["amount_yen"] == settlement
        for record in project["budget_records"]:
            assert record["fiscal_year"] == 2025
        # The annex does not distinguish initial vs revised budget.
        assert "明示されて" in by_kind["revised_budget"]["note"]


def test_detailed_kpis() -> None:
    kpis = _load(BASE / "project_kpis.json")
    schema = _schema("kpi.schema.json")
    for kpi in kpis:
        jsonschema.validate(kpi, schema)
    assert len(kpis) == 43
    projects = _load(BASE / "projects.json")
    assert {k["project_id"] for k in kpis} == {p["id"] for p in projects}
    detailed = {(k["project_id"], k["name"]) for k in kpis}
    embedded = {(p["id"], k["name"]) for p in projects for k in p["kpis"]}
    assert detailed == embedded
    for kpi in kpis:
        # No per-KPI annual actuals publication was identified, so
        # every KPI carries one explicit not_published actual.
        assert kpi["assessment"] == "not_assessable"
        assert len(kpi["actuals"]) == 1
        actual = kpi["actuals"][0]
        assert actual["period"] == "令和7年度"
        assert actual["status"] == "not_published"
        assert actual["value"] is None
        assert "公表" in kpi["definition"]
        assert set(kpi["sources"]) <= SOURCE_IDS


def test_spot_values_match_strategy_kpi_table() -> None:
    kpis = {k["id"]: k for k in _load(BASE / "project_kpis.json")}
    river = kpis[PREFIX + "creative-reconstruction-kpi-kumagawa-river-improvement-rate"]
    assert river["baseline"]["value"] == 47.4
    assert river["target"]["value"] == 52.8
    shipments = kpis[PREFIX + "industrial-hub-kpi-manufactured-goods-shipments"]
    assert shipments["baseline"]["period"] == "令和4年"
    assert shipments["baseline"]["value"] == 34785
    assert shipments["target"]["value"] == 45400
    happiness = kpis[PREFIX + "children-youth-shining-kpi-children-happiness-rate"]
    assert happiness["baseline"]["value"] == "小学校（公立）47.2、中学校（公立）38.8"
    assert happiness["target"]["value"] == "小学校（公立）・中学校（公立）ともに55.0"
    mannaka = kpis[PREFIX + "children-youth-shining-kpi-kodomo-mannaka-support-rate"]
    assert mannaka["baseline"]["status"] == "not_published"
    assert mannaka["baseline"]["value"] is None
    assert mannaka["target"]["value"] == 55.0
    migration = kpis[PREFIX + "migration-related-population-kpi-domestic-net-migration"]
    assert migration["baseline"]["value"] == -1624
    assert migration["target"]["value"] == "令和5（2023）年の実績値を維持"
    assert migration["direction"] == "maintain"
    agri_welfare = kpis[PREFIX + "food-capital-kpi-agri-welfare-matching-contracts"]
    assert agri_welfare["baseline"]["value"] == 19
    assert agri_welfare["target"]["value"] == 75


def test_evidence_packets_cover_projects() -> None:
    packets = _load(BASE / "project_evidence_packets.json")
    schema = _schema("evidence_packet.schema.json")
    for packet in packets:
        jsonschema.validate(packet, schema)
    projects = _load(BASE / "projects.json")
    assert {p["subject_id"] for p in packets} == {p["id"] for p in projects}
    for packet in packets:
        fields = {c["field"] for c in packet["claims"]}
        assert {
            "registration_unit",
            "official_title",
            "selection",
            "purpose",
            "responsible_department",
            "budget_records",
            "official_evaluation",
            "kpis",
        } <= fields
        assert all(c["decision"] == "accepted" for c in packet["claims"])
        # The annual KPI-publication question stays open.
        assert packet["open_questions"]


def test_project_sources_catalog() -> None:
    catalog = _load(ROOT / "data" / "catalog" / "kumamoto_prefecture_project_sources.json")
    jsonschema.validate(catalog, _schema("source_catalog.schema.json"))
    ids = {r["id"] for r in catalog["records"]}
    assert ids == SOURCE_IDS
    assert all(r["municipality_key"] == "kumamoto-prefecture" for r in catalog["records"])
    projects = _load(BASE / "projects.json")
    for project in projects:
        assert set(project["sources"]) <= ids
