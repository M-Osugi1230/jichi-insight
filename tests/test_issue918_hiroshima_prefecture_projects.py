"""Issue #918: Hiroshima Prefecture priority projects (stage 2).

The registration unit is the policy domain (施策領域) of the
prefecture's plan "安心▷誇り▷挑戦 ひろしまビジョン" (October 2020),
because the prefecture's annual implementation report (主要施策の成果
に関する説明書 / ビジョン実施状況報告書) publishes, for each domain,
its KPI tables with targets, actuals and the official achievement
status for FY2021-FY2025. The latest report is the FY2025 edition,
based on the original 2020 vision; the revised vision (June 2026)
has no implementation report yet, and no cross-version mapping is
made without an official correspondence table. The old vision has
no pillar layer above the 17 domains, so the first ten domains in
the report's published order are selected (never by amount). The
prefecture publishes no per-domain amounts and no per-domain
rating, so amounts stay unregistered and the official evaluation
is registered per KPI by converting the printed achievement status
(達成=achieved, 概ね達成=mostly_achieved, 未達成=not_achieved,
実績未確定・「―」=not_assessable). Segmented KPIs (by sex, school
type, cancer type, ...) are registered as one table entry with
composite string values, whereas the report's progress summary
counts segments individually (185 KPIs in total), so the counts
intentionally differ.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
MID = "jp-local-340006"
BASE = ROOT / "data" / "reviewed" / "hiroshima-prefecture"

EXPECTED_KPI_COUNTS = {
    "jp-local-340006-project-2025-children-childrearing": 11,
    "jp-local-340006-project-2025-education": 12,
    "jp-local-340006-project-2025-health": 12,
    "jp-local-340006-project-2025-medical-care-longterm-care": 13,
    "jp-local-340006-project-2025-inclusive-community": 7,
    "jp-local-340006-project-2025-disaster-prevention-mitigation": 10,
    "jp-local-340006-project-2025-public-safety-livelihood-security": 15,
    "jp-local-340006-project-2025-work-style-reform-diverse-participation": 9,
    "jp-local-340006-project-2025-industrial-innovation": 27,
    "jp-local-340006-project-2025-agriculture-forestry-fisheries": 15,
}
# Achievement distribution per domain as printed in the FY2025
# implementation report (achieved / mostly / partially / not /
# not assessable), counted per KPI table entry.
EXPECTED_GRADES = {
    "jp-local-340006-project-2025-children-childrearing": (4, 0, 0, 5, 2),
    "jp-local-340006-project-2025-education": (6, 0, 0, 5, 1),
    "jp-local-340006-project-2025-health": (0, 0, 0, 4, 8),
    "jp-local-340006-project-2025-medical-care-longterm-care": (2, 0, 0, 3, 8),
    "jp-local-340006-project-2025-inclusive-community": (2, 0, 0, 3, 2),
    "jp-local-340006-project-2025-disaster-prevention-mitigation": (4, 1, 0, 5, 0),
    "jp-local-340006-project-2025-public-safety-livelihood-security": (8, 0, 0, 6, 1),
    "jp-local-340006-project-2025-work-style-reform-diverse-participation": (3, 0, 0, 1, 5),
    "jp-local-340006-project-2025-industrial-innovation": (16, 0, 0, 7, 4),
    "jp-local-340006-project-2025-agriculture-forestry-fisheries": (6, 4, 0, 4, 1),
}
_TERM = "jp-local-340006-executive-2025-11-29"
# Promise links registered by stage 3 (Issue #921): the governor's
# bulletin items whose theme clearly matches a policy domain. The
# culture / related-population item, the tourism items, the
# furusato-nozei item and the peace items have no corresponding
# domain among the ten and stay unlinked.
EXPECTED_PROMISE_LINKS = {
    "jp-local-340006-project-2025-children-childrearing": [],
    "jp-local-340006-project-2025-education": [],
    "jp-local-340006-project-2025-health": [],
    "jp-local-340006-project-2025-medical-care-longterm-care": [],
    "jp-local-340006-project-2025-inclusive-community": [],
    "jp-local-340006-project-2025-disaster-prevention-mitigation": [
        f"{_TERM}-promise-007",
        f"{_TERM}-promise-008",
        f"{_TERM}-promise-009",
    ],
    "jp-local-340006-project-2025-public-safety-livelihood-security": [],
    "jp-local-340006-project-2025-work-style-reform-diverse-participation": [
        f"{_TERM}-promise-004",
        f"{_TERM}-promise-005",
    ],
    "jp-local-340006-project-2025-industrial-innovation": [
        f"{_TERM}-promise-005",
    ],
    "jp-local-340006-project-2025-agriculture-forestry-fisheries": [
        f"{_TERM}-promise-001",
        f"{_TERM}-promise-002",
        f"{_TERM}-promise-003",
    ],
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
        # Stage 3 (Issue #921) registered the governor's promises;
        # only the domains with a clear thematic match are linked.
        assert project["related_promise_ids"] == EXPECTED_PROMISE_LINKS[project["id"]]
        # The old vision has no layer above the policy domains.
        assert project["parent_policy"] is None
        assert project["responsible_department"] is None
        assert len(project["kpis"]) == EXPECTED_KPI_COUNTS[project["id"]]
        grades = tuple(
            sum(1 for k in project["kpis"] if k["assessment"] == a) for a in ASSESSMENTS
        )
        assert grades == EXPECTED_GRADES[project["id"]]


def test_selection_catalog_covers_population() -> None:
    catalog = _load(ROOT / "data" / "catalog" / "hiroshima_priority_project_selection.json")
    assert catalog["issue"] == 918
    assert catalog["population"]["project_count"] == 17
    numbers = [s["area_number"] for s in catalog["selections"]]
    assert numbers == list(range(1, 11))
    titles = [s["official_title"] for s in catalog["selections"]]
    assert titles == [
        "子供・子育て",
        "教育",
        "健康",
        "医療・介護",
        "地域共生社会",
        "防災・減災",
        "治安・暮らしの安全",
        "働き方改革・多様な主体の活躍",
        "産業イノベーション",
        "農林水産業",
    ]
    projects = _load(BASE / "projects.json")
    assert {s["project_id"] for s in catalog["selections"]} == {p["id"] for p in projects}
    assert {s["series_id"] for s in catalog["selections"]} == {p["series_id"] for p in projects}


def test_amounts_and_domain_evaluation_absent() -> None:
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
    assert len(kpis) == 131
    projects = _load(BASE / "projects.json")
    assert {k["project_id"] for k in kpis} == {p["id"] for p in projects}
    # Embedded project KPIs mirror the detailed records one to one.
    detailed = {(k["project_id"], k["name"]) for k in kpis}
    embedded = {(p["id"], k["name"]) for p in projects for k in p["kpis"]}
    assert detailed == embedded
    not_published = 0
    for kpi in kpis:
        assert len(kpi["actuals"]) == 1
        actual = kpi["actuals"][0]
        assert actual["period"] == "令和7年度"
        assert kpi["baseline"]["period"] == "令和6年度"
        assert kpi["target"]["period"] == "令和7年度"
        if actual["status"] == "not_published":
            not_published += 1
            assert actual["value"] is None
            assert kpi["assessment"] == "not_assessable"
            assert "公表" in kpi["definition"]
        else:
            assert actual["status"] == "available"
            assert actual["value"] is not None
    # 32 KPIs have no published FY2025 actual in the report
    # (survey-cycle indicators awaiting scheduled publication and
    # indicators printed as "―").
    assert not_published == 32


def test_spot_values_match_evaluation_book() -> None:
    kpis = {k["id"]: k for k in _load(BASE / "project_kpis.json")}
    teachers = kpis[
        "jp-local-340006-project-2025-children-childrearing-kpi-employed-nursery-teachers"
    ]
    assert teachers["baseline"]["value"] == 14544
    assert teachers["target"]["value"] == 14324
    assert teachers["actuals"][0]["status"] == "not_published"
    fraud = kpis[
        "jp-local-340006-project-2025-public-safety-livelihood-security-kpi-special-fraud-damage"
    ]
    assert fraud["target"]["value"] == "2億円以下"
    assert fraud["actuals"][0]["value"] == "約26億3,202万円"
    assert fraud["assessment"] == "not_achieved"
    cancer = kpis["jp-local-340006-project-2025-health-kpi-cancer-screening-rate"]
    assert cancer["target"]["value"] == "全て50％以上"
    assert cancer["actuals"][0]["value"] == (
        "胃がん51.4％、肺がん50.5％、大腸がん45.8％、子宮頸がん43.2％、乳がん47.2％"
    )
    assert cancer["baseline"]["status"] == "not_published"
    sediment = kpis[
        "jp-local-340006-project-2025-disaster-prevention-mitigation"
        "-kpi-sediment-disaster-countermeasure-sites"
    ]
    assert sediment["target"]["value"] == "約3,710箇所"
    assert sediment["actuals"][0]["value"] == 3660
    monitoring = kpis[
        "jp-local-340006-project-2025-public-safety-livelihood-security"
        "-kpi-wide-area-driving-monitoring-system"
    ]
    assert monitoring["target"]["status"] == "not_published"
    assert monitoring["actuals"][0]["value"] == "広域運転監視システムの稼働"
    assert monitoring["assessment"] == "achieved"


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
        # The cross-version question (revised vision of June 2026)
        # stays open for every domain.
        assert packet["open_questions"]


def test_project_sources_catalog() -> None:
    catalog = _load(ROOT / "data" / "catalog" / "hiroshima_project_sources.json")
    jsonschema.validate(catalog, _schema("source_catalog.schema.json"))
    ids = {r["id"] for r in catalog["records"]}
    assert ids == {
        "hiroshima-pref-vision-2020",
        "hiroshima-pref-action-plan-2025",
        "hiroshima-pref-evaluation-fy2025-book",
        "hiroshima-pref-evaluation-fy2025-page",
    }
    assert all(r["municipality_key"] == "hiroshima-prefecture" for r in catalog["records"])
    projects = _load(BASE / "projects.json")
    for project in projects:
        assert set(project["sources"]) <= ids
    kpis = _load(BASE / "project_kpis.json")
    for kpi in kpis:
        assert set(kpi["sources"]) <= ids
