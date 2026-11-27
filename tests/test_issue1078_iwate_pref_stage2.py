"""Issue #1078: Iwate Prefecture stage-2 priority projects.

Registration unit: the 10 policy fields (政策分野) of the Long-Term
Vision of the Iwate Prefectural Plan (いわて県民計画, 2019-2028). The
prefecture's policy evaluation measures and publishes achievement per
policy field (the FY2023 implementation report gives the per-field
distribution of the A-D grades for both the happiness-related
indicators and the implementation indicators), so the policy field is
the canonical unit (stage-1 plan_review). The population is all 10
fields; because the unit equals the population, all 10 are registered
in published order rather than selected. The Long-Term Vision names
2-4 key indicators per field (29 entries including re-listings) but
publishes no numeric targets for them; per-indicator values live only
in the full implementation reports, whose latest edition is published
through a kintone viewer that could not be machine-verified. KPIs are
therefore registered at the level actually published in a verifiable
official source: the per-field FY2023 achievement shares of the two
indicator families (20 KPIs). Field-level budget totals are not
published, so amounts stay null with the gap stated explicitly.
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "reviewed" / "iwate-prefecture"
MID = "jp-local-030007"
PREFIX = "jp-local-030007-project-2019-"

EXPECTED_TITLES = [
    "健康・余暇",
    "家族・子育て",
    "教育",
    "居住環境・コミュニティ",
    "安全",
    "仕事・収入",
    "歴史・文化",
    "自然環境",
    "社会基盤",
    "参画",
]

EXPECTED_SLUGS = [
    "health-leisure",
    "family-childrearing",
    "education",
    "living-environment-community",
    "safety",
    "work-income",
    "history-culture",
    "natural-environment",
    "social-infrastructure",
    "participation",
]

# FY2023 (Reiwa 5) implementation report summary: per-field grade
# distribution of the happiness-related indicators (A, B, C, D counts
# and evaluated total) and the A-or-B share.
EXPECTED_HAPPINESS = {
    "health-leisure": (9, 5, 0, 1, 3, 56),
    "family-childrearing": (7, 3, 1, 0, 3, 57),
    "education": (18, 6, 9, 0, 3, 83),
    "living-environment-community": (6, 4, 0, 0, 2, 67),
    "safety": (5, 2, 0, 0, 3, 40),
    "work-income": (14, 7, 5, 0, 2, 86),
    "history-culture": (3, 3, 0, 0, 0, 100),
    "natural-environment": (5, 2, 3, 0, 0, 100),
    "social-infrastructure": (5, 2, 1, 0, 2, 60),
    "participation": (7, 5, 1, 0, 1, 86),
}

# FY2023 implementation indicators: evaluated counts and the published
# A-or-B shares per field.
EXPECTED_IMPLEMENTATION = {
    "health-leisure": (62, 81),
    "family-childrearing": (47, 87),
    "education": (94, 80),
    "living-environment-community": (33, 88),
    "safety": (29, 76),
    "work-income": (99, 86),
    "history-culture": (7, 100),
    "natural-environment": (26, 92),
    "social-infrastructure": (41, 85),
    "participation": (23, 83),
}

SOURCE_IDS = {
    "iwate-pref-plan-page",
    "iwate-pref-long-term-vision-final-draft",
    "iwate-pref-fy2023-implementation-report-summary",
    "iwate-pref-fy2024-implementation-report-page",
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
    assert [p["id"] for p in projects] == [PREFIX + s for s in EXPECTED_SLUGS]
    for project in projects:
        assert project["municipality_id"] == MID
        assert project["fiscal_year"] == 2019
        assert project["review_status"] == "reviewed"
        assert project["parent_policy"] == "いわて県民計画（2019～2028）長期ビジョン"
        # Stage 3 (Issue #1086) registered the governor's promises
        # and linked them here; the exact links are pinned by
        # tests/test_issue1086_iwate_pref_stage3.py.
        assert isinstance(project["related_promise_ids"], list)
        # The plan names no responsible department per policy field.
        assert project["responsible_department"] is None
        # target_population key is mandatory (ProjectRecord type).
        assert "target_population" in project
        assert project["target_population"] is None
        assert len(project["kpis"]) == 2
        for kpi in project["kpis"]:
            assert kpi["assessment"] == "not_assessable"
            assert kpi["baseline"] is None
            assert kpi["target"] is None


def test_selection_catalog_covers_population() -> None:
    catalog = _load(
        ROOT / "data" / "catalog" / "iwate_prefecture_priority_project_selection.json"
    )
    assert catalog["issue"] == 1078
    assert catalog["municipality_id"] == MID
    assert catalog["population"]["project_count"] == 10
    assert catalog["population"]["fiscal_year"] == 2019
    numbers = [s["area_number"] for s in catalog["selections"]]
    assert numbers == list(range(1, 11))
    titles = [s["official_title"] for s in catalog["selections"]]
    assert titles == EXPECTED_TITLES
    assert catalog["selection_rule"]["pillars"] == EXPECTED_TITLES
    projects = _load(BASE / "projects.json")
    assert {s["project_id"] for s in catalog["selections"]} == {p["id"] for p in projects}
    assert {s["series_id"] for s in catalog["selections"]} == {
        p["series_id"] for p in projects
    }


def test_amounts_absent_and_evaluation_published_form() -> None:
    projects = _load(BASE / "projects.json")
    for project in projects:
        slug = project["id"].removeprefix(PREFIX)
        n, a, b, c, d, _share = EXPECTED_HAPPINESS[slug]
        assert len(project["budget_records"]) == 1
        record = project["budget_records"][0]
        assert record["kind"] == "initial_budget"
        assert record["fiscal_year"] == 2026
        assert record["amount_yen"] is None
        assert "公表していない" in record["note"]
        evaluation = project["official_evaluation"]
        assert evaluation is not None
        # The prefecture publishes no single grade per field; the
        # registered rating is the published per-field distribution.
        assert f"達成【A】{a}" in evaluation["rating"]
        assert f"概ね達成【B】{b}" in evaluation["rating"]
        assert f"やや遅れ【C】{c}" in evaluation["rating"]
        assert f"遅れ【D】{d}" in evaluation["rating"]
        assert f"評価対象{n}指標" in evaluation["rating"]
        assert "Jichi Insight独自の評価ではない" in evaluation["note"]


def test_detailed_kpis() -> None:
    kpis = _load(BASE / "project_kpis.json")
    schema = _schema("kpi.schema.json")
    for kpi in kpis:
        jsonschema.validate(kpi, schema)
    assert len(kpis) == 20
    projects = _load(BASE / "projects.json")
    assert {k["project_id"] for k in kpis} == {p["id"] for p in projects}
    # Embedded project KPIs mirror the detailed records one to one.
    detailed = {(k["project_id"], k["name"]) for k in kpis}
    embedded = {(p["id"], k["name"]) for p in projects for k in p["kpis"]}
    assert detailed == embedded
    for kpi in kpis:
        assert kpi["assessment"] == "not_assessable"
        assert kpi["baseline"]["status"] == "not_published"
        assert kpi["baseline"]["value"] is None
        assert kpi["target"]["status"] == "not_published"
        assert kpi["target"]["value"] is None
        assert len(kpi["actuals"]) == 1
        assert kpi["actuals"][0]["period"] == "2023年度"
        assert kpi["actuals"][0]["status"] == "available"
        assert set(kpi["sources"]) <= SOURCE_IDS


def test_spot_values_match_fy2023_report_summary() -> None:
    kpis = {k["id"]: k for k in _load(BASE / "project_kpis.json")}
    for slug, (_n, _a, _b, _c, _d, share) in EXPECTED_HAPPINESS.items():
        kpi = kpis[PREFIX + slug + "-kpi-happiness-indicator-achievement"]
        assert kpi["actuals"][0]["value"] == share
    for slug, (_count, share) in EXPECTED_IMPLEMENTATION.items():
        kpi = kpis[PREFIX + slug + "-kpi-implementation-indicator-achievement"]
        assert kpi["actuals"][0]["value"] == share
    # Cross-checks against the published totals: 79 happiness-related
    # indicators evaluated, 461 implementation indicators evaluated.
    assert sum(v[0] for v in EXPECTED_HAPPINESS.values()) == 79
    assert sum(v[0] for v in EXPECTED_IMPLEMENTATION.values()) == 461


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
    catalog = _load(ROOT / "data" / "catalog" / "iwate_prefecture_project_sources.json")
    jsonschema.validate(catalog, _schema("source_catalog.schema.json"))
    ids = {r["id"] for r in catalog["records"]}
    assert ids == SOURCE_IDS
    assert all(r["municipality_key"] == "iwate-prefecture" for r in catalog["records"])
    projects = _load(BASE / "projects.json")
    for project in projects:
        assert set(project["sources"]) <= ids
    kpis = _load(BASE / "project_kpis.json")
    for kpi in kpis:
        assert set(kpi["sources"]) <= ids
