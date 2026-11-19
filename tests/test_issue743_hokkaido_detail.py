"""Issue #743: the Reviewed Hokkaido plan, fiscal and governor detail is published."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
WEB = ROOT / "apps/web"
FINANCE = (WEB / "lib/hokkaidoFinance.ts").read_text(encoding="utf-8")
CATALOG = (WEB / "lib/catalog.ts").read_text(encoding="utf-8")
QUALITY = (WEB / "lib/dataQuality.ts").read_text(encoding="utf-8")
DISCOVERY = (WEB / "lib/municipalityDiscovery.ts").read_text(encoding="utf-8")
PAGE = (WEB / "app/municipalities/hokkaido-prefecture/page.tsx").read_text(
    encoding="utf-8"
)
EXPORT = (ROOT / "scripts/validate_static_export.py").read_text(encoding="utf-8")


def load(relative):
    return json.loads((DATA / relative).read_text(encoding="utf-8"))


def test_real_finance_and_evidence_have_three_initial_and_51_settlement_records():
    base = "reviewed/hokkaido-prefecture"
    budget = load(f"{base}/fiscal_records.json")
    settlement = load(f"{base}/settlement_records.json")
    evidence = load(f"{base}/evidence_packets.json")
    settlement_evidence = load(f"{base}/settlement_evidence_packets.json")
    assert len(budget) == 3
    assert len(settlement) == 51
    assert len(evidence) == 3
    assert len(settlement_evidence) == 51
    assert all(
        x["review_status"] == "reviewed" and x["municipality_id"] == "jp-local-010006"
        for x in budget + settlement
    )
    assert all(
        x["stage"] == "initial_budget"
        and x["account_type"] == "general"
        and x["fiscal_year"] == 2026
        for x in budget
    )
    assert all(
        x["stage"] == "settlement"
        and x["account_type"] == "ordinary"
        and x["fiscal_year"] in (2022, 2023, 2024)
        for x in settlement
    )
    assert {x["subject_id"] for x in evidence + settlement_evidence} == {
        x["id"] for x in budget + settlement
    }
    assert 'data/reviewed/hokkaido-prefecture/settlement_records.json' in FINANCE
    assert 'data/reviewed/hokkaido-prefecture/settlement_evidence_packets.json' in FINANCE


def test_plan_review_and_governor_are_reviewed_without_imputed_promises():
    plan = load("reviewed/hokkaido-prefecture/plan_review.json")
    assert plan["review_status"] == "reviewed"
    assert len(plan["records"]) == 4
    assert all(record["decision"] == "accepted" for record in plan["records"])
    assert "hokkaidoPlanReview.records" in PAGE
    for metric in ("total_revenue", "local_tax", "total_expenditure"):
        assert f'hokkaidoBudgetRecord("{metric}")' in PAGE
    assert '<FiscalReview municipality="北海道"' in PAGE
    assert 'id="fiscal-detail"' in PAGE
    assert 'fiscalDetailHref="#fiscal-detail"' in PAGE
    assert "term.municipality_id === hokkaidoFinance.municipality.id" in PAGE
    assert "governorPromises.length > 0" in PAGE
    assert "公約原文：未登録" in PAGE
    assert "段階3で登録予定" in PAGE
    assert "段階4で登録予定" in PAGE
    assert "重点事業は段階2で登録中" in PAGE
    assert "hokkaidoFinanceSources.map" in PAGE
    assert (WEB / "app/municipalities/hokkaido/page.tsx").exists()


def test_catalog_quality_discovery_and_static_copy_are_real_and_differentiated():
    assert 'href: "/municipalities/hokkaido-prefecture"' in CATALOG
    assert '"hokkaido-prefecture": hokkaidoFinance.records' in QUALITY
    assert '"hokkaido-prefecture": hokkaidoFinance.evidencePackets' in QUALITY
    assert '"hokkaido-prefecture": "北海道"' in QUALITY
    assert 'officialCode === hokkaidoFinance.municipality.official_code' in DISCOVERY
    assert 'promises: false, assembly: false, projects: false' in DISCOVERY
    assert '"municipalities/hokkaido-prefecture/index.html"' in EXPORT
    assert '"2026年3月19日に原案可決"' in EXPORT
    assert '"北海道議会の個別レコードは未登録"' in EXPORT
    assert 'hokkaido_prefecture_finance_sources.json' in CATALOG
    assert 'hokkaido_prefecture_finance_sources.json' in EXPORT
    assert '"公約原文：未登録"' not in EXPORT
