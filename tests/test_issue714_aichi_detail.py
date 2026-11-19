"""Issue #714 — Aichi detail page uses reviewed records without inventing promises."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
WEB = ROOT / "apps/web"
FINANCE = (WEB / "lib/aichiFinance.ts").read_text(encoding="utf-8")
CATALOG = (WEB / "lib/catalog.ts").read_text(encoding="utf-8")
QUALITY = (WEB / "lib/dataQuality.ts").read_text(encoding="utf-8")
PAGE = (WEB / "app/municipalities/aichi-prefecture/page.tsx").read_text(
    encoding="utf-8"
)
DISCOVERY = (WEB / "lib/municipalityDiscovery.ts").read_text(encoding="utf-8")


def test_real_finance_records_and_evidence_are_wired():
    root = DATA / "reviewed/aichi-prefecture"
    budget = json.loads((root / "fiscal_records.json").read_text(encoding="utf-8"))
    settlements = json.loads(
        (root / "settlement_records.json").read_text(encoding="utf-8")
    )
    budget_packets = json.loads(
        (root / "evidence_packets.json").read_text(encoding="utf-8")
    )
    settlement_packets = json.loads(
        (root / "settlement_evidence_packets.json").read_text(encoding="utf-8")
    )
    assert len(budget) == 3
    assert len(settlements) == 51
    assert len(budget_packets) == 3
    assert len(settlement_packets) == 51
    assert all(
        record["review_status"] == "reviewed"
        and record["municipality_id"] == "jp-local-230006"
        for record in budget + settlements
    )
    assert all(
        item["review_status"] == "reviewed"
        and item["stage"] == "settlement"
        and item["account_type"] == "ordinary"
        and item["fiscal_year"] in (2022, 2023, 2024)
        for item in settlements
    )
    assert 'data/reviewed/aichi-prefecture/settlement_records.json' in FINANCE
    assert 'data/reviewed/aichi-prefecture/settlement_evidence_packets.json' in FINANCE


def test_page_has_plan_budget_three_year_finance_governor_and_sources():
    assert "aichiPlanReview.records" in PAGE
    assert 'aichiBudgetRecord("total_revenue")' in PAGE
    assert 'aichiBudgetRecord("local_tax")' in PAGE
    assert 'aichiBudgetRecord("total_expenditure")' in PAGE
    assert 'id="fiscal-detail"' in PAGE
    assert '<FiscalReview municipality="愛知県"' in PAGE
    assert 'fiscalDetailHref="#fiscal-detail"' in PAGE
    assert 'term.municipality_id === aichiFinance.municipality.id' in PAGE
    assert 'governorPromises.length > 0' in PAGE
    assert "公約原文：未登録" in PAGE
    assert "県議会の個別レコードが未登録" in PAGE
    assert "aichiFinanceSources.map" in PAGE
    assert (WEB / "app/municipalities/aichi/page.tsx").exists()


def test_catalog_quality_and_discovery_are_not_overclaimed():
    assert 'href: "/municipalities/aichi-prefecture"' in CATALOG
    assert 'fiscalSummary: "Reviewed 54項目（当初予算3件・決算51件）"' in CATALOG
    assert '"aichi-prefecture": aichiFinance.records' in QUALITY
    assert '"aichi-prefecture": aichiFinance.evidencePackets' in QUALITY
    assert 'officialCode === aichiFinance.municipality.official_code' in DISCOVERY
    assert "promises: false, assembly: false, projects: false" in DISCOVERY
