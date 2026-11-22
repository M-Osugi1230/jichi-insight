"""Issue #964: Niigata Prefecture stage-2 priority projects.

Registration unit: the 19 basic policies (基本政策) of Chapter 6 of the
Niigata Prefecture Comprehensive Plan (新潟県総合計画 ～住んでよし、
訪れてよしの新潟県～, adopted March 2025, plan period FY2025-FY2032).
The prefecture publishes no annual evaluation for the new plan (Chapter 7
of the plan provides internal yearly monitoring and external expert
evaluation only against the FY2028 and FY2032 targets), so the plan's own
policy unit is the canonical unit. Ten series are selected by cycling
through the six policy pillars in published order (Hiroshima City
precedent). KPIs are the plan's own outcome indicators (達成目標（成果指標）
一覧（第6章関係）): baseline = the plan's current value, target = the
FY2032 target (the FY2028 interim target is quoted in each definition).
No annual actuals or per-indicator achievement grades are published, so
actuals are empty and every assessment is not_assessable.
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "reviewed" / "niigata-prefecture"
MID = "jp-local-150002"
PREFIX = "jp-local-150002-project-2025-"

EXPECTED_KPI_COUNTS = {
    PREFIX + "accelerated-disaster-prevention": 8,
    PREFIX + "safe-community-infrastructure": 7,
    PREFIX + "childrearing-support-environment": 5,
    PREFIX + "regional-medical-and-health": 10,
    PREFIX + "respect-and-coexistence": 3,
    PREFIX + "participatory-society": 4,
    PREFIX + "exchange-population-tourism": 5,
    PREFIX + "international-hub-exchange": 6,
    PREFIX + "challengers-and-business-environment": 12,
    PREFIX + "education-for-dreams": 17,
}

EXPECTED_TITLES = [
    "一段加速した防災・減災対策の推進",
    "安全・安心な地域を支える基盤づくり",
    "こども・子育てを支える環境の整備",
    "地域医療の確保と健康立県の実現",
    "誰もが個人として尊重され、共に暮らせる社会の実現",
    "共同参画社会の実現",
    "多様な地域資源を活かした交流人口の拡大",
    "日本海側の国際拠点化と北東・東南アジアをはじめ諸外国との交流促進",
    "挑戦する人や企業が生まれ、集まる環境の整備",
    "将来の夢や希望を育みかなえる教育の推進",
]


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
    assert [p["official_title"] for p in projects] == EXPECTED_TITLES
    for project in projects:
        assert project["municipality_id"] == MID
        assert project["fiscal_year"] == 2025
        assert project["review_status"] == "reviewed"
        # Stage 3 (governor's promises) is not registered yet.
        assert project["related_promise_ids"] == []
        # The parent policy is the plan's policy pillar (政策の柱).
        assert project["parent_policy"]
        # The plan names no responsible department per basic policy.
        assert project["responsible_department"] is None
        assert len(project["kpis"]) == EXPECTED_KPI_COUNTS[project["id"]]
        # No annual actuals are published for the new plan.
        for kpi in project["kpis"]:
            assert kpi["actual"] is None
            assert kpi["assessment"] == "not_assessable"


def test_selection_catalog_covers_population() -> None:
    catalog = _load(
        ROOT / "data" / "catalog" / "niigata_prefecture_priority_project_selection.json"
    )
    assert catalog["issue"] == 964
    assert catalog["municipality_id"] == MID
    assert catalog["population"]["project_count"] == 19
    assert catalog["population"]["fiscal_year"] == 2025
    numbers = [s["area_number"] for s in catalog["selections"]]
    assert numbers == [1, 2, 7, 8, 10, 11, 12, 13, 14, 18]
    titles = [s["official_title"] for s in catalog["selections"]]
    assert titles == EXPECTED_TITLES
    assert len(catalog["selection_rule"]["pillars"]) == 6
    projects = _load(BASE / "projects.json")
    assert {s["project_id"] for s in catalog["selections"]} == {p["id"] for p in projects}
    assert {s["series_id"] for s in catalog["selections"]} == {
        p["series_id"] for p in projects
    }


def test_amounts_and_official_evaluation_absent() -> None:
    projects = _load(BASE / "projects.json")
    for project in projects:
        assert project["official_evaluation"] is None
        assert len(project["budget_records"]) == 1
        record = project["budget_records"][0]
        assert record["kind"] == "initial_budget"
        assert record["fiscal_year"] == 2025
        assert record["amount_yen"] is None
        assert "公表していない" in record["note"]


def test_detailed_kpis() -> None:
    kpis = _load(BASE / "project_kpis.json")
    schema = _schema("kpi.schema.json")
    for kpi in kpis:
        jsonschema.validate(kpi, schema)
    assert len(kpis) == 77
    projects = _load(BASE / "projects.json")
    assert {k["project_id"] for k in kpis} == {p["id"] for p in projects}
    # Embedded project KPIs mirror the detailed records one to one.
    detailed = {(k["project_id"], k["name"]) for k in kpis}
    embedded = {(p["id"], k["name"]) for p in projects for k in p["kpis"]}
    assert detailed == embedded
    for kpi in kpis:
        # The plan publishes current values and FY2028/FY2032 targets
        # only; no annual actuals or achievement grades exist yet.
        assert kpi["actuals"] == []
        assert kpi["assessment"] == "not_assessable"
        assert kpi["baseline"]["status"] == "available"
        assert kpi["baseline"]["value"] is not None
        assert kpi["target"]["status"] == "available"
        assert kpi["target"]["value"] is not None
        assert "令和10年度目標値" in kpi["definition"]
        assert "not_assessable" in kpi["definition"]


def test_spot_values_match_plan_indicator_list() -> None:
    kpis = {k["id"]: k for k in _load(BASE / "project_kpis.json")}
    hazard = kpis[PREFIX + "accelerated-disaster-prevention-kpi-hazard-map-municipalities"]
    assert hazard["baseline"]["value"] == 4
    assert hazard["baseline"]["period"] == "令和5年度"
    assert hazard["target"]["value"] == 29
    assert hazard["target"]["period"] == "令和14年度"
    river = kpis[PREFIX + "accelerated-disaster-prevention-kpi-river-improvement-rate"]
    assert river["baseline"]["value"] == 54.4
    assert river["target"]["value"] == 55.2
    gap = kpis[PREFIX + "childrearing-support-environment-kpi-university-enrollment-gap"]
    assert gap["baseline"]["value"] == 28.2
    assert gap["target"]["value"] == 22.0
    assert gap["direction"] == "decrease"
    cancer = kpis[PREFIX + "regional-medical-and-health-kpi-cancer-age-adjusted-mortality"]
    assert cancer["baseline"]["value"] == "男性83.6人、女性54.6人"
    assert cancer["target"]["value"] == "男性54.0人、女性42.7人"
    inclusive = kpis[PREFIX + "respect-and-coexistence-kpi-inclusive-support-municipalities"]
    assert inclusive["baseline"]["value"] == 0
    assert inclusive["target"]["value"] == 30
    eruboshi = kpis[PREFIX + "participatory-society-kpi-eruboshi-certifications"]
    assert eruboshi["baseline"]["value"] == 73
    assert eruboshi["target"]["value"] == 185
    inbound = kpis[PREFIX + "exchange-population-tourism-kpi-inbound-travel-consumption"]
    assert inbound["baseline"]["value"] == 106
    assert inbound["target"]["value"] == 360
    exports = kpis[PREFIX + "international-hub-exchange-kpi-company-exports"]
    assert exports["baseline"]["value"] == 4941
    assert exports["target"]["value"] == 5868
    # The export indicator is registered once, under the international
    # hub policy where the plan lists it as a primary indicator; the
    # challengers policy only re-lists it (【再掲】, related).
    assert not any(
        k["name"] == "県内企業の輸出額"
        for k in kpis.values()
        if k["project_id"] == PREFIX + "challengers-and-business-environment"
    )
    income = kpis[PREFIX + "challengers-and-business-environment-kpi-per-capita-income"]
    assert income["baseline"]["value"] == 2934
    assert income["target"]["value"] == 3476
    research = kpis[PREFIX + "education-for-dreams-kpi-joint-research-count"]
    assert research["name"] == "大学等と県内企業・地方自治体との共同・受託研究"
    assert research["baseline"]["value"] == 178
    assert research["target"]["value"] == 292


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
        # The publication format of the plan's future evaluations
        # stays open for every project.
        assert packet["open_questions"]


def test_project_sources_catalog() -> None:
    catalog = _load(ROOT / "data" / "catalog" / "niigata_prefecture_project_sources.json")
    jsonschema.validate(catalog, _schema("source_catalog.schema.json"))
    ids = {r["id"] for r in catalog["records"]}
    assert ids == {
        "niigata-pref-plan-page",
        "niigata-pref-plan-full-text",
        "niigata-pref-plan-summary",
        "niigata-pref-policy-division-page",
    }
    assert all(r["municipality_key"] == "niigata-prefecture" for r in catalog["records"])
    projects = _load(BASE / "projects.json")
    for project in projects:
        assert set(project["sources"]) <= ids
    kpis = _load(BASE / "project_kpis.json")
    for kpi in kpis:
        assert set(kpi["sources"]) <= ids
