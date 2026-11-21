"""Issue #887:宮城県・仙台市のReviewed Web 仕上げの事実検証."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "apps" / "web"
REGISTRY = (WEB / "lib" / "projectRegistry.ts").read_text(encoding="utf-8")
ASSEMBLIES = (WEB / "lib" / "assemblyRegistry.ts").read_text(encoding="utf-8")
PROJECT_INDEX = (WEB / "app" / "projects" / "page.tsx").read_text(encoding="utf-8")
ASSEMBLY_INDEX = (WEB / "app" / "assemblies" / "page.tsx").read_text(encoding="utf-8")
ASSEMBLY_DETAIL = (WEB / "app" / "assemblies" / "[slug]" / "page.tsx").read_text(encoding="utf-8")
PREF_PAGE = (
    WEB / "app" / "municipalities" / "miyagi-prefecture" / "page.tsx"
).read_text(encoding="utf-8")
CITY_PAGE = (
    WEB / "app" / "municipalities" / "sendai-city" / "page.tsx"
).read_text(encoding="utf-8")
DISCOVERY = (WEB / "lib" / "municipalityDiscovery.ts").read_text(encoding="utf-8")
CATALOG = (WEB / "lib" / "catalog.ts").read_text(encoding="utf-8")
EXPORT = (ROOT / "scripts" / "validate_static_export.py").read_text(encoding="utf-8")


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_reviewed_projects_and_display_units():
    for slug, name, _prefix in (
        ("miyagi-prefecture", "宮城県", "miyagi"),
        ("sendai-city", "仙台市", "sendai"),
    ):
        projects = load(f"data/reviewed/{slug}/projects.json")
        catalog_name = "miyagi" if slug == "miyagi-prefecture" else "sendai_city"
        source = load(f"data/catalog/{catalog_name}_priority_project_selection.json")
        assert len(projects) == 10
        assert len({p["series_id"] for p in projects}) == 10
        assert len(source["selections"]) == 10
        by_id = {project["id"]: project for project in projects}
        for item in source["selections"]:
            assert (
                by_id[item["project_id"]]["series_id"],
                by_id[item["project_id"]]["official_title"],
            ) == (item["series_id"], item["official_title"])
        assert all(p["review_status"] == "reviewed" for p in projects)
        assert all(
            p["official_evaluation"] and p["official_evaluation"]["rating"] for p in projects
        )
        assert f'"{slug}": {{ name: "{name}"' in REGISTRY
        assert f'key === "{slug}"' in PROJECT_INDEX
        assert f'projectRegistry["{slug}"].projects.some' in DISCOVERY

    miyagi = load("data/reviewed/miyagi-prefecture/project_kpis.json")
    assert len(miyagi) == 85
    assert "登録単位：施策（10系列）" in PROJECT_INDEX
    assert "登録単位：事業（10系列）" in PROJECT_INDEX
    assert "仙台市の公式自己評価" in CITY_PAGE
    assert "施策単位の重点事業10系列" in PREF_PAGE
    assert "27自治体の Reviewed 事業レコード" in PROJECT_INDEX
    assert "事業単位の当初予算額：未登録（0円ではありません）" in CITY_PAGE


def test_registered_budget_values_and_plan_names():
    pref = load("data/reviewed/miyagi-prefecture/fiscal_records.json")
    city = load("data/reviewed/sendai-city/fiscal_records.json")
    def budget(records):
        return {row["metric"]: row["amount_yen"] for row in records
                if row["stage"] == "initial_budget" and row["fiscal_year"] == 2026}
    assert budget(pref)["total_revenue"] == 1_095_923_909_000
    assert budget(pref)["local_tax"] == 344_600_000_000
    assert budget(city)["total_revenue"] == 730_647_000_000
    assert budget(city)["local_tax"] == 254_846_000_000
    assert any("2026年3月18日" in row["note"] for row in pref)
    assert any("2026年3月12日" in row["note"] for row in city)
    assert "新・宮城の将来ビジョン" in PREF_PAGE
    assert "仙台市基本計画2021-2030" in CITY_PAGE
    for slug in ("miyagi-prefecture", "sendai-city"):
        settlements = load(f"data/reviewed/{slug}/settlement_records.json")
        assert len(settlements) == 51
        assert {row["fiscal_year"] for row in settlements} == {2022, 2023, 2024}


def test_governor_and_mayor_election_votes_terms_promises():
    terms = load("data/entities/executives/executive_terms.json")
    promises = load("data/entities/executives/promises.json")
    evidence = load("data/entities/executives/evidence_packets.json")
    for municipality_id, office, name, start, end, vote, page in (
        (
            "jp-local-040002", "governor", "村井 嘉浩",
            "2025-11-21", "2029-11-20", "340,190票", PREF_PAGE,
        ),
        (
            "jp-local-041009", "mayor", "郡 和子",
            "2025-08-22", "2029-08-21", "204,844票", CITY_PAGE,
        ),
    ):
        term = next(
            row
            for row in terms
            if row["municipality_id"] == municipality_id
            and row["office"] == office
            and row["status"] == "current"
        )
        assert (term["person_name"], term["term_start"], term["term_end"]) == (name, start, end)
        assert len([
            p
            for p in promises
            if p["executive_term_id"] == term["id"] and p["review_status"] == "reviewed"
        ]) == 4
        packet = next(row for row in evidence if row["subject_id"] == term["id"])
        assert vote in next(
            c["statement"] for c in packet["claims"] if c["field"] == "election_date"
        )
        assert vote in page
    assert "governorPromises.length" in PREF_PAGE
    assert "mayorPromises.length" in CITY_PAGE
    assert 'href="/promises#miyagi-prefecture"' in PREF_PAGE
    assert 'href="/promises#sendai-city"' in CITY_PAGE


def test_assemblies_keep_actual_voting_publication_granularity():
    assert '"miyagi-prefecture": registry(' in ASSEMBLIES
    assert '"sendai-city": registry(' in ASSEMBLIES
    assert '"miyagi-prefecture", "sendai-city"' in ASSEMBLIES
    assert "27議会" in ASSEMBLY_INDEX
    assert "27議会の一覧に戻る" in ASSEMBLY_DETAIL
    assert "本会議の表決そのものの事後記録" in PREF_PAGE
    assert "採決に先立って表明された会派態度の集約ではありません" in PREF_PAGE
    assert "宮城県議会" in PREF_PAGE
    assert "仙台市議会" in CITY_PAGE
    assert "会派別賛否" in CITY_PAGE
    assert "議員個人別の賛否は公表されておらず" in CITY_PAGE
    assert "member_votes" in ASSEMBLIES
    assert len(load("data/reviewed/miyagi-prefecture/assembly/votes.json")) == 28
    assert load("data/reviewed/miyagi-prefecture/assembly/faction_votes.json") == []
    assert len(load("data/reviewed/sendai-city/assembly/faction_votes.json")) == 576


def test_reviewed_navigation_and_scoped_validation():
    for key in ("miyagi-prefecture", "sendai-city"):
        assert f'key: "{key}"' in DISCOVERY
        assert f'projectRegistry["{key}"].projects.some' in DISCOVERY
        assert f'href: "/municipalities/{key}"' in CATALOG
    assert "validate_miyagi_cluster_data_facts()" in EXPORT
    assert "validate_miyagi_cluster_export()" in EXPORT
    assert "miyagi_cluster_project_detail_files()" in EXPORT
    assert 'aria-labelledby="{re.escape(section_id)}"' in EXPORT
    assert 'record["official_title"] not in section.group(1)' in EXPORT
    assert "27議会" in EXPORT
