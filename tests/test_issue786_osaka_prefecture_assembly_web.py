"""Issue #786: Osaka cluster dedicated page and stage-four assembly Web registration."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
WEB = ROOT / "apps/web"
REGISTRY = (WEB / "lib/assemblyRegistry.ts").read_text(encoding="utf-8")
DISCOVERY = (WEB / "lib/municipalityDiscovery.ts").read_text(encoding="utf-8")
DETAIL = (WEB / "app/assemblies/[slug]/page.tsx").read_text(encoding="utf-8")
INDEX = (WEB / "app/assemblies/page.tsx").read_text(encoding="utf-8")
OSAKA_PAGE_PATH = WEB / "app/municipalities/osaka-prefecture/page.tsx"
VALIDATOR = (ROOT / "scripts/validate_static_export.py").read_text(encoding="utf-8")


def load(slug, name):
    return json.loads((DATA / "reviewed" / slug / "assembly" / name).read_text(encoding="utf-8"))


def test_osaka_assembly_records_are_reviewed_and_registry_has_twelve_entries():
    for slug, expected in (
        ("osaka-prefecture", (79, 61, 387, 89)),
        ("osaka-city", (26, 26, 260, 37)),
        ("sakai-city", (61, 33, 70, 37)),
    ):
        assembly = load(slug, "assembly_records.json")
        disclosure = load(slug, "disclosure_profiles.json")
        assert len(assembly) == 1 and assembly[0]["review_status"] == "reviewed"
        assert disclosure[0]["review_status"] == "reviewed"
        assert len(load(slug, "proposals.json")) == expected[0]
        assert len(load(slug, "votes.json")) == expected[1]
        assert len(load(slug, "faction_votes.json")) == expected[2]
        assert len(load(slug, "political_activity_expenses.json")) == expected[3]
        assert f'"{slug}": registry(' in REGISTRY
    assert "osakaPrefAssembly" in REGISTRY
    assert "osakaCityAssembly" in REGISTRY
    assert "sakaiAssembly" in REGISTRY
    assert REGISTRY.count('"osaka-prefecture"') >= 2
    assert len([line for line in REGISTRY.splitlines() if line.strip().startswith('"') and 'registry(' in line]) >= 12
    assert '"osaka-prefecture", "osaka-city", "sakai-city"' in REGISTRY


def test_osaka_prefecture_dedicated_page_uses_reviewed_data_and_assembly():
    assert OSAKA_PAGE_PATH.is_file()
    page = OSAKA_PAGE_PATH.read_text(encoding="utf-8")
    assert 'osakaFinance' in page and 'osakaPlanReview' in page
    assert 'projectRegistry["osaka-prefecture"]' in page
    assert 'currentExecutiveTerms.find' in page
    assert 'id="assembly"' in page
    assert 'assemblies["osaka-prefecture"]' in page
    assert "請願第36号" in page
    assert "第1〜4項と第5項" in page
    assert "継続審査中" in page
    assert "89単位" in page


def test_discovery_gates_and_disclosure_copy_are_municipality_specific():
    assert 'assemblies["osaka-prefecture"].assembly.review_status' in DISCOVERY
    assert 'assemblies["osaka-prefecture"].disclosure.review_status' in DISCOVERY
    assert 'assemblies[city.slug].assembly.review_status' in DISCOVERY
    assert 'slug==="osaka-city"' in DETAIL
    assert "個人交付分" in DETAIL and "市会図書室" in DETAIL
    assert 'slug==="sakai-city"' in DETAIL
    assert "主な議案" in DETAIL and "陳情回答綴" in DETAIL
    assert "第1〜4項" in DETAIL and "第5項" in DETAIL
    assert "18件" in DETAIL and "継続審査中" in DETAIL
    assert "12議会" in INDEX
    assert "大阪府議会" in INDEX and "大阪市会" in INDEX and "堺市議会" in INDEX


def test_static_export_validator_requires_osaka_assembly_pages_and_scoped_copy():
    assert "validate_osaka_assembly_scope" in VALIDATOR
    assert "failures.extend(validate_osaka_assembly_scope())" in VALIDATOR
    assert '"公約原文：未登録"' not in VALIDATOR
    assert '"osaka-prefecture", "osaka-city", "sakai-city"' in VALIDATOR
