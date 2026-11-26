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
    registry_entries = [
        line for line in REGISTRY.splitlines()
        if line.strip().startswith('"') and "registry(" in line
    ]
    assert len(registry_entries) >= 12
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
    assert "37議会" in INDEX
    registry = (WEB / "lib/assemblyRegistry.ts").read_text(encoding="utf-8")
    assert "osaka-prefecture" in registry and "osaka-city" in registry
    assert "sakai-city" in registry
    for slug, name in (
        ("osaka-prefecture", "大阪府議会"),
        ("osaka-city", "大阪市会"),
        ("sakai-city", "堺市議会"),
    ):
        records = json.loads(
            (DATA / f"reviewed/{slug}/assembly/assembly_records.json").read_text(
                encoding="utf-8"
            )
        )
        assert any(record["name"] == name for record in records)


def test_static_export_validator_requires_osaka_assembly_pages_and_scoped_copy():
    assert "validate_osaka_assembly_scope" in VALIDATOR
    assert "failures.extend(validate_osaka_assembly_scope())" in VALIDATOR
    assert '"公約原文：未登録"' not in VALIDATOR
    assert '"osaka-prefecture", "osaka-city", "sakai-city"' in VALIDATOR

def test_osaka_prefecture_page_matches_reviewed_plan_promises_and_project_selection():
    page = OSAKA_PAGE_PATH.read_text(encoding="utf-8")
    projects = json.loads(
        (DATA / "reviewed/osaka-prefecture/projects.json").read_text(encoding="utf-8")
    )
    selection = json.loads(
        (DATA / "catalog/osaka_priority_project_selection.json").read_text(encoding="utf-8")
    )
    plan = json.loads(
        (DATA / "reviewed/osaka-prefecture/plan_review.json").read_text(encoding="utf-8")
    )
    promises = json.loads(
        (DATA / "entities/executives/promises.json").read_text(encoding="utf-8")
    )
    osaka_promises = [
        item for item in promises
        if item["municipality_id"] == "jp-local-270008"
        and item["review_status"] in {"reviewed", "verified"}
    ]

    # Promise count must match the actual reviewed source records, not copied Hokkaido text.
    assert len(osaka_promises) == 7
    assert "公約原文7件" in page
    assert "公約原文15件" not in page

    # The ten selected Osaka project series have no published official assessment.
    assert len(projects) == 10
    assert all(project["official_evaluation"] is None for project in projects)
    assert "事業単位の公式評価は公表されていません" in page
    assert "一次政策評価" not in page
    assert "総合判定" not in page

    # Population and selection rule must reproduce the reviewed 52-project universe.
    assert selection["population"]["project_count"] == 52
    assert len(selection["selections"]) == 10
    assert "府政運営の基本方針2026" in page
    assert "第2「知事重点事業」の52件" in page
    assert "柱1→柱2→柱3" in page
    assert "柱1の第4分野" in selection["selection_rule"]["description"]
    assert "10件に到達" in selection["selection_rule"]["description"]
    assert "構成予算事業費の合算" in page
    assert "重点事業単位の総額は一覧自体に印字されていません" in page
    assert all(
        "構成予算事業" in project["budget_records"][0]["note"]
        and "一覧は知事重点事業単位の総額を印字していない" in project["budget_records"][0]["note"]
        for project in projects
    )

    # The page must follow the actual Osaka plan review: joint Vision, revised March 2023,
    # with annual basic policy and governor-priority projects as its implementation layer.
    accepted = [record for record in plan["records"] if record["decision"] == "accepted"]
    identity = next(
        record for record in accepted
        if record["evidence_role"] == "current_plan_identity"
    )
    implementation = next(
        record for record in accepted
        if record["evidence_role"] == "implementation_layer"
    )
    assert "副首都ビジョン" in identity["statement"]
    assert "2023年3月の改定版" in identity["statement"]
    assert "府政運営の基本方針" in implementation["statement"]
    assert "知事重点事業" in implementation["statement"]
    assert "副首都ビジョン" in page
    assert "2023年3月改定版" in page
    assert "府政運営の基本方針" in page
    assert "大阪府総合計画" not in page
    assert "2024年7月策定" not in page
    assert "2024年度から概ね10年間" not in page

    # Guard against copied Hokkaido-specific policy and evaluation terminology.
    for forbidden in ("道政", "道による", "基本評価調書", "121施策"):
        assert forbidden not in page
