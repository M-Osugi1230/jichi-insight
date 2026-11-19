"""Issue #692: generic fiscal-detail pages are conditional on Reviewed settlement packages."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
WEB = ROOT / "apps/web"
LOADER = (WEB / "lib/genericCityFinance.ts").read_text(encoding="utf-8")
GATE = (WEB / "lib/municipalityDiscovery.ts").read_text(encoding="utf-8")
PAGE = (WEB / "app/municipalities/[slug]/page.tsx").read_text(encoding="utf-8")
REVIEW = (WEB / "components/FiscalReview.tsx").read_text(encoding="utf-8")
PANEL = (WEB / "components/MunicipalityDiscoveryPanel.tsx").read_text(encoding="utf-8")


def test_existing_phase15_cities_have_no_optional_settlement_package():
    queue = json.loads(
        (DATA / "catalog/phase15_core_capital_review_queue.json").read_text(encoding="utf-8")
    )
    reviewed = [row for row in queue["execution_queue"] if row["status"] == "reviewed_complete"]
    assert len(reviewed) == 67
    for row in reviewed:
        completion_file = Path(row["completion_path"]).name
        slug = completion_file.removesuffix("_phase15_completion.json") + "-city"
        assert not (DATA / "reviewed" / slug / "settlement_records.json").exists(), slug


def test_missing_settlement_does_not_render_or_activate_fiscal_details():
    assert 'if (!fs.existsSync(settlementPath)) return null;' in LOADER
    assert "const fiscalDetail = loadGenericCityFinance(slug);" in PAGE
    assert 'fiscalDetailHref={fiscalDetail ? "#fiscal-detail" : undefined}' in PAGE
    assert "{fiscalDetail ? (" in PAGE
    assert 'id="fiscal-detail"' in PAGE
    assert 'available.finance && Boolean(fiscalDetailHref)' in PANEL
    assert "const hasFinance = city ? loadGenericCityFinance(city.slug) !== null : false;" in GATE
    assert (
        "return { finance: hasFinance, promises: false, assembly: false, "
        "projects: false, key: null };"
    ) in GATE


def test_pilot_package_requires_reviewed_ordinary_settlement_with_evidence():
    assert '"settlement_records.json"' in LOADER
    assert '"settlement_evidence_packets.json"' in LOADER
    assert "municipality.official_code !== city.officialCode" in LOADER
    assert "record.stage !== \"settlement\"" in LOADER
    assert "record.account_type !== \"ordinary\"" in LOADER
    assert "record.review_status !== \"reviewed\"" in LOADER
    assert "!evidenceSubjects.has(record.id)" in LOADER
    assert "if (settlement.length === 0) return null;" in LOADER
    assert 'sources={fiscalDetail.sources}' in PAGE
    assert "sources?: FiscalSource[]" in REVIEW
    assert "matchedSources" in REVIEW


def test_dedicated_three_city_and_other_deep_dive_gates_remain_intact():
    for city in ("fukuoka-prefecture", "fukuoka-city", "kitakyushu-city"):
        page = (WEB / f"app/municipalities/{city}/page.tsx").read_text(encoding="utf-8")
        assert '<div id="fiscal-detail"' in page
        assert "<FiscalReview" in page

    assert 'term.municipality_id === municipality.id' in GATE
    assert 'promise.executive_term_id === term.id' in GATE
    assert 'assembly.assembly.review_status === "reviewed"' in GATE
    assert 'project.review_status === "reviewed"' in GATE
    assert "key: matched" in GATE
