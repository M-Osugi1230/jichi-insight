"""Issue #1080: Aomori Prefecture stage-2 priority projects.

Registration unit: the 26 policies of the Aomori Prefecture Basic Plan
"A Bridge to the Aomori New Era" (青森県基本計画「青森新時代」への架け橋,
adopted December 2023 after an assembly vote on 2023-12-08, plan period
FY2024-FY2028). The stage-0 assumption of 26 policies was confirmed
against the plan's own published structure (7 policy themes carrying
4/4/3/5/4/3/3 policies, and 75 measures in total). KPIs are the
observation indicators published per measure in the Policy Check
Report 2026 (政策点検レポート2026, published August 2026), observation
indicator list (pp.179-203), registered under the policy they belong
to: 279 records, with multi-series indicators split per series and
indicators re-listed under another policy registered there as well.
The prefecture publishes per-measure self-evaluation symbols
(◎/〇/△/－) only in the measure sheets; this registration transcribes
the published indicator list and does not convert those symbols, so
every assessment is not_assessable. No per-policy amounts or rating
labels are published, so budget amounts and official_evaluation stay
null with the reason recorded.
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "reviewed" / "aomori-prefecture"
MID = "jp-local-020001"
PREFIX = "jp-local-020001-project-2025-"

EXPECTED_TITLES = [
    "豊かさを実感できる力強い農林水産業の実現",
    "地域経済の成長を支える県内産業の競争力強化",
    "若者を惹きつけるしごとづくり",
    "産業を支えるDXの推進",
    "県民一人ひとりの健康づくりの推進",
    "がんの克服をめざす体制づくり",
    "持続可能な地域医療サービスの整備",
    "高齢者や障がい者が安心して暮らす共生社会の実現",
    "希望と喜びを持って子育てできる環境づくり",
    "あおもりの未来をつくるこどもたちのための学校教育改革",
    "こども・若者に届く包括的な支援の充実・強化",
    "再生可能エネルギーとの共生と環境配慮型ビジネスの推進",
    "カーボンニュートラルに向けた脱炭素社会の実現",
    "資源効率の高い循環型社会の実現",
    "豊かな自然環境の継承",
    "原子力施設の安全確保対策と原子力防災対策の充実",
    "国内外とつながる観光の推進",
    "輸出・海外ビジネスの拡大と物流の確保",
    "国際交流の推進",
    "暮らしと交流を支える交通ネットワークづくり",
    "元気な地域づくり・人づくり",
    "安心で快適な生活基盤づくり",
    "文化・スポーツの振興",
    "安全・安心な県土づくりを推進する社会基盤の整備",
    "産業・交流を支える社会基盤の整備",
    "防災・減災の推進や危機管理機能の向上",
]

EXPECTED_KPI_COUNTS = {
    PREFIX + "agriculture-strength": 20,
    PREFIX + "industry-competitiveness": 12,
    PREFIX + "youth-jobs": 9,
    PREFIX + "industry-dx": 6,
    PREFIX + "health-promotion": 9,
    PREFIX + "cancer-care": 18,
    PREFIX + "regional-medical-care": 8,
    PREFIX + "inclusive-society": 9,
    PREFIX + "childrearing-environment": 8,
    PREFIX + "school-education-reform": 31,
    PREFIX + "children-youth-support": 7,
    PREFIX + "renewable-energy-coexistence": 6,
    PREFIX + "carbon-neutral": 5,
    PREFIX + "circular-society": 9,
    PREFIX + "natural-environment": 11,
    PREFIX + "nuclear-safety": 6,
    PREFIX + "tourism-promotion": 14,
    PREFIX + "exports-logistics": 9,
    PREFIX + "international-exchange": 5,
    PREFIX + "transport-network": 10,
    PREFIX + "community-development": 17,
    PREFIX + "safe-living-infrastructure": 16,
    PREFIX + "culture-sports": 9,
    PREFIX + "safe-land-infrastructure": 8,
    PREFIX + "industry-exchange-infrastructure": 10,
    PREFIX + "disaster-prevention-crisis": 7,
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
    assert len(projects) == 26
    assert [p["official_title"] for p in projects] == EXPECTED_TITLES
    for project in projects:
        assert project["municipality_id"] == MID
        assert project["fiscal_year"] == 2025
        assert project["review_status"] == "reviewed"
        # Stage 3 has not registered the governor's promises yet.
        assert project["related_promise_ids"] == []
        # The parent policy is the plan's policy theme (政策テーマ).
        assert project["parent_policy"].startswith("政策テーマ「")
        # The plan names no responsible department per policy.
        assert project["responsible_department"] is None
        # target_population is a required key; the plan publishes no
        # per-policy target population, so it stays null.
        assert "target_population" in project
        assert project["target_population"] is None
        assert len(project["kpis"]) == EXPECTED_KPI_COUNTS[project["id"]]
        for kpi in project["kpis"]:
            # The prefecture's self-evaluation symbols are not
            # converted in this registration.
            assert kpi["assessment"] == "not_assessable"


def test_selection_catalog_covers_population() -> None:
    catalog = _load(
        ROOT / "data" / "catalog" / "aomori_prefecture_priority_project_selection.json"
    )
    assert catalog["issue"] == 1080
    assert catalog["municipality_id"] == MID
    assert catalog["population"]["project_count"] == 26
    assert catalog["population"]["fiscal_year"] == 2025
    numbers = [s["area_number"] for s in catalog["selections"]]
    assert numbers == list(range(1, 27))
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
        # The prefecture publishes per-measure narrative check results
        # but no per-policy rating label, so no rating is registered.
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
    assert len(kpis) == 279
    projects = _load(BASE / "projects.json")
    assert {k["project_id"] for k in kpis} == {p["id"] for p in projects}
    # Embedded project KPIs mirror the detailed records one to one.
    detailed = {(k["project_id"], k["name"]) for k in kpis}
    embedded = {(p["id"], k["name"]) for p in projects for k in p["kpis"]}
    assert detailed == embedded
    for kpi in kpis:
        assert kpi["assessment"] == "not_assessable"
        assert kpi["baseline"]["status"] == "available"
        assert kpi["baseline"]["value"] is not None
        # Every actual is a published value from the report's list.
        for actual in kpi["actuals"]:
            assert actual["status"] == "available"
            assert actual["value"] is not None
        # The non-conversion of the prefecture's self-evaluation
        # symbols is documented in every definition.
        assert "換算は行わない" in kpi["definition"]
        if kpi["target"]["value"] is None:
            assert kpi["target"]["status"] == "not_applicable"


def test_spot_values_match_policy_check_report() -> None:
    kpis = {k["id"]: k for k in _load(BASE / "project_kpis.json")}
    retail = kpis[PREFIX + "agriculture-strength-kpi-retail-distribution-sales"]
    assert retail["baseline"]["value"] == 291
    assert retail["baseline"]["period"] == "令和5年度"
    assert retail["actuals"][-1]["value"] == 226
    assert retail["actuals"][-1]["period"] == "令和6年度"
    assert retail["target"]["value"] == 300
    assert retail["target"]["period"] == "令和10年度"
    # Cross-checked against the measure sheet because the indicator
    # list's baseline/current layout is hard to read.
    users = kpis[PREFIX + "youth-jobs-kpi-startup-support-new-users"]
    assert users["baseline"]["value"] == 625
    assert users["baseline"]["period"] == "令和元年度〜令和5年度平均"
    assert users["actuals"][-1]["value"] == 705
    assert users["target"]["value"] == 737
    ghg = kpis[PREFIX + "carbon-neutral-kpi-ghg-emissions"]
    assert ghg["baseline"]["value"] == 17517
    assert ghg["baseline"]["period"] == "平成25年度"
    assert ghg["actuals"][-1]["value"] == 12001
    assert ghg["target"]["value"] == 8581
    assert ghg["target"]["period"] == "令和12年度"
    # The measure sheet gives the current year as FY2024, not the
    # FY2023 printed in the indicator list.
    sos = kpis[PREFIX + "health-promotion-kpi-sos-education-rate-elementary"]
    assert sos["actuals"][-1]["value"] == 73
    assert sos["actuals"][-1]["period"] == "令和6年度"
    # The age split sums to the published totals (1,768 / 1,768 /
    # 1,622), so the under-65 target of 596 stands as printed.
    psych = kpis[
        PREFIX + "inclusive-society-kpi-long-term-psychiatric-inpatients-non-elderly"
    ]
    assert psych["baseline"]["value"] == 579
    assert psych["target"]["value"] == 596
    # A qualitative target stays non-numeric.
    fill = kpis[PREFIX + "industry-competitiveness-kpi-job-fill-rate-agriculture"]
    assert fill["target"]["value"] is None
    assert fill["target"]["status"] == "not_applicable"
    # A range target (40%-60%) stays non-numeric with direction range.
    women = kpis[PREFIX + "community-development-kpi-women-council-members-rate"]
    assert women["direction"] == "range"
    assert women["target"]["value"] is None
    # Indicators re-listed under another policy are registered there.
    assert (
        PREFIX + "childrearing-environment-kpi-male-childcare-leave-rate" in kpis
    )
    assert PREFIX + "community-development-kpi-male-childcare-leave-rate" in kpis
    assert PREFIX + "exports-logistics-kpi-hachinohe-port-container-volume" in kpis
    assert (
        PREFIX
        + "industry-exchange-infrastructure-kpi-hachinohe-port-container-volume"
        in kpis
    )


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
    catalog = _load(ROOT / "data" / "catalog" / "aomori_prefecture_project_sources.json")
    jsonschema.validate(catalog, _schema("source_catalog.schema.json"))
    ids = {r["id"] for r in catalog["records"]}
    assert len(ids) == 6
    assert {
        "aomori-pref-plan-page",
        "aomori-pref-plan-overview",
        "aomori-pref-plan-chapter3",
        "aomori-pref-policy-check-2026-page",
        "aomori-pref-policy-check-2026-report",
        "aomori-pref-budget-fy2026-theme-projects",
    } <= ids
    assert all(r["municipality_key"] == "aomori-prefecture" for r in catalog["records"])
    projects = _load(BASE / "projects.json")
    for project in projects:
        assert set(project["sources"]) <= ids
    kpis = _load(BASE / "project_kpis.json")
    for kpi in kpis:
        assert set(kpi["sources"]) <= ids
