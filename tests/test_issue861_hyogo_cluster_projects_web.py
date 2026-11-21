"""Issue #861: Reviewed Hyogo/Kobe stage-two Web integration and scoped copy."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "apps" / "web"
REGISTRY = (WEB / "lib" / "projectRegistry.ts").read_text(encoding="utf-8")
INDEX = (WEB / "app" / "projects" / "page.tsx").read_text(encoding="utf-8")
DISCOVERY = (WEB / "lib" / "municipalityDiscovery.ts").read_text(encoding="utf-8")
GENERIC = (WEB / "app" / "municipalities" / "[slug]" / "page.tsx").read_text(encoding="utf-8")
DETAIL = (
    WEB / "app" / "projects" / "[municipality]" / "[series]" / "page.tsx"
).read_text(encoding="utf-8")
EXPORT = (ROOT / "scripts" / "validate_static_export.py").read_text(encoding="utf-8")


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_reviewed_selection_matches_registered_series_and_sources():
    cases = (
        ("hyogo-prefecture", "jp-local-280003",
         "hyogo_priority_project_selection.json", "hyogo_project_sources.json", 2025),
        ("kobe-city", "jp-local-281000",
         "kobe_city_priority_project_selection.json", "kobe_city_project_sources.json", 2026),
    )
    for slug, municipality_id, selection_name, sources_name, year in cases:
        base = f"data/reviewed/{slug}"
        municipality = load(f"{base}/municipality.json")
        projects = load(f"{base}/projects.json")
        packets = load(f"{base}/project_evidence_packets.json")
        selection = load(f"data/catalog/{selection_name}")
        sources = load(f"data/catalog/{sources_name}")
        source_ids = {source["id"] for source in sources["records"]}
        assert municipality["id"] == municipality_id
        assert municipality["data_status"] == "reviewed"
        assert len(projects) == len(selection["selections"]) == len(packets) == 10
        assert len({project["series_id"] for project in projects}) == 10
        assert load(f"{base}/project_kpis.json") == []
        assert {packet["subject_id"] for packet in packets} == {
            project["id"] for project in projects
        }
        project_by_id = {project["id"]: project for project in projects}
        for selected in selection["selections"]:
            actual = project_by_id[selected["project_id"]]
            assert (selected["series_id"], selected["official_title"]) == (
                actual["series_id"], actual["official_title"]
            )
        for project in projects:
            assert project["municipality_id"] == municipality_id
            assert project["fiscal_year"] == year
            assert project["review_status"] == "reviewed"
            assert project["official_evaluation"] is None
            assert project["kpis"] == []
            assert set(project["sources"]) <= source_ids
            assert len(project["budget_records"]) == 1
            assert project["budget_records"][0]["amount_yen"] is None


def test_registry_and_detail_routes_preserve_reviewed_scope():
    for slug, prefix, name in (
        ("hyogo-prefecture", "hyogo", "兵庫県"),
        ("kobe-city", "kobe", "神戸市"),
    ):
        assert f'"{slug}": {{ name: "{name}"' in REGISTRY
        for suffix in ("Projects", "Kpis", "Evidence", "ProjectSources", "Selection"):
            assert f"{prefix}{suffix}" in REGISTRY
        assert f'projectRegistry["{slug}"].projects.some' in DISCOVERY
    assert 'Object.entries(projectRegistry).flatMap' in DETAIL
    assert 'id={key}' in INDEX
    assert "area.name}｜登録事業" in INDEX
    assert "27自治体の Reviewed 事業レコード" in INDEX
    assert "projectHref={isProjectArea(slug)" in GENERIC


def test_two_units_and_missing_values_are_not_misattributed():
    hyogo = load("data/catalog/hyogo_priority_project_selection.json")
    kobe = load("data/catalog/kobe_city_priority_project_selection.json")
    assert hyogo["population"]["project_count"] == 66
    assert len(hyogo["selection_rule"]["pillars"]) == 3
    assert {entry["direction_number"] for entry in hyogo["selections"]} == set(range(1, 9))
    population = kobe["population"]
    assert (population["direction_count"], population["policy_count"],
            population["measure_count"], population["unique_measure_count"],
            population["kpi_count"]) == (3, 14, 80, 62, 21)
    assert len(kobe["selection_rule"]["pillars"]) == 3
    for phrase in (
        "登録単位：取組方針項目（10系列）",
        "取組方針66項目", "固有64項目", "187指標",
        "登録単位：基本政策（10系列）", "基本政策14件",
        "主な施策80件", "方向性単位のKPI21件", "Well-Being指標",
        "未公表・未登録", "金額未登録は0円を意味しません",
    ):
        assert phrase in INDEX
    assert 'key === "hyogo-prefecture"' in INDEX
    assert 'key === "kobe-city"' in INDEX
    assert "area.selection.rule" in INDEX


def test_discovery_gates_require_matching_reviewed_municipalities():
    # Stage 3/4 Reviewed terms and assembly records are now available (Issue #870).
    # Their gates must remain scoped to the exact Reviewed municipality identity.
    for source, slug in (
        ("hyogoPrefectureMunicipality", "hyogo-prefecture"),
        ("kobeCityMunicipality", "kobe-city"),
    ):
        assert f"officialCode === {source}.official_code" in DISCOVERY
        assert f'{source}.data_status === "reviewed"' in DISCOVERY
        assert f'projectRegistry["{slug}"].projects.some' in DISCOVERY
        assert f"const municipalityId = {source}.id" in DISCOVERY
        assert "project.municipality_id === municipalityId" in DISCOVERY
        assert f'const entry = assemblies["{slug}"]' in DISCOVERY
        assert 'entry.assembly.id.startsWith(municipalityId + "-assembly-")' in DISCOVERY
    assert 'promises: hasReviewedExecutivePromises(municipalityId)' in DISCOVERY
    assert 'assembly: hasAssembly, projects: hasProjects' in DISCOVERY
    assert 'key: "hyogo-prefecture", finance: hasFinance' in DISCOVERY
    assert 'key: "kobe-city", finance: loadGenericCityFinance("kobe-city") !== null' in DISCOVERY

def test_export_validates_each_municipality_section_and_all_detail_routes():
    assert "def validate_hyogo_cluster_data_facts()" in EXPORT
    assert "def validate_hyogo_cluster_export()" in EXPORT
    assert "def hyogo_cluster_project_detail_files()" in EXPORT
    assert "validate_hyogo_cluster_data_facts()" in EXPORT
    assert "validate_hyogo_cluster_export()" in EXPORT
    assert "hyogo_cluster_project_detail_files()" in EXPORT
    assert "section = re.search(" in EXPORT
    assert 'rf\'<section\\b(?=[^>]*\\bid="{re.escape(slug)}")' in EXPORT
    assert 'project["official_title"] not in content' in EXPORT
    assert "27自治体の Reviewed 事業レコード" in EXPORT
