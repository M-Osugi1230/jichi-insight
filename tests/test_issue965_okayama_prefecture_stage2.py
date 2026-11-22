"""Issue #965: Okayama Prefecture priority projects (stage 2).

The registration unit is the strategic program (戦略プログラム,
22 programs) of the 4th "晴れの国おかやま生き活きプラン"
(adopted March 2025, plan period FY2025-FY2028), because the
prefecture's administrative evaluation publishes, for each
program, a program achievement level (政策評価, 5-point scale)
and a per-program evaluation sheet (施策評価) carrying, for every
measure, the indicators' current values, FY2028 targets, FY2025
actuals, achievement rates and grades (達成度). The latest
evaluation is the FY2026-cycle edition (令和8年度行政評価,
FY2025 results, published 2026-11-13). Ten series are selected
by cycling through the four priority strategies in the plan's
published order (round 1: I-1, II-1, III-1, IV-1; round 2: I-2,
II-2, III-2, IV-2; round 3: I-3, II-3), never by amount. The
prefecture publishes no per-program amounts, so amounts stay
unregistered; it does publish a per-program achievement level,
so official_evaluation is registered. The KPI assessment
converts the printed grade (達成度): 5 and 4 -> achieved,
3 -> partially_achieved, 2 and 1 -> not_achieved, and no
printed grade (indicators the prefecture excluded from
evaluation because the FY2025 actual was not yet known) ->
not_assessable. Indicators printed identically on several
measures' sheets are registered once per program.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
MID = "jp-local-330001"
BASE = ROOT / "data" / "reviewed" / "okayama-prefecture"
PREFIX = "jp-local-330001-project-2025-"

EXPECTED_KPI_COUNTS = {
    PREFIX + "marriage-encounter-support": 4,
    PREFIX + "learning-ability": 13,
    PREFIX + "business-attraction-investment": 7,
    PREFIX + "healthcare-enhancement": 11,
    PREFIX + "pregnancy-childrearing-support": 6,
    PREFIX + "moral-physical-education": 13,
    PREFIX + "corporate-earning-power": 8,
    PREFIX + "welfare-services": 8,
    PREFIX + "childcare-work-balance": 7,
    PREFIX + "diverse-education-needs": 8,
}
# (achieved, mostly_achieved, partially_achieved, not_achieved,
# not_assessable) per project, from the printed grades.
EXPECTED_GRADES = {
    PREFIX + "marriage-encounter-support": (3, 0, 1, 0, 0),
    PREFIX + "learning-ability": (3, 0, 9, 1, 0),
    PREFIX + "business-attraction-investment": (4, 0, 1, 2, 0),
    PREFIX + "healthcare-enhancement": (4, 0, 7, 0, 0),
    PREFIX + "pregnancy-childrearing-support": (2, 0, 2, 2, 0),
    PREFIX + "moral-physical-education": (4, 0, 8, 0, 1),
    PREFIX + "corporate-earning-power": (5, 0, 3, 0, 0),
    PREFIX + "welfare-services": (5, 0, 3, 0, 0),
    PREFIX + "childcare-work-balance": (3, 0, 2, 2, 0),
    PREFIX + "diverse-education-needs": (4, 0, 2, 0, 2),
}
EXPECTED_LEVELS = {
    PREFIX + "marriage-encounter-support": 4.0,
    PREFIX + "learning-ability": 3.1,
    PREFIX + "business-attraction-investment": 3.8,
    PREFIX + "healthcare-enhancement": 3.6,
    PREFIX + "pregnancy-childrearing-support": 2.8,
    PREFIX + "moral-physical-education": 3.3,
    PREFIX + "corporate-earning-power": 3.6,
    PREFIX + "welfare-services": 3.6,
    PREFIX + "childcare-work-balance": 3.3,
    PREFIX + "diverse-education-needs": 4.0,
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
        # Stage 3 (promises) has not run yet for Okayama.
        assert project["related_promise_ids"] == []
        assert project["parent_policy"].startswith(
            "第4次晴れの国おかやま生き活きプランの重点戦略"
        )
        assert project["responsible_department"]
        assert len(project["kpis"]) == EXPECTED_KPI_COUNTS[project["id"]]
        grades = tuple(
            sum(1 for k in project["kpis"] if k["assessment"] == a)
            for a in ASSESSMENTS
        )
        assert grades == EXPECTED_GRADES[project["id"]]


def test_selection_catalog_covers_population() -> None:
    catalog = _load(
        ROOT / "data" / "catalog" / "okayama_prefecture_priority_project_selection.json"
    )
    assert catalog["issue"] == 965
    assert catalog["population"]["project_count"] == 22
    codes = [s["program_code"] for s in catalog["selections"]]
    assert codes == [
        "I-1", "II-1", "III-1", "IV-1",
        "I-2", "II-2", "III-2", "IV-2",
        "I-3", "II-3",
    ]
    titles = [s["official_title"] for s in catalog["selections"]]
    assert titles == [
        "出会い・結婚応援プログラム",
        "学ぶ力育成プログラム",
        "企業誘致・投資促進プログラム",
        "保健医療充実プログラム",
        "妊娠・出産・子育て支援プログラム",
        "徳育・体育推進プログラム",
        "企業の「稼ぐ力」強化プログラム",
        "福祉サービス推進プログラム",
        "子育てと仕事の両立支援プログラム",
        "多様な教育ニーズ支援プログラム",
    ]
    projects = _load(BASE / "projects.json")
    assert {s["project_id"] for s in catalog["selections"]} == {
        p["id"] for p in projects
    }
    assert {s["series_id"] for s in catalog["selections"]} == {
        p["series_id"] for p in projects
    }
    assert [p["id"] for p in projects] == [
        s["project_id"] for s in catalog["selections"]
    ]


def test_amounts_absent_and_program_levels_present() -> None:
    projects = _load(BASE / "projects.json")
    for project in projects:
        evaluation = project["official_evaluation"]
        assert evaluation is not None
        level = EXPECTED_LEVELS[project["id"]]
        assert evaluation["rating"] == f"プログラム達成レベル {level}（5段階評価）"
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
    assert len(kpis) == 85
    projects = _load(BASE / "projects.json")
    assert {k["project_id"] for k in kpis} == {p["id"] for p in projects}
    detailed = {(k["project_id"], k["name"]) for k in kpis}
    embedded = {(p["id"], k["name"]) for p in projects for k in p["kpis"]}
    assert detailed == embedded
    totals = {"achieved": 0, "partially_achieved": 0, "not_achieved": 0,
              "not_assessable": 0}
    not_published = 0
    for kpi in kpis:
        totals[kpi["assessment"]] += 1
        assert len(kpi["actuals"]) == 1
        actual = kpi["actuals"][0]
        assert actual["period"] == "令和7年度"
        assert kpi["target"]["period"] == "令和10年度"
        # The sheets do not print the fiscal year of the current
        # value, so the baseline period is not fabricated.
        assert kpi["baseline"]["period"] == "計画策定時"
        if actual["status"] == "not_published":
            not_published += 1
            assert actual["value"] is None
            assert kpi["assessment"] == "not_assessable"
            assert "評価の対象外" in kpi["definition"]
        else:
            assert actual["status"] == "available"
            assert actual["value"] is not None
    assert totals == {
        "achieved": 37,
        "partially_achieved": 38,
        "not_achieved": 7,
        "not_assessable": 3,
    }
    # Three indicators were excluded from evaluation by the
    # prefecture because the FY2025 actual was not yet known.
    assert not_published == 3


def test_spot_values_match_evaluation_sheets() -> None:
    kpis = {k["id"]: k for k in _load(BASE / "project_kpis.json")}
    marriage = kpis[PREFIX + "marriage-encounter-support-kpi-marriage-rate"]
    assert marriage["baseline"]["value"] == 3.7
    assert marriage["target"]["value"] == 3.9
    assert marriage["actuals"][0]["value"] == 3.72
    assert marriage["assessment"] == "partially_achieved"
    passport = kpis[
        PREFIX + "marriage-encounter-support-kpi-marriage-passport-new-sponsors"
    ]
    # The current value is not published (printed as "-").
    assert passport["baseline"]["status"] == "not_published"
    assert passport["baseline"]["value"] is None
    assert passport["target"]["value"] == 70
    assert passport["actuals"][0]["value"] == 134
    assert passport["assessment"] == "achieved"
    births = kpis[PREFIX + "pregnancy-childrearing-support-kpi-births"]
    assert births["baseline"]["value"] == 11575
    assert births["target"]["value"] == 12238
    assert births["actuals"][0]["value"] == 10426
    # The printed rate is 85.7%, but the prefecture's own grade is
    # 2 (its grade bands depend on the indicator type), so the
    # registered assessment follows the grade, not the rate.
    assert births["assessment"] == "not_achieved"
    fertility = kpis[PREFIX + "pregnancy-childrearing-support-kpi-total-fertility-rate"]
    assert fertility["baseline"]["value"] == 1.32
    assert fertility["target"]["value"] == 1.37
    assert fertility["actuals"][0]["value"] == 1.23
    assert fertility["assessment"] == "partially_achieved"
    gap = kpis[PREFIX + "learning-ability-kpi-national-test-gap-elementary"]
    assert gap["baseline"]["value"] == -1
    assert gap["target"]["value"] == 1
    assert gap["actuals"][0]["value"] == 0
    assert gap["assessment"] == "partially_achieved"
    investment = kpis[PREFIX + "business-attraction-investment-kpi-new-location-investment"]
    assert investment["baseline"]["value"] == 1185
    assert investment["target"]["value"] == 3000
    assert investment["actuals"][0]["value"] == 3403.4
    assert investment["assessment"] == "achieved"
    violence = kpis[PREFIX + "moral-physical-education-kpi-violence-incidents-index"]
    assert violence["baseline"]["value"] == 72.4
    assert violence["target"]["value"] == 70
    assert violence["actuals"][0]["status"] == "not_published"
    assert violence["actuals"][0]["value"] is None
    assert violence["assessment"] == "not_assessable"
    assert violence["direction"] == "decrease"


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


def test_project_sources_catalog() -> None:
    catalog = _load(
        ROOT / "data" / "catalog" / "okayama_prefecture_project_sources.json"
    )
    jsonschema.validate(catalog, _schema("source_catalog.schema.json"))
    ids = {r["id"] for r in catalog["records"]}
    assert ids == {
        "okayama-pref-plan4-book",
        "okayama-pref-plan4-leaflet-page",
        "okayama-pref-eval-fy2025-page",
        "okayama-pref-eval-fy2025-policy-book",
        "okayama-pref-eval-fy2025-sheet-marriage-encounter-support",
        "okayama-pref-eval-fy2025-sheet-learning-ability",
        "okayama-pref-eval-fy2025-sheet-business-attraction-investment",
        "okayama-pref-eval-fy2025-sheet-healthcare-enhancement",
        "okayama-pref-eval-fy2025-sheet-pregnancy-childrearing-support",
        "okayama-pref-eval-fy2025-sheet-moral-physical-education",
        "okayama-pref-eval-fy2025-sheet-corporate-earning-power",
        "okayama-pref-eval-fy2025-sheet-welfare-services",
        "okayama-pref-eval-fy2025-sheet-childcare-work-balance",
        "okayama-pref-eval-fy2025-sheet-diverse-education-needs",
    }
    assert all(
        r["municipality_key"] == "okayama-prefecture" for r in catalog["records"]
    )
    projects = _load(BASE / "projects.json")
    for project in projects:
        assert set(project["sources"]) <= ids
    kpis = _load(BASE / "project_kpis.json")
    for kpi in kpis:
        assert set(kpi["sources"]) <= ids
