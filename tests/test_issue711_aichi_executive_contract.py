"""Issue #711: prepare the Web executive registry for Aichi's data-only term PR."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "apps/web/lib"
WEB = ROOT / "apps/web/app"


def test_aichi_official_code_is_mapped_to_dedicated_page():
    executives = (LIB / "executives.ts").read_text(encoding="utf-8")
    catalog = (LIB / "catalog.ts").read_text(encoding="utf-8")
    assert '"jp-local-230006": "aichi-prefecture"' in executives
    assert '| "aichi-prefecture"' in catalog
    assert '"aichi-prefecture": {' in catalog
    assert 'href: "/municipalities/aichi-prefecture"' in catalog
    assert 'status: "財政データ公開"' in catalog
    assert 'fiscalSummary: "Reviewed 54項目（当初予算3件・決算51件）"' in catalog
    assert (WEB / "municipalities/aichi/page.tsx").exists()
    assert (WEB / "municipalities/aichi-prefecture/page.tsx").exists()


def test_executive_page_does_not_claim_every_term_has_reviewed_promises():
    page = (WEB / "executives/page.tsx").read_text(encoding="utf-8")
    assert "executivesWithReviewedPromises" in page
    assert 'promise.review_status === "reviewed"' in page
    assert 'promisesForExecutive(term).length ? "原文公約登録済み" : "未登録"' in page
    assert "公約が未登録の首長も含みます" in page
    assert "未登録の首長を登録済みとは扱いません" in page
    assert "3首長の原文公約を分割・登録済み" not in page


def test_financial_quality_now_includes_real_aichi_records():
    page = (LIB / "dataQuality.ts").read_text(encoding="utf-8")
    assert 'type FiscalMunicipalityKey = Exclude<MunicipalityKey, "aichi-prefecture">' not in page
    assert '"aichi-prefecture": aichiFinance.records' in page
    assert '"aichi-prefecture": aichiFinance.evidencePackets' in page
    assert '"aichi-prefecture": fukuokaPrefectureFinance.records' not in page


def test_empty_promise_terms_render_status_without_fake_records():
    page = (WEB / "promises/page.tsx").read_text(encoding="utf-8")
    assert 'promisesForExecutive(term).filter(p=>p.review_status==="reviewed")' in page
    assert 'promises.length > 0 ? `Reviewed 公約原文' in page
    assert '"公約原文：未登録"' in page
    assert "promises.length === 0" in page
    assert "公約が存在しない、または公表されていないことを示すものではありません" in page
    assert "公約が未登録の首長" in page
