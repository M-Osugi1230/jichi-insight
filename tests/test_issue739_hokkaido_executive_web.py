"""Issue #739: a data-only Hokkaido governor term is safely exposed by Web.

The term and sources are supplied by PR #738. This Web PR must not
fabricate promises or a fiscal detail page before their Reviewed UI exists.
"""

import json
import runpy
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
LIB = ROOT / "apps/web/lib"
APP = ROOT / "apps/web/app"
EXPORT = (ROOT / "scripts/validate_static_export.py").read_text(
    encoding="utf-8"
)


def load(path):
    return json.loads((DATA / path).read_text(encoding="utf-8"))


def test_hokkaido_term_is_reviewed_and_promises_registered_in_stage3():
    # Stage 1 (Issue #737/#739) registered the term with no manifesto
    # source; stage 3 (Issue #749) registered the official 2023
    # election bulletin and 15 promise records, superseding the
    # earlier unregistered state this test originally pinned.
    terms = load("entities/executives/executive_terms.json")
    promises = load("entities/executives/promises.json")
    hokkaido = [term for term in terms if term["municipality_id"] == "jp-local-010006"]
    assert len(hokkaido) == 1
    term = hokkaido[0]
    assert term["person_name"] == "鈴木 直道"
    assert term["office"] == "governor"
    assert term["status"] == "current"
    assert term["term_start"] == "2023-04-23"
    assert term["term_end"] == "2027-04-22"
    assert term["review_status"] == "reviewed"
    assert term["manifesto_source_ids"] == [
        "hokkaido-pref-governor-election-2023-bulletin"
    ]
    registered = [
        record for record in promises
        if record["municipality_id"] == term["municipality_id"]
        or record["executive_term_id"] == term["id"]
    ]
    assert len(registered) == 15


def test_executive_registry_maps_all_six_existing_and_hokkaido():
    page = (LIB / "executives.ts").read_text(encoding="utf-8")
    for code, key in (
        ("010006", "hokkaido-prefecture"),
        ("230006", "aichi-prefecture"),
        ("400009", "fukuoka-prefecture"),
        ("401307", "fukuoka-city"),
        ("401005", "kitakyushu-city"),
        ("231002", "nagoya-city"),
        ("232114", "toyota-city"),
    ):
        assert f'"jp-local-{code}": "{key}"' in page
    assert "currentExecutiveTerms = executiveTerms as ExecutiveTerm[]" in page
    assert "executiveMunicipality(term)" in (
        APP / "executives/page.tsx"
    ).read_text(encoding="utf-8")


def test_catalog_links_published_hokkaido_detail_and_keeps_policy_page():
    catalog = (LIB / "catalog.ts").read_text(encoding="utf-8")
    assert '| "hokkaido-prefecture"' in catalog
    assert '"hokkaido-prefecture": {' in catalog
    assert 'name: "北海道"' in catalog
    assert 'href: "/municipalities/hokkaido-prefecture"' in catalog
    assert 'status: "財政データ公開"' in catalog
    assert "Reviewed 54項目（当初予算3件・決算51件）" in catalog
    assert (APP / "municipalities/hokkaido/page.tsx").is_file()
    assert (APP / "municipalities/hokkaido-prefecture/page.tsx").is_file()


def test_hokkaido_financial_quality_counts_real_reviewed_web_data():
    quality = (LIB / "dataQuality.ts").read_text(encoding="utf-8")
    assert (
        'type FiscalMunicipalityKey = Exclude<MunicipalityKey, "hokkaido-prefecture">'
        not in quality
    )
    assert '"hokkaido-prefecture": hokkaidoFinance.records' in quality
    assert '"hokkaido-prefecture": hokkaidoFinance.evidencePackets' in quality
    assert '"aichi-prefecture": aichiFinance.records' in quality
    assert '"toyota-city": toyotaCityFinance.records' in quality


def test_static_copy_preserves_hokkaido_unregistered_promise_status():
    page = (APP / "promises/page.tsx").read_text(encoding="utf-8")
    executive = (APP / "executives/page.tsx").read_text(encoding="utf-8")
    assert 'promisesForExecutive(term).filter(p=>p.review_status==="reviewed")' in page
    assert "promises.length > 0" in page
    assert '"公約原文：未登録"' in page
    assert "promises.length === 0" in page
    assert 'promisesForExecutive(term).length ? "原文公約登録済み" : "未登録"' in executive
    assert '"北海道・鈴木 直道"' in EXPORT
    assert 'def validate_hokkaido_promise_scope()' in EXPORT
    assert "failures.extend(validate_hokkaido_promise_scope())" in EXPORT
    assert 'expected_status = "公約原文：" + "未登録"' in EXPORT
    assert '"公約原文：未登録"' not in EXPORT
    assert '"北海道・知事"' in EXPORT
    assert '"2023年4月23日"' in EXPORT


def test_hokkaido_export_scope_rejects_other_municipality_unregistered_copy(tmp_path):
    validator = runpy.run_path(str(ROOT / "scripts/validate_static_export.py"))
    check = validator["validate_hokkaido_promise_scope"]
    output = tmp_path / "promises" / "index.html"
    output.parent.mkdir(parents=True)

    other_section = (
        '<section id="toyota-city"><h2>豊田市・太田 稔彦</h2>'
        '<p>公約原文：未登録</p></section>'
    )
    hokkaido_section = (
        '<section class="area" id="hokkaido-prefecture">'
        '<h2>北海道・鈴木 直道</h2><p>{status}</p></section>'
    )

    with patch.dict(check.__globals__, {"EXPORT_ROOT": tmp_path}):
        output.write_text(
            other_section + hokkaido_section.format(status="Reviewed 公約原文 1件"),
            encoding="utf-8",
        )
        assert any("unregistered" in msg for msg in check())

        output.write_text(
            other_section + hokkaido_section.format(status="公約原文：未登録"),
            encoding="utf-8",
        )
        assert check() == []

        output.write_text(other_section, encoding="utf-8")
        assert any("missing the Hokkaido section" in msg for msg in check())
