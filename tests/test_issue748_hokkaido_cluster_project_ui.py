"""Issue #748: Hokkaido stage-two project Web pages and disclosure boundaries."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
WEB = ROOT / "apps/web"
REGISTRY = (WEB / "lib/projectRegistry.ts").read_text(encoding="utf-8")
REVIEW = (WEB / "components/ProjectReview.tsx").read_text(encoding="utf-8")
INDEX = (WEB / "app/projects/page.tsx").read_text(encoding="utf-8")
DETAIL = (WEB / "app/projects/[municipality]/[series]/page.tsx").read_text(
    encoding="utf-8"
)
HOKKAIDO = (WEB / "app/municipalities/hokkaido-prefecture/page.tsx").read_text(
    encoding="utf-8"
)
DISCOVERY = (WEB / "lib/municipalityDiscovery.ts").read_text(encoding="utf-8")
GENERIC = (WEB / "app/municipalities/[slug]/page.tsx").read_text(
    encoding="utf-8"
)
EXPORT = (ROOT / "scripts/validate_static_export.py").read_text(
    encoding="utf-8"
)


def load_json(path):
    return json.loads((DATA / path).read_text(encoding="utf-8"))


def test_cluster_project_series_reviewed_and_evidence_registered():
    cases = (
        ("hokkaido-prefecture", "010006", "hokkaido_project_sources.json", 21),
        ("sapporo-city", "011002", "sapporo_city_project_sources.json", 10),
        ("asahikawa-city", "012041", "asahikawa_project_sources.json", 0),
    )
    for slug, code, catalog, expected_kpis in cases:
        root = f"reviewed/{slug}"
        projects = load_json(f"{root}/projects.json")
        kpis = load_json(f"{root}/project_kpis.json")
        evidence = load_json(f"{root}/project_evidence_packets.json")
        sources = {
            source["id"] for source in load_json(f"catalog/{catalog}")["records"]
        }
        assert len(projects) == 10
        assert len({project["series_id"] for project in projects}) == 10
        assert len(evidence) == 10
        assert len(kpis) == expected_kpis
        assert all(
            project["municipality_id"] == f"jp-local-{code}"
            and project["review_status"] == "reviewed"
            and project["sources"]
            and all(source_id in sources for source_id in project["sources"])
            for project in projects
        )
        assert {packet["subject_id"] for packet in evidence} == {
            project["id"] for project in projects
        }
        assert all(packet["review_status"] == "reviewed" for packet in evidence)
        assert all(kpi["review_status"] == "reviewed" for kpi in kpis)


def test_registry_preserves_six_existing_areas_and_adds_three():
    for slug in (
        "fukuoka-prefecture",
        "fukuoka-city",
        "kitakyushu-city",
        "aichi-prefecture",
        "nagoya-city",
        "toyota-city",
        "hokkaido-prefecture",
        "sapporo-city",
        "asahikawa-city",
    ):
        assert f'"{slug}":' in REGISTRY
    for name in (
        "hokkaidoProjects",
        "sapporoProjects",
        "asahikawaProjects",
        "hokkaidoKpis",
        "sapporoKpis",
        "asahikawaKpis",
        "hokkaidoProjectSources",
        "sapporoProjectSources",
        "asahikawaProjectSources",
    ):
        assert name in REGISTRY
    assert "Object.entries(projectRegistry).flatMap" in DETAIL
    assert 'id={key}' in INDEX
    assert "data-filter-entry" in INDEX
    assert "12自治体の Reviewed 事業レコード" in INDEX
    assert "area.name" in INDEX


def test_hokkaido_budget_is_not_a_settlement_or_independent_rating():
    projects = load_json("reviewed/hokkaido-prefecture/projects.json")
    assert all(project["official_evaluation"] is not None for project in projects)
    assert all(
        budget["kind"] == "initial_budget"
        for project in projects
        for budget in project["budget_records"]
    )
    assert "基本評価調書の「予算額」" in REVIEW
    assert "当初予算ベース" in REVIEW
    assert "決算額ではありません" in REVIEW
    assert "北海道の一次政策評価・総合判定" in REVIEW
    assert "独自評価や順位付けは行いません" in INDEX
    assert 'id="priority-projects"' in HOKKAIDO
    assert 'projectHref="#priority-projects"' in HOKKAIDO
    assert "reviewedProjects.map" in HOKKAIDO
    assert "project.official_evaluation?.rating" in HOKKAIDO
    assert "projects.kpis.filter" in HOKKAIDO
    assert "<ProjectReview" in HOKKAIDO
    assert "重点事業は段階2で登録中" not in HOKKAIDO


def test_sapporo_and_asahikawa_no_unpublished_assessment_or_inferred_rank():
    for slug in ("sapporo-city", "asahikawa-city"):
        projects = load_json(f"reviewed/{slug}/projects.json")
        assert all(p["official_evaluation"] is None for p in projects)
    assert 'area === "sapporo-city"' in REVIEW
    assert 'area === "asahikawa-city"' in REVIEW
    assert "事業単位の公式評価は公表されていません" in REVIEW
    assert 'key === "sapporo-city"' in INDEX
    assert 'key === "asahikawa-city"' in INDEX
    assert "独自の評価・順位付けをしません" in INDEX


def test_discovery_routes_to_reviewed_projects_without_opening_other_gates():
    assert 'officialCode === hokkaidoFinance.municipality.official_code' in DISCOVERY
    assert 'projectRegistry["hokkaido-prefecture"].projects.some' in DISCOVERY
    assert 'project.municipality_id === hokkaidoFinance.municipality.id' in DISCOVERY
    assert 'promises: hasPromises, assembly: false, projects: hasProjects' in DISCOVERY
    assert "isProjectArea(city.slug)" in DISCOVERY
    assert 'project.municipality_id === `jp-local-${officialCode}`' in DISCOVERY
    assert 'projectHref={isProjectArea(slug)' in GENERIC
    assert 'href: projectHref ?? "/projects"' not in DISCOVERY


def test_export_requires_cluster_pages_and_actual_budget_copy():
    assert '"projects/index.html"' in EXPORT
    assert '"municipalities/hokkaido-prefecture/index.html"' in EXPORT
    assert '"基本評価調書の「予算額」"' in EXPORT
    assert '"北海道の総合判定は道の一次政策評価の判定"' in EXPORT
    assert '"事業単位の公式評価は公表されていません"' in EXPORT
    assert "def hokkaido_cluster_project_detail_files()" in EXPORT
    assert "hokkaido_cluster_project_detail_files()" in EXPORT
