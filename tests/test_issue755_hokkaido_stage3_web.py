"""Issue #755: stacked stage-three Web registration and municipality-scoped status."""

import json
import runpy
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
WEB = ROOT / "apps/web"
EXECUTIVES = (WEB / "lib/executives.ts").read_text(encoding="utf-8")
CATALOG = (WEB / "lib/catalog.ts").read_text(encoding="utf-8")
QUALITY = (WEB / "lib/dataQuality.ts").read_text(encoding="utf-8")
DISCOVERY = (WEB / "lib/municipalityDiscovery.ts").read_text(encoding="utf-8")
PROMISES = (WEB / "app/promises/page.tsx").read_text(encoding="utf-8")
HOKKAIDO = (WEB / "app/municipalities/hokkaido-prefecture/page.tsx").read_text(
    encoding="utf-8"
)
EXPORT = (ROOT / "scripts/validate_static_export.py").read_text(encoding="utf-8")


def load(relative):
    return json.loads((DATA / relative).read_text(encoding="utf-8"))


def test_governor_and_mayor_registered_promises_match_ground_truth():
    terms = load("entities/executives/executive_terms.json")
    promises = load("entities/executives/promises.json")
    cases = (
        ("010006", "鈴木 直道", 15),
        ("011002", "秋元 克広", 13),
        ("012041", "今津 寛介", 0),
    )
    for code, name, count in cases:
        matches = [t for t in terms if t["municipality_id"] == f"jp-local-{code}"]
        assert len(matches) == 1
        term = matches[0]
        assert term["person_name"] == name
        assert term["review_status"] == "reviewed"
        reviewed = [
            p for p in promises if p["executive_term_id"] == term["id"]
            and p["municipality_id"] == term["municipality_id"]
            and p["review_status"] == "reviewed"
        ]
        assert len(reviewed) == count
        assert bool(term["manifesto_source_ids"]) == (count > 0)


def test_executive_metadata_and_quality_registration():
    for code, slug in (
        ("010006", "hokkaido-prefecture"),
        ("011002", "sapporo-city"),
        ("012041", "asahikawa-city"),
    ):
        assert f'"jp-local-{code}": "{slug}"' in EXECUTIVES
        assert f'"{slug}": {{' in CATALOG
        assert f'"{slug}": ' in QUALITY
    assert '| "sapporo-city"' in CATALOG
    assert '| "asahikawa-city"' in CATALOG
    assert 'href: "/municipalities/sapporo-city"' in CATALOG
    assert 'href: "/municipalities/asahikawa-city"' in CATALOG
    assert "Reviewed 公約13件" in CATALOG
    assert "公約原文は未登録" in CATALOG
    assert (WEB / "app/municipalities/[slug]/page.tsx").is_file()


def test_hokkaido_governor_and_discovery_gates_follow_reviewed_records():
    assert "公約原文15件が段階3で登録済み" in HOKKAIDO
    assert "manifestoSourcesForExecutive(governor)" in HOKKAIDO
    assert "鈴木直道知事の公約原文15件と根拠を見る" in HOKKAIDO
    assert "北海道議会の個別レコードは未登録（段階4で登録予定）" in HOKKAIDO
    assert "知事公約の原文は未登録" not in HOKKAIDO
    assert 'promises: hasPromises, assembly: false, projects: hasProjects' in DISCOVERY
    assert "project.municipality_id ===" in DISCOVERY
    assert "promise.municipality_id === term.municipality_id" in DISCOVERY
    assert 'term.municipality_id === `jp-local-${officialCode}`' in DISCOVERY
    assert "isProjectArea(city.slug)" in DISCOVERY
    assert "promisesForExecutive(term)" in PROMISES


def test_all_three_promise_sections_have_independent_expected_states(tmp_path):
    validator = runpy.run_path(str(ROOT / "scripts/validate_static_export.py"))
    checks = (
        validator["validate_hokkaido_promise_scope"],
        validator["validate_sapporo_promise_scope"],
        validator["validate_asahikawa_promise_scope"],
    )
    output = tmp_path / "promises" / "index.html"
    output.parent.mkdir(parents=True)
    sections = (
        '<section id="hokkaido-prefecture"><h2>北海道・鈴木 直道</h2>'
        '<p>Reviewed 公約原文 15件</p></section>',
        '<section id="sapporo-city"><h2>札幌市・秋元 克広</h2>'
        '<p>Reviewed 公約原文 13件</p></section>',
        '<section id="asahikawa-city"><h2>旭川市・今津 寛介</h2>'
        '<p>公約原文：未登録</p></section>',
    )
    with patch.dict(checks[0].__globals__, {"EXPORT_ROOT": tmp_path}):
        output.write_text("".join(sections), encoding="utf-8")
        assert all(check() == [] for check in checks)

        incorrect = (
            sections[0],
            sections[1],
            sections[2].replace("公約原文：未登録", "Reviewed 公約原文 1件"),
        )
        output.write_text("".join(incorrect), encoding="utf-8")
        assert checks[0]() == []
        assert checks[1]() == []
        assert checks[2]()

        incorrect = (
            sections[0].replace("15件", "14件"),
            sections[1],
            sections[2],
        )
        output.write_text("".join(incorrect), encoding="utf-8")
        assert checks[0]()
        assert checks[1]() == []
        assert checks[2]() == []

        incorrect = (
            sections[0],
            sections[1].replace("13件", "12件"),
            sections[2],
        )
        output.write_text("".join(incorrect), encoding="utf-8")
        assert checks[0]() == []
        assert checks[1]()
        assert checks[2]() == []


def test_export_checks_are_scoped_not_unconditional_unregistered_copy():
    assert '"公約原文：未登録"' not in EXPORT
    assert 'def validate_asahikawa_promise_scope()' in EXPORT
    assert 'def validate_sapporo_promise_scope()' in EXPORT
    assert 'def validate_hokkaido_promise_scope()' in EXPORT
    assert "failures.extend(validate_hokkaido_promise_scope())" in EXPORT
    assert "failures.extend(validate_sapporo_promise_scope())" in EXPORT
    assert "failures.extend(validate_asahikawa_promise_scope())" in EXPORT
    assert '"Reviewed 公約原文：15件"' in EXPORT
