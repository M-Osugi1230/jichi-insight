"""Issue #720: three-city project routing keeps financial and rating provenance."""

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
AICHI = (WEB / "app/municipalities/aichi-prefecture/page.tsx").read_text(
    encoding="utf-8"
)
GENERIC = (WEB / "app/municipalities/[slug]/page.tsx").read_text(
    encoding="utf-8"
)
DISCOVERY = (WEB / "lib/municipalityDiscovery.ts").read_text(encoding="utf-8")
PANEL = (WEB / "components/MunicipalityDiscoveryPanel.tsx").read_text(
    encoding="utf-8"
)


def read_json(relative):
    return json.loads((DATA / relative).read_text(encoding="utf-8"))


def test_registered_series_and_evidence_are_reviewed_and_linkable():
    cases = (
        ("aichi-prefecture", "230006", "aichi_project_sources.json"),
        ("nagoya-city", "231002", "nagoya_city_project_sources.json"),
        ("toyota-city", "232114", "toyota_project_sources.json"),
    )
    for slug, code, catalog in cases:
        prefix = f"reviewed/{slug}"
        projects = read_json(f"{prefix}/projects.json")
        kpis = read_json(f"{prefix}/project_kpis.json")
        evidence = read_json(f"{prefix}/project_evidence_packets.json")
        sources = {
            item["id"] for item in read_json(f"catalog/{catalog}")["records"]
        }
        assert len(projects) == 10
        assert len({record["series_id"] for record in projects}) == 10
        assert len(evidence) == 10
        assert all(
            record["review_status"] == "reviewed"
            and record["municipality_id"] == f"jp-local-{code}"
            for record in projects
        )
        assert all(
            item["review_status"] == "reviewed"
            and any(p["id"] == item["project_id"] for p in projects)
            for item in kpis
        )
        assert all(record["sources"] for record in projects)
        assert all(
            source in sources
            for record in projects
            for source in record["sources"]
        )
        assert all(
            packet["subject_id"] in {item["id"] for item in projects}
            for packet in evidence
        )


def test_project_registry_and_details_preserve_three_legacy_areas():
    assert 'export type ProjectArea = "fukuoka-prefecture"' in REGISTRY
    for slug in (
        "fukuoka-prefecture",
        "fukuoka-city",
        "kitakyushu-city",
        "aichi-prefecture",
        "nagoya-city",
        "toyota-city",
    ):
        assert f'"{slug}":' in REGISTRY
    for name in (
        "aichiProjects",
        "nagoyaProjects",
        "toyotaProjects",
        "aichiKpis",
        "nagoyaKpis",
        "toyotaKpis",
    ):
        assert name in REGISTRY
    assert "Object.entries(projectRegistry).flatMap" in DETAIL
    assert "project.review_status ===" in INDEX
    assert 'id={key}' in INDEX
    assert "data-filter-entry" in INDEX


def test_aichi_section_shows_records_and_unmodified_official_ratings():
    projects = read_json("reviewed/aichi-prefecture/projects.json")
    assert all(
        record["official_evaluation"]
        and record["official_evaluation"]["rating"].startswith(
            ("A", "B", "C", "D", "E")
        )
        for record in projects
    )
    assert 'id="priority-projects"' in AICHI
    assert "reviewedProjects.map" in AICHI
    assert "project.budget_records.map" in AICHI
    assert "project.official_evaluation?.rating" in AICHI
    assert "FY2026 当初予算額は億円単位" in AICHI
    assert "<ProjectReview" in AICHI
    assert 'projectHref="#priority-projects"' in AICHI


def test_nagoya_proposal_and_toyota_unpublished_project_ratings():
    nagoya = read_json("reviewed/nagoya-city/projects.json")
    toyota = read_json("reviewed/toyota-city/projects.json")
    assert all(
        "予定額" in record["budget_records"][0]["note"] for record in nagoya
    )
    assert all(record["official_evaluation"] is None for record in toyota)
    assert "予算案段階の予定額（成立後の事業別予算額ではありません）" in REVIEW
    assert "FY2026 当初予算・億円単位で公表された概数" in REVIEW
    assert "事業単位の公式評価は公表されていません" in REVIEW
    assert "目標・施策単位の進捗や叙述" in REVIEW
    assert "project.official_evaluation?.rating" in INDEX


def test_eligibility_gate_is_reviewed_and_not_based_on_city_name_alone():
    assert "isProjectArea(city.slug)" in DISCOVERY
    assert 'project.review_status === "reviewed"' in DISCOVERY
    assert "project.municipality_id ===" in DISCOVERY
    assert "projects: hasProjects" in DISCOVERY
    assert "projects: true" in DISCOVERY
    assert "projects: false" in DISCOVERY
    assert "promises: false, assembly: false" in DISCOVERY
    assert "projectHref={isProjectArea(slug)" in GENERIC
    assert 'projectHref ?? "/projects"' in PANEL
