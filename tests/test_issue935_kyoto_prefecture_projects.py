"""Issue #935: Kyoto Prefecture priority projects (stage 2).

The registration unit is the field-level basic policy (分野別基本施策,
20 fields) of the current "京都府総合計画" (adopted October 2019,
revised December 2022), because the prefecture's annual
implementation report (実施状況報告書) publishes, for each of the 20
fields, the full numerical-target tables with baselines, final
targets, FY2025 actuals and the achievement rate against the annual
reference target (section 1(3) 数値目標の状況). The "8つのビジョン"
layer only carries narrative progress notes plus headline targets
for selected indicators, and has only nine units (eight visions
plus infrastructure), so it cannot host a ten-series selection; the
plan's three parts stand side by side and no official field-to-
vision correspondence table exists, so parent_policy stays null.
The latest report is the FY2025 edition (published October 2026);
the next plan is still being drafted. The first ten fields in the
report's published order are selected (never by amount). The
prefecture publishes no per-field amounts and no per-field rating,
so amounts stay unregistered and official_evaluation stays null;
the KPI assessment converts the printed achievement rate
(>=100% achieved, <100% not_achieved, no printed rate
not_assessable). Segmented KPIs (by school level/subject, sex,
cancer type, ...) are registered as one table entry with composite
string values, whereas the report's field summary counts segments
individually (112 items in total, 51 of them with an FY2025
target), so the counts intentionally differ.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
MID = "jp-local-260002"
BASE = ROOT / "data" / "reviewed" / "kyoto-prefecture"

EXPECTED_KPI_COUNTS = {
    "jp-local-260002-project-2025-hopeful-childrearing": 7,
    "jp-local-260002-project-2025-dream-education": 6,
    "jp-local-260002-project-2025-health-medical-longevity": 7,
    "jp-local-260002-project-2025-care-welfare": 4,
    "jp-local-260002-project-2025-human-rights": 4,
    "jp-local-260002-project-2025-all-genders-participation": 4,
    "jp-local-260002-project-2025-disability-friendly": 5,
    "jp-local-260002-project-2025-foreign-residents-vibrant": 3,
    "jp-local-260002-project-2025-community-bonds": 7,
    "jp-local-260002-project-2025-sports-for-all": 4,
}
# Achievement distribution per field as printed in the FY2025
# implementation report (achieved / mostly / partially / not /
# not assessable), counted per KPI table entry.
EXPECTED_GRADES = {
    "jp-local-260002-project-2025-hopeful-childrearing": (1, 0, 0, 5, 1),
    "jp-local-260002-project-2025-dream-education": (2, 0, 0, 1, 3),
    "jp-local-260002-project-2025-health-medical-longevity": (1, 0, 0, 1, 5),
    "jp-local-260002-project-2025-care-welfare": (1, 0, 0, 3, 0),
    "jp-local-260002-project-2025-human-rights": (0, 0, 0, 3, 1),
    "jp-local-260002-project-2025-all-genders-participation": (0, 0, 0, 4, 0),
    "jp-local-260002-project-2025-disability-friendly": (0, 0, 0, 0, 5),
    "jp-local-260002-project-2025-foreign-residents-vibrant": (1, 0, 0, 1, 1),
    "jp-local-260002-project-2025-community-bonds": (3, 0, 0, 4, 0),
    "jp-local-260002-project-2025-sports-for-all": (2, 0, 0, 1, 1),
}
ASSESSMENTS = [
    "achieved",
    "mostly_achieved",
    "partially_achieved",
    "not_achieved",
    "not_assessable",
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
    for project in projects:
        assert project["municipality_id"] == MID
        assert project["fiscal_year"] == 2025
        assert project["review_status"] == "reviewed"
        # Stage 3 (promises) has not run yet for Kyoto.
        assert project["related_promise_ids"] == []
        # The plan's three parts stand side by side; fields are not
        # subordinate to the visions and no mapping table exists.
        assert project["parent_policy"] is None
        assert project["responsible_department"] is None
        assert len(project["kpis"]) == EXPECTED_KPI_COUNTS[project["id"]]
        grades = tuple(
            sum(1 for k in project["kpis"] if k["assessment"] == a) for a in ASSESSMENTS
        )
        assert grades == EXPECTED_GRADES[project["id"]]


def test_selection_catalog_covers_population() -> None:
    catalog = _load(ROOT / "data" / "catalog" / "kyoto_priority_project_selection.json")
    assert catalog["issue"] == 935
    assert catalog["population"]["project_count"] == 20
    numbers = [s["area_number"] for s in catalog["selections"]]
    assert numbers == list(range(1, 11))
    titles = [s["official_title"] for s in catalog["selections"]]
    assert titles == [
        "希望あふれる子育て",
        "夢を実現する教育",
        "安心できる健康・医療と人生100年時代",
        "安心できる介護・福祉の実現",
        "人権が尊重される社会",
        "男性も女性も誰もが活躍できる社会",
        "障害者が暮らしやすい社会",
        "留学生・外国人が生き生きと暮らせる社会",
        "コミュニティが大切にされる社会",
        "誰もが親しみ夢が広がるスポーツ",
    ]
    projects = _load(BASE / "projects.json")
    assert {s["project_id"] for s in catalog["selections"]} == {p["id"] for p in projects}
    assert {s["series_id"] for s in catalog["selections"]} == {
        p["series_id"] for p in projects
    }


def test_amounts_and_field_evaluation_absent() -> None:
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
    assert len(kpis) == 51
    projects = _load(BASE / "projects.json")
    assert {k["project_id"] for k in kpis} == {p["id"] for p in projects}
    # Embedded project KPIs mirror the detailed records one to one.
    detailed = {(k["project_id"], k["name"]) for k in kpis}
    embedded = {(p["id"], k["name"]) for p in projects for k in p["kpis"]}
    assert detailed == embedded
    totals = {"achieved": 0, "not_achieved": 0, "not_assessable": 0}
    not_published = 0
    for kpi in kpis:
        totals[kpi["assessment"]] += 1
        assert len(kpi["actuals"]) == 1
        actual = kpi["actuals"][0]
        assert actual["period"].startswith("令和7")
        if actual["status"] == "not_published":
            not_published += 1
            assert actual["value"] is None
            assert kpi["assessment"] == "not_assessable"
            assert "公表" in kpi["definition"]
        else:
            assert actual["status"] == "available"
            assert actual["value"] is not None
    # The report's own field summary counts 51 FY2025-target items:
    # 11 at >=100%, 23 below 100%, the rest without a printed rate.
    assert totals == {"achieved": 11, "not_achieved": 23, "not_assessable": 17}
    # 14 KPIs have no published FY2025 actual (publication scheduled
    # later, survey-cycle indicators, or printed as "-").
    assert not_published == 14


def test_spot_values_match_evaluation_book() -> None:
    kpis = {k["id"]: k for k in _load(BASE / "project_kpis.json")}
    prefix = "jp-local-260002-project-2025-"
    declaration = kpis[prefix + "hopeful-childrearing-kpi-workplace-declaration-companies"]
    assert declaration["baseline"]["value"] == 1642
    assert declaration["target"]["value"] == 3000
    assert declaration["actuals"][0]["value"] == 3386
    assert declaration["assessment"] == "achieved"
    waiting = kpis[prefix + "hopeful-childrearing-kpi-nursery-waiting-children"]
    assert waiting["baseline"]["value"] == 6
    assert waiting["target"]["value"] == 0
    assert waiting["actuals"][0]["value"] == 15
    assert waiting["assessment"] == "not_achieved"
    fertility = kpis[prefix + "hopeful-childrearing-kpi-total-fertility-rate"]
    assert fertility["baseline"]["value"] == 1.22
    assert fertility["target"]["value"] == "全国平均並み"
    assert fertility["actuals"][0]["period"] == "令和7年"
    assert fertility["actuals"][0]["value"] == 1.03
    assert fertility["assessment"] == "not_assessable"
    physicians = kpis[prefix + "health-medical-longevity-kpi-physicians-underserved-areas"]
    # The report carries the values replaced by the revised medical
    # plan (baseline 259 in FY2023, target 462 in FY2029), not the
    # original plan's 248 / 260.
    assert physicians["baseline"]["value"] == 259
    assert physicians["baseline"]["period"] == "令和5年度"
    assert physicians["target"]["value"] == 462
    assert physicians["target"]["period"] == "令和11年度"
    assert physicians["actuals"][0]["value"] == 292
    capacity = kpis[prefix + "care-welfare-kpi-care-facility-capacity"]
    assert capacity["baseline"]["value"] == 23966
    assert capacity["target"]["value"] == 24757
    assert capacity["actuals"][0]["value"] == 24361
    assert capacity["assessment"] == "not_achieved"
    cancer = kpis[prefix + "health-medical-longevity-kpi-cancer-screening-rate"]
    assert cancer["baseline"]["value"] == (
        "胃がん38.7、肺がん43.9、大腸がん39.8、乳がん44.3、子宮がん38.9"
    )
    assert cancer["target"]["value"] == 50.0
    assert cancer["target"]["period"] == "令和7年"
    assert cancer["actuals"][0]["status"] == "not_published"
    donations = kpis[prefix + "community-bonds-kpi-hometown-tax-donations"]
    assert donations["baseline"]["value"] == 1.64
    assert donations["target"]["value"] == 4
    assert donations["actuals"][0]["value"] == 17.2
    assert donations["assessment"] == "achieved"
    migration = kpis[prefix + "community-bonds-kpi-net-migration"]
    assert migration["baseline"]["value"] == -3874
    assert migration["target"]["value"] == "0以上"
    assert migration["actuals"][0]["value"] == -3753
    assert migration["assessment"] == "not_achieved"
    shared = kpis[prefix + "community-bonds-kpi-shared-vision-communities"]
    assert shared["baseline"]["status"] == "not_published"
    assert shared["baseline"]["value"] is None
    assert shared["actuals"][0]["value"] == 14
    assert shared["assessment"] == "achieved"
    stadium = kpis[prefix + "sports-for-all-kpi-kyoto-stadium-users"]
    assert stadium["baseline"]["value"] == 225
    assert stadium["actuals"][0]["value"] == 584
    assert stadium["assessment"] == "achieved"


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
        # The next-plan question stays open for every field.
        assert packet["open_questions"]


def test_project_sources_catalog() -> None:
    catalog = _load(ROOT / "data" / "catalog" / "kyoto_project_sources.json")
    jsonschema.validate(catalog, _schema("source_catalog.schema.json"))
    ids = {r["id"] for r in catalog["records"]}
    assert ids == {
        "kyoto-pref-plan-page",
        "kyoto-pref-basic-plan-2022",
        "kyoto-pref-evaluation-fy2025-book",
        "kyoto-pref-evaluation-page",
    }
    assert all(r["municipality_key"] == "kyoto-prefecture" for r in catalog["records"])
    projects = _load(BASE / "projects.json")
    for project in projects:
        assert set(project["sources"]) <= ids
    kpis = _load(BASE / "project_kpis.json")
    for kpi in kpis:
        assert set(kpi["sources"]) <= ids
