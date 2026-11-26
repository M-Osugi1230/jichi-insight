"""Issue #1026: Akita Prefecture stage-2 priority projects.

Registration unit: the measures (施策) of Chapter 4 of the Akita
Prefecture Comprehensive Plan (秋田県総合計画 ～秋田再興への第一歩～,
adopted March 2026, plan period FY2026-FY2029). The prefecture's policy
evaluation has historically been published at measure level (施策評価),
and the new plan itself prescribes progress management through that
evaluation system, so the measure is the canonical unit (stage-1
plan_review). The population is all 30 measures under the eight
policies; ten are selected by cycling through the policies in published
order (precedent of earlier clusters' stage 2). KPIs are the plan's own
indicator tables printed per direction under each measure: baseline =
the plan's current value (mostly FY2024, some FY2025 or 2023 as printed;
four indicators print no baseline), target = the FY2029 target (the
FY2026-FY2028 interim targets are quoted in each definition). No annual
actuals or official evaluations are published for the new plan yet, so
actuals are empty and every assessment is not_assessable. Measure-level
budget totals are not published (the FY2026 budget overview publishes
policy-level totals and individual program amounts), so amounts stay
null with the gap stated explicitly.
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "reviewed" / "akita-prefecture"
MID = "jp-local-050008"
PREFIX = "jp-local-050008-project-2026-"

EXPECTED_KPI_COUNTS = {
    PREFIX + "akita-life-migration-employment": 7,
    PREFIX + "marriage-childrearing-hope": 10,
    PREFIX + "heart-moving-tourism": 6,
    PREFIX + "food-brand-sales": 6,
    PREFIX + "agriculture-food-security": 18,
    PREFIX + "sme-management-innovation": 12,
    PREFIX + "medical-nursing-care-system": 11,
    PREFIX + "children-healthy-growth": 10,
    PREFIX + "disaster-resilient-community": 13,
    PREFIX + "nature-environment-heritage": 8,
}

# Stage 3 (Issue #1038) registered the governor's promises and
# linked five of them, by content, to three of these projects.
_TERM = "jp-local-050008-executive-2025-04-20"
EXPECTED_RELATED_PROMISES = {
    PREFIX + "akita-life-migration-employment": [f"{_TERM}-promise-007"],
    PREFIX + "marriage-childrearing-hope": [],
    PREFIX + "heart-moving-tourism": [],
    PREFIX + "food-brand-sales": [],
    PREFIX + "agriculture-food-security": [],
    PREFIX + "sme-management-innovation": [],
    PREFIX + "medical-nursing-care-system": [
        f"{_TERM}-promise-006",
        f"{_TERM}-promise-012",
    ],
    PREFIX + "children-healthy-growth": [
        f"{_TERM}-promise-013",
        f"{_TERM}-promise-014",
    ],
    PREFIX + "disaster-resilient-community": [],
    PREFIX + "nature-environment-heritage": [],
}

EXPECTED_TITLES = [
    "移住・就職で未来を拓く「あきた暮らし」を実現する",
    "出会いから子育てまで希望が持てる社会を実現する",
    "「心が動くあきたの観光」を実現する",
    "「あきたの美酒・美食」のブランド力と販売力を強化する",
    "日本の食を支える農業を実現する",
    "「人への投資」と経営革新により中小企業の経営基盤を強化する",
    "持続可能な医療・介護サービス提供体制を構築する",
    "全てのこどもの健やかな心身と自ら学ぶ意欲を育てる",
    "気候変動等に対応した災害に強い地域社会を実現する",
    "豊かな自然と良好な環境を次世代に継承する",
]

# Indicators whose plan table prints no baseline value ("―").
NO_BASELINE_KPI_SUFFIXES = {
    "marriage-childrearing-hope-kpi-childcare-worker-matching",
    "marriage-childrearing-hope-kpi-child-rights-awareness",
    "agriculture-food-security-kpi-smart-tech-farm-rate",
    "nature-environment-heritage-kpi-shirakami-revisit-rate",
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
    assert [p["official_title"] for p in projects] == EXPECTED_TITLES
    for project in projects:
        assert project["municipality_id"] == MID
        assert project["fiscal_year"] == 2026
        assert project["review_status"] == "reviewed"
        # Stage 3 (Issue #1038) registered the governor's promises;
        # the content-matched projects carry the inferred links.
        assert (
            project["related_promise_ids"]
            == EXPECTED_RELATED_PROMISES[project["id"]]
        )
        # The parent policy is the plan's policy (政策).
        assert project["parent_policy"]
        # The plan names no responsible department per measure.
        assert project["responsible_department"] is None
        assert len(project["kpis"]) == EXPECTED_KPI_COUNTS[project["id"]]
        # No annual actuals are published for the new plan.
        for kpi in project["kpis"]:
            assert kpi["actual"] is None
            assert kpi["assessment"] == "not_assessable"


def test_selection_catalog_covers_population() -> None:
    catalog = _load(
        ROOT / "data" / "catalog" / "akita_prefecture_priority_project_selection.json"
    )
    assert catalog["issue"] == 1026
    assert catalog["municipality_id"] == MID
    assert catalog["population"]["project_count"] == 30
    assert catalog["population"]["fiscal_year"] == 2026
    numbers = [s["area_number"] for s in catalog["selections"]]
    assert numbers == [1, 2, 4, 5, 9, 13, 16, 19, 24, 27]
    titles = [s["official_title"] for s in catalog["selections"]]
    assert titles == EXPECTED_TITLES
    assert len(catalog["selection_rule"]["pillars"]) == 8
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
        assert record["fiscal_year"] == 2026
        assert record["amount_yen"] is None
        assert "公表していない" in record["note"]


def test_detailed_kpis() -> None:
    kpis = _load(BASE / "project_kpis.json")
    schema = _schema("kpi.schema.json")
    for kpi in kpis:
        jsonschema.validate(kpi, schema)
    assert len(kpis) == 101
    projects = _load(BASE / "projects.json")
    assert {k["project_id"] for k in kpis} == {p["id"] for p in projects}
    # Embedded project KPIs mirror the detailed records one to one.
    detailed = {(k["project_id"], k["name"]) for k in kpis}
    embedded = {(p["id"], k["name"]) for p in projects for k in p["kpis"]}
    assert detailed == embedded
    no_baseline_ids = set()
    for kpi in kpis:
        # The plan publishes current values and FY2026-FY2029 targets
        # only; no annual actuals or achievement grades exist yet.
        assert kpi["actuals"] == []
        assert kpi["assessment"] == "not_assessable"
        assert kpi["target"]["status"] == "available"
        assert kpi["target"]["value"] is not None
        assert kpi["target"]["period"] == "2029年度"
        assert "2029年度目標値" in kpi["definition"]
        assert "not_assessable" in kpi["definition"]
        if kpi["baseline"]["status"] == "not_published":
            assert kpi["baseline"]["value"] is None
            no_baseline_ids.add(kpi["id"])
        else:
            assert kpi["baseline"]["status"] == "available"
            assert kpi["baseline"]["value"] is not None
    # Exactly the four indicators whose plan table prints "―".
    assert {i.removeprefix(PREFIX) for i in no_baseline_ids} == NO_BASELINE_KPI_SUFFIXES


def test_spot_values_match_plan_indicator_tables() -> None:
    kpis = {k["id"]: k for k in _load(BASE / "project_kpis.json")}
    migration = kpis[PREFIX + "akita-life-migration-employment-kpi-migration-pref-involved"]
    assert migration["baseline"]["value"] == 782
    assert migration["baseline"]["period"] == "2024年度"
    assert migration["target"]["value"] == 1030
    hs = kpis[PREFIX + "akita-life-migration-employment-kpi-high-school-local-employment-rate"]
    assert hs["baseline"]["value"] == 73.2
    assert hs["target"]["value"] == 80.0
    marriages = kpis[PREFIX + "marriage-childrearing-hope-kpi-marriages"]
    assert marriages["baseline"]["value"] == 2247
    assert marriages["target"]["value"] == 2360
    konkatsu = kpis[PREFIX + "marriage-childrearing-hope-kpi-job-hunting-unmarried-rate"]
    assert konkatsu["baseline"]["value"] == 8.0
    assert konkatsu["baseline"]["period"] == "2025年度"
    guests = kpis[PREFIX + "heart-moving-tourism-kpi-guest-nights"]
    assert guests["baseline"]["value"] == 3150
    assert guests["target"]["value"] == 3673
    cruise = kpis[PREFIX + "heart-moving-tourism-kpi-cruise-ship-calls"]
    assert cruise["baseline"]["value"] == 33
    assert cruise["baseline"]["period"] == "2025年度"
    sales = kpis[PREFIX + "food-brand-sales-kpi-antenna-shop-sales"]
    assert sales["baseline"]["value"] == 660116
    assert sales["target"]["value"] == 775720
    carriers = kpis[PREFIX + "agriculture-food-security-kpi-core-farm-entities"]
    assert carriers["baseline"]["value"] == 9380
    assert carriers["target"]["value"] == 7710
    assert carriers["direction"] == "decrease"
    rice = kpis[PREFIX + "agriculture-food-security-kpi-rice-harvest"]
    assert rice["baseline"]["value"] == 490000
    assert rice["target"]["value"] == 512500
    doctors = kpis[PREFIX + "medical-nursing-care-system-kpi-hospital-fulltime-doctors"]
    assert doctors["baseline"]["value"] == 1418
    assert doctors["target"]["value"] == 1500
    cancer = kpis[PREFIX + "medical-nursing-care-system-kpi-cancer-age-adjusted-mortality"]
    assert cancer["baseline"]["value"] == 76.2
    assert cancer["target"]["value"] == 60.1
    assert cancer["direction"] == "decrease"
    bridge = kpis[PREFIX + "disaster-resilient-community-kpi-emergency-road-bridge-seismic-rate"]
    # The plan's printed target sits below the printed current value;
    # both are registered exactly as published.
    assert bridge["baseline"]["value"] == 87.3
    assert bridge["target"]["value"] == 86.5
    cod = kpis[PREFIX + "nature-environment-heritage-kpi-hachiro-lake-cod"]
    assert cod["baseline"]["value"] == 7.4
    assert cod["target"]["value"] == 7.1
    assert cod["direction"] == "decrease"


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
        assert packet["open_questions"]
        # The review rests on the owner's 2026-11-15 delegation to
        # Muse and is never recorded as the owner's own review.
        unit_claim = next(
            c for c in packet["claims"] if c["field"] == "registration_unit"
        )
        assert "2026年11月15日" in unit_claim["review_note"]
        assert "所有者本人のレビューではない" in unit_claim["review_note"]


def test_project_sources_catalog() -> None:
    catalog = _load(ROOT / "data" / "catalog" / "akita_prefecture_project_sources.json")
    jsonschema.validate(catalog, _schema("source_catalog.schema.json"))
    ids = {r["id"] for r in catalog["records"]}
    assert ids == {
        "akita-pref-plan-page",
        "akita-pref-plan-full-text",
        "akita-pref-fy2026-budget-overview",
    }
    assert all(r["municipality_key"] == "akita-prefecture" for r in catalog["records"])
    projects = _load(BASE / "projects.json")
    for project in projects:
        assert set(project["sources"]) <= ids
    kpis = _load(BASE / "project_kpis.json")
    for kpi in kpis:
        assert set(kpi["sources"]) <= ids
