"""Issue #908: Reviewed Shizuoka Web-finish contracts and source-grounded copy."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "apps" / "web"

def src(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")

def data(path: str):
    return json.loads(src(path))

PROJECT_REGISTRY = src("apps/web/lib/projectRegistry.ts")
ASSEMBLY_REGISTRY = src("apps/web/lib/assemblyRegistry.ts")
PROJECTS = src("apps/web/app/projects/page.tsx")
ASSEMBLIES = src("apps/web/app/assemblies/page.tsx")
ASSEMBLY_DETAIL = src("apps/web/app/assemblies/[slug]/page.tsx")
PREFECTURE = src("apps/web/app/municipalities/shizuoka-prefecture/page.tsx")
CITY_RENDERER = src("apps/web/components/ShizuokaCityReview.tsx")
GENERIC_CITY_ROUTE = src("apps/web/app/municipalities/[slug]/page.tsx")
GATES = src("apps/web/lib/municipalityDiscovery.ts")
CATALOG = src("apps/web/lib/catalog.ts")
EXPORT_VALIDATOR = src("scripts/validate_static_export.py")


def test_registered_pillar_measure_basic_policy_series_and_kpis():
    for slug, code, kpi_count, year, registration_unit in (
        ("shizuoka-prefecture", "220001", 46, 2025, "政策の柱"),
        ("shizuoka-city", "221007", 23, 2026, "施策"),
        ("hamamatsu-city", "221309", 18, 2025, "基本政策"),
    ):
        municipality = data(f"data/reviewed/{slug}/municipality.json")
        projects = data(f"data/reviewed/{slug}/projects.json")
        kpis = data(f"data/reviewed/{slug}/project_kpis.json")
        packets = data(f"data/reviewed/{slug}/project_evidence_packets.json")
        prefix = ("shizuoka" if slug == "shizuoka-prefecture"
                  else "shizuoka_city" if slug == "shizuoka-city" else "hamamatsu_city")
        selection_name = ("shizuoka" if slug == "shizuoka-prefecture" else prefix)
        selection = data(f"data/catalog/{selection_name}_priority_project_selection.json")
        sources = data(f"data/catalog/{prefix}_project_sources.json")
        assert municipality["official_code"] == code
        assert municipality["id"] == f"jp-local-{code}"
        assert municipality["data_status"] == "reviewed"
        assert len(projects) == len(selection["selections"]) == len(packets) == 10
        assert len({record["series_id"] for record in projects}) == 10
        assert len(kpis) == kpi_count
        by_id = {record["id"]: record for record in projects}
        source_ids = {row["id"] for row in sources["records"]}
        assert {packet["subject_id"] for packet in packets} == set(by_id)
        for selected in selection["selections"]:
            record = by_id[selected["project_id"]]
            assert (selected["series_id"], selected["official_title"]) == (
                record["series_id"], record["official_title"])
        for record in projects:
            assert record["fiscal_year"] == year
            assert record["review_status"] == "reviewed"
            assert record["official_evaluation"] is None
            assert all(item["amount_yen"] is None for item in record["budget_records"])
            assert set(record["sources"]).issubset(source_ids)
        assert f'"{slug}": {{ name:' in PROJECT_REGISTRY
        assert f'key === "{slug}"' in PROJECTS
        assert f"登録単位：{registration_unit}" in PROJECTS


def test_plan_scope_and_budget_are_exact_registered_facts():
    expected = (
        ("shizuoka-prefecture", 1_414_100_000_000, 542_000_000_000),
        ("shizuoka-city", 403_500_000_000, 148_938_000_000),
        ("hamamatsu-city", 440_100_000_000, 160_600_000_000),
    )
    for slug, revenue, local_tax in expected:
        budget = data(f"data/reviewed/{slug}/fiscal_records.json")
        amounts = {item["metric"]: item["amount_yen"] for item in budget
                   if item["fiscal_year"] == 2026 and item["stage"] == "initial_budget"}
        assert amounts["total_revenue"] == revenue
        assert amounts["local_tax"] == local_tax
        settlements = data(f"data/reviewed/{slug}/settlement_records.json")
        assert len(settlements) == 51
        assert {item["fiscal_year"] for item in settlements} == {2022, 2023, 2024}
    assert "静岡県総合計画～しずおか ウェルビーイングプラン～" in PREFECTURE
    assert "第5次静岡市総合計画" in CITY_RENDERER
    assert "浜松市総合計画第2期基本計画" in CITY_RENDERER
    assert "政策8本・政策の柱24本・取組197・成果指標101" in PREFECTURE
    assert "9分野・45政策・101施策" in CITY_RENDERER
    assert "7分野・25基本政策・125政策" in CITY_RENDERER


def test_governor_and_mayors_reuse_reviewed_terms_votes_and_promises():
    terms = data("data/entities/executives/executive_terms.json")
    promises = data("data/entities/executives/promises.json")
    packets = data("data/entities/executives/evidence_packets.json")
    for municipality_id, office, name, start, end, vote, count, page in (
        ("jp-local-220001", "governor", "鈴木 康友", "2024-05-26", "2028-05-25", "728,500票", 9, PREFECTURE),
        ("jp-local-221007", "mayor", "難波 喬司", "2023-04-13", "2027-04-12", "149,117票", 3, CITY_RENDERER),
        ("jp-local-221309", "mayor", "中野 祐介", "2023-05-01", "2027-04-30", "246,745票", 10, CITY_RENDERER),
    ):
        term = next(item for item in terms if item["municipality_id"] == municipality_id
                    and item["office"] == office and item["status"] == "current")
        assert (term["person_name"], term["term_start"], term["term_end"]) == (name, start, end)
        assert len([item for item in promises if item["executive_term_id"] == term["id"]
                    and item["review_status"] == "reviewed"]) == count
        packet = next(item for item in packets if item["subject_id"] == term["id"])
        assert vote in next(claim["statement"] for claim in packet["claims"]
                            if claim["field"] == "election_date")
        assert vote in page


def test_assembly_granularity_and_pending_records_are_not_inferred():
    for slug, name, count in (
        ("shizuoka-prefecture", "静岡県議会", 43),
        ("shizuoka-city", "静岡市議会", 56),
        ("hamamatsu-city", "浜松市議会", 69),
    ):
        assembly = data(f"data/reviewed/{slug}/assembly/assembly_records.json")[0]
        proposals = data(f"data/reviewed/{slug}/assembly/proposals.json")
        assert assembly["name"] == name
        assert len(proposals) == count
        assert f'"{slug}": registry(' in ASSEMBLY_REGISTRY
    pref_proposals = data("data/reviewed/shizuoka-prefecture/assembly/proposals.json")
    assert len([p for p in pref_proposals if p["outcome"] == "pending"]) == 17
    assert "未議決（pending）" in PREFECTURE
    pref_disclosure = data("data/reviewed/shizuoka-prefecture/assembly/disclosure_profiles.json")[0]
    note = next(row["note"] for row in pref_disclosure["items"] if row["item"] == "faction_votes")
    assert "本会議の表決そのものの事後記録" in note
    assert "事後記録" in ASSEMBLY_DETAIL
    assert "会派別賛否" in CITY_RENDERER
    assert len(data("data/reviewed/shizuoka-city/assembly/faction_votes.json")) == 495
    hamamatsu_votes = data("data/reviewed/hamamatsu-city/assembly/votes.json")
    assert sum(len(vote.get("member_votes", [])) for vote in hamamatsu_votes) == 2728
    assert data("data/reviewed/hamamatsu-city/assembly/faction_votes.json") == []
    assert "議員別賛否2,728件" in ASSEMBLY_DETAIL
    assert "27議会" in ASSEMBLIES
    assert "27議会の一覧に戻る" in ASSEMBLY_DETAIL


def test_reviewed_gates_generic_city_routes_and_scoped_static_contract():
    assert '{ slug: "shizuoka-city" }' in GENERIC_CITY_ROUTE
    assert '{ slug: "hamamatsu-city" }' in GENERIC_CITY_ROUTE
    assert 'return <ShizuokaCityReview slug={slug} />' in GENERIC_CITY_ROUTE
    for slug in ("shizuoka-prefecture", "shizuoka-city", "hamamatsu-city"):
        assert f'href: "/municipalities/{slug}"' in CATALOG
        assert f'slug: "{slug}"' in GATES
        assert f'"{slug}"' in PROJECT_REGISTRY
    assert 'entry.assembly.id.startsWith(municipalityId + "-assembly-")' in GATES
    assert "27自治体の Reviewed 事業レコード" in PROJECTS
    assert "def shizuoka_cluster_project_detail_files()" in EXPORT_VALIDATOR
    assert "def validate_shizuoka_cluster_data_facts()" in EXPORT_VALIDATOR
    assert "def validate_shizuoka_cluster_export()" in EXPORT_VALIDATOR
    assert "_shizuoka_scoped_text" in EXPORT_VALIDATOR
    assert 'record["official_title"] not in project_section' in EXPORT_VALIDATOR
    assert "27議会" in EXPORT_VALIDATOR
    sitemap = src("apps/web/app/sitemap.ts")
    for slug in ("shizuoka-prefecture", "shizuoka-city", "hamamatsu-city"):
        assert f'"/municipalities/{slug}"' in sitemap
