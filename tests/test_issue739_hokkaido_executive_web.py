"""Issue #739: a data-only Hokkaido governor term is safely exposed by Web.

The term and sources are supplied by PR #738. This Web PR must not
fabricate promises or a fiscal detail page before their Reviewed UI exists.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
LIB = ROOT / "apps/web/lib"
APP = ROOT / "apps/web/app"
EXPORT = (ROOT / "scripts/validate_static_export.py").read_text(
    encoding="utf-8"
)


def load(path):
    return json.loads((DATA / path).read_text(encoding="utf-8"))


def test_hokkaido_term_is_reviewed_and_has_no_registered_promises():
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
    assert term["manifesto_source_ids"] == []
    assert not [
        record for record in promises
        if record["municipality_id"] == term["municipality_id"]
        or record["executive_term_id"] == term["id"]
    ]


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


def test_catalog_uses_existing_hokkaido_policy_page_not_fake_fiscal_page():
    catalog = (LIB / "catalog.ts").read_text(encoding="utf-8")
    assert '| "hokkaido-prefecture"' in catalog
    assert '"hokkaido-prefecture": {' in catalog
    assert 'name: "北海道"' in catalog
    assert 'href: "/municipalities/hokkaido"' in catalog
    assert 'status: "資料索引中"' in catalog
    assert "財政詳細ページは未公開" in catalog
    assert (APP / "municipalities/hokkaido/page.tsx").is_file()
    assert not (APP / "municipalities/hokkaido-prefecture/page.tsx").exists()


def test_legacy_financial_quality_does_not_impute_hokkaido_web_data():
    quality = (LIB / "dataQuality.ts").read_text(encoding="utf-8")
    assert 'type FiscalMunicipalityKey = Exclude<MunicipalityKey, "hokkaido-prefecture">' in quality
    assert "Record<FiscalMunicipalityKey," in quality
    assert '"hokkaido-prefecture": aichiFinance.records' not in quality
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
