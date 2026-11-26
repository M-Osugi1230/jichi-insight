"""Issue #1022: Fukushima Prefecture stage-2 priority projects.

Registration unit: the 18 policies of the Fukushima Prefecture
Comprehensive Plan (福島県総合計画, adopted October 2021, plan period
FY2022-FY2030). The prefecture's progress management is published per
policy (政策分野別主要施策評価調書 and the policy-linked indicator list),
so the plan's policy unit and the official evaluation unit coincide and
all 18 policies are registered without sampling. KPIs are the 34
policy-linked indicators of the FY2026 progress-management material 1-3
（政策に紐付く指標一覧）, expanded to 39 records because three indicators
publish several series (healthy life expectancy by sex, physicians and
nurses prefecture-wide / Soso, produce price recovery for rice / peach /
beef). Baselines are the prefecture's published current values, targets
are the FY2030 targets, actuals are the published yearly series, and the
prefecture's judgements are converted as 達成=achieved,
達成見込み=mostly_achieved, 未達成・未達成見込み=not_achieved,
判定なし=not_assessable. No per-policy amounts or rating labels are
published, so budget amounts and official_evaluation stay null with the
reason recorded.
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "reviewed" / "fukushima-prefecture"
MID = "jp-local-070009"
PREFIX = "jp-local-070009-project-2025-"

EXPECTED_TITLES = [
    "全国に誇れる健康長寿県へ",
    "結婚・出産・子育ての希望をかなえる環境づくり",
    "「福島ならでは」の教育の充実",
    "誰もがいきいきと暮らせる県づくり",
    "福島への新しい人の流れづくり",
    "東日本大震災・原子力災害からの復興・再生",
    "災害に強く治安が確保されている安全・安心な県づくり",
    "安心の医療、介護・福祉提供体制の整備",
    "環境と調和・共生する県づくり",
    "過疎・中山間地域の持続的な発展",
    "ふれあいと親しみのある魅力あふれる県づくり",
    "地域産業の持続的発展",
    "福島イノベーション・コースト構想の推進",
    "もうかる農林水産業の実現",
    "再生可能エネルギー先駆けの地の実現",
    "魅力を最大限いかした観光・交流の促進",
    "福島の産業を支える人材の確保・育成",
    "地域を結ぶ社会基盤の整備促進",
]

EXPECTED_KPI_COUNTS = {
    PREFIX + "health-longevity": 2,
    PREFIX + "marriage-childbirth-childrearing": 1,
    PREFIX + "fukushima-education": 2,
    PREFIX + "inclusive-community-life": 1,
    PREFIX + "new-inflow-of-people": 1,
    PREFIX + "reconstruction-and-revitalization": 5,
    PREFIX + "disaster-resilience-and-safety": 2,
    PREFIX + "medical-care-welfare-system": 5,
    PREFIX + "environment-coexistence": 1,
    PREFIX + "depopulated-mountainous-areas": 1,
    PREFIX + "community-charm": 2,
    PREFIX + "regional-industry-development": 1,
    PREFIX + "innovation-coast-initiative": 4,
    PREFIX + "profitable-agriculture-forestry-fisheries": 6,
    PREFIX + "renewable-energy-frontier": 1,
    PREFIX + "tourism-and-exchange": 1,
    PREFIX + "industrial-workforce": 1,
    PREFIX + "regional-transport-infrastructure": 2,
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
    assert len(projects) == 18
    assert [p["official_title"] for p in projects] == EXPECTED_TITLES
    for project in projects:
        assert project["municipality_id"] == MID
        assert project["fiscal_year"] == 2025
        assert project["review_status"] == "reviewed"
        # Stage 3 (Issue #1034) registered the governor's promises
        # and linked them here; the exact links are pinned by
        # tests/test_issue1034_fukushima_pref_stage3.py.
        assert isinstance(project["related_promise_ids"], list)
        # The parent policy is the plan's field (分野).
        assert project["parent_policy"] in {"「ひと」分野", "「暮らし」分野", "「しごと」分野"}
        # The plan names no responsible department per policy.
        assert project["responsible_department"] is None
        assert len(project["kpis"]) == EXPECTED_KPI_COUNTS[project["id"]]
        for kpi in project["kpis"]:
            assert kpi["assessment"] in {
                "achieved", "mostly_achieved", "not_achieved", "not_assessable",
            }


def test_selection_catalog_covers_population() -> None:
    catalog = _load(
        ROOT / "data" / "catalog" / "fukushima_prefecture_priority_project_selection.json"
    )
    assert catalog["issue"] == 1022
    assert catalog["municipality_id"] == MID
    assert catalog["population"]["project_count"] == 18
    assert catalog["population"]["fiscal_year"] == 2025
    numbers = [s["area_number"] for s in catalog["selections"]]
    assert numbers == list(range(1, 19))
    titles = [s["official_title"] for s in catalog["selections"]]
    assert titles == EXPECTED_TITLES
    projects = _load(BASE / "projects.json")
    assert {s["project_id"] for s in catalog["selections"]} == {p["id"] for p in projects}
    assert {s["series_id"] for s in catalog["selections"]} == {
        p["series_id"] for p in projects
    }


def test_amounts_and_official_evaluation_absent() -> None:
    projects = _load(BASE / "projects.json")
    for project in projects:
        # The prefecture publishes narrative policy evaluations but no
        # per-policy rating label, so no rating is registered.
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
    assert len(kpis) == 39
    projects = _load(BASE / "projects.json")
    assert {k["project_id"] for k in kpis} == {p["id"] for p in projects}
    # Embedded project KPIs mirror the detailed records one to one.
    detailed = {(k["project_id"], k["name"]) for k in kpis}
    embedded = {(p["id"], k["name"]) for p in projects for k in p["kpis"]}
    assert detailed == embedded
    for kpi in kpis:
        assert kpi["baseline"]["status"] == "available"
        assert kpi["baseline"]["value"] is not None
        # Every actual is a published value from the prefecture's series.
        for actual in kpi["actuals"]:
            assert actual["status"] == "available"
            assert actual["value"] is not None
        assert "換算" in kpi["definition"]


def test_spot_values_match_progress_materials() -> None:
    kpis = {k["id"]: k for k in _load(BASE / "project_kpis.json")}
    male = kpis[PREFIX + "health-longevity-kpi-healthy-life-expectancy-male"]
    assert male["baseline"]["value"] == 71.54
    assert male["baseline"]["period"] == "平成28年度"
    assert male["target"]["value"] == 75.60
    assert male["target"]["period"] == "令和12年度"
    assert [a["value"] for a in male["actuals"]] == [72.28, 71.89]
    assert male["assessment"] == "not_achieved"
    migration = kpis[PREFIX + "new-inflow-of-people-kpi-net-migration"]
    assert migration["baseline"]["value"] == -6278
    assert migration["target"]["value"] == 0
    assert migration["actuals"][-1]["value"] == -7617
    assert migration["actuals"][-1]["period"] == "令和7年度"
    crime = kpis[PREFIX + "disaster-resilience-and-safety-kpi-crime-incidents"]
    # The crime target is qualitative (year-on-year decrease), not numeric.
    assert crime["target"]["value"] is None
    assert crime["target"]["status"] == "not_applicable"
    assert crime["actuals"][-1]["value"] == 8674
    assert crime["assessment"] == "achieved"
    physicians = kpis[PREFIX + "medical-care-welfare-system-kpi-physicians-prefecture"]
    # Biennial survey: only FY2020/FY2022/FY2024 actuals are published.
    assert [a["period"] for a in physicians["actuals"]] == [
        "令和2年度", "令和4年度", "令和6年度",
    ]
    assert physicians["actuals"][-1]["value"] == 4162
    assert physicians["target"]["value"] == 4518
    evacuees = kpis[PREFIX + "reconstruction-and-revitalization-kpi-evacuees"]
    # No prefectural judgement is published for the evacuee indicators.
    assert evacuees["assessment"] == "not_assessable"
    assert evacuees["actuals"][-1]["value"] == 23410
    shipments = kpis[
        PREFIX + "regional-industry-development-kpi-manufacturing-shipments"
    ]
    assert shipments["assessment"] == "mostly_achieved"
    assert shipments["actuals"][-1]["value"] == 56345
    tourism = kpis[PREFIX + "tourism-and-exchange-kpi-tourist-visitors"]
    assert tourism["baseline"]["value"] == 35454
    assert tourism["target"]["value"] == 68700
    assert tourism["actuals"][-1]["value"] == 57573
    renewable = kpis[PREFIX + "renewable-energy-frontier-kpi-renewable-energy-introduction"]
    assert renewable["baseline"]["value"] == 43.4
    assert renewable["target"]["value"] == 70.0
    assert renewable["assessment"] == "mostly_achieved"


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
            "review_basis",
        } <= fields
        assert all(c["decision"] == "accepted" for c in packet["claims"])
        # The review is delegated to Muse (2026-11-15), never recorded
        # as the owner's own review.
        basis = next(c for c in packet["claims"] if c["field"] == "review_basis")
        assert "所有者本人のレビューではない" in basis["statement"]
        assert packet["open_questions"]


def test_project_sources_catalog() -> None:
    catalog = _load(ROOT / "data" / "catalog" / "fukushima_prefecture_project_sources.json")
    jsonschema.validate(catalog, _schema("source_catalog.schema.json"))
    ids = {r["id"] for r in catalog["records"]}
    assert len(ids) == 24
    assert {
        "fukushima-pref-plan-page",
        "fukushima-pref-plan-chapter4-framework",
        "fukushima-pref-plan-indicator-list",
        "fukushima-pref-progress-2026-page",
        "fukushima-pref-progress-2026-evaluation-sheets",
        "fukushima-pref-progress-2026-policy-indicators",
    } <= ids
    assert all(r["municipality_key"] == "fukushima-prefecture" for r in catalog["records"])
    projects = _load(BASE / "projects.json")
    for project in projects:
        assert set(project["sources"]) <= ids
    kpis = _load(BASE / "project_kpis.json")
    for kpi in kpis:
        assert set(kpi["sources"]) <= ids
