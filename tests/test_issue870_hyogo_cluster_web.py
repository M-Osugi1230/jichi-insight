"""Issue #870: Hyogo dedicated page and reviewed stage 3/4 web contracts."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "apps" / "web"
PAGE = (
    WEB / "app" / "municipalities" / "hyogo-prefecture" / "page.tsx"
).read_text(encoding="utf-8")
REGISTRY = (WEB / "lib" / "assemblyRegistry.ts").read_text(encoding="utf-8")
INDEX = (WEB / "app" / "assemblies" / "page.tsx").read_text(encoding="utf-8")
DETAIL = (WEB / "app" / "assemblies" / "[slug]" / "page.tsx").read_text(encoding="utf-8")
DISCOVERY = (WEB / "lib" / "municipalityDiscovery.ts").read_text(encoding="utf-8")
CATALOG = (WEB / "lib" / "catalog.ts").read_text(encoding="utf-8")
EXPORT = (ROOT / "scripts" / "validate_static_export.py").read_text(encoding="utf-8")


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_plan_and_finance_copy_agree_with_registered_hyogo_facts():
    plan = load("data/reviewed/hyogo-prefecture/plan_review.json")
    texts = " ".join(row["statement"] for row in plan["records"])
    assert "ひょうごビジョン2050" in texts
    assert "兵庫県地域創生戦略" in texts
    assert "3つの柱" in texts
    assert "8つの方向性" in texts
    fiscal = load("data/reviewed/hyogo-prefecture/fiscal_records.json")
    settlement = load("data/reviewed/hyogo-prefecture/settlement_records.json")
    assert len(fiscal) == 3
    assert len(settlement) == 51
    assert {row["fiscal_year"] for row in settlement} == {2022, 2023, 2024}
    assert "ひょうごビジョン2050" in PAGE
    assert "第三期" in PAGE
    assert "hyogoFinance.records.length" in PAGE
    assert "settlements.length" in PAGE
    assert "Reviewed 重点事業" in PAGE
    assert 'projectHref="#priority-projects"' in PAGE


def test_executive_terms_votes_and_promises_are_verbatim_reviewed_facts():
    terms = load("data/entities/executives/executive_terms.json")
    promises = load("data/entities/executives/promises.json")
    packets = load("data/entities/executives/evidence_packets.json")
    rows = (
        ("jp-local-280003", "governor", "斎藤 元彦", "2024-11-17", "2028-11-16", "1,113,911票", 18),
        ("jp-local-281000", "mayor", "久元 喜造", "2025-11-20", "2029-11-19", "275,273票", 28),
    )
    for municipality_id, office, name, start, end, vote, count in rows:
        term = next(
            t for t in terms
            if t["municipality_id"] == municipality_id
            and t["office"] == office and t["status"] == "current"
        )
        assert (term["person_name"], term["term_start"], term["term_end"]) == (name, start, end)
        assert len([
            p for p in promises
            if p["executive_term_id"] == term["id"] and p["review_status"] == "reviewed"
        ]) == count
        evidence = next(p for p in packets if p["subject_id"] == term["id"])
        assert vote in next(
            c["statement"] for c in evidence["claims"] if c["field"] == "election_date"
        )
        assert vote in PAGE
    assert "governorPromises.length" in PAGE
    assert "mayorPromises.length" in PAGE
    assert 'href="/promises#hyogo-prefecture"' in PAGE
    assert 'href="/promises#kobe-city"' in PAGE


def test_assembly_registry_has_22_reviewed_assemblies_and_source_scope():
    for slug, name, count in (
        ("hyogo-prefecture", "兵庫県議会", 103),
        ("kobe-city", "神戸市会", 79),
    ):
        records = load(f"data/reviewed/{slug}/assembly/assembly_records.json")
        proposals = load(f"data/reviewed/{slug}/assembly/proposals.json")
        assert records[0]["name"] == name
        assert records[0]["review_status"] == "reviewed"
        assert len(proposals) == count
        assert f'"{slug}": registry(' in REGISTRY
        assert f'"{slug}"' in REGISTRY[REGISTRY.index("export const assemblySlugs"):]
    assert "24議会" in INDEX
    assert "神戸市会" in INDEX
    assert "24議会の一覧に戻る" in DETAIL
    assert 'href: "/municipalities/hyogo-prefecture"' in CATALOG


def test_prefecture_faction_attitude_is_not_conflated_with_roll_call():
    disclosure = load("data/reviewed/hyogo-prefecture/assembly/disclosure_profiles.json")[0]
    note = next(row["note"] for row in disclosure["items"] if row["item"] == "faction_votes")
    assert "表決そのものの記録ではなく" in note
    assert "採決に先立って" in note
    assert "議会事務局が集約した" in note
    for phrase in ("表決そのものの記録ではなく", "採決に先立って", "議会事務局が集約した"):
        assert phrase in PAGE
        assert phrase in DETAIL
    assert "voteDisclosure?.note" in PAGE
    assert "現員82人" in DETAIL


def test_reviewed_gates_and_section_scoped_static_assertions():
    assert 'key: "hyogo-prefecture", finance: hasFinance' in DISCOVERY
    assert 'key: "kobe-city", finance:' in DISCOVERY
    assert "hasReviewedExecutivePromises(municipalityId)" in DISCOVERY
    assert "assembly: hasAssembly, projects: hasProjects" in DISCOVERY
    assert "def validate_hyogo_web_finish_data_facts()" in EXPORT
    assert "def validate_hyogo_web_finish_export()" in EXPORT
    assert "validate_hyogo_web_finish_data_facts()" in EXPORT
    assert "validate_hyogo_web_finish_export()" in EXPORT
    assert "aria-labelledby" in EXPORT
    assert "section.group(1)" in EXPORT
    assert "24議会" in EXPORT
