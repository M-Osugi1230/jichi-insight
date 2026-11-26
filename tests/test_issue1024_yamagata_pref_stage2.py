"""Issue #1024: Yamagata Prefecture stage-2 priority projects.

Registration unit: the 22 policies (政策) of the prefecture-wide part of
the Late Implementation Plan (後期実施計画, FY2025-FY2029) of the 4th
Yamagata Prefecture Comprehensive Development Plan (第4次山形県総合発展
計画, adopted March 2020; late implementation plan adopted March 2025).
The stage-1 plan review had floated "28 policies" as a candidate count;
the plan booklet itself lists 22 policies (pillar 1: 4, pillar 2: 4,
pillar 3: 3, pillar 4: 6, pillar 5: 5), and 28 is the number of target
indicators (目標指標) set on those policies. The population is therefore
22, confirmed against the plan booklet and the long-term vision summary.
Ten policies are selected by cycling through the five policy pillars in
published order (Niigata Prefecture precedent). KPIs are the policies'
target indicators only: baseline = the plan's current value, target =
the FY2029 target. The prefecture's progress evaluation (as of the end
of FY2025, council material 2-1) publishes only aggregate category
counts for all 28 target indicators, not per-indicator actuals or
achievement grades, so actuals are empty, official_evaluation is null,
and every assessment is not_assessable. Two indicators are new and
publish no current value ("―" in the plan); their baselines are
registered as not_published with a null value rather than filled in.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "reviewed" / "yamagata-prefecture"
MID = "jp-local-060003"
PREFIX = "jp-local-060003-project-2025-"

EXPECTED_KPI_COUNTS = {
    PREFIX + "school-education": 2,
    PREFIX + "lifelong-learning": 1,
    PREFIX + "agricultural-workforce-foundation": 1,
    PREFIX + "profitable-agriculture": 1,
    PREFIX + "industrial-innovation-iot": 1,
    PREFIX + "regional-industry-sme-growth": 1,
    PREFIX + "crisis-management": 2,
    PREFIX + "everyday-risk-resilience": 2,
    PREFIX + "future-technology-implementation": 1,
    PREFIX + "transport-network": 1,
}

EXPECTED_TITLES = [
    "学校教育の充実",
    "生涯を通じた多様な学びの機会の充実",
    "やまがたの農業を支える人材の育成と基盤形成",
    "収益性の高い農業の展開",
    "ＩｏＴなどの先端技術の活用等による産業イノベーションの創出",
    "地域産業の振興・活性化と中小企業等の成長・発展",
    "大規模災害への対応など危機管理機能の充実強化",
    "暮らしの様々なリスクへの対応力の強化",
    "暮らしや産業の発展基盤となるＩＣＴなど未来技術の早期実装",
    "国内外の活力を呼び込む多様で重層的な交通ネットワークの形成",
]

SOURCE_IDS = {
    "yamagata-pref-plan-page",
    "yamagata-pref-late-implementation-plan",
    "yamagata-pref-plan-long-term-summary",
    "yamagata-pref-plan-progress-evaluation-fy2025",
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
        assert project["fiscal_year"] == 2025
        assert project["review_status"] == "reviewed"
        # Stage 3 (governor's promises) is not registered yet.
        assert project["related_promise_ids"] == []
        # The parent policy is the plan's policy pillar (政策の柱).
        assert project["parent_policy"]
        # The plan names no responsible department per policy.
        assert project["responsible_department"] is None
        assert len(project["kpis"]) == EXPECTED_KPI_COUNTS[project["id"]]
        # No per-indicator actuals are published for the late plan.
        for kpi in project["kpis"]:
            assert kpi["actual"] is None
            assert kpi["assessment"] == "not_assessable"


def test_selection_catalog_covers_population() -> None:
    catalog = _load(
        ROOT / "data" / "catalog" / "yamagata_prefecture_priority_project_selection.json"
    )
    assert catalog["issue"] == 1024
    assert catalog["municipality_id"] == MID
    # The plan booklet lists 22 policies; 28 is the count of target
    # indicators, not of policies (stage-1 candidate corrected).
    assert catalog["population"]["project_count"] == 22
    assert catalog["population"]["fiscal_year"] == 2025
    assert "22件" in catalog["population"]["description"]
    assert "28" in catalog["population"]["description"]
    numbers = [s["area_number"] for s in catalog["selections"]]
    assert numbers == [1, 2, 5, 6, 9, 10, 12, 13, 18, 19]
    titles = [s["official_title"] for s in catalog["selections"]]
    assert titles == EXPECTED_TITLES
    assert len(catalog["selection_rule"]["pillars"]) == 5
    projects = _load(BASE / "projects.json")
    assert {s["project_id"] for s in catalog["selections"]} == {p["id"] for p in projects}
    assert {s["series_id"] for s in catalog["selections"]} == {p["series_id"] for p in projects}


def test_amounts_and_official_evaluation_absent() -> None:
    projects = _load(BASE / "projects.json")
    for project in projects:
        # The prefecture publishes progress only as aggregate category
        # counts across all 28 target indicators, not per policy.
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
    assert len(kpis) == 13
    projects = _load(BASE / "projects.json")
    assert {k["project_id"] for k in kpis} == {p["id"] for p in projects}
    # Embedded project KPIs mirror the detailed records one to one.
    detailed = {(k["project_id"], k["name"]) for k in kpis}
    embedded = {(p["id"], k["name"]) for p in projects for k in p["kpis"]}
    assert detailed == embedded
    not_published = {
        PREFIX + "lifelong-learning-kpi-adult-learning-participation",
        PREFIX + "future-technology-implementation-kpi-digital-service-convenience",
    }
    for kpi in kpis:
        assert kpi["actuals"] == []
        assert kpi["assessment"] == "not_assessable"
        assert kpi["target"]["status"] == "available"
        assert kpi["target"]["value"] is not None
        assert kpi["target"]["period"] == "令和11年度"
        assert "not_assessable" in kpi["definition"]
        if kpi["id"] in not_published:
            # New indicators: the plan shows "―" for the current value.
            assert kpi["baseline"]["status"] == "not_published"
            assert kpi["baseline"]["value"] is None
        else:
            assert kpi["baseline"]["status"] == "available"
            assert kpi["baseline"]["value"] is not None


def test_spot_values_match_plan_indicator_list() -> None:
    kpis = {k["id"]: k for k in _load(BASE / "project_kpis.json")}
    subjects = kpis[PREFIX + "school-education-kpi-academic-achievement-subjects"]
    assert subjects["baseline"]["value"] == "4科目中0科目"
    assert subjects["baseline"]["period"] == "令和6年度"
    assert subjects["target"]["value"] == "全科目"
    proactive = kpis[PREFIX + "school-education-kpi-proactive-learning-students"]
    assert proactive["baseline"]["value"] == "小6：81.5％、中3：82.6％"
    assert proactive["target"]["value"] == "小6：84.0％、中3：85.1％"
    learning = kpis[PREFIX + "lifelong-learning-kpi-adult-learning-participation"]
    assert learning["baseline"]["value"] is None
    assert learning["target"]["value"] == 80
    farmers = kpis[PREFIX + "agricultural-workforce-foundation-kpi-new-farmers-tohoku-rank"]
    assert farmers["baseline"]["value"] == "東北1位"
    assert farmers["target"]["value"] == "東北1位"
    assert farmers["direction"] == "maintain"
    income = kpis[PREFIX + "profitable-agriculture-kpi-farm-management-income"]
    assert income["baseline"]["value"] == 338
    assert income["baseline"]["period"] == "令和2～5年平均"
    assert income["target"]["value"] == 550
    per_worker = kpis[PREFIX + "industrial-innovation-iot-kpi-manufacturing-value-added-per-worker"]
    assert per_worker["baseline"]["value"] == 1163
    assert per_worker["baseline"]["period"] == "令和4年"
    assert per_worker["target"]["value"] == 1280
    value_added = kpis[PREFIX + "regional-industry-sme-growth-kpi-manufacturing-value-added"]
    assert value_added["baseline"]["value"] == 11431
    assert value_added["target"]["value"] == 12500
    storm = kpis[PREFIX + "crisis-management-kpi-storm-flood-deaths"]
    assert storm["baseline"]["value"] == 0
    assert storm["target"]["value"] == 0
    assert storm["direction"] == "maintain"
    snow = kpis[PREFIX + "crisis-management-kpi-snow-deaths"]
    assert snow["baseline"]["value"] == 1
    assert snow["baseline"]["period"] == "令和5年度"
    assert snow["target"]["value"] == 0
    assert snow["direction"] == "decrease"
    offenses = kpis[PREFIX + "everyday-risk-resilience-kpi-penal-code-offenses"]
    assert offenses["baseline"]["value"] == 3052
    assert offenses["target"]["value"] == "3,052件未満"
    traffic = kpis[PREFIX + "everyday-risk-resilience-kpi-traffic-deaths"]
    assert traffic["baseline"]["value"] == 24
    assert traffic["target"]["value"] == "24人以下"
    digital = kpis[PREFIX + "future-technology-implementation-kpi-digital-service-convenience"]
    assert digital["baseline"]["value"] is None
    assert digital["baseline"]["status"] == "not_published"
    assert digital["target"]["value"] == "上昇"
    passengers = kpis[PREFIX + "transport-network-kpi-public-transport-passengers"]
    assert passengers["baseline"]["value"] == 35361
    assert passengers["baseline"]["period"] == "令和4年度"
    assert passengers["target"]["value"] == 45700


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
        # The correction of the stage-1 candidate count (28 indicators
        # vs 22 policies) is recorded in every packet.
        unit_claim = next(c for c in packet["claims"] if c["field"] == "registration_unit")
        assert "22件" in unit_claim["review_note"]


def test_project_sources_catalog() -> None:
    catalog = _load(ROOT / "data" / "catalog" / "yamagata_prefecture_project_sources.json")
    jsonschema.validate(catalog, _schema("source_catalog.schema.json"))
    ids = {r["id"] for r in catalog["records"]}
    assert ids == SOURCE_IDS
    for record in catalog["records"]:
        assert record["municipality_key"] == "yamagata-prefecture"
    # Every source referenced by the reviewed data exists in the catalog.
    projects = _load(BASE / "projects.json")
    kpis = _load(BASE / "project_kpis.json")
    referenced = {s for p in projects for s in p["sources"]}
    referenced |= {s for k in kpis for s in k["sources"]}
    assert referenced <= ids


def test_web_registry_wiring() -> None:
    registry = (ROOT / "apps" / "web" / "lib" / "projectRegistry.ts").read_text(encoding="utf-8")
    assert '"yamagata-prefecture"' in registry
    assert "yamagata_prefecture_project_sources.json" in registry
    assert "yamagata_prefecture_priority_project_selection.json" in registry
    assert "yamagata-prefecture/projects.json" in registry
    assert "yamagata-prefecture/project_kpis.json" in registry
    assert "yamagata-prefecture/project_evidence_packets.json" in registry
